from typing import Optional, List, Union
from database import SessionLocal, Transaction, Participant
import random

def check_bad_password(password: str) -> Optional[str]:
    """
    Checks if a password passes conditions
    Returns:
        None: if the password passes
        Error message (String): if the password fails
    """
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

def normalize_name(name, name_lookup=None):
    """
    Normalize a name consistently.
    If name exists in lookup, use that canonical version.
    Otherwise, properly capitalize the name.
    """
    # Clean the input
    cleaned_name = name.strip()
    if not cleaned_name:
        return cleaned_name
        
    # Check for existing canonical version
    if name_lookup:
        lower_name = cleaned_name.lower()
        if lower_name in name_lookup:
            return name_lookup[lower_name]
    
    # For new names, ensure consistent capitalization
    # (capitalize first letter of each word)
    return " ".join(word.capitalize() for word in cleaned_name.split())

def update_session_names(db, session, trip_id):
    """
    Completely rebuild the session name lists from the database
    to ensure consistency.
    """
    # Query all unique participants and payers from the database for this trip
    participants_query = (
        db.query(Participant.name)
        .join(Transaction, Participant.trans_id == Transaction.trans_id)
        .filter(Transaction.trip_id == trip_id)
        .distinct()
    )
    
    payers_query = (
        db.query(Participant.name)
        .join(Transaction, Participant.trans_id == Transaction.trans_id)
        .filter(Transaction.trip_id == trip_id, Participant.is_payer == True)
        .distinct()
    )
    
    # Get results as lists of names
    all_participants = [p[0] for p in participants_query.all()]
    all_payers = [p[0] for p in payers_query.all()]
    
    # Update session with fresh data
    session["unique_participants"] = all_participants
    session["unique_payers"] = all_payers
    
    # Return the name lists for immediate use
    return all_participants, all_payers

# generate artificial transactions for testing the algorithm 
def generate_transactions(num_people, num_transactions_per_person=10, max_amount=100):
    """
    Generate a list of transactions of the form [lender, borrower, amount].

    Args:
      - num_people: how many unique people (named "P0", "P1", …).
      - num_transactions_per_person: average number of transactions per person.
      - max_amount: upper bound for a single transaction’s amount.
    """
    people = [f"P{i}" for i in range(num_people)]
    transactions = []
    for _ in range(num_people * num_transactions_per_person):
        lender, borrower = random.sample(people, 2)
        amount = round(random.uniform(1, max_amount), 2)
        transactions.append([lender, borrower, amount])
    return transactions