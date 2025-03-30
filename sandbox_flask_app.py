# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session, url_for, flash
from database import SessionLocal, UserGroup, Transaction 
from flask_session import Session
import bcrypt

app = Flask(__name__)  # create the instance of the flask class

app.config["SESSION_PERMANENT"] = False  # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem"  # not sure if this is the right configuration
Session(app)

@app.route('/', methods=["GET", "POST"])
def show_login_page():
    if request.method == "POST":
        groupid = request.form.get("loggroupid")
        password = request.form.get("logpass")

        if not groupid:
            return render_template('login_result.html', message="Group name missing")
        elif not password:
            return render_template('login_result.html', message="Password missing")

        # Create a database session
        db = SessionLocal()
        user = db.query(UserGroup).filter(UserGroup.username == groupid).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session["groupid"] = groupid
            session["user_id"] = user.id  # Store user ID in session
            db.close()
            return redirect('/dashboard')
        else:
            db.close()
            return render_template('login_result.html', message="Invalid username or password")
                

    return render_template('login.html')


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("newloggroupid")
        password = request.form.get("newlogpass")

        print("Received Sign-Up Data:")  # Debugging
        print("Username:", username)
        print("Password:", password)

        if not username or not password:
            return render_template('signup_result.html', message="Username or password missing")

        db = SessionLocal()

        # Check if username exists
        existing_user = db.query(UserGroup).filter(UserGroup.username == username).first()
        if existing_user:
            db.close()
            return render_template('signup_result.html', message="Username already exists")

        # Hash password (for security)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = UserGroup(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.close()

        return render_template('signup_result.html', message="Sign-up successful!")

    return render_template('signup.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get("tripSelection") == "Choose...":
            return render_template('dashboard.html', message="Trip selection missing")
        elif not request.form.get("yourtripname"):
            return render_template('dashboard.html', message="Trip name missing")

        trip_button_str = str(request.form.get('tripSelection'))

        # make sure the input is one of the allowed inputs (not absolutely necessary in the drop-down case)
        if trip_button_str not in ['beach', 'dinner', 'skiing', 'museum', 'film', 'other']:
            return render_template('dashboard.html',
                                   printed_result='You must select one of the trip types.')

        session["trip_type"] = request.form.get('tripSelection')
        session["trip_name"] = request.form.get('yourtripname')
        
        return redirect('/transactions')
    return render_template('dashboard.html')


@app.route('/transactions', methods=['GET'])
def transactions():
    if "groupid" not in session:
        return redirect('/')
        
    db = SessionLocal()
    
    # Retrieve only transactions related to the user's group_id
    group_id = session["groupid"]
    transactions = db.query(Transaction).filter(Transaction.user_id == group_id).all()
    
    # Get all users for the forms (filtered by group)
    user_groups = db.query(UserGroup).filter(UserGroup.id == group_id).all()
    
    # Fetch unique payers from the filtered transactions
    unique_payers = db.query(Transaction.payer).filter(Transaction.user_id == group_id).distinct().all()
    unique_payers = [payer[0] for payer in unique_payers]  # Convert list of tuples to list of strings

    # Format transactions data for the template
    transactions_data = []
    unique_participants = set()  # Track unique participants
    for transaction in transactions:
        # Parse participant IDs from comma-separated values
        participant_ids = transaction.participants.split(',') if transaction.participants else []
        
        # Get participant names
        participant_names = [p.strip() for p in transaction.participants.split(',') if p.strip()]
        unique_participants.update(participant_names)
        
        transactions_data.append({
            "id": transaction.id,
            "name": transaction.transaction_name,
            "payer": transaction.payer,  # Already stored as a name
            "amount": transaction.amount,
            "participants": ", ".join(participant_names)
        })
    
    db.close()
    trip_name = session.get("trip_name", "Your Trip")

    return render_template("transactions.html", 
                           transactions=transactions_data, 
                           user_groups=user_groups, 
                           unique_payers=unique_payers,  
                           unique_participants=list(unique_participants),  
                           trip_name=trip_name)



@app.route('/transactions/add', methods=["POST"])
def add_transaction():
    if "groupid" not in session:
        return redirect('/')
        
    db = SessionLocal()
    data = request.form

    # Handle payer selection
    payer = data.get("payer")
    payer_custom = data.get("payer_custom")

    if payer == "other" and payer_custom:
        payer = payer_custom.strip()  # Use custom payer name

    # Handle participants selection or manual entry
    selected_participants = data.getlist("participants")  # Selected from dropdown
    manual_participants = data.get("participants_names")  # Manually entered

    if manual_participants:  
        # Use manually entered names (clean up spaces and remove empty entries)
        participants = ",".join([p.strip() for p in manual_participants.split(",") if p.strip()])
    else:
        # Use selected participant IDs
        participants = ",".join(selected_participants)

    new_transaction = Transaction(
        transaction_name=data["transaction_name"],
        payer=payer,  # Store payer name directly
        amount=float(data["amount"]),
        participants=participants,  # Store as a comma-separated string
        user_id = session["user_id"]
    )
    
    db.add(new_transaction)
    db.commit()
    db.close()
    
    flash("Transaction added successfully!", "success")
    return redirect('/transactions')



@app.route('/transactions/edit/<int:id>', methods=["POST"])
def edit_transaction(id):
    if "groupid" not in session:
        return redirect('/')
        
    db = SessionLocal()
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    
    if not transaction:
        db.close()
        flash("Transaction not found!", "error")
        return redirect('/transactions')
    
    data = request.form
    participants = ",".join(request.form.getlist("participants"))
    
    transaction.transaction_name = data["transaction_name"]
    transaction.payer = int(data["payer"])
    transaction.amount = float(data["amount"])
    transaction.participants = participants
    
    db.commit()
    db.close()
    
    flash("Transaction updated successfully!", "success")
    return redirect('/transactions')


@app.route('/transactions/delete/<int:id>', methods=["POST"])
def delete_transaction(id):
    if "groupid" not in session:
        return redirect('/')
        
    db = SessionLocal()
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    
    if not transaction:
        db.close()
        flash("Transaction not found!", "error")
        return redirect('/transactions')
    
    db.delete(transaction)
    db.commit()
    db.close()
    
    flash("Transaction deleted successfully!", "success")
    return redirect('/transactions')


if __name__ == "__main__":
    print("✅ Starting Flask app...")
    app.run(debug=True, use_reloader=False)