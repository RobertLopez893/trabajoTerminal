import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score
)

CORPUS_PATH      = "./output/corpus_final.csv"
RESULTADOS_PATH  = "./output/training_results"
os.makedirs(RESULTADOS_PATH, exist_ok=True)

PREENTRENO_MODELO = "bert-base-multilingual-cased"
MAX_TOKEN_LEN     = 128
BATCH_SIZE        = 32
NUM_EPOCAS        = 4
APRENDIZAJE_RATE  = 2e-5
NUM_CLASES        = 3
SEM_RANDOM        = 42
CAP_CLASE_BAJA    = 5_000
GOAL_CLASES       = 4_000

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


def cargar_balancear(ruta_corpus):
    print("\n[1/5] Cargando y balanceando corpus...")
    datos = pd.read_csv(ruta_corpus, encoding="utf-8-sig")
    datos = datos.dropna(subset=["texto_mensaje", "nivel_riesgo"]).copy()
    datos["nivel_riesgo"] = datos["nivel_riesgo"].astype(int)

    print(f"  Total original: {len(datos):>10,} mensajes")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n = (datos.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:>10,}  ({n/len(datos)*100:.1f}%)")

    clase_baja  = datos[datos.nivel_riesgo == 0]
    clase_media = datos[datos.nivel_riesgo == 1]
    clase_alta  = datos[datos.nivel_riesgo == 2]

    muestra_baja = clase_baja.sample(
        n=min(CAP_CLASE_BAJA, len(clase_baja)),
        random_state=SEM_RANDOM
    )
    muestra_media = clase_media.sample(
        n=GOAL_CLASES,
        replace=True,
        random_state=SEM_RANDOM
    )
    muestra_alta = clase_alta.sample(
        n=GOAL_CLASES,
        replace=True,
        random_state=SEM_RANDOM
    )

    balanceado = pd.concat(
        [muestra_baja, muestra_media, muestra_alta]
    ).sample(frac=1, random_state=SEM_RANDOM).reset_index(drop=True)

    print(f"\n  Corpus balanceado: {len(balanceado):,} mensajes")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n = (balanceado.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:>8,}")

    return balanceado


class ConversacionDataset(Dataset):
    def __init__(self, mensajes, etiquetas, tokenizer, max_len):
        self.mensajes  = mensajes
        self.etiquetas = etiquetas
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.mensajes)

    def __getitem__(self, idx):
        tokens = self.tokenizer(
            str(self.mensajes[idx]),
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids":      tokens["input_ids"].squeeze(),
            "attention_mask": tokens["attention_mask"].squeeze(),
            "etiqueta":       torch.tensor(self.etiquetas[idx], dtype=torch.long)
        }


def evaluar(modelo, loader):
    modelo.eval()
    predicciones = []
    reales       = []

    with torch.no_grad():
        for batch in loader:
            ids     = batch["input_ids"].to(device)
            mascara = batch["attention_mask"].to(device)
            labels  = batch["etiqueta"].to(device)

            salidas = modelo(input_ids=ids, attention_mask=mascara)
            preds   = torch.argmax(salidas.logits, dim=1)

            predicciones.extend(preds.cpu().numpy())
            reales.extend(labels.cpu().numpy())

    return np.array(reales), np.array(predicciones)


def mostrar_metricas(reales, predicciones, epoca):
    nombres_clases = ["Bajo (0)", "Medio (1)", "Alto (2)"]
    print(f"\n  Epoch {epoca}")
    print(classification_report(reales, predicciones, target_names=nombres_clases, digits=4))

    f1_macro = f1_score(reales, predicciones, average="macro")
    print(f"  F1 Macro: {f1_macro:.4f}")

    return f1_macro


def guardar_matriz_confusion(reales, predicciones, epoca):
    matriz         = confusion_matrix(reales, predicciones)
    nombres_clases = ["Bajo (0)", "Medio (1)", "Alto (2)"]

    plt.figure(figsize=(7, 5))
    sns.heatmap(matriz, annot=True, fmt="d", cmap="Blues",
                xticklabels=nombres_clases,
                yticklabels=nombres_clases)
    plt.title(f"Matriz de Confusion - Epoch {epoca}")
    plt.ylabel("Etiqueta real")
    plt.xlabel("Etiqueta predicha")
    plt.tight_layout()

    ruta = os.path.join(RESULTADOS_PATH, f"confusion_epoch{epoca}.png")
    plt.savefig(ruta)
    plt.close()


