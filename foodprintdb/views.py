import base64
import imghdr
from flask import render_template, request, session, redirect, url_for, flash
from data import Database
from forms import RegisterForm, RecordForm, ConsumptionForm, UpdateUser
from passlib.hash import sha256_crypt
from functools import wraps
from user import User


db = Database()

def home():
    records = db.get_public_records()
    return render_template('home.html', records = records)

def user_check(recordid):
    record = db.get_record(recordid)
    if record is None or not ('logged_in' in session):
        return False
    elif record['userid'] == session['id']:
        return True
    else:
        return False

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login', 'danger')
            return redirect(url_for('login'))
    return wrap

def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        user.name = form.name.data
        user.username = form.username.data
        user.password = sha256_crypt.encrypt(str(form.password.data))
        username_check = db.get_user(user.username)
        if username_check is not None:
            return render_template('register.html', form=form, error="User already exists")
        db.add_user(user)
        flash("You are now registered.", "success")
        return redirect('/login')

    return render_template('register.html', form=form)

def login():
    if request.method == 'POST':
        user = User()
        user.username = request.form['username']
        user.password_candidate = request.form['password']
        result = db.get_user(user.username)
        if result:
            password = result['password']
            if sha256_crypt.verify(user.password_candidate, password):
                session['logged_in'] = True
                session['username'] = user.username
                session['name'] = result['name']
                session['id'] = result['id']
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid password"
                return render_template('login.html', error=error)
        else:
            error = "Username not found"
            return render_template('login.html', error=error)
    return render_template('login.html')

def record(id):
    record = db.get_record(id)
    if record is None:
        records = db.get_public_records()
        return render_template('home.html', error="Record not found", records = records)
    consumptions, results = db.get_consumptions(id)
    userid = record['userid']
    user = db.get_user(id=userid)
    username = user['username']
    if int(record['isprivate']) and (not user_check(id)):
        return render_template('home.html', error="This Record is private")
    if consumptions:
        return render_template('/record.html', consumptions=consumptions, results= results, record=record, username=username)
    else:
        msg = "Looks like there is no consumption in this record"
        return render_template('/record.html', msg=msg, record=record, username=username)

@is_logged_in
def dashboard():
    records = db.get_records(session['id'])
    if records:
        return render_template('dashboard.html', records=records)
    else:
        msg = "Looks like you don't have a records"
        return render_template('dashboard.html', msg=msg)

@is_logged_in
def create_record():
    form = RecordForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        comment = form.comment.data
        userid = session['id']
        if request.form.get("isprivate") == "1":
            isprivate = 1
        else:
            isprivate = 0
        db.create_record(title, comment, userid, isprivate)
        flash('Record created', 'success')
        return redirect(url_for('dashboard'))
    return render_template('create_record.html', form=form)

@is_logged_in
def edit_record(id):
    if not user_check(id):
        records = db.get_public_records()
        error = "You are not allowed to do this command."
        return render_template('home.html', error=error, records=records)
    record = db.get_record(id)
    consumptions, results = db.get_consumptions(id)
    if consumptions:
        if request.method == "POST":
            form_consumption_ids = request.form.getlist("consumption_ids")
            for form_consumption_id in form_consumption_ids:
                db.delete_consumption(form_consumption_id, id)
            return redirect(url_for('edit_record', id=id))
        return render_template('/edit_record.html', consumptions=consumptions, record=record)
    else:
        msg = "Looks like you don't have a consumption in this record"
        return render_template('edit_record.html', msg=msg, record=record)

