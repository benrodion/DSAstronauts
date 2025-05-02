import pytest
from pytest_mock import MockFixture
from app.sandbox_flask_app import app, Group
from app.database import SessionLocal
import bcrypt
from flask import session, url_for
from werkzeug.datastructures import ImmutableMultiDict
from app.sandbox_flask_app import app, normalize_name, update_session_names
from app.database import Transaction, Participant, Trip
from app.forms import AddTransactionForm, EditTransactionForm, DeleteTransactionForm

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing
        "SECRET_KEY": "test_key"
    })
    with app.test_client() as client:
        yield client


def test_add_transaction_form_validation(client):
    """Test AddTransactionForm with valid and invalid input"""
    with client.application.test_request_context():
        valid_form = AddTransactionForm(formdata=ImmutableMultiDict({
            'transaction_name': 'Dinner',
            'amount': 50.00,
            'payer': 'John',
            'participants': ['Alice', 'Bob']
        }))
        valid_form.payer.choices = [('John', 'John'), ('Alice', 'Alice'), ('Bob', 'Bob')]
        valid_form.participants.choices = [('Alice', 'Alice'), ('Bob', 'Bob')]
        assert valid_form.validate()

        empty_name_form = AddTransactionForm(formdata=ImmutableMultiDict({
            'transaction_name': '',
            'amount': 50.00,
            'payer': 'John'
        }))
        empty_name_form.payer.choices = [('John', 'John')]
        empty_name_form.participants.choices = []
        assert not empty_name_form.validate()
        assert 'transaction_name' in empty_name_form.errors

        negative_amount_form = AddTransactionForm(formdata=ImmutableMultiDict({
            'transaction_name': 'Dinner',
            'amount': -10.00,
            'payer': 'John'
        }))
        negative_amount_form.payer.choices = [('John', 'John')]
        negative_amount_form.participants.choices = []
        assert not negative_amount_form.validate()
        assert 'amount' in negative_amount_form.errors



def test_edit_transaction_form_validation(client):
    """Test EditTransactionForm with valid and invalid input"""
    with client.application.test_request_context():
        valid_form = EditTransactionForm(formdata=ImmutableMultiDict({
            'transaction_name': 'Updated Dinner',
            'amount': 75.00,
            'payer': 'Alice',
            'participants': ['John', 'Bob']
        }))
        valid_form.payer.choices = [('John', 'John'), ('Alice', 'Alice'), ('Bob', 'Bob')]
        valid_form.participants.choices = [('John', 'John'), ('Bob', 'Bob')]
        assert valid_form.validate()

        empty_name_form = EditTransactionForm(formdata=ImmutableMultiDict({
            'transaction_name': '',
            'amount': 75.00,
            'payer': 'Alice'
        }))
        empty_name_form.payer.choices = [('Alice', 'Alice')]
        empty_name_form.participants.choices = []
        assert not empty_name_form.validate()
        assert 'transaction_name' in empty_name_form.errors


def test_delete_transaction_form(client):
    """Ensure DeleteTransactionForm has a submit field"""
    with client.application.test_request_context():
        form = DeleteTransactionForm()
        assert form.submit is not None


def test_normalize_name_basic():
    """Test normalize_name handles capitalization and whitespace"""
    assert normalize_name("john") == "John"
    assert normalize_name("ALICE") == "Alice"
    assert normalize_name("bob smith") == "Bob Smith"
    assert normalize_name("  david  ") == "David"
    assert normalize_name(" emma  jones ") == "Emma Jones"
    assert normalize_name("") == ""
    assert normalize_name("   ") == ""

def test_update_session_names(mock_db, mocker):
    """Test the update_session_names function."""
    # Mock session dictionary
    mock_session = {}

    # Mock trip_id
    trip_id = 1

    # Mock participants and payers
    mock_participants = [
        ("John",),
        ("Alice",),
        ("Bob",)
    ]
    mock_payers = [
        ("John",),
        ("Alice",)
    ]

    # Configure the mock database queries
    mock_db.query.return_value.join.return_value.filter.return_value.distinct.return_value.all.side_effect = [
        mock_participants,  # First call for participants
        mock_payers         # Second call for payers
    ]

    # Call the function
    result_participants, result_payers = update_session_names(mock_db, mock_session, trip_id)

    # Assertions
    assert result_participants == ["John", "Alice", "Bob"]
    assert result_payers == ["John", "Alice"]
    assert mock_session["unique_participants"] == ["John", "Alice", "Bob"]
    assert mock_session["unique_payers"] == ["John", "Alice"]

    # Verify the database queries were called correctly
    assert mock_db.query.call_count == 2
    mock_db.query.assert_any_call(Participant.name)


