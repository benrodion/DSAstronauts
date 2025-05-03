# -*- coding: utf-8 -*-

from flask import render_template, request, redirect, session, jsonify, flash, url_for
from app.database import SessionLocal, Group, Trip, Transaction, Participant 
from flask_session import Session
import bcrypt
from app.helpers import check_bad_password, prepare_transactions_for_split, normalize_name, update_session_names
from app.forms import *
from app.splitwise import OptimalSplit
from app import app 

app.secret_key = 'keyyyy'

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

        return render_template('signup_result_succes.html', message="Sign-up successful!")
    
    else:
        return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'group_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    trip_form = TripForm()
    db = SessionLocal()
    previous_trips = db.query(Trip).filter(Trip.group_id == session['group_id']).all()

    if trip_form.validate_on_submit():
        selected_type = trip_form.tripSelection.data
        tripname = trip_form.yourtripname.data.strip()

        # Check if trip already exists
        existing_trip = db.query(Trip).filter(
            Trip.tripname == tripname,
            Trip.group_id == session['group_id']
        ).first()

        if existing_trip:
            trip_form.yourtripname.errors.append("Trip already exists. Please use another name.")
            db.close()
            return render_template('dashboard.html', previous_trips=previous_trips, trip_form=trip_form)

        # Create a new trip
        new_trip = Trip(tripname=tripname, triptype=selected_type, group_id=session["group_id"])
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)

        # Set session variables
        session["trip_id"] = new_trip.trip_id
        session["tripname"] = new_trip.tripname

        db.close()
        return redirect('/transactions')

    db.close()
    return render_template('dashboard.html', previous_trips=previous_trips, trip_form=trip_form)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        trip_id = request.form.get('trip_id')
        if trip_id:
            session['trip_id'] = trip_id

    if "trip_id" not in session:
        flash("No trip selected. Please select a trip first.", "warning")
        return redirect('/dashboard')

    if 'group_id' not in session:
        return jsonify({'message': 'Unauthorized'}), 401

    current_trip_id = session["trip_id"]
    db = SessionLocal()

    try:
        # Retrieve tripname and set it in the session
        trip = db.query(Trip).filter(Trip.trip_id == current_trip_id).first()
        if not trip:
            flash("Trip not found", "danger")
            return redirect('/dashboard')
            
        tripname = trip.tripname
        session["tripname"] = tripname

        # Retrieve transactions
        transactions = db.query(Transaction).filter(Transaction.trip_id == current_trip_id).all()

        # Format transactions data for the template
        transactions_data = []

        for transaction in transactions:
            participant_names = [p.name for p in transaction.participants]
            payers = [p.name for p in transaction.participants if p.is_payer]
            
            payer_str = ", ".join(payers) if payers else "N/A"

            transactions_data.append({
                "id": transaction.trans_id,
                "name": transaction.tr_name,
                "payer": payer_str,
                "amount": transaction.amount,
                "participants": ", ".join(participant_names)
            })

        # Update session with fresh participant/payer lists from database
        all_participants, all_payers = update_session_names(db, session, current_trip_id)

        # Initialize forms with the updated lists
        add_tr_form = AddTransactionForm()
        edit_tr_form = EditTransactionForm()
        delete_tr_form = DeleteTransactionForm()
        
        # Set choices for the forms
        if all_payers:
            add_tr_form.payer.choices = [(payer, payer) for payer in all_payers] + [("other", "Other (Type Name)")]
            edit_tr_form.payer.choices = [(payer, payer) for payer in all_payers] + [("other", "Other (Type Name)")]
        
        if all_participants:
            add_tr_form.participants.choices = [(p, p) for p in all_participants]
            edit_tr_form.participants.choices = [(p, p) for p in all_participants]

        return render_template("transactions.html", 
                            transactions=transactions_data, 
                            unique_payers=all_payers,
                            unique_participants=all_participants,
                            tripname=tripname,
                            add_tr_form=add_tr_form,
                            edit_tr_form=edit_tr_form,
                            delete_tr_form=delete_tr_form)
    
    except Exception as e:
        flash(f"Error loading transactions: {str(e)}", "danger")
        return redirect('/dashboard')
    
    finally:
        db.close()


