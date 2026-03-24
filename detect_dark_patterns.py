import sys
import torch
import pickle
import numpy as np
import json
from collections import Counter

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup
from transformers import BertTokenizer, BertForSequenceClassification

# ===============================
# 1. CHECK COMMAND-LINE INPUT
# ===============================

if len(sys.argv) != 2:
    print("Usage: python detect_dark_patterns.py <URL>")
    sys.exit(1)

URL = sys.argv[1]

# ===============================
# 2. LOAD TRAINED MODEL & ENCODER
# ===============================

MODEL_PATH = "model/bert_model"

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(
    MODEL_PATH,
    output_attentions=True
)

model.eval()

with open(f"{MODEL_PATH}/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

device = torch.device("cpu")
model.to(device)

# ===============================
# 3. LOAD SEVERITY WEIGHTS
# ===============================

with open("severity_weights.json", "r") as f:
    severity_weights = json.load(f)

# ===============================
# 4. WEB SCRAPING
# ===============================

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

driver.get(URL)
html = driver.page_source
driver.quit()

soup = BeautifulSoup(html, "html.parser")

tags = ["p", "span", "button", "a", "li", "h1", "h2", "h3"]
snippets = []

for tag in tags:
    for element in soup.find_all(tag):
        text = element.get_text(strip=True)
        if text and len(text.split()) > 2:
            snippets.append(text)

snippets = list(set(snippets))

print(f"\nURL: {URL}")
print(f"Total snippets extracted: {len(snippets)}")

# ===============================
# 5. BERT INFERENCE + ATTENTION
# ===============================

predictions = []

for text in snippets:

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        attentions = outputs.attentions

    probs = torch.softmax(logits, dim=1).cpu().numpy()[0]

    pred_id = int(np.argmax(probs))
    confidence = float(probs[pred_id])
    label = label_encoder.inverse_transform([pred_id])[0]

    # ---- Clean Attention Explanation ----
    last_layer_attention = attentions[-1]
    avg_attention = last_layer_attention.mean(dim=1).squeeze()
    token_importance = avg_attention.mean(dim=0)

    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    token_scores = list(zip(tokens, token_importance.cpu().numpy()))

    # Remove special and subword tokens
    filtered_tokens = [
        (tok, score) for tok, score in token_scores
        if tok not in ["[CLS]", "[SEP]"] and not tok.startswith("##")
    ]

    top_tokens = sorted(filtered_tokens, key=lambda x: x[1], reverse=True)[:5]

    predictions.append((text, label, confidence, top_tokens))

# ===============================
# 6. SCORING LOGIC (CONFIDENCE × SEVERITY)
# ===============================

dark_predictions = [
    (t, l, c, tok) for t, l, c, tok in predictions if l != "Not Dark Pattern"
]

dark_count = len(dark_predictions)
total_count = len(snippets)

weighted_sum = 0

for t, l, c, tok in dark_predictions:
    weight = severity_weights.get(l, 0.7)
    weighted_sum += c * weight

manipulation_score = weighted_sum / total_count if total_count > 0 else 0

label_counts = Counter([l for _, l, _, _ in dark_predictions])

# ===============================
# 7. RISK LEVEL INTERPRETATION
# ===============================

if manipulation_score < 0.1:
    risk_level = "LOW"
elif manipulation_score < 0.25:
    risk_level = "MODERATE"
else:
    risk_level = "HIGH"

# ===============================
# 8. OUTPUT
# ===============================

print(f"\nDark pattern snippets detected: {dark_count}")
print(f"Manipulation Score: {manipulation_score:.3f} ({risk_level})")

print("\nCategory Breakdown:")
for label, count in label_counts.items():
    print(f"- {label}: {count}")

print("\nTop Manipulative Snippets with Explanation:\n")

dark_predictions = sorted(
    dark_predictions, key=lambda x: x[2], reverse=True
)

for text, label, conf, tokens in dark_predictions[:5]:
    print(f"[{label} | Confidence: {conf:.2f}]")
    print("Snippet:", text)
    print("Key Influential Tokens:", [tok for tok, _ in tokens])
    print("-" * 60)