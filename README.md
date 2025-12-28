# 🏦 Enterprise Banking AI Agent

A full-stack, privacy-first banking assistant capable of routing **77 distinct banking intents**.

This project implements a **Hybrid AI Architecture** that combines **BERT-based Intent Classification**, **Named Entity Recognition (NER)**, and **Retrieval Augmented Generation (RAG)** to handle both transactional commands and policy questions with high precision.

Unlike standard chatbots, this agent features a **Real SQL Transaction Ledger**, meaning it actually checks balances, deducts funds, and logs transfers in a local database.

---

## 🚀 Key Features

* **Hybrid Intelligence:** Dynamically switches between **Action Execution** (e.g., transfers, freezing cards) and **Knowledge Retrieval** (e.g., explaining fees).
* **Real SQL Ledger:** Integrated `SQLite` database that persists user balances and transaction history. It is not just text; it is a real banking backend.
* **Deterministic Logic Router:** A custom-built Python router that prioritizes critical banking actions over general chit-chat to prevent hallucinations.
* **Local & Secure:** Runs entirely on CPU (No OpenAI/Google API keys required). Perfect for banking compliance where data cannot leave the premise.
* **Heuristic Intent Correction:** A custom logic layer that fixes model ambiguity (e.g., distinguishing "Transfer to Saketh" from general complaints).

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **Containerization:** Docker
* **Database:** SQLite (Built-in, zero config)
* **ML Models:**
    * *Intent:* Fine-tuned `distilbert-base-uncased` on the **Banking77** dataset.
    * *NER:* `dslim/bert-base-NER` for extracting Names (`PER`) and Amounts.
    * *Embeddings:* `sentence-transformers/all-MiniLM-L6-v2`.
* **Vector DB:** FAISS (for high-speed RAG retrieval).
* **Frontend:** HTML5, CSS3, Vanilla JavaScript.

---

## 🧠 System Architecture

The system uses a pipeline of specialized engines:

1.  **The Dispatcher (Intent Model):** Instantly classifies the user's text into one of 77 categories.
2.  **The Extractor (NER Model):** Scans the text for critical details like **Names** (Who to pay?) or **Dates**.
3.  **The Logic Router:** The "Brain" that decides:
    * *Critical Action?* → **Execute SQL Transaction** (via `database.py`).
    * *Policy Question?* → **Trigger RAG Search** (via `rag_engine.py`).
4.  **The Vault (Database):** A persistent storage layer that tracks the user's $5,000 starting balance and logs every successful transfer.

---

## ☁️ Enterprise Deployment Guide (AWS EC2 + Docker)

This guide covers deploying the agent on a production Linux server.

### 1. Infrastructure Requirements
* **Cloud Provider:** AWS EC2 (or any VPS)
* **OS:** Ubuntu 24.04 LTS
* **Instance Size:** `t3.small` (2 vCPU, 2GB RAM)
* **Ports:** Open `22` (SSH) and `8000` (HTTP)
* **Network:** Elastic IP (Static IP) recommended for stability.

### 2. Server Provisioning (Anti-Crash Setup)
Since AI models are memory-intensive, we must first enable "Swap Memory" to prevent the server from freezing during the build process.

```bash
# SSH into your instance
ssh -i "your-key.pem" ubuntu@your-ip

# Create 4GB of Swap (Emergency RAM)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Installation
```bash
# 1. Install Docker & Utilities
sudo apt update
sudo apt install -y docker.io python3-pip unzip

# 2. Clone the Repository
git clone [https://github.com/yourusername/banking-agent.git](https://github.com/yourusername/banking-agent.git)
cd banking-agent
```

### 4. Model Hydration (Host Side)
To keep the Docker image light and stable, we download the AI models on the host machine first and then mount them.

```bash
# Install temporary download tools
pip install --break-system-packages transformers huggingface_hub torch

# A. Download NER Model (Reliable Version)
# Note: We use dslim/bert-base-NER to avoid authentication errors
python3 -c "from transformers import AutoTokenizer, AutoModelForTokenClassification; import os; os.makedirs('models/ner', exist_ok=True); AutoTokenizer.from_pretrained('dslim/bert-base-NER').save_pretrained('models/ner'); AutoModelForTokenClassification.from_pretrained('dslim/bert-base-NER').save_pretrained('models/ner')"

# B. Download Intent Model
wget [https://github.com/Saketh2611/fine_tune_BERT/releases/download/v1.0/banking_intent_model.zip](https://github.com/Saketh2611/fine_tune_BERT/releases/download/v1.0/banking_intent_model.zip)
unzip -o banking_intent_model.zip -d models/intent/
```

### 5. Launch Application
Build the container and run it. We use a volume (`-v`) to persist the database so user data survives restarts.

```bash
# Build the Image
sudo docker build -t banking-agent .

# Run the Container (Restart Always ensures 100% Uptime)
sudo docker run -d \
  -p 8000:8000 \
  -v $(pwd)/banking_system.db:/app/banking_system.db \
  --restart always \
  --name bank-app \
  banking-agent
```

**Your agent is now live at:** `http://YOUR_ELASTIC_IP:8000`

---

## 🧪 Testing Guide (Example Queries)

Once the system is running, try these queries to test different parts of the architecture.

### ✅ Test 1: Real Transactions (SQL + NER)
* **User:** "Transfer $100 to John."
    * **Result:** "✅ Success! Sent $100.0 to John. New Balance: $4900.00"
    * **Mechanism:** Extracts Entity ("John") → Updates SQL DB → Returns Confirmation.

* **User:** "Transfer $10,000 to Sarah."
    * **Result:** "❌ Insufficient Funds. Your balance is $4900.00"
    * **Mechanism:** Checks SQL DB Balance → Rejects Transaction.

### ✅ Test 2: Critical Safety Rules (Rule Engine)
* **User:** "I lost my card!"
    * **Result:** "🚨 **SECURITY ALERT:** I have temporarily frozen your account..."
    * **Mechanism:** Triggers `lost_or_stolen_card` intent → Hardcoded Safety Block.

### ✅ Test 3: Policy Knowledge (RAG System)
* **User:** "What is the fee for international transfers?"
    * **Result:** "Policy Info: International transaction fees are 3%..."
    * **Mechanism:** Triggers `exchange_rate` intent → Searches Vector DB → Returns Text.

---

## 📂 Project Structure

```text
banking_agent/
├── app.py                 # Main FastAPI application & Logic Router
├── database.py            # SQLite Manager (The Bank Vault)
├── rag_engine.py          # RAG Class for handling FAISS search
├── build_rag.py           # Script to vectorize knowledge_base.txt
├── requirements.txt       # Python dependencies
├── banking_system.db      # The SQL Database (Persistent Volume)
├── Dockerfile             # Container configuration
├── data/
│   ├── knowledge_base.txt # The Policy Manual (Text source)
│   └── banking_faiss.index# The Vector Database (Generated)
├── models/
│   ├── intent/            # Fine-tuned DistilBERT (Banking77)
│   └── ner/               # dslim/bert-base-NER (Entity Extraction)
└── static/
    └── index.html         # Frontend Chat Interface
```

## ⚠️ Maintenance
* **View Logs:** `sudo docker logs -f bank-app`
* **Restart App:** `sudo docker restart bank-app`
* **Reset Database:** Stop the container, delete `banking_system.db` on the host, and restart.