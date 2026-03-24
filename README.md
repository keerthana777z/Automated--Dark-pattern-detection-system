# 🚀 Automated Dark Pattern Detection & Monitoring System

## 📌 Overview

This project presents an end-to-end **Explainable AI system** designed to detect **dark patterns in websites** using Natural Language Processing and automation.

It goes beyond simple classification by integrating:

* Real-time web scraping
* Context-aware NLP (BERT)
* Severity-based scoring
* Automated monitoring pipeline
* Interactive analytics dashboard

The system enables continuous monitoring of websites to identify manipulative UI/UX practices at scale.

---

## 🎯 Key Features

* 🔍 **Real-time Website Scraping** using Selenium
* 🧠 **BERT-based Multi-class Classification** (8 dark pattern categories)
* ⚖️ **Severity-weighted Manipulation Score**
* 🧩 **Explainable AI (Attention-based Token Importance)**
* 📊 **Interactive Dashboard (Streamlit)**
* ⚙️ **FastAPI Backend for Automation**
* 🔁 **n8n Workflow Automation (Scheduled Monitoring)**
* 🗄️ **SQLite Database for Historical Tracking**

---

## 🧠 Problem Statement

Dark patterns are deceptive design practices used in websites to manipulate user behavior (e.g., hidden costs, forced continuity, misdirection).

Traditional detection methods:

* ❌ Rule-based → not scalable
* ❌ Manual → time-consuming

👉 This project solves it using **AI + automation + monitoring**

---

## 🏗️ System Architecture

```
n8n Scheduler (every 2 mins)
        ↓
FastAPI (/run-monitor)
        ↓
Web Scraping (Selenium)
        ↓
BERT Classification + Explainability
        ↓
Severity-weighted Scoring
        ↓
SQLite Database
        ↓
Streamlit Dashboard (Visualization)
```

---

## ⚙️ Tech Stack

| Layer      | Technology               |
| ---------- | ------------------------ |
| NLP Model  | BERT (Transformers)      |
| Backend    | FastAPI                  |
| Frontend   | Streamlit                |
| Scraping   | Selenium + BeautifulSoup |
| Automation | n8n (Docker)             |
| Database   | SQLite                   |
| Deployment | Docker                   |

---

## 📊 Model Details

* Model: `bert-base-uncased`
* Task: Multi-class classification (8 categories)
* Dataset Size: ~3,868 samples
* Training:

  * Epochs: 3
  * Batch Size: 8
  * Learning Rate: 2e-5
  * Stratified Split: 80-20

### 📈 Performance

* Accuracy: ~90–92%
* F1 Score: ~89–91%

---

## ⚖️ Manipulation Scoring System

The system computes a **severity-weighted score**:

[
Score = \frac{\sum (confidence × severity_weight)}{total_snippets}
]

Each dark pattern category is assigned a weight:

* Forced Continuity → High impact
* Hidden Costs → High
* Misdirection → Medium

👉 This makes the system **business-relevant**, not just ML-based.

---

## 📊 Dashboard Features

* 🔎 Manual website analysis
* 📈 Time-series trend analysis
* 📦 Dark pattern distribution
* 🚨 Risk classification (Low / Moderate / High)
* 🧾 Token-level explanation
* 🔁 Monitoring management (Add / Pause / Delete)

---

## 🔁 Automation (n8n)

* Runs every **2 minutes**
* Calls API endpoint `/run-monitor`
* Automatically:

  * Scrapes websites
  * Performs analysis
  * Stores results

👉 Enables **continuous real-time monitoring**

---

## ▶️ How to Run

### 1️⃣ Clone Repository

```bash
git clone https://github.com/keerthana777z/Automated--Dark-pattern-detection-system.git
cd Automated--Dark-pattern-detection-system
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Train Model

```bash
python train_bert.py
```

---

### 4️⃣ Run Dashboard

```bash
streamlit run app.py
```

---

### 5️⃣ Run Backend API

```bash
uvicorn api_server:app --reload
```

---

### 6️⃣ Start n8n (Automation)

```bash
docker-compose up
```

Open:

```
http://localhost:5678
```

---

## 📁 Project Structure

```
project/
│── app.py                  # Streamlit dashboard
│── analyzer.py             # NLP + scraping logic
│── monitor.py              # Monitoring pipeline
│── api_server.py           # FastAPI backend
│── database.py             # SQLite operations
│── train_bert.py           # Model training
│── severity_weights.json   # Scoring weights
│── model/                  # Trained model (ignored in repo)
│── docker-compose.yml      # n8n setup
```

---

## ⚠️ Notes

* The `model/` folder is excluded from GitHub
* Train the model locally before running
* Chrome must be installed for Selenium

---

## 🚀 Future Enhancements

* 🖼️ Multimodal detection (UI + text)
* 🌐 Browser extension
* 📢 Alert system for risk spikes
* ☁️ Cloud deployment

---

## 💡 Key Highlights

✔ End-to-end AI system (not just a model)
✔ Real-time automation pipeline
✔ Explainable AI integration
✔ Production-ready architecture

---

## 👩‍💻 Author

**Keerthana A.R.**