def guardar_grafica_f1(historial):
    epochs = range(1, len(historial["f1_macro"]) + 1)

    plt.figure(figsize=(8, 4))
    plt.plot(epochs, historial["f1_macro"], marker="o",
             color="green", linewidth=2, label="F1 Macro")
    plt.plot(epochs, historial["loss"], marker="s", linestyle="--",
             color="steelblue", linewidth=2, label="Loss")
    plt.title("ANIMOON - F1 Macro y Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Score / Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(RESULTADOS_PATH, "historial_entrenamiento.png")
    plt.savefig(ruta)
    plt.close()


def entrenar():
    datos = cargar_balancear(CORPUS_PATH)

    mensajes_train, mensajes_val, etiquetas_train, etiquetas_val = train_test_split(
        datos["texto_mensaje"].tolist(),
        datos["nivel_riesgo"].tolist(),
        test_size=0.2,
        stratify=datos["nivel_riesgo"],
        random_state=SEM_RANDOM
    )
    print(f"\n  Train: {len(mensajes_train):,} | Validacion: {len(mensajes_val):,}")

    print(f"\n[2/5] Descargando {PREENTRENO_MODELO}...")
    tokenizer = BertTokenizer.from_pretrained(PREENTRENO_MODELO)
    modelo    = BertForSequenceClassification.from_pretrained(
        PREENTRENO_MODELO,
        num_labels=NUM_CLASES
    )
    modelo.to(device)

    print("\n[3/5] Preparando DataLoaders...")
    dataset_train = ConversacionDataset(mensajes_train, etiquetas_train, tokenizer, MAX_TOKEN_LEN)
    dataset_val   = ConversacionDataset(mensajes_val,   etiquetas_val,   tokenizer, MAX_TOKEN_LEN)

    loader_train = DataLoader(dataset_train, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=2, pin_memory=True)
    loader_val   = DataLoader(dataset_val,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=2, pin_memory=True)

    pesos = compute_class_weight(
        class_weight="balanced",
        classes=np.array([0, 1, 2]),
        y=etiquetas_train
    )
    pesos_tensor = torch.tensor(pesos, dtype=torch.float).to(device)
    print(f"\n  Pesos -> Bajo: {pesos[0]:.3f} | Medio: {pesos[1]:.3f} | Alto: {pesos[2]:.3f}")

    perdida_fn  = nn.CrossEntropyLoss(weight=pesos_tensor)
    optimizador = AdamW(modelo.parameters(), lr=APRENDIZAJE_RATE, weight_decay=0.01)

    pasos_totales = len(loader_train) * NUM_EPOCAS
    scheduler     = get_linear_schedule_with_warmup(
        optimizador,
        num_warmup_steps=pasos_totales // 10,
        num_training_steps=pasos_totales
    )

    print(f"\n[4/5] Entrenando {NUM_EPOCAS} epochs...")
    mejor_f1  = 0.0
    historial = {"loss": [], "f1_macro": []}

    for epoca in range(1, NUM_EPOCAS + 1):
        print(f"\n{'━'*45}")
        print(f"  Epoch {epoca}/{NUM_EPOCAS}")
        print(f"{'━'*45}")

        modelo.train()
        loss_acumulado = 0.0

        for batch in tqdm(loader_train, desc=f"  Epoch {epoca}"):
            ids     = batch["input_ids"].to(device)
            mascara = batch["attention_mask"].to(device)
            labels  = batch["etiqueta"].to(device)

            optimizador.zero_grad()
            salidas = modelo(input_ids=ids, attention_mask=mascara)
            loss    = perdida_fn(salidas.logits, labels)
            loss.backward()

            nn.utils.clip_grad_norm_(modelo.parameters(), max_norm=1.0)

            optimizador.step()
            scheduler.step()
            loss_acumulado += loss.item()

        loss_promedio = loss_acumulado / len(loader_train)
        print(f"\n  Loss epoch {epoca}: {loss_promedio:.4f}")

        reales, predicciones = evaluar(modelo, loader_val)
        f1_macro             = mostrar_metricas(reales, predicciones, epoca)
        guardar_matriz_confusion(reales, predicciones, epoca)

        historial["loss"].append(loss_promedio)
        historial["f1_macro"].append(f1_macro)

        if f1_macro > mejor_f1:
            mejor_f1    = f1_macro
            ruta_modelo = os.path.join(RESULTADOS_PATH, "mejor_modelo")
            modelo.save_pretrained(ruta_modelo)
            tokenizer.save_pretrained(ruta_modelo)
            print(f"\n  Mejor modelo guardado (F1 Macro: {mejor_f1:.4f})")

    print(f"\n[5/5] Guardando grafica...")
    guardar_grafica_f1(historial)

    print(f"\n{'━'*45}")
    print(f"  Entrenamiento completo")
    print(f"  Mejor F1 Macro : {mejor_f1:.4f}")
    print(f"  Modelo en      : {RESULTADOS_PATH}/mejor_modelo/")
    print(f"{'━'*45}")


if __name__ == "__main__":
    entrenar()