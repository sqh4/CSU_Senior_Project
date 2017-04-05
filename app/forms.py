from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class EmployeeForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])

class ClientForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])