import googlemaps
import sqlite3
import itertools
from flask import render_template, flash, redirect
from app import app
from .forms import EmployeeForm, ClientForm

gmaps = googlemaps.Client(key='AIzaSyBO2_t1JfE-VN3MoEoqfsqulE_OVYhGkGs')


@app.route('/')
@app.route('/index')


def index():
    return render_template('index.html',
                           title='Home',
                           employees=employees(), clients=clients())

@app.route('/addemp', methods=['GET', 'POST'])
def add_employee(): 
    conn = sqlite3.connect('Database.db')
    form = EmployeeForm()
    dist_info = []
    msg=''
    if form.validate_on_submit():
        if not gmaps.geocode(address=form.address.data):
            flash('Could not validate address: ' + form.address.data)
            flash('Please check employee address and try again.')
            return redirect('/addemp')
        conn.execute("INSERT INTO Employee (FName, MName, LName, Address, Mode) VALUES (?,'',?,?,?)", [form.first_name.data, form.last_name.data, form.address.data, form.mode.data])
        conn.commit()  
        flash(form.first_name.data + ' ' + form.last_name.data + ' has been added to the employee record.')
        flash(msg)
        return redirect('/addemp')
    conn.close()

    return render_template('addemp.html',
                           title='Enter employee',
                           form=form, msg=msg, dist=dist_info)

@app.route('/addclient', methods=['GET', 'POST'])
def add_client():
    conn = sqlite3.connect('Database.db')
    form = ClientForm()
    msg = ''
    dist_info = []
    if form.validate_on_submit():
        if not gmaps.geocode(address=form.address.data):
            flash('Could not validate address: ' + form.address.data)
            flash('Please check employee address and try again.')
            return redirect('/addemp')
        conn.execute("INSERT INTO Client (FName, MName, LName, Address) VALUES (?,'',?,?)", [form.first_name.data, form.last_name.data, form.address.data])
        conn.commit()
        flash(form.first_name.data + ' ' + form.last_name.data + ' has been added to the client record.')
        return redirect('/addclient')
    conn.close()
    return render_template('addclient.html',
                           title='Enter client',
                           form=form, msg=msg, dist=dist_info)

def dist_table():
    dist_table = []
    for employee in employees():
        origin = employee['address']
        tmode = employee['mode']
        clis = clients()
        destinations = [c['address'] for c in clis]
        dmatrix = gmaps.distance_matrix(origin, destinations, units='imperial', mode=tmode)
        dist_info = []
        i = 0
        for client in clis:
            dmx = {'fname': client['fname'],
                   'lname': client['lname'],
                   'address': client['address'],
                   'distance': dmatrix['rows'][0]['elements'][i]['distance']['text'],
                   'travel_time': dmatrix['rows'][0]['elements'][i]['duration']['text']}
            i+=1
            dist_info.append(dmx)
        dist_table.append({'fname': employee['fname'],
                           'lname': employee['lname'],
                           'address': origin,
                           'mode': employee['mode'],
                           'dist_info': dist_info})
    return dist_table

@app.route('/distances')
def distances():
    return render_template('distances.html', title='Raw distance matrix', distances=dist_table())

def employees():
    conn = sqlite3.connect('Database.db')
    employee_list = []
    cursor = conn.execute("SELECT FName, MName, LName, Address, Mode FROM Employee")
    for row in cursor:
        employee = {}
        employee['fname'] = row[0]
        employee['lname'] = row[2]
        employee['address'] = row[3]
        employee['mode'] = row[4]
        employee_list.append(employee)
    conn.close()
    return employee_list

def clients():
    conn = sqlite3.connect('Database.db')
    client_list = []
    cursor = conn.execute("SELECT FName, MName, LName, Address FROM Client")
    for row in cursor:
        client = {}
        client['fname'] = row[0]
        client['lname'] = row[2]
        client['address'] = row[3]
        client_list.append(client)
    conn.close()
    return client_list
