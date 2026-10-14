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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegúrese de que el CSV esté en la carpeta output
CORPUS_PATH = os.path.join(BASE_DIR, "output", "corpus_definitivo_v3.csv")
RESULTADOS_PATH = os.path.join(BASE_DIR, "output", "training_results_v5")

os.makedirs(RESULTADOS_PATH, exist_ok=True)

# --- CAMBIO AL MODELO NATIVO EN ESPAÑOL (BETO) ---
PREENTRENO_MODELO = "dccuchile/bert-base-spanish-wwm-cased"
MAX_TOKEN_LEN     = 128
VENTANA_MENSAJES  = 5
BATCH_SIZE        = 32

# --- HIPERPARÁMETROS OPTIMIZADOS ---
NUM_EPOCAS        = 20      # Más tiempo para aprender patrones complejos
APRENDIZAJE_RATE  = 1e-5    # Tasa más suave para evitar inestabilidad en las últimas épocas
LORA_R            = 32      # Mayor capacidad de representación matricial
LORA_ALPHA        = 64      # Escalado ajustado al nuevo R
LORA_DROPOUT      = 0.1
# -----------------------------------

NUM_CLASES        = 3
SEM_RANDOM        = 42

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Dispositivo: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")


def construir_ventanas(datos, ventana=VENTANA_MENSAJES):
    print(f"\n  Construyendo ventanas de {ventana} mensajes...")
    filas = []

    for id_bloque, grupo in datos.groupby("id_bloque"):
        grupo     = grupo.sort_values("orden_mensaje").reset_index(drop=True)
        mensajes  = grupo["texto_mensaje"].tolist()
        etiquetas = grupo["nivel_riesgo"].tolist()
        emisores  = grupo["emisor"].tolist()

        for i in range(len(mensajes)):
            inicio         = max(0, i - ventana + 1)
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


def cargar_datos(ruta_corpus):
    print("\n[1/5] Cargando corpus y separando por conversaciones...")
    datos = pd.read_csv(ruta_corpus, encoding="utf-8-sig")
    datos = datos.dropna(subset=["texto_mensaje", "nivel_riesgo"]).copy()
    datos["nivel_riesgo"] = datos["nivel_riesgo"].astype(int)

    # 1. Identificar el riesgo máximo de cada conversación para estratificar
    riesgo_por_bloque = datos.groupby('id_bloque')['nivel_riesgo'].max().reset_index()
    
    # 2. Separar IDs de conversaciones en Train y Val (80/20)
    train_ids, val_ids = train_test_split(
        riesgo_por_bloque['id_bloque'],
        test_size=0.2,
        stratify=riesgo_por_bloque['nivel_riesgo'],
        random_state=SEM_RANDOM
    )

    # 3. Filtrar los DataFrames originales usando los IDs aislados
    df_train_full = datos[datos['id_bloque'].isin(train_ids)].copy()
    df_val_full = datos[datos['id_bloque'].isin(val_ids)].copy()

    # 4. Construir las ventanas respetando la integridad de la conversación
    print("\n -> Procesando Train Set:")
    df_train = construir_ventanas(df_train_full)
    print("\n -> Procesando Validation Set:")
    df_val = construir_ventanas(df_val_full) # Validación se queda intacta para reflejar la realidad

    # 5. Balanceo suave (Eliminamos el undersampling de clase baja)
    clase_baja  = df_train[df_train.nivel_riesgo == 0]
    clase_media = df_train[df_train.nivel_riesgo == 1]
    clase_alta  = df_train[df_train.nivel_riesgo == 2]

    # Clonamos ligeramente el Nivel 2 solo si es menor al Nivel 1 para darles el mismo peso
    if len(clase_alta) < len(clase_media):
        clase_alta = clase_alta.sample(n=len(clase_media), replace=True, random_state=SEM_RANDOM)

    # Concatenamos usando TODA la clase baja
    df_train_bal = pd.concat([clase_baja, clase_media, clase_alta]).sample(frac=1, random_state=SEM_RANDOM).reset_index(drop=True)
    
    print(f"\n  Split Final Limpio -> Train: {len(df_train_bal):,} ventanas | Val: {len(df_val):,} ventanas")

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
    plt.title("ANIMOON - F1 Macro y Loss (BETO + LoRA + Ventana)")
    plt.xlabel("Epoch")
    plt.ylabel("Score / Loss")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(RESULTADOS_PATH, "historial_entrenamiento.png")
    plt.savefig(ruta)
    plt.close()


def entrenar():
    df_train_bal, df_val_bal = cargar_datos(CORPUS_PATH)

    textos_train    = df_train_bal["texto_ventana"].tolist()
    etiquetas_train = df_train_bal["nivel_riesgo"].tolist()
    textos_val      = df_val_bal["texto_ventana"].tolist()
    etiquetas_val   = df_val_bal["nivel_riesgo"].tolist()

    print(f"\n[2/5] Descargando {PREENTRENO_MODELO} y configurando LoRA...")
    tokenizer   = BertTokenizer.from_pretrained(PREENTRENO_MODELO)
    modelo_base = BertForSequenceClassification.from_pretrained(
        PREENTRENO_MODELO,
        num_labels=NUM_CLASES,
        use_safetensors=True
    )

    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["query", "value"],
        modules_to_save=["classifier", "pooler"],
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

    class OrdinalLoss(nn.Module):
        def __init__(self, pesos):
            super().__init__()
            self.ce = nn.CrossEntropyLoss(weight=pesos)
            self.mse = nn.MSELoss()
            
        def forward(self, logits, targets):
            loss_ce = self.ce(logits, targets)
            probs = torch.softmax(logits, dim=1)
            valores_predichos = probs[:, 0]*0 + probs[:, 1]*1 + probs[:, 2]*2
            loss_mse = self.mse(valores_predichos, targets.float())
            return loss_ce + (loss_mse * 0.3)

    perdida_fn = OrdinalLoss(pesos_tensor)
    optimizador = AdamW(modelo.parameters(), lr=APRENDIZAJE_RATE, weight_decay=0.01)

    pasos_totales = len(loader_train) * NUM_EPOCAS
    scheduler     = get_linear_schedule_with_warmup(
        optimizador,
        num_warmup_steps=pasos_totales // 10,
        num_training_steps=pasos_totales
    )

    print(f"\n[4/5] Entrenando {NUM_EPOCAS} epochs con LoRA...")
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