@app.route('/transactions/add', methods=["POST"])
def add_transaction():
    """Add a new transaction to the current trip."""
    # Check if required session variables exist
    if "group_id" not in session or "trip_id" not in session:
        flash("No active trip selected", "warning")
        return redirect('/')

    db = SessionLocal()
    try:
        # Get unique names from session for case-insensitive lookups
        unique_payers = session.get('unique_payers', [])
        unique_participants = session.get('unique_participants', [])
        
        # Create a case-insensitive lookup dictionary
        all_known_names = unique_payers + unique_participants
        name_lookup = {name.lower(): name for name in all_known_names}
        
        # Create the form and populate it with choices
        add_tr_form = AddTransactionForm()
        if unique_payers:
            add_tr_form.payer.choices = [(payer, payer) for payer in unique_payers] + [("other", "Other (Type Name)")]
        
        if unique_participants:
            add_tr_form.participants.choices = [(p, p) for p in unique_participants]
        
        if add_tr_form.validate_on_submit():
            # Get basic transaction data
            transaction_name = add_tr_form.transaction_name.data
            amount = add_tr_form.amount.data
            
            # Process payer information
            if add_tr_form.payer.data == "other" and add_tr_form.payer_custom.data.strip():
                payer = normalize_name(add_tr_form.payer_custom.data, name_lookup)
            else:
                payer = normalize_name(add_tr_form.payer.data, name_lookup)
                
            # Process participants information
            selected_participants = [normalize_name(p, name_lookup) for p in add_tr_form.participants.data]
            
            # Handle new participants added via JavaScript
            new_participants = []
            if add_tr_form.participants_names.data:
                new_participants_raw = add_tr_form.participants_names.data.split(",")
                new_participants = [normalize_name(p, name_lookup) for p in new_participants_raw if p.strip()]
            
            # Combine all participants
            all_participants = selected_participants + new_participants
            
            # Validation
            if not payer or not all_participants:
                flash("Please provide a payer and at least one participant", "danger")
                return redirect('/transactions')
                
            # Make sure payer is included in participants list
            if not any(p.lower() == payer.lower() for p in all_participants):
                all_participants.append(payer)
                
            # Remove duplicates while preserving case from known names
            participant_set = set()
            final_participants = []
            
            for name in all_participants:
                name_lower = name.lower()
                if name_lower not in participant_set:
                    participant_set.add(name_lower)
                    final_participants.append(name)
            
            # Create the transaction record
            new_transaction = Transaction(
                tr_name=transaction_name,
                amount=float(amount),
                trip_id=session["trip_id"]
            )
            db.add(new_transaction)
            db.flush()  # Get the ID without committing
            
            # Add all participants to the transaction
            for name in final_participants:
                participant = Participant(
                    name=name,
                    is_payer=(name.lower() == payer.lower()),
                    trans_id=new_transaction.trans_id
                )
                db.add(participant)
                
            # Commit all changes
            db.commit()
            
            # Update session with FRESH data from database
            update_session_names(db, session, session["trip_id"])
            
            flash("Transaction added successfully!", "success")
            return redirect('/transactions')
        
        else:
            print("Form did not validate")
            print(add_tr_form.errors)
            
    except Exception as e:
        db.rollback()
        flash(f"Error adding transaction: {str(e)}", "danger")
        
    finally:
        db.close()
        
    return redirect('/transactions')

