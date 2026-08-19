import os

import numpy as np
import pandas as pd
from datasets import Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


MODEL_NAME = "distilbert-base-uncased"
DATASET_PATH = "training/dataset.csv"
OUTPUT_DIR = "models/lgs-requirement-classifier"


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(
    DATASET_PATH,
    encoding="utf-8-sig"
)

df.columns = df.columns.str.strip()

print("Columns found:", df.columns.tolist())
print(df.head())

if "text" not in df.columns or "label" not in df.columns:
    raise ValueError(
        f"Dataset must contain 'text' and 'label' columns. "
        f"Found: {df.columns.tolist()}"
    )

labels = sorted(df["label"].unique())

labels = sorted(df["label"].unique())

label2id = {
    label: index
    for index, label in enumerate(labels)
}

id2label = {
    index: label
    for label, index in label2id.items()
}

df["label"] = df["label"].map(label2id)

print("\nClasses:")
for label, index in label2id.items():
    print(f"{index}: {label}")


# ============================================================
# TRAIN / VALIDATION SPLIT
# ============================================================

train_df, validation_df = train_test_split(
    df,
    test_size=0.25,
    random_state=42,
    stratify=df["label"]
)

train_dataset = Dataset.from_pandas(
    train_df.reset_index(drop=True)
)

validation_dataset = Dataset.from_pandas(
    validation_df.reset_index(drop=True)
)


# ============================================================
# TOKENIZER
# ============================================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)


def tokenize(batch):
    return tokenizer(
        batch["text"],
        padding="max_length",
        truncation=True,
        max_length=128
    )


train_dataset = train_dataset.map(
    tokenize,
    batched=True
)

validation_dataset = validation_dataset.map(
    tokenize,
    batched=True
)


# ============================================================
# MODEL
# ============================================================

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id
)


# ============================================================
# EVALUATION METRICS
# ============================================================

def compute_metrics(eval_pred):

    predictions, labels_true = eval_pred

    predictions = np.argmax(
        predictions,
        axis=1
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            labels_true,
            predictions,
            average="weighted",
            zero_division=0
        )
    )

    accuracy = accuracy_score(
        labels_true,
        predictions
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


# ============================================================
# TRAINING CONFIGURATION
# ============================================================

training_args = TrainingArguments(
    output_dir="training/results",
    num_train_epochs=6,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_steps=1,
    report_to="none"
)


# ============================================================
# TRAIN
# ============================================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=validation_dataset,
    compute_metrics=compute_metrics
)

print("\nStarting Transformer fine-tuning...\n")

trainer.train()


# ============================================================
# EVALUATE
# ============================================================

print("\nEvaluating model...\n")

results = trainer.evaluate()

print("\nEvaluation Results")
print("------------------")

for key, value in results.items():

    if isinstance(value, float):
        print(f"{key}: {value:.4f}")

    else:
        print(f"{key}: {value}")


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

trainer.save_model(
    OUTPUT_DIR
)

tokenizer.save_pretrained(
    OUTPUT_DIR
)

print(
    f"\nModel saved to: {OUTPUT_DIR}"
)