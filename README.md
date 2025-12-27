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
* **Database:** SQLite (Built-in, zero config)
* **ML Models:**
    * *Intent:* Fine-tuned `distilbert-base-uncased` on the **Banking77** dataset.
    * *NER:* `bert-base-ner` for extracting Names (`PER`) and Amounts.
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

## 📦 Installation & Setup

### 1. Prerequisites
* Python 3.8+
* Virtual Environment (Recommended)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/banking-agent.git
cd banking-agent

# Install dependencies
pip install fastapi uvicorn transformers torch sentence-transformers faiss-cpu pydantic
```

### 3. Model Setup (Important!)
Since AI models are too large for standard git, we use a hybrid approach:

**Step A: Download Public Models**
Run the included setup script to automatically fetch the NER and Embedding models:
```bash
python setup_models.py
```

**Step B: Download Custom Intent Model**
1.  Go to the **[Releases Page](../../releases)** of this repository.
2.  Download `intent_model.zip`.
3.  Extract it into the folder: `models/intent/`.
   *(Your folder structure should look like: `models/intent/config.json`, etc.)*

### 4. Build the Knowledge Base
Run this script once to vectorize the text policy file:
```bash
python build_rag.py
# Output: ✅ Success! Index saved to data/banking_faiss.index
```

### 5. Run the Server
```bash
python app.py
```
* **Note:** The first run will automatically create `banking_system.db` with a default user ("Admin") and **$5,000 balance**.
* Access the interface at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Testing Guide (Example Queries)

Once the system is running, try these queries to test different parts of the architecture.

### ✅ Test 1: Real Transactions (SQL + NER)
* **User:** "Transfer $500 to David."
    * **Result:** "✅ Success! Sent $500.0 to David. New Balance: $4500.00"
    * **Mechanism:** Extracts Entity → Updates SQL DB → Returns Confirmation.

* **User:** "Transfer $10,000 to Sarah."
    * **Result:** "❌ Insufficient Funds. Your balance is $4500.00"
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
├── setup_models.py        # Script to download public AI models
├── requirements.txt       # Python dependencies
├── banking_system.db      # The SQL Database (Auto-created)
├── data/
│   ├── knowledge_base.txt # The Policy Manual (Text source)
│   └── banking_faiss.index# The Vector Database (Generated)
├── models/
│   ├── intent/            # (Download this from Releases)
│   └── ner/               # (Auto-downloaded by setup script)
└── static/
    └── index.html         # Frontend Chat Interface
```

## ⚠️ Troubleshooting
* **Windows Users:** If the server crashes immediately, ensure you are **not** using `reload=True` in `app.py`. Windows struggles with reloading heavy PyTorch models. The current code is already optimized for this.
* **Resetting Money:** To reset your balance back to $5,000, simply delete the `banking_system.db` file and restart the app.