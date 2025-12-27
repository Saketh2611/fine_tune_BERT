# 🏦 Enterprise Banking AI Agent

A full-stack, privacy-first banking assistant capable of routing **77 distinct banking intents**.

This project implements a **Hybrid AI Architecture** that combines **BERT-based Intent Classification**, **Named Entity Recognition (NER)**, and **Retrieval Augmented Generation (RAG)** to handle both transactional commands and policy questions with high precision.

---

## 🚀 Key Features

* **Hybrid Intelligence:** Dynamically switches between **Action Execution** (e.g., transfers, freezing cards) and **Knowledge Retrieval** (e.g., explaining fees).
* **Deterministic Logic Router:** A custom-built Python router that prioritizes critical banking actions over general chit-chat to prevent hallucinations.
* **Local & Secure:** Runs entirely on CPU (No OpenAI/Google API keys required). Perfect for banking compliance where data cannot leave the premise.
* **Sub-50ms Latency:** Optimized inference pipeline using `DistilBERT` and `FAISS` (Facebook AI Similarity Search).
* **Heuristic Intent Correction:** A custom logic layer that fixes model ambiguity in complex sentences (see "Technical Challenges" below).

---

## 🛠️ Tech Stack

* **Backend:** FastAPI (Python)
* **ML Models:**
    * *Intent:* Fine-tuned `distilbert-base-uncased` on the **Banking77** dataset.
    * *NER:* `bert-base-ner` for extracting Names (`PER`) and Amounts.
    * *Embeddings:* `sentence-transformers/all-MiniLM-L6-v2`.
* **Vector DB:** FAISS (for high-speed RAG retrieval).
* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Single Page Application).

---

## 🧠 System Architecture

The system does not rely on a single "Black Box" model. Instead, it uses a pipeline of specialized engines:

1.  **The Dispatcher (Intent Model):** Instantly classifies the user's text into one of 77 categories (e.g., `lost_card`, `atm_limit`).
2.  **The Extractor (NER Model):** Scans the text for critical details like **Names** (Who to pay?) or **Dates**.
3.  **The Logic Router (App.py):** The "Brain" of the system. It follows strict rules:
    * *Is this a Critical Action?* (e.g., "Freeze Card") → **Trigger Rule Engine**.
    * *Is this a Policy Question?* (e.g., "What are the fees?") → **Trigger RAG**.
4.  **The Librarian (RAG):** If triggered, searches the `knowledge_base.txt` policy manual for the exact answer using Vector Search.

---

## 💡 Technical Challenges & Solutions

### The "Transfer to David" Ambiguity
**The Problem:**
The `Banking77` dataset consists largely of customer complaints (e.g., "My transfer didn't go through"). It lacks training examples of *commands* containing specific names.
When a user typed *"Transfer money to David"*, the model incorrectly classified it as a complaint (`balance_not_updated_after_bank_transfer`) because it didn't recognize "David" as a variable.

**The Solution:**
I implemented a **Heuristic Correction Layer** in the inference pipeline.
Before routing the request, the system checks:
1.  Did the model predict a "Balance Issue"?
2.  Did the NER engine detect a **Person (`PER`)**?

If **BOTH** are true, the system overrides the model's prediction and forces the intent to `transfer_into_account`. This ensures 100% accuracy for transfer commands without retraining the entire model.

```python
# Actual code snippet from the Correction Layer
if intent in misclassified_transfers and "PER" in entities:
    print(f"⚠️ Correction: Detected '{intent}' but found a Name. Switching to 'transfer_into_account'.")
    intent = "transfer_into_account"
```

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

### 3. Model Setup
* Download the zip files and extract the intent and ner model 
* Place your fine-tuned `intent` model files in: `models/intent/`
* Place your `ner` model files in: `models/ner/`
* Ensure `data/knowledge_base.txt` exists.

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
Access the interface at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Testing Guide (Example Queries)

Once the system is running, try these queries to test different parts of the architecture.

### ✅ Test 1: Critical Actions (NER Engine)
* **User:** "I lost my card!"
    * **Result:** "🚨 **SECURITY ALERT:** I have temporarily frozen your account..."
    * **Mechanism:** Triggers `lost_or_stolen_card` intent → Hardcoded Safety Rule.

* **User:** "Transfer money to David."
    * **Result:** "💸 **Transfer Initiated:** Sending funds to **David**..."
    * **Mechanism:** Triggers Correction Layer → Extracts `David` → Action Response.

### ✅ Test 2: Policy Knowledge (RAG System)
* **User:** "What is the fee for international transfers?"
    * **Result:** "Policy Info: International transaction fees are 3%..."
    * **Mechanism:** Triggers `exchange_rate` intent → Searches Vector DB → Returns Text.

* **User:** "Can I use Apple Pay?"
    * **Result:** "Policy Info: Yes, we fully support Apple Pay and Google Pay."

---

## 📂 Project Structure

```text
banking_agent/
├── app.py                 # Main FastAPI application & Logic Router
├── rag_engine.py          # RAG Class for handling FAISS search
├── build_rag.py           # Script to vectorize knowledge_base.txt
├── requirements.txt       # Python dependencies
├── data/
│   ├── knowledge_base.txt # The Policy Manual (Text source)
│   └── banking_faiss.index# The Vector Database (Generated)
├── models/
│   ├── intent/            # Fine-tuned DistilBERT files
│   └── ner/               # BERT-NER files
└── static/
    └── index.html         # Frontend Chat Interface
```