@is_logged_in
def profile():
    form = UpdateUser(request.form)
    form.name.data = session['name']
    form.username.data = session['username']
    user = db.get_user(session['username'])
    totalcons = db.total_consumption(session['id'])[0]
    if totalcons is None:
        totalcons = 0
    totalrecords = user['totalrecords']
    if request.method == 'POST' and form.validate():
        if request.form['password'] != "":
            password = sha256_crypt.encrypt(str(request.form['password']))
        else:
            password = None

        if request.form['name'] == "":
            name = None
        else:
            name = request.form['name']

        if (name is None or name == session['name']) and password is None:
            return render_template('profile.html', form=form, totalrecords=totalrecords, totalcons=totalcons, msg="Nothing changed")
        id = session['id']
        db.update_user(id, name=name, password=password)
        session['name'] = name
        flash("Successfully updated", 'success')
        return redirect(url_for('dashboard'))
    return render_template("profile.html", form=form, totalrecords=totalrecords, totalcons=totalcons, )

@is_logged_in
def delete_user():
    form = RegisterForm()
    if request.method == 'POST':
        userid = session['id']
        password_candidate = request.form['password']
        user = db.get_user(session['username'])
        if sha256_crypt.verify(password_candidate, user['password']):
            db.delete_user(userid)
            session.clear()
            flash("Your account successfully deleted", "success")
            return redirect(url_for('login'))
        else:
            flash("Wrong password", "danger")
            return redirect(url_for('delete_user'))
    return render_template("delete_user.html", form=form)

@is_logged_in
def edit_record_info(id):
    if not user_check(id):
        records = db.get_public_records()
        error = "You are not allowed to do this command."
        return render_template('home.html', error=error, records=records)
    record = db.get_record(id)
    form = RecordForm(request.form)
    form.title.data = record['title']
    form.comment.data = record['comment']
    checked = record['isprivate']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        comment = request.form['comment']
        if request.form.get("isprivate") == "1":
            isprivate = 1
        else:
            isprivate = 0
        if request.files["inputFile"]:
            file = request.files["inputFile"]
        db.update_record(id, title, comment, isprivate)
        flash('Record updated', 'success')
        return redirect(url_for('edit_record', id=id))

    return render_template('/edit_record_info.html', form=form, checked=checked)

@is_logged_in
def delete_record(id):
    if not user_check(id):
        records = db.get_public_records()
        error = "You are not allowed to do this command."
        return render_template('home.html', error=error, records=records)
    db.delete_record(id)
    flash('Record deleted', 'success')
    return redirect(url_for('dashboard'))

@is_logged_in
def add_consumption(id):
    if not user_check(id):
        consumptions = db.get_public_consumptions()
        error = "You are not allowed to do this command."
        return render_template('home.html', error=error, records=records)
    form = ConsumptionForm(request.form)
    flash('Please enter one of these Meat Types: beef, lamb, chicken, pork.', 'success')
    if request.method == 'POST' and form.validate():
        title = form.title.data
        meattype = form.meattype.data
        portion = form.portion.data
        amount = form.amount.data
        db.add_consumption(title, meattype, portion, amount, id)
        flash('Consumption added', 'success')
        return redirect(url_for('edit_record', id=id))
    return render_template('add_consumption.html', form=form)

@is_logged_in
def edit_consumption(id):
    consumption = db.get_consumption(id)
    if (consumption is None) or (not user_check(consumption['recordid'])):
        records = db.get_public_records()
        error = "You are not allowed to do this command."
        return render_template('home.html', error=error, records=records)
    form = ConsumptionForm(request.form)
    form.title.data = consumption['title']
    form.meattype.data = consumption['meattype']
    form.portion.data = consumption['portion']
    form.amount.data = consumption['amount']
    if request.method == "POST" and form.validate():
        title = request.form['title']
        meattype = request.form['meattype']
        portion = request.form['portion']
        amount = request.form['amount']
        db.update_consumption(title, meattype, portion, amount, id)
        flash('consumption updated', 'success')
        return redirect(url_for('edit_record', id=consumption['recordid']))
    return render_template('edit_consumption.html', form=form)

@is_logged_in
def logout():
    session.clear()
    flash('You have been successfully logged out', 'success')
    return redirect(url_for('login'))
