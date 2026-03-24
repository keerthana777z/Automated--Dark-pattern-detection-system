import pandas as pd
import numpy as np
import torch
import os
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    Trainer,
    TrainingArguments
)
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""


# =====================================================
# 1. LOAD DATA (FROM R-PROCESSED OUTPUT)
# =====================================================

DATA_PATH = "../data/processed/cleaned_dark_patterns.csv"

df = pd.read_csv(DATA_PATH)

print("Initial dataset shape:", df.shape)
print(df.head())

# =====================================================
# 2. HARD TEXT SANITIZATION (CRITICAL FIX)
# =====================================================

def safe_text(x):
    if x is None:
        return ""
    if not isinstance(x, str):
        return ""
    x = x.strip()
    if x == "":
        return ""
    if x.lower() in ["nan", "none", "null"]:
        return ""
    return x

df["clean_text"] = df["clean_text"].apply(safe_text)

# Drop invalid rows
df = df[df["clean_text"] != ""].reset_index(drop=True)

print("Dataset shape after sanitization:", df.shape)

# =====================================================
# 3. LABEL ENCODING
# =====================================================

label_encoder = LabelEncoder()
df["label_id"] = label_encoder.fit_transform(df["label"])

num_labels = len(label_encoder.classes_)
print("Number of classes:", num_labels)

# Save label encoder
os.makedirs("bert_model", exist_ok=True)
with open("bert_model/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# =====================================================
# 4. TRAIN–VALIDATION SPLIT
# =====================================================

X_train, X_val, y_train, y_val = train_test_split(
    df["clean_text"],
    df["label_id"],
    test_size=0.2,
    stratify=df["label_id"],
    random_state=42
)

# =====================================================
# 5. TOKENIZATION (PYTHON 3.13 SAFE)
# =====================================================

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

train_texts = X_train.astype(str).tolist()
val_texts   = X_val.astype(str).tolist()

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=128
)

val_encodings = tokenizer(
    val_texts,
    truncation=True,
    padding=True,
    max_length=128
)

# =====================================================
# 6. TORCH DATASET
# =====================================================

class DarkPatternDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels.reset_index(drop=True)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels.iloc[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = DarkPatternDataset(train_encodings, y_train)
val_dataset = DarkPatternDataset(val_encodings, y_val)

# =====================================================
# 7. LOAD BERT MODEL
# =====================================================

model = BertForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=num_labels
)

# =====================================================
# 8. TRAINING CONFIG
# =====================================================

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir="./logs",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to="none",
    no_cuda=True   
)


# =====================================================
# 9. METRICS
# =====================================================

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    return {"accuracy": accuracy_score(labels, preds)}

# =====================================================
# 10. TRAINER
# =====================================================

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# =====================================================
# 11. TRAIN MODEL
# =====================================================

trainer.train()

# =====================================================
# 12. FINAL EVALUATION
# =====================================================

preds_output = trainer.predict(val_dataset)
preds = np.argmax(preds_output.predictions, axis=1)

print("\nClassification Report:\n")
print(
    classification_report(
        y_val,
        preds,
        target_names=label_encoder.classes_
    )
)

# =====================================================
# 13. SAVE MODEL
# =====================================================

model.save_pretrained("bert_model")
tokenizer.save_pretrained("bert_model")

print("\n✅ BERT training completed successfully")
