import sqlite3

DB_NAME = "banking_system.db"

def init_db():
    """Initialize the database with a mock user and 5000 balance."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # 1. Create Tables
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, name TEXT, balance REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS transactions 
                 (id INTEGER PRIMARY KEY, type TEXT, amount REAL, recipient TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # 2. Check if user exists, if not, create default user "Admin"
    c.execute("SELECT count(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (name, balance) VALUES ('Admin', 5000.0)")
        print("🏦 SQL: Created default user with $5,000 balance.")
    
    conn.commit()
    conn.close()

def get_balance():
    """Get the current balance of the Admin user."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE id=1")
    balance = c.fetchone()[0]
    conn.close()
    return balance

def process_transfer(amount, recipient):
    """
    1. Check funds.
    2. Deduct money.
    3. Record transaction.
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Check Balance
    c.execute("SELECT balance FROM users WHERE id=1")
    current_balance = c.fetchone()[0]
    
    if current_balance < amount:
        conn.close()
        return False, f"❌ Insufficient Funds. Your balance is ${current_balance:.2f}"
    
    # Deduct Money
    new_balance = current_balance - amount
    c.execute("UPDATE users SET balance=? WHERE id=1", (new_balance,))
    
    # Log Transaction
    c.execute("INSERT INTO transactions (type, amount, recipient) VALUES (?, ?, ?)", 
              ("TRANSFER", amount, recipient))
    
    conn.commit()
    conn.close()
    
    return True, f"✅ Success! Sent ${amount} to {recipient}. New Balance: ${new_balance:.2f}"