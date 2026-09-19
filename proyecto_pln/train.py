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
from peft import (
    get_peft_model,
    LoraConfig,
    TaskType
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score
)

CORPUS_PATH       = "./output/corpus_final.csv"
RESULTADOS_PATH   = "./output/training_results"
os.makedirs(RESULTADOS_PATH, exist_ok=True)

PREENTRENO_MODELO = "bert-base-multilingual-cased"
MAX_TOKEN_LEN     = 128
VENTANA_MENSAJES  = 5
BATCH_SIZE        = 32
NUM_EPOCAS        = 4
APRENDIZAJE_RATE  = 2e-5
NUM_CLASES        = 3
SEM_RANDOM        = 42
CAP_CLASE_BAJA    = 5_000
GOAL_CLASES       = 4_000

LORA_R            = 8
LORA_ALPHA        = 16
LORA_DROPOUT      = 0.1

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


def construir_ventanas(datos, ventana=VENTANA_MENSAJES):
    print(f"\n  Construyendo ventanas de {ventana} mensajes...")
    filas = []

    for id_bloque, grupo in datos.groupby("id_bloque"):
        grupo = grupo.sort_values("orden_mensaje").reset_index(drop=True)
        mensajes   = grupo["texto_mensaje"].tolist()
        etiquetas  = grupo["nivel_riesgo"].tolist()
        emisores   = grupo["emisor"].tolist()

        for i in range(len(mensajes)):
            inicio  = max(0, i - ventana + 1)
            ventana_textos = []
            for j in range(inicio, i + 1):
                ventana_textos.append(f"{emisores[j]}: {mensajes[j]}")
            texto_ventana = " | ".join(ventana_textos)
            filas.append({
                "texto_ventana": texto_ventana,
                "nivel_riesgo":  etiquetas[i]
            })

    df_ventanas = pd.DataFrame(filas)
    print(f"  Ventanas construidas: {len(df_ventanas):,}")
    return df_ventanas


def balancear_train(df_train):
    clase_baja  = df_train[df_train.nivel_riesgo == 0]
    clase_media = df_train[df_train.nivel_riesgo == 1]
    clase_alta  = df_train[df_train.nivel_riesgo == 2]

    muestra_baja = clase_baja.sample(
        n=min(CAP_CLASE_BAJA, len(clase_baja)),
        random_state=SEM_RANDOM
    )
    muestra_media = clase_media.sample(
        n=min(GOAL_CLASES, len(clase_media)),
        replace=len(clase_media) < GOAL_CLASES,
        random_state=SEM_RANDOM
    )
    muestra_alta = clase_alta.sample(
        n=min(GOAL_CLASES, len(clase_alta)),
        replace=len(clase_alta) < GOAL_CLASES,
        random_state=SEM_RANDOM
    )

    balanceado = pd.concat(
        [muestra_baja, muestra_media, muestra_alta]
    ).sample(frac=1, random_state=SEM_RANDOM).reset_index(drop=True)

    return balanceado


def cargar_datos(ruta_corpus):
    print("\n[1/5] Cargando corpus...")
    datos = pd.read_csv(ruta_corpus, encoding="utf-8-sig")
    datos = datos.dropna(subset=["texto_mensaje", "nivel_riesgo"]).copy()
    datos["nivel_riesgo"] = datos["nivel_riesgo"].astype(int)

    print(f"  Total: {len(datos):,} mensajes")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n = (datos.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:,}  ({n/len(datos)*100:.1f}%)")

    df_ventanas = construir_ventanas(datos)

    df_train, df_val = train_test_split(
        df_ventanas,
        test_size=0.2,
        stratify=df_ventanas["nivel_riesgo"],
        random_state=SEM_RANDOM
    )

    print(f"\n  Split sobre datos reales:")
    print(f"  Train: {len(df_train):,} | Validacion: {len(df_val):,}")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n_t = (df_train.nivel_riesgo == nivel).sum()
        n_v = (df_val.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: train={n_t:>6,}  val={n_v:>5,}")

    df_train_bal = balancear_train(df_train)

    print(f"\n  Train balanceado: {len(df_train_bal):,} mensajes")
    for nivel, nombre in [(0, "Bajo  "), (1, "Medio "), (2, "Alto  ")]:
        n = (df_train_bal.nivel_riesgo == nivel).sum()
        print(f"  Clase {nivel} {nombre}: {n:,}")

    return df_train_bal, df_val


class VentanaDataset(Dataset):
    def __init__(self, textos, etiquetas, tokenizer, max_len):
        self.textos    = textos
        self.etiquetas = etiquetas
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.textos)

    def __getitem__(self, idx):
        tokens = self.tokenizer(
            str(self.textos[idx]),
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
    plt.title("ANIMOON - F1 Macro y Loss (LoRA + Ventana)")
    plt.xlabel("Epoch")
    plt.ylabel("Score / Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(RESULTADOS_PATH, "historial_entrenamiento.png")
    plt.savefig(ruta)
    plt.close()


def entrenar():
    df_train_bal, df_val = cargar_datos(CORPUS_PATH)

    textos_train   = df_train_bal["texto_ventana"].tolist()
    etiquetas_train = df_train_bal["nivel_riesgo"].tolist()
    textos_val     = df_val["texto_ventana"].tolist()
    etiquetas_val  = df_val["nivel_riesgo"].tolist()

    print(f"\n[2/5] Descargando {PREENTRENO_MODELO} y configurando LoRA...")
    tokenizer = BertTokenizer.from_pretrained(PREENTRENO_MODELO)
    modelo_base = BertForSequenceClassification.from_pretrained(
        PREENTRENO_MODELO,
        num_labels=NUM_CLASES
    )

    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["query", "value"],
        bias="none"
    )
    modelo = get_peft_model(modelo_base, lora_config)
    modelo.to(device)

    params_totales     = sum(p.numel() for p in modelo.parameters())
    params_entrenables = sum(p.numel() for p in modelo.parameters() if p.requires_grad)
    print(f"\n  Parametros totales    : {params_totales:,}")
    print(f"  Parametros LoRA       : {params_entrenables:,}  ({params_entrenables/params_totales*100:.2f}%)")

    print("\n[3/5] Preparando DataLoaders...")
    dataset_train = VentanaDataset(textos_train, etiquetas_train, tokenizer, MAX_TOKEN_LEN)
    dataset_val   = VentanaDataset(textos_val,   etiquetas_val,   tokenizer, MAX_TOKEN_LEN)

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

    print(f"\n[4/5] Entrenando {NUM_EPOCAS} epochs con LoRA...")
    print(f"  Ventana de analisis: {VENTANA_MENSAJES} mensajes")
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