@pytest.fixture
def mock_db(mocker):
    """Mock database session"""
    mock_session = mocker.patch('sandbox_flask_app.SessionLocal')
    mock_instance = mocker.MagicMock()
    mock_session.return_value = mock_instance
    return mock_instance

def test_transactions_get_no_group_id(client, mock_db):
    with client.session_transaction() as sess:
        sess['trip_id'] = 1

    response = client.get('/transactions')
    assert response.status_code == 401  # Unauthorized
    assert response.json == {'message': 'Unauthorized'}

def test_transactions_get_trip_not_found(client, mock_db):
    with client.session_transaction() as sess:
        sess['trip_id'] = 1
        sess['group_id'] = 1

    mock_db.query().filter().first.return_value = None

    response = client.get('/transactions')
    assert response.status_code == 302  # Redirect to dashboard


def test_add_transaction_route(client, mock_db, mocker):
    """Test adding a transaction"""
    with client.session_transaction() as sess:
        sess.update({
            'group_id': 1,
            'trip_id': 1,
            'unique_payers': ['John', 'Alice'],
            'unique_participants': ['John', 'Alice', 'Bob']
        })

    form_data = {
        'transaction_name': 'Lunch',
        'amount': '30.00',
        'payer': 'John',
        'participants': ['Alice', 'Bob'],
        'payer_custom': '',
        'participants_names': ''
    }

    # Patch the function in sandbox_flask_app module
    mocker.patch('sandbox_flask_app.update_session_names', return_value=(['John', 'Alice', 'Bob'], ['John', 'Alice']))
    response = client.post('/transactions/add', data=form_data)

    assert response.status_code == 302
    mock_db.add.assert_called()
    mock_db.flush.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()


def test_add_transaction_with_custom_payer(client, mock_db, mocker):
    """Test adding transaction with custom payer name"""
    with client.session_transaction() as sess:
        sess.update({
            'group_id': 1,
            'trip_id': 1,
            'unique_payers': ['John', 'Alice'],
            'unique_participants': ['John', 'Alice', 'Bob']
        })

    form_data = {
        'transaction_name': 'Museum Tickets',
        'amount': '40.00',
        'payer': 'other',
        'payer_custom': 'Charlie',
        'participants': ['Alice', 'Bob'],
        'participants_names': ''
    }

    mocker.patch('sandbox_flask_app.update_session_names', return_value=(['John', 'Alice', 'Bob', 'Charlie'], ['John', 'Alice', 'Charlie']))
    response = client.post('/transactions/add', data=form_data)

    assert response.status_code == 302
    mock_db.add.assert_called()
    mock_db.commit.assert_called_once()


def test_edit_transaction_route(client, mock_db, mocker):
    """Test editing a transaction"""
    # Create mock transaction and participants
    mock_transaction = mocker.MagicMock(spec=Transaction)
    mock_transaction.trans_id = 1
    mock_transaction.tr_name = 'Original Dinner'
    mock_transaction.amount = 50.0

    participants = [
        mocker.MagicMock(spec=Participant, name='John', is_payer=True),
        mocker.MagicMock(spec=Participant, name='Alice', is_payer=False)
    ]

    # Configure get and filter_by methods for different queries
    def mock_query_side_effect(*args):
        query = mocker.MagicMock()
        if args and args[0] == Transaction:
            query.filter_by.return_value.first.return_value = mock_transaction
        elif args and args[0] == Participant:
            query.filter_by.return_value.all.return_value = participants
        return query

    mock_db.query.side_effect = mock_query_side_effect

    # Setup session data
    with client.session_transaction() as sess:
        sess.update({
            'group_id': 1,
            'trip_id': 1,
            'tripname': 'Summer Trip',
            'unique_payers': ['John', 'Alice'],
            'unique_participants': ['John', 'Alice', 'Bob']
        })

    # Clear the mock to reset call counts
    mock_db.close.reset_mock()
    
    # Mock update_session_names to avoid database queries
    mocker.patch('sandbox_flask_app.update_session_names', return_value=(['John', 'Alice', 'Bob'], ['John', 'Alice']))
    
    # Making an initial GET request to edit page
    client.get('/transactions/edit/1')
    
    # Reset the mock DB close method before the POST request
    mock_db.close.reset_mock()
    
    # Now perform the POST request to submit changes
    response = client.post('/transactions/edit/1', data={
        'transaction_name': 'Updated Dinner',
        'amount': '75.00',
        'payer': 'Alice',
        'participants': ['John'],
        'payer_custom': '',
        'participants_names': ''
    })

    # Assertions
    assert response.status_code == 302  # Should redirect
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()  # Should be called once after the POST


