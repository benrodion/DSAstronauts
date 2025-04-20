from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import InputRequired, NumberRange, Length, DataRequired

class AddTransactionForm(FlaskForm):
    transaction_name = StringField(
        'Transaction Name',
        validators=[
            DataRequired(),
            InputRequired(message="Please input the transaction name"),
            Length(min=1, max=50, message="Name should be 1 to 50 characters long")
        ]
    )
    amount = DecimalField('Amount', validators=[InputRequired(), NumberRange(min=0)])
    
    payer = SelectField('Payer', choices=[("other", "Other (Type Name)")], validators=[DataRequired(), InputRequired()])
    payer_custom = StringField('New payer')
    participants = SelectMultipleField(
        'Select Participants',
        option_widget=widgets.CheckboxInput()
    )
    participants_names = StringField('New participants (comma-separated)')


# To be finalized!!!
class EditTransactionForm(FlaskForm):
    transaction_name = StringField('Transaction Name', validators=[InputRequired(message= "Please input the transaction name"), Length(min = 1, max = 50, message = "Name should be 1 to 50 characters long")])
    amount = DecimalField('Amount', validators=[InputRequired(), NumberRange(min=0)])

    payer = SelectField('Payer', choices=[], validators=[InputRequired()])
    payer_custom = StringField('New payer')
    
    participants = SelectMultipleField(
        'Select Participants',
        option_widget=widgets.CheckboxInput()
    )
    
    participants_names = StringField('New participants (comma-separated)')

class DeleteTransactionForm(FlaskForm):
    submit = SubmitField('Delete')
