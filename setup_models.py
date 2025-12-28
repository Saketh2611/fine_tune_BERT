import os
from transformers import AutoTokenizer, AutoModelForTokenClassification

def download_ner():
    print("⏳ Downloading NER Model (bert-base-ner)...")
    save_path = "./models/ner"
    
    # Create directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Download and save model + tokenizer
    tokenizer = AutoTokenizer.from_pretrained("bert-base-ner")
    model = AutoModelForTokenClassification.from_pretrained("bert-base-ner")
    
    tokenizer.save_pretrained(save_path)
    model.save_pretrained(save_path)
    print(f"✅ NER Model saved to {save_path}")

if __name__ == "__main__":
    download_ner()