from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired


class EmployeeForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    mode = SelectField('mode', choices=[('driving', 'car'),
                                        ('transit', 'bus'),
                                        ('bicycling', 'bicycle'),
                                        ('walking', 'walking')])

class ClientForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])

class EmployeeList(Form):
    add_new = SubmitField('Add New')
    edit = SubmitField('Edit')
    manage_services = SubmitField('Manage Clients')
    mark_inactive = SubmitField('Mark Inactive')
    selected = SelectField('Select an Employee', choices=[])

class ClientList(Form):
    add_new = SubmitField('Add New')
    edit = SubmitField('Edit')
    manage_clients = SubmitField('Manage Clients')
    mark_inactive = SubmitField('Mark Inactive')
    selected = SelectField('Select a Client', choices=[])

class EmployeeEdit(Form):
    #empID = SelectField('empID')
    is_active = BooleanField('is_active')
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])
    mode = SelectField('mode', choices=[('driving', 'car'),
                                        ('transit', 'bus'),
                                        ('bicycling', 'bicycle'),
                                        ('walking', 'walking')])

class ClientEdit(Form):
    is_active = BooleanField('is_active', default='true')
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    address = StringField('address', validators=[DataRequired()])