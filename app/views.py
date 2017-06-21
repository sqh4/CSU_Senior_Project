import googlemaps
import sqlite3
import itertools
from flask import render_template, flash, redirect
from app import app
from .forms import EmployeeForm, ClientForm, EmployeeEdit, ClientEdit, EmployeeList, ClientList
from os import path

ROOT = path.dirname(path.realpath(__file__))
gmaps = googlemaps.Client(key='AIzaSyBO2_t1JfE-VN3MoEoqfsqulE_OVYhGkGs')
workingID = -1


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           title='Home')

@app.route('/emplist', methods=['GET', 'POST'])
def employee_list():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    global workingID
    workingID = -1
    form = EmployeeList()
    emps = employees()
    #size of the list of employees displayed to the user, 20 is default max
    size = 20
    form.selected.choices = [(e['id'], (e['fname'] +' '+ e['lname']+':\t'+ e['address']) +' | '+ e['mode'])
                            for e in emps]

    if len(emps) < size:
        size = len(emps)
    if form.add_new.data:
        flash('Adding new employee')
        return redirect('/addemp')
    if form.selected.data != 'None':
        if form.edit.data:
            workingID = int(form.selected.data)
            flash('Editing employee with ID: ' + form.selected.data)
            return redirect('/editemp')
        if form.manage_clients.data:
            flash(form.selected.data)
        if form.mark_inactive.data:
            #eid = form.selected.data
            #conn.execute("UPDATE Employee SET Inactive = 1 WHERE EmpID = ?". [eid])
            #conn.commit()
            flash('Marked inactive action verified')
    return render_template('emplist.html', title='Employee List', form=form, display_size=size)

@app.route('/clientlist', methods=['GET', 'POST'])
def client_list():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    global workingID
    workingID = -1
    form = ClientList()
    clis = clients()
    #size of the list of employees displayed to the user, 20 is default max
    size = 20
    form.selected.choices = [(e['id'], (e['fname'] +' '+ e['lname']+':\t'+ e['address']))
                            for e in clis]
    if len(clis) < size:
        size = len(clis)
    if form.add_new.data:
        flash('Adding new client')
        return redirect('/addclient')
    if form.selected.data != 'None':
        if form.edit.data:
            workingID = int(form.selected.data)
            flash('Editing client with ID: ' + form.selected.data)
            return redirect('/editclient')
        if form.manage_services.data:
            flash(form.selected.data)
        if form.mark_inactive.data:
            #eid = form.selected.data
            #put SQL code here
            flash('Marked inactive action verified')
    return render_template('clientlist.html', title='Client List', form=form, display_size=size)

@app.route('/addemp', methods=['GET', 'POST'])
def add_employee():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
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
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
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

@app.route('/editemp', methods=['GET', 'POST'])
def edit_employee():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    global workingID
    form = EmployeeEdit()
    title = 'Error: no employee selected.'
    #form.empID.choices = [(e['id'], (e['fname'] +' '+ e['lname'])) for e in employees()]
    #routed from the employee list
    if workingID > -1:
        e = employee(workingID)
        title = 'Editing ' + e['fname'] + ' ' + e['lname']
        form.first_name.data = e['fname']
        form.last_name.data = e['lname']
        form.address.data = e['address']
        form.mode.data = e['mode']
    if form.validate_on_submit():
        conn.execute("UPDATE Employee SET Fname = ?, lname = ?, address = ?, mode = ? WHERE EmpID = ?", [form.first_name.data, form.last_name.data, form.address.data, form.mode.data, workingID])
        conn.commit()

    return render_template('editemp.html', title = title,
                           form = form)

@app.route('/editclient', methods=['GET', 'POST'])
def edit_client():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    global workingID
    form = ClientEdit()
    title = 'Error: no client selected.'
    if workingID > -1:
        e = client(workingID)
        title = 'Editing ' + e['fname'] + ' ' + e['lname']
        form.first_name.data = e['fname']
        form.last_name.data = e['lname']
        form.address.data = e['address']
    if form.validate_on_submit():
        conn.execute("UPDATE Client SET Fname = ?, lname = ?, address = ?, mode = ? WHERE ClientID = ?", [form.first_name.data, form.last_name.data, form.address.data, form.mode.data, workingID])
        conn.commit()

    return render_template('editclient.html', title = title,
                           form = form)

def dist_to_clients(employee):
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
        i += 1
        dist_info.append(dmx)
    return dist_info

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

def employee(id):
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    cursor = conn.execute("SELECT FName, MName, LName, Address, Mode, EmpID FROM Employee WHERE EmpID = '%s'" % id)
    emp = {}
    for row in cursor:
        emp['fname'] = row[0]
        emp['lname'] = row[2]
        emp['address'] = row[3]
        emp['mode'] = row[4]
        emp['id'] = row[5]
    conn.close()
    return emp

def client(id):
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    cursor = conn.execute("SELECT FName, MName, LName, Address, ClientID FROM Client WHERE ClientID = '%s'" % id)
    cli = {}
    for row in cursor:
        cli['fname'] = row[0]
        cli['lname'] = row[2]
        cli['address'] = row[3]
        cli['id'] = row[4]
    conn.close()
    return cli

def employees():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    employee_list = []
    cursor = conn.execute("SELECT FName, MName, LName, Address, Mode, EmpID FROM Employee ORDER BY LName")
    for row in cursor:
        employee = {}
        employee['fname'] = row[0]
        employee['lname'] = row[2]
        employee['address'] = row[3]
        employee['mode'] = row[4]
        employee['id'] = row[5]
        employee_list.append(employee)
    conn.close()
    return employee_list

def clients():
    conn = sqlite3.connect(path.join(ROOT, 'Database.db'))
    client_list = []
    cursor = conn.execute("SELECT FName, MName, LName, Address, ClientID FROM Client ORDER BY LName")
    for row in cursor:
        client = {}
        client['fname'] = row[0]
        client['lname'] = row[2]
        client['address'] = row[3]
        client['id'] = row[4]
        client_list.append(client)
    conn.close()
    return client_list
