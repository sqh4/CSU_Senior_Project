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
    conn = sqlite3.connect('test.db')
    employees = []
    clients = []
    cursor = conn.execute("SELECT FName, MName, LName, Address FROM Employee")
    for row in cursor:
        employee = {}
        employee['fname'] = row[0]
        employee['lname'] = row[2] 
        employee['address'] = row[3]
        employees.append(employee)
    cursor = conn.execute("SELECT FName, MName, LName, Address FROM Client")
    for row in cursor:
        client = {}
        client['fname'] = row[0]
        client['lname'] = row[2]
        client['address'] = row[3]
        clients.append(client)
    return render_template('index.html',
                           title='Home',
                           employees=employees, clients=clients)
    conn.close()

@app.route('/addemp', methods=['GET', 'POST'])

def add_employee(): 
    conn = sqlite3.connect('test.db')
    form = EmployeeForm()
    msg = 'Distance to available clients will be generated on submission'
    dist_info = []
    if form.validate_on_submit():
        msg = form.first_name.data + ' ' + form.last_name.data + ' has been added.  Distance to available clients:'
        conn.execute("INSERT INTO Employee VALUES (?,'',?,?)", [form.first_name.data, form.last_name.data, form.address.data])
        conn.commit()
        clients = []
        cursor = conn.execute("SELECT FName, MName, LName, Address FROM Client")
        for row in cursor:
            client = {}
            client['fname'] = row[0]
            client['lname'] = row[2]
            client['address'] = row[3]
            clients.append(client)
        for client in clients:
            dmx = {'fname': client['fname'], 'lname': client['lname'], 'di': gmaps.distance_matrix(form.address.data, client['address'], units='imperial')}
            dist_info.append(dmx)

    return render_template('addemp.html',
                           title='Enter employee',
                           form=form, msg=msg, dist=dist_info)
    conn.close()
    
@app.route('/addclient', methods=['GET', 'POST'])
def add_client():
    conn = sqlite3.connect('test.db')
    form = ClientForm()
    msg = 'Distance to available employees will be generated on submission'
    dist_info = []
    if form.validate_on_submit():
        msg = form.first_name.data + ' ' + form.last_name.data + ' has been added.  Distance to available employees:'
        conn.execute("INSERT INTO Client VALUES (?,'',?,?)", [form.first_name.data, form.last_name.data, form.address.data])
        conn.commit()       
#        for employee in employees:
#            dmx = {'fname': employee['fname'], 'lname': employee['lname'],
#                   'di': gmaps.distance_matrix(form.address.data, employee['address'], units='imperial')}
#            dist_info.append(dmx)
    return render_template('addclient.html',
                           title='Enter client',
                           form=form, msg=msg, dist=dist_info)

@app.route('/distances')
def distances():
    conn = sqlite3.connect('test.db')
    origins = []
    destinations = []
    cursor = conn.execute("SELECT Address FROM Employee")
    for row in cursor:
        origins.append(row[0])
    cursor = conn.execute("SELECT Address FROM Client")
    for row in cursor:
        destinations.append(row[0])
    dist_matrix = gmaps.distance_matrix(origins, destinations)
    return render_template('distances.html', title='Raw distance matrix', distances=dist_matrix)

