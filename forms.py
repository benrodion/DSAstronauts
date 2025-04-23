from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, SelectField, SelectMultipleField, widgets, SubmitField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Length, DataRequired, Regexp, ValidationError


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

class SignUpForm(FlaskForm):
    groupname = StringField(validators=[DataRequired(), Length(min = 4, max = 30, message = "Name should be 1 to 30 characters long")])
    password = PasswordField(validators=[DataRequired(), Length(min = 4, max = 20, message = "Password should be 4 to 20 characters long")])
    # Regexp('^\w+$', message = "Password cannot contain spaces")
    #  confirm password?
    # password = PasswordField('New Password', [EqualTo('confirm', message='Passwords must match')])
    # confirm  = PasswordField('Repeat Password')
    submit = SubmitField("Submit")

    def validate_password(self, password):
    # Check for whitespaces
        if ' ' in password.data:
            raise ValidationError('Password cannot contain whitespaces.')


class LoginForm(FlaskForm):
    groupname = StringField(validators=[DataRequired(), Length(min = 4, max = 30, message = "Name should be 1 to 30 characters long")])
    password = PasswordField(validators=[DataRequired(), Length(min = 4, max = 20, message = "Password should be 4 to 20 characters long")])

    submit = SubmitField("Submit")

    def validate_password(self, password):
    # Check for whitespaces
        if ' ' in password.data:
            raise ValidationError('Password cannot contain whitespaces.')