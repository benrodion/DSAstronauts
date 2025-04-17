# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session, jsonify, flash
from database import SessionLocal, Group, Trip, Transaction, Participant 
from flask_session import Session
import bcrypt
from helpers import check_bad_password
from sqlalchemy import distinct


app = Flask(__name__)  # create the instance of the flask class

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=["GET", "POST"])
def show_login_page():
    if request.method == "POST":
        groupname = request.form.get("loggroupid")
        password = request.form.get("logpass")

        if not groupname:
            return render_template('login_result.html', message="Group name missing")
        elif not password:
            return render_template('login_result.html', message="Password missing")

        db = SessionLocal()
        user = db.query(Group).filter(Group.groupname == groupname).first()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session["groupname"] = groupname
            session['group_id'] = user.group_id
            return redirect('/dashboard')
        else:
            return render_template('login_result.html', message="Invalid username or password")

    return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("newloggroupid")
        password = request.form.get("newlogpass")

        print("Received Sign-Up Data:")
        print("Username:", username)
        print("Password:", password)

        if not username or not password:
            return render_template('signup_result.html', message="Username or password missing")
        
        if check_bad_password(password):
            return render_template('signup_result.html', message=check_bad_password(password))

        db = SessionLocal()
        existing_user = db.query(Group).filter(Group.groupname == username).first()
        if existing_user:
            db.close()
            return render_template('signup_result.html', message="Username already exists")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = Group(groupname=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.close()

        return render_template('signup_result.html', message="Sign-up successful!")

    return render_template('signup.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'group_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
   
    db = SessionLocal()
    # Fetch previous trips for the group
    previous_trips = db.query(Trip).filter(Trip.group_id == session['group_id']).all()
    
    if request.method == 'POST':
        # Get form values
        selected_type = request.form.get("tripSelection", "")
        trip_name = request.form.get("yourtripname", "")
        
        # Validation
        if selected_type not in ['beach', 'dinner', 'skiing', 'museum', 'film', 'other']:
            db.close()
            return render_template('login_result.html', 
                                  message="Trip selection missing")
                                  
        if not trip_name:
            db.close()
            return render_template('login_result.html', 
                                  message="Trip name missing")
        
        # Check if trip exists
        existing_trip = db.query(Trip).filter(Trip.tripname == trip_name, Trip.group_id == session['group_id']).first()
        if existing_trip:
            db.close()
            return render_template('dashboard.html', 
                                  message="Trip already exists. Please use another name")
        
        # Create new trip
        session["trip_type"] = selected_type
        session["trip_name"] = trip_name
        
        new_trip = Trip(tripname=trip_name, triptype=selected_type, group_id=session["group_id"])
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)
        session["trip_id"] = new_trip.trip_id
        db.close()
        
        return render_template('transactions.html', trip_name=new_trip.tripname, trip_id=new_trip.trip_id)
   
    db.close()
    return render_template('dashboard.html', previous_trips=previous_trips)


@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if "trip_id" not in session:
        return redirect('/')
    if 'group_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401
        
    current_trip_id = session["trip_id"]    

    db = SessionLocal()
    
    # Retrieve only transactions related to the user's group_id
    transactions = db.query(Transaction).filter(Transaction.trip_id == current_trip_id).all()
    
    # Get all participants for the forms (filtered by group)
    participants =(
        db.query(distinct(Participant.name))
        .join(Transaction, Participant.trans_id == Transaction.trans_id)
        .join(Trip, Transaction.trip_id == Trip.trip_id)
        .filter(Trip.group_id == session["group_id"])
        .all()
    )
    
    # Format transactions data for the template
    transactions_data = []
    unique_participants = set()
    unique_payers = set()  # Optional: collect unique payers too

    for transaction in transactions:
        # Extract all participant names
        participant_names = [p.name for p in transaction.participants]

        # Add to unique participants
        unique_participants.update(participant_names)

        # Identify payer(s) for this transaction
        payers = [p.name for p in transaction.participants if p.is_payer]
        if payers:
            unique_payers.update(payers)
            payer_str = ", ".join(payers)
        else:
            payer_str = "N/A"

        transactions_data.append({
            "id": transaction.trans_id,
            "name": transaction.tr_name,
            "payer": payer_str,
            "amount": transaction.amount,
            "participants": ", ".join(participant_names)
        })

    db.close()
    trip_name = session.get("trip_name", "Your Trip")

    return render_template("transactions.html", 
                        transactions=transactions_data, 
                        unique_payers=list(unique_payers),
                        unique_participants=list(unique_participants),
                        trip_name=trip_name)


@app.route('/transactions/add', methods=["POST"])
def add_transaction():
    if "group_id" not in session or "trip_id" not in session:
        return redirect('/')
    
    db = SessionLocal()
    try:
        # Get form data with error handling
        transaction_name = request.form.get("transaction_name")
        amount = request.form.get("amount")
        
        # Handle payer selection
        payer = request.form.get("payer")
        payer_custom = request.form.get("payer_custom")
        
        # If "other" is selected, use the custom input field
        if payer == "other" and payer_custom:
            payer = payer_custom.strip()
        
        # Get participants from both sources
        selected_participants = request.form.getlist("participants") 
        new_participants_str = request.form.get("participants_names", "")
        new_participants = [p.strip() for p in new_participants_str.split(",") if p.strip()]
        
        # Combine both lists
        participant_names = selected_participants + new_participants
        
        # Validate required data
        if not transaction_name or not amount or not payer or not participant_names:
            flash("Please fill in all required fields", "danger")
            return redirect('/transactions')
        
        # Make sure the payer is in the participants list
        if payer.strip().lower() not in [p.strip().lower() for p in participant_names]:
            participant_names.append(payer)
            
        # Create new Transaction
        new_transaction = Transaction(
            tr_name=transaction_name,
            amount=float(amount),
            trip_id=session["trip_id"]
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        
        # Add participants
        for name in participant_names:
            # Fix the comparison with case-insensitive matching
            is_payer = (name.strip().lower() == payer.strip().lower())
            participant = Participant(
                name=name.strip(), 
                is_payer=is_payer, 
                trans_id=new_transaction.trans_id
            )
            db.add(participant)
        
        db.commit()
        flash("Transaction added successfully!", "success")
        
    except Exception as e:
        db.rollback()
        flash(f"Error adding transaction: {str(e)}", "danger")
        
    finally:
        db.close()
        
    return redirect('/transactions')

@app.route('/transactions/edit/<int:id>', methods=["POST"])
def edit_transaction(id):
    if "group_id" not in session:
        return redirect('/')

    db = SessionLocal()
    transaction = db.query(Transaction).filter(Transaction.trans_id == id).first()

    if not transaction:
        db.close()
        flash("Transaction not found!", "error")
        return redirect('/transactions')

    data = request.form

    payer = data.get("payer")
    payer_custom = data.get("payer_custom")
    if payer == "other" and payer_custom:
        payer = payer_custom.strip()

    selected_participants = data.getlist("participants")
    manual_participants = data.get("participants_names")

    if manual_participants:
        participant_names = [p.strip() for p in manual_participants.split(",") if p.strip()]
    else:
        participant_names = [p.strip() for p in selected_participants if p.strip()]

    # Update transaction fields
    transaction.tr_name = data["transaction_name"]
    transaction.amount = float(data["amount"])

    # Delete old participants
    db.query(Participant).filter(Participant.trans_id == transaction.trans_id).delete()

    # Add updated participants
    for name in participant_names:
        is_payer = (name == payer)
        db.add(Participant(name=name, is_payer=is_payer, trans_id=transaction.trans_id))

    db.commit()
    db.close()

    flash("Transaction updated successfully!", "success")
    return redirect('/transactions')


@app.route('/transactions/delete/<int:id>', methods=["POST"])
def delete_transaction(id):
    if "group_id" not in session:
        return redirect('/')

    db = SessionLocal()
    transaction = db.query(Transaction).filter(Transaction.trans_id == id).first()

    if not transaction:
        db.close()
        flash("Transaction not found!", "error")
        return redirect('/transactions')

    # Delete associated participants first
    db.query(Participant).filter(Participant.trans_id == transaction.trans_id).delete()
    db.delete(transaction)
    db.commit()
    db.close()

    flash("Transaction deleted successfully!", "success")
    return redirect('/transactions')


if __name__ == "__main__":
    print("✅ Starting Flask app...")
    app.run(debug=True, use_reloader=False)
