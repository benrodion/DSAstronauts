from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SelectMultipleField, widgets, SubmitField
from wtforms.validators import InputRequired, NumberRange, Length, DataRequired, ValidationError

def not_empty_or_spaces(form, field):
    if not field.data or field.data.strip() == "":
        raise ValidationError('Trip name cannot be empty or only spaces.')
    
class TripForm(FlaskForm):
    tripSelection = SelectField('Pick a Trip', choices=[
        ('', 'Choose...'),
        ('beach', 'Beach Trip'),
        ('dinner', 'Dinner'),
        ('skiing', 'Skiing Trip'),
        ('museum', 'Museum Trip'),
        ('film', 'Movies'),
        ('other', 'Other')
    ], validators=[DataRequired(message="Trip selection is required.")])

    yourtripname = StringField(
        'Enter Trip Name',
        validators=[
            DataRequired(message="Trip name is required."), 
            not_empty_or_spaces, 
            Length(min=1, max=50, message="Name should be 1 to 50 characters long")])

    submit = SubmitField('Create Trip')


class AddTransactionForm(FlaskForm):
    transaction_name = StringField(
        'Transaction Name',
        validators=[
            DataRequired(),
            InputRequired(message="Please input the transaction name"),
            Length(min=1, max=50, message="Name should be 1 to 50 characters long")
        ]
    )
    amount = DecimalField(
        'Amount',
        validators = [
            InputRequired(), 
            NumberRange(min=0)])
    
    payer = SelectField(
        'Payer',
         choices=[("other", "Other (Type Name)")], 
         validators=[DataRequired(), InputRequired()])
    
    payer_custom = StringField(
        'New payer')
        
    participants = SelectMultipleField(
        'Select Participants',
        option_widget = widgets.CheckboxInput()
    )

    participants_names = StringField(
        'New participants (comma-separated)')

class EditTransactionForm(FlaskForm):
    transaction_name = StringField(
        'Transaction Name',
        validators=[
            DataRequired(),
            InputRequired(message="Please input the transaction name"),
            Length(min=0, max=50, message="Name should be up to 50 characters long")
        ]
    )
    amount = DecimalField('Amount', validators=[InputRequired(), NumberRange(min=0)])
    
    payer = SelectField('Payer', choices=[("other", "Other (Type Name)")], validators=[DataRequired(), InputRequired()])
    payer_custom = StringField(
        'New payer')

    participants = SelectMultipleField(
        'Select Participants',
        option_widget=widgets.CheckboxInput()
    )
    participants_names = StringField(
        'New participant')
                                    

class DeleteTransactionForm(FlaskForm):
    submit = SubmitField('Delete')
