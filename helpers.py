from typing import Optional, List, Union
from database import SessionLocal, Transaction, Participant

def check_bad_password(password: str) -> Optional[str]:
    if len(password) < 4:
        return "Password must be at least 4 characters."
    if ' ' in password:
        return "Password cannot contain spaces."
    return

def prepare_transactions_for_split(trip_id: int) -> List[List[Union[str, float]]]:
    """
    Prepares transaction data for the OptimalSplit algorithm in splitwise.py.
    Returns a list of [payer, borrower, amount] entries based on a given trip ID.
    """
    db = SessionLocal()
    result = []

    transactions = db.query(Transaction).filter(Transaction.trip_id == trip_id).all()

    for transaction in transactions:
        participants = transaction.participants
        payers = [p.name for p in participants if p.is_payer]
        borrowers = [p.name for p in participants if not p.is_payer]

        if not payers or len(payers) != 1:
            continue  # skip if missing or multiple payers

        if not borrowers:
            continue  # skip if no borrowers

        payer = payers[0]
        amount_cents = round(float(transaction.amount) * 100)
        split_cents = amount_cents // len(participants)

        for p in participants:
            if p.name != payer:
                result.append([payer, p.name, split_cents / 100])

    db.close()
    return result
