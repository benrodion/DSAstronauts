from typing import Optional
from database import SessionLocal, Transaction, Participant

def check_bad_password(password: str) -> Optional[str]:
    if len(password) < 4:
        return "Password must be at least 4 characters."
    if ' ' in password:
        return "Password cannot contain spaces."
    return

def prepare_transactions_for_split(trip_id):
    db = SessionLocal()
    result = []

    transactions = db.query(Transaction).filter(Transaction.trip_id == trip_id).all()

    for transaction in transactions:
        participants = transaction.participants
        payers = [p.name for p in participants if p.is_payer]
        if not payers or len(payers) != 1:
            continue  # skip if no clear payer

        payer = payers[0]
        borrowers = [p.name for p in participants if not p.is_payer]
        if not borrowers:
            continue

        split_amount = float(transaction.amount) / len(borrowers)
        for borrower in borrowers:
            result.append([payer, borrower, round(split_amount, 2)])

    db.close()
    return result