@app.route('/transactions/edit/<int:id>', methods=["GET", "POST"])
def edit_transaction(id):
    """Edit an existing transaction."""
    if "group_id" not in session or "trip_id" not in session:
        flash("No active trip selected", "warning")
        return redirect('/')

    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter_by(trans_id=id).first()
        if not transaction:
            flash("Transaction not found!", "danger")
            return redirect('/transactions')

        participants = db.query(Participant).filter_by(trans_id=transaction.trans_id).all()
        payer_name = next((p.name for p in participants if p.is_payer), None)
        participant_names = [p.name for p in participants]

        # Get fresh participant and payer lists from database
        all_participants, all_payers = update_session_names(db, session, session["trip_id"])
        
        # Create forms with updated choices
        edit_tr_form = EditTransactionForm()
        add_tr_form = AddTransactionForm()
        delete_tr_form = DeleteTransactionForm()
        
        # Add the current transaction's participants and payers to the lists to ensure they're included
        all_payer_names = set(all_payers)
        all_participant_names = set(all_participants)
        
        if payer_name and payer_name not in all_payer_names:
            all_payers.append(payer_name)
            all_payer_names.add(payer_name)
        
        for name in participant_names:
            if name not in all_participant_names:
                all_participants.append(name)
                all_participant_names.add(name)
        
        # Create a comprehensive case-insensitive lookup
        name_lookup = {name.lower(): name for name in all_participants + all_payers}

        # Update form choices for both forms
        edit_tr_form.payer.choices = [(payer, payer) for payer in all_payers if payer] + [("other", "Other (Type Name)")]
        edit_tr_form.participants.choices = [(p, p) for p in all_participants if p]
        
        add_tr_form.payer.choices = [(payer, payer) for payer in all_payers if payer] + [("other", "Other (Type Name)")]
        add_tr_form.participants.choices = [(p, p) for p in all_participants if p]

        # Handle AJAX GET request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == "GET":
            return jsonify({
                "name": transaction.tr_name,
                "amount": float(transaction.amount),
                "payer": payer_name,
                "participants": participant_names
            })

        # Handle POST request
        if edit_tr_form.validate_on_submit():
            # Update transaction basics
            transaction.tr_name = edit_tr_form.transaction_name.data
            transaction.amount = float(edit_tr_form.amount.data)

            # Determine payer
            if edit_tr_form.payer.data == "other" and edit_tr_form.payer_custom.data.strip():
                payer = normalize_name(edit_tr_form.payer_custom.data, name_lookup)
            else:
                payer = normalize_name(edit_tr_form.payer.data, name_lookup)

            # Gather participants
            selected_participants = [normalize_name(p, name_lookup) for p in edit_tr_form.participants.data]
            new_participants = []
            if edit_tr_form.participants_names.data:
                new_participants = [normalize_name(name, name_lookup) for name in edit_tr_form.participants_names.data.split(",") if name.strip()]
            
            all_participants = selected_participants + new_participants

            if not payer:
                flash("Please specify a payer.", "danger")
                return redirect(url_for('edit_transaction', id=id))

            if not all_participants:
                flash("Please specify at least one participant.", "danger")
                return redirect(url_for('edit_transaction', id=id))

            if payer.lower() not in [p.lower() for p in all_participants]:
                all_participants.append(payer)

            # Ensure unique participants (case-insensitive)
            seen = set()
            final_participants = []
            for name in all_participants:
                lname = name.lower()
                if lname not in seen:
                    seen.add(lname)
                    final_participants.append(name)

            # Remove old participants and add new ones
            db.query(Participant).filter_by(trans_id=transaction.trans_id).delete()

            for name in final_participants:
                db.add(Participant(
                    name=name,
                    is_payer=(name.lower() == payer.lower()),
                    trans_id=transaction.trans_id
                ))

            # Update database
            db.commit()
            
            # Update session with fresh data after changes
            update_session_names(db, session, session["trip_id"])
            
            flash("Transaction updated successfully!", "success")
            return redirect('/transactions')

        # Populate form fields for GET
        if request.method == "GET" and not request.headers.get('X-Requested-With'):
            edit_tr_form.transaction_name.data = transaction.tr_name
            edit_tr_form.amount.data = transaction.amount

            # Set payer field
            payer_found = False
            if payer_name:
                for choice in edit_tr_form.payer.choices:
                    if choice[0].lower() == payer_name.lower():
                        edit_tr_form.payer.data = choice[0]
                        payer_found = True
                        break
                        
            if not payer_found:
                edit_tr_form.payer.data = "other"
                edit_tr_form.payer_custom.data = payer_name

            # Set participants fields
            known = []
            unknown = []

            for p in participant_names:
                if p.lower() == payer_name.lower():
                    continue  # skip payer from participants list
                
                found = False
                for choice in edit_tr_form.participants.choices:
                    if choice[0].lower() == p.lower():
                        known.append(choice[0])
                        found = True
                        break
                        
                if not found:
                    unknown.append(p)

            edit_tr_form.participants.data = known
            edit_tr_form.participants_names.data = ",".join(unknown) if unknown else ""

        transaction_data = {
            "id": transaction.trans_id,
            "name": transaction.tr_name,
            "amount": float(transaction.amount),
            "payer": payer_name,
            "participants": participant_names
        }

        return render_template(
            'transactions.html', 
            edit_tr_form=edit_tr_form,
            add_tr_form=add_tr_form,
            delete_tr_form=delete_tr_form,
            transaction=transaction_data,
            unique_payers=all_payers,
            unique_participants=all_participants,
            trip_id=session["trip_id"],
            tripname=session["tripname"])

    except Exception as e:
        db.rollback()
        flash(f"Error updating transaction: {str(e)}", "danger")
        return redirect('/transactions')

    finally:
        db.close()

@app.route('/transactions/delete/<int:id>', methods=["POST"])
def delete_transaction(id):
    if "group_id" not in session:
        return redirect('/')
    
    delete_tr_form = DeleteTransactionForm()

    if delete_tr_form.validate_on_submit():
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
    else:
        flash("Invalid delete request (possible CSRF detected)", "error")

    return redirect('/transactions')

@app.route('/calculate_split')
def calculate_split():
    # Check if trip_id and tripname are in the session
    trip_id = session.get("trip_id")
    tripname = session.get("tripname")

    # If not in session, try to retrieve from query parameters
    if not trip_id or not tripname:
        trip_id = request.args.get("trip_id")
        tripname = request.args.get("tripname")

    # If still missing, redirect to the dashboard
    if not trip_id or not tripname:
        flash("No trip selected. Please select a trip first.", "warning")
        return redirect('/dashboard')

    # Convert trip_id to integer
    try:
        trip_id = int(trip_id)
    except ValueError:
        flash("Invalid trip ID.", "danger")
        return redirect('/dashboard')

    # Prepare transactions for the split
    transactions = prepare_transactions_for_split(trip_id)
    splitter = OptimalSplit()
    result = splitter.minTransfers(transactions)

    return render_template("calculate.html", result=result, tripname=tripname)

@app.route('/contact', methods=["GET"])
def contact():
    return render_template('contact.html')

#if __name__ == "__main__":
    #print("✅ Starting Flask app...")
    #app.run(debug=True, use_reloader=False)