def test_delete_transaction_route(client, mock_db, mocker):
    """Test deleting a transaction"""
    mock_transaction = mocker.MagicMock(spec=Transaction)
    mock_transaction.trans_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_transaction

    with client.session_transaction() as sess:
        sess.update({'group_id': 1, 'trip_id': 1})

    response = client.post('/transactions/delete/1', data={'submit': 'Delete'})

    assert response.status_code == 302
    mock_db.query.return_value.filter.return_value.delete.assert_called()
    mock_db.delete.assert_called_once_with(mock_transaction)
    mock_db.commit.assert_called_once()
    mock_db.close.assert_called_once()


def test_complete_transaction_workflow(client, mock_db, mocker):
    """End-to-end test: Add, Edit, and Delete a transaction"""
    # Setup mock Trip
    mock_trip = mocker.MagicMock(spec=Trip)
    mock_trip.trip_id = 1
    mock_trip.tripname = "Summer Vacation"
    
    # Setup mock Transaction that will be created
    mock_transaction = mocker.MagicMock(spec=Transaction)
    # Explicitly set the attributes we need on the mock
    mock_transaction.trans_id = 100
    mock_transaction.tr_name = 'Dinner'
    mock_transaction.amount = 60.0

    # Setup mock Participants
    mock_participants = [
        mocker.MagicMock(spec=Participant, name='John', is_payer=True),
        mocker.MagicMock(spec=Participant, name='Alice', is_payer=False),
        mocker.MagicMock(spec=Participant, name='Bob', is_payer=False)
    ]

    # Configure mock DB queries
    def mock_query_side_effect(*args):
        query = mocker.MagicMock()
        if args and args[0] == Trip:
            query.filter.return_value.first.return_value = mock_trip
        elif args and args[0] == Transaction:
            # For GET /edit/100 and POST /delete/100
            query.filter_by.return_value.first.return_value = mock_transaction
            # For transaction listing
            query.filter.return_value.all.return_value = [mock_transaction]
        elif args and args[0] == Participant:
            query.filter_by.return_value.all.return_value = mock_participants
        return query

    mock_db.query.side_effect = mock_query_side_effect

    # Setup session to simulate being logged in
    with client.session_transaction() as sess:
        sess.update({
            'group_id': 1,
            'trip_id': 1,
            'tripname': "Summer Vacation",
            'unique_payers': ['John', 'Alice'],
            'unique_participants': ['John', 'Alice', 'Bob'],
            'group_name': 'TestGroup',  # Add this to fully authenticate
            'logged_in': True  # Add this to authenticate
        })

    # Mock the update_session_names function
    mocker.patch('sandbox_flask_app.update_session_names', return_value=(['John', 'Alice', 'Bob'], ['John', 'Alice']))

    # Add transaction
    # Configure mock_db.add to capture the Transaction object
    mock_db.add = mocker.MagicMock()
    
    add_data = {
        'transaction_name': 'Dinner',
        'amount': '60.00',
        'payer': 'John',
        'participants': ['Alice', 'Bob'],
        'payer_custom': '',
        'participants_names': ''
    }
    
    add_response = client.post('/transactions/add', data=add_data)
    assert add_response.status_code == 302  # Should redirect after adding

    # Edit transaction
    edit_get_response = client.get('/transactions/edit/100')
    assert edit_get_response.status_code == 200  # Should display edit form

    # Reset mock DB's close method before the POST request
    mock_db.close.reset_mock()
    
    edit_data = {
        'transaction_name': 'Fancy Dinner',
        'amount': '75.00',
        'payer': 'Alice',
        'participants': ['John', 'Bob'],
        'payer_custom': '',
        'participants_names': ''
    }
    
    edit_response = client.post('/transactions/edit/100', data=edit_data)
    assert edit_response.status_code == 302  # Should redirect after editing
    
    # Dekete Transaction
    # Reset mock DB before delete
    mock_db.close.reset_mock()
    
    delete_data = {'submit': 'Delete'}
    delete_response = client.post('/transactions/delete/100', data=delete_data)
    assert delete_response.status_code == 302  # Should redirect after deleting
    
    # Make sure the transaction was deleted
    mock_db.delete.assert_called_once()
    mock_db.commit.assert_called()

# To check whether all tests work, run this: pytest transactions_tests.py