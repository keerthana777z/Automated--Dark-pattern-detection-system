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


MODEL_PATH = "model/bert_model"

tokenizer = BertTokenizer.from_pretrained(MODEL_PATH)
model = BertForSequenceClassification.from_pretrained(
    MODEL_PATH,
    output_attentions=True
)

model.eval()
device = torch.device("cpu")
model.to(device)

with open(f"{MODEL_PATH}/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

with open("severity_weights.json", "r") as f:
    severity_weights = json.load(f)


def analyze_website(url):

    # ✅ FIXED SELENIUM SETUP
    options = Options()

    # ❌ REMOVE Linux path (IMPORTANT)
    # options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless=new")   # better for Mac
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ AUTO DRIVER DOWNLOAD
    service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # 🔽 SCRAPING
    driver.get(url)
    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    tags = ["p","span","button","a","li","h1","h2","h3"]
    snippets = []

    for tag in tags:
        for element in soup.find_all(tag):
            text = element.get_text(strip=True)
            if text and len(text.split()) > 2:
                snippets.append(text)

    snippets = list(set(snippets))

    predictions = []

    for text in snippets:

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        inputs = {k: v.to(device) for k,v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            attentions = outputs.attentions

        probs = torch.softmax(logits,dim=1).cpu().numpy()[0]

        pred_id = int(np.argmax(probs))
        confidence = float(probs[pred_id])
        label = label_encoder.inverse_transform([pred_id])[0]

        # 🔽 ATTENTION-BASED EXPLAINABILITY
        last_layer_attention = attentions[-1]
        avg_attention = last_layer_attention.mean(dim=1).squeeze()
        token_importance = avg_attention.mean(dim=0)

        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        token_scores = list(zip(tokens, token_importance.cpu().numpy()))

        filtered_tokens = [
            tok for tok,_ in token_scores
            if tok not in ["[CLS]","[SEP]"] and not tok.startswith("##")
        ][:5]

        class_probs = {
            label_encoder.classes_[i]: float(probs[i])
            for i in range(len(probs))
        }

        predictions.append({
            "text": text,
            "label": label,
            "confidence": confidence,
            "tokens": filtered_tokens,
            "probabilities": class_probs
        })

    # 🔽 FILTER DARK PATTERNS
    dark_predictions = [
        p for p in predictions if p["label"] != "Not Dark Pattern"
    ]

    # 🔥 SEVERITY-WEIGHTED SCORING
    weighted_sum = 0

    for p in dark_predictions:
        weight = severity_weights.get(p["label"],0.7)
        weighted_sum += p["confidence"] * weight

    manipulation_score = (
        weighted_sum / len(snippets) if len(snippets)>0 else 0
    )

    label_counts = Counter([p["label"] for p in dark_predictions])

    # 🔽 RISK CLASSIFICATION
    if manipulation_score < 0.1:
        risk_level = "LOW"
    elif manipulation_score < 0.25:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    return {
        "total_snippets": len(snippets),
        "dark_count": len(dark_predictions),
        "score": manipulation_score,
        "risk_level": risk_level,
        "category_breakdown": dict(label_counts),
        "dark_snippets": dark_predictions
    }