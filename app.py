import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline
from contextlib import asynccontextmanager
import os
import re

# IMPORT THE DATABASE MODULE
import database

# Import RAG
try:
    from rag_engine import BankingRAG
except ImportError:
    BankingRAG = None

# ==========================================
# 1. GLOBAL VARIABLES
# ==========================================
MODELS = {
    "intent": None,
    "ner": None,
    "rag": None
}

# ==========================================
# 2. LIFESPAN MANAGER (Safe Startup)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Loads models ONLY when the server starts.
    Prevents Windows multiprocessing crashes.
    """
    print("🚀 SYSTEM STARTUP: Initializing Database & Models...")
    
    # A. Initialize Database
    database.init_db()

    # B. Load Models
    try:
        print("⏳ Loading Intent Model...")
        MODELS["intent"] = pipeline("text-classification", model="./models/intent", tokenizer="./models/intent", top_k=1)
        
        print("⏳ Loading NER Model...")
        MODELS["ner"] = pipeline("token-classification", model="./models/ner", tokenizer="./models/ner", aggregation_strategy="simple")

        try:
            if os.path.exists("./data/banking_faiss.index") and BankingRAG:
                print("⏳ Loading RAG Engine...")
                MODELS["rag"] = BankingRAG()
                print("✅ ALL MODELS LOADED SUCCESSFULLY")
            else:
                print("⚠️ WARNING: FAISS Index not found. RAG will be disabled.")
        except Exception:
            pass

    except Exception as e:
        print(f"❌ CRITICAL ERROR LOADING MODELS: {e}")
    
    yield
    print("🛑 SYSTEM SHUTDOWN: Cleaning up...")

# ==========================================
# 3. APP CONFIGURATION
# ==========================================
app = FastAPI(title="Enterprise Banking Agent", lifespan=lifespan)

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ==========================================
# 4. HELPER FUNCTIONS
# ==========================================
def extract_amount(entities):
    for key, val in entities.items():
        clean_val = re.sub(r'[^\d.]', '', val)
        try:
            if clean_val and float(clean_val) > 0:
                return float(clean_val)
        except ValueError:
            continue
    return None

# ==========================================
# 5. API ENDPOINTS
# ==========================================
class UserQuery(BaseModel):
    text: str

@app.get("/")
def home():
    if os.path.exists("static/index.html"):
        return FileResponse('static/index.html')
    return {"error": "static/index.html not found."}

@app.post("/chat")
def chat_endpoint(query: UserQuery):
    if not MODELS["intent"]: 
        raise HTTPException(status_code=500, detail="Models are loading...")

    # A. PREDICTIONS
    intent_res = MODELS["intent"](query.text)[0][0]
    intent = intent_res['label']
    conf = intent_res['score']

    raw_entities = MODELS["ner"](query.text)
    entities = {e['entity_group']: e['word'] for e in raw_entities}

    response = {"bot_reply": "", "source": "Logic", "extracted_entities": entities}

    # B. CORRECTION LAYER (Updated for "Saketh")
    misclassified_transfers = [
        "balance_not_updated_after_bank_transfer",
        "top_up_by_bank_transfer_charge", 
        "transfer_fee_charged",
        "transaction_charged_twice"
    ]
    
    has_person = "PER" in entities
    is_explicit_command = query.text.lower().startswith(("transfer", "send", "pay"))

    if (intent in misclassified_transfers) and (has_person or is_explicit_command):
        print(f"⚠️ LOGIC OVERRIDE: '{intent}' -> 'transfer_into_account'")
        intent = "transfer_into_account"

    # C. ROUTING LOGIC
    action_intents = [
        "lost_or_stolen_card", "lost_or_stolen_phone", "change_pin",
        "order_physical_card", "get_physical_card", "get_virtual_card",
        "get_disposable_virtual_card", "activate_my_card", "terminate_account",
        "edit_personal_details", "verify_top_up", 
        "transfer_into_account", 
        "top_up_failed", "card_not_working", "cancel_transfer", "pending_transfer"       
    ]

    rag_intents = [
        "age_limit", "apple_pay_or_google_pay", "atm_support", "automatic_top_up",
        "balance_not_updated_after_bank_transfer", "balance_not_updated_after_cheque_or_cash_deposit",
        "beneficiary_not_allowed", "card_about_to_expire", "card_acceptance",
        "card_arrival", "card_delivery_estimate", "card_linking", "card_payment_fee_charged",
        "card_payment_not_recognised", "card_payment_wrong_exchange_rate", "card_swallowed", "cash_withdrawal_charge",
        "cash_withdrawal_not_recognised", "compromised_card", "contactless_not_working", "country_support",
        "declined_card_payment", "declined_cash_withdrawal", "declined_transfer", "direct_debit_payment_not_recognised",
        "disposable_card_limits", "exchange_charge", "exchange_rate", "exchange_via_app",
        "extra_charge_on_statement", "failed_transfer", "fiat_currency_support", 
        "getting_spare_card", "getting_virtual_card", 
        "passcode_forgotten", "pending_card_payment", "pending_cash_withdrawal",
        "pending_top_up", "pin_blocked", "receiving_money", "Refund_not_showing_up",
        "request_refund", "reverted_card_payment", "supported_cards_and_currencies", 
        "top_up_by_bank_transfer_charge", "top_up_by_card_charge", "top_up_by_cash_or_cheque", 
        "top_up_limits", "top_up_reverted", "topping_up_by_card", "transaction_charged_twice", "transfer_fee_charged",
        "transfer_not_received_by_recipient", "transfer_timing", "unable_to_verify_identity",
        "verify_my_identity", "verify_source_of_funds", "virtual_card_not_working",
        "visa_or_mastercard", "why_verify_identity", "wrong_amount_of_cash_received", "wrong_exchange_rate_for_cash_withdrawal"
    ]

    # --- ROUTE A: ACTIONS ---
    if intent in action_intents:
        response["source"] = "NER Engine + SQL DB"
        
        if intent == "transfer_into_account":
            person = entities.get("PER", "Unknown Recipient")
            amount = extract_amount(entities)
            
            if amount:
                success, msg = database.process_transfer(amount, person)
                response["bot_reply"] = f"💸 <b>Transfer Status:</b> {msg}"
            else:
                current_bal = database.get_balance()
                response["bot_reply"] = f"💸 I can help transfer funds to <b>{person}</b>. Please specify an amount (e.g., $500). <br>💰 <i>Current Balance: ${current_bal}</i>"

        elif intent in ["lost_or_stolen_card", "lost_or_stolen_phone"]:
            response["bot_reply"] = "🚨 <b>SECURITY ALERT:</b> I have temporarily frozen your account to prevent fraud."
        elif intent == "change_pin":
            response["bot_reply"] = "🔐 <b>Security:</b> A PIN reset link has been sent to your mobile."
        elif intent == "order_physical_card":
            response["bot_reply"] = "💳 <b>Order Received:</b> Your new card will arrive in 5-7 days."
        elif intent == "terminate_account":
            response["bot_reply"] = "⚠️ <b>Account Closure:</b> Request submitted. We are sorry to see you go."
        else:
            response["bot_reply"] = f"⚙️ <b>Action:</b> Processing request for '{intent}'..."

    # --- ROUTE B: RAG ---
    elif intent in rag_intents:
        if MODELS["rag"]:
            docs = MODELS["rag"].search(query.text)
            if docs:
                response["bot_reply"] = f"<b>Policy Info:</b><br>{docs[0]}"
                response["source"] = "RAG System"
            else:
                response["bot_reply"] = "I checked the policy but found no specific answer."
        else:
            response["bot_reply"] = "The Knowledge Base is currently offline."

    # --- ROUTE C: FALLBACK ---
    else:
        response["bot_reply"] = f"I understood '{intent}' but I don't have a workflow for it."

    return {"user_query": query.text, "predicted_intent": intent, "confidence": conf, "result": response}

if __name__ == "__main__":
    # 🚨 CRITICAL FIX FOR WINDOWS CRASHES
    # We MUST disable reload because Windows + PyTorch + Multiprocessing = Crash
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)