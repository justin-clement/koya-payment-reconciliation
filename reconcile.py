#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
import pendulum

total = 0.0
count = 0

all_transactions = {}
successful_transactions = {}

def record_singular_transaction(id, status, amount, time):
    """Ensures only the latest record of a transaction is recorded."""
    
    # CHECK IF THE TRANSACTION EXISTS ALREADY.
    existing_transaction = all_transactions.get(id)
    
    # IF IT DOES NOT EXIST, RECORD IT.
    if existing_transaction is None:
        all_transactions[id] = {
            "status": status, 
            "amount": amount, 
            "time": time
        }
    
    # IF A RECORD EXISTS ALREADY, CHECK WHICH IS MORE RECENT.    
    elif existing_transaction is not None:
        existing_time = existing_transaction["time"]
        if existing_time > time:
            pass
        else:
           all_transactions[id] = {
                "status": status, 
                "amount": amount, 
                "time": time
            } 
    
def filter_successful_transactions():
    """Extract successful transactions."""
    
    global total
    
    for id, details in all_transactions.items():
        if details["status"] == "success":
            successful_transactions[id] = details
            total += details["amount"]           
            
                

with open("payments.jsonl") as f:
    
    # FOR EACH LINE (EACH TRANSACTION RECORD).
    for line in f:
        
        # GET EACH LINE.
        event = json.loads(line)
        
        # FETCH THE TRANSACTION DETAILS.
        id = event.get("txn_id", "VOID")
        status = event.get("status")
        amount = event.get("amount")
        transaction_time = event.get("ts")
        
        # CONDITIONS FOR VALID TRANSACTIONS.
        valid_id = True if len(id) == 15 else False
        valid_time = True if transaction_time is not None else False
        valid_status = True if status in {"failed", "pending", "success"} else False
        valid_amount = True if isinstance(amount, (float, str)) else False
        
        # FILTER VALID TRANSACTIONS.
        if all([valid_id, valid_time, valid_status, valid_amount]):
            
            # CHANGE THE UTC STRING TO A DATETIME OBJECT FOR EASY USE.
            transaction_time = pendulum.parse(transaction_time)
            
            # AMOUNTS THAT ARE STRINGS SHOULD BE CHANGED TO FLOATS.
            if isinstance(amount, str):
                amount = float(amount.replace(",", ""))
                 
            record_singular_transaction(id, status, amount, transaction_time)

# FINALLY, FILTER AND GET THE TOTAL NUMBER OF SUCCESSFUL TRANSACTIONS.          
filter_successful_transactions()   
count = len(successful_transactions)          

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print(f"Difference: {count - expected if count > expected else expected - count}")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
