from flask import Flask , render_template , request , redirect , url_for , session , flash
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired , Email , ValidationError
import bcrypt
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_mysqldb import MySQL


import qrcode
app = Flask(__name__ , static_url_path='/static')
app.config['SEND _FILE_MAX_AGE_DEFAULT'] = 0
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
app.secret_key = 'AtharvaBhole'
mysql = MySQL(app)

class RegisterForm(FlaskForm):
    name = StringField('name',validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')
    img = FileField('img', validators=[FileRequired(), FileAllowed(['jpg','png','jpeg'])])

class DeleteForm(FlaskForm):
    eventname = StringField('name', validators=[DataRequired()])
    submit = SubmitField('Delete')

class CreateForm(FlaskForm):
    eventname = StringField('name', validators=[DataRequired()])
    img = FileField('img', validators=[FileRequired(), FileAllowed(['jpg','png','jpeg'])])
    submit = SubmitField('Create')

class LoginForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    

@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        return render_template('admin.html')
    else:
        flash('Please Login First')
        return redirect(url_for('adminlogin'))
    
@app.route('/createevent', methods=['GET','POST'])
def createevent():
    if 'admin_id' in session:
        return render_template('createevent.html')
    else:
        flash('Please Login First')
        return redirect(url_for('adminlogin'))

@app.route('/deletevent', methods=['GET','POST'])
def deleteevent():
    if 'admin_id' in session:
        return render_template('deleteevent.html')
    else:
        flash('Please Login First')
        return redirect(url_for('adminlogin'))

@app.route('/')
def index():
    return render_template('landing.html')
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_data WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            print("Login Passed")
            return redirect(url_for('evepass'))
        else:
            print("Login Failed")
            flash("Login Failed. Invalid Credentials")
            return redirect(url_for('signup'))
    if 'user_id' in session:
        return redirect(url_for('evepass'))
    return render_template('basic.html',form = form)

@app.route('/evepass')
def evepass():
    if 'user_id' in session:
        id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_data WHERE id = %s", (id,))
        user = cursor.fetchone()
        name = user[1]
        email = user[2]
        return render_template('eventpass.html', name = name , email = email)
    else:
        return redirect(url_for('login'))
@app.route('/adminlogout')
def adminlogout():
    session.pop('admin_id',None)
    return redirect(url_for('adminlogin'))

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/adminprofile')
def adminprofile():
    return render_template('adminprofile.html')


@app.route('/signup',methods=['GET','POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashedpassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        image = form.img.data
        image.save(f'./auth/static/user_img/{name}.png')
        features = qrcode.QRCode(version=1,box_size=40,border=5)
        features.add_data(name)
        features.make(fit=True) 
        # the fit will adjust the qrcode into the box to make it fit to the box
        generate_img = features.make_image(fill_color="black", back_color="white")
        generate_img.save(f'./auth/static/qrs/{name}.png')
        # img = os.open('qrcode.png')
        # Store data in DB
        cursor = mysql.connection.cursor()
        # HERE WE NEED TO CREATE A UNIQUE QR CODE FOR THE USER AND STORE IT IN THE LOCAL HOST
        cursor.execute("INSERT INTO user_data(name, email, password) VALUES(%s, %s, %s)", (name, email, hashedpassword))
        mysql.connect.commit()
        cursor.close()
        
        return redirect(url_for('login'))
    

    return render_template('reg.html', form = form)


@app.route('/adminreg', methods=['GET','POST'])
def adminreg():

    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashedpassword = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')
        image = form.img.data
        image.save(f'./auth/static/admin_img/{name}.png') 
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO admin(name, email, password) VALUES(%s, %s, %s)", (name, email, hashedpassword))
        mysql.connect.commit()
        cursor.close()
        return redirect(url_for('adminlogin'))
    

    return render_template('adminreg.html', form = form)


@app.route('/event1')
def event1():
    if 'user_id' in session:
        id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user_data WHERE id = %s", (id,))
        user = cursor.fetchone()
        cursor.close()
        cursor = mysql.connection.cursor()
        name = user[1]
        cursor.execute(''' INSERT INTO event_data1 VALUES(%s,%s)''',(id,name))
        mysql.connect.commit()
        cursor.close()
        return redirect(url_for('evepass'))
    else:
        return redirect('/login')


@app.route('/adminlogin', methods=['GET','POST'])
def adminlogin():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['admin_id'] = user[0]
            print("Login Passed")
            return redirect(url_for('admin'))
        else:
            print("Login Failed")
            flash("Login Failed. Invalid Credentials")
            return redirect(url_for('adminreg'))
    if 'admin_id' in session:
        return redirect(url_for('admin'))
    return render_template('adminlogin.html',form = form)


@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/fb')
def fb():
    return redirect('https://www.facebook.com')

@app.route('/twit')
def twit():
    return redirect('https://www.twitter.com')


@app.route('/createform', methods=['GET','POST'])
def createform():
    form = CreateForm()
    if form.validate_on_submit():
        eventname = form.eventname.data
        img = form.img.data
        img.save(f'./auth/static/images/{eventname}.png')
        mydb = mysql.connection.cursor()
        mydb.execute(f'CREATE TABLE {eventname} (id INT)')
        mydb.execute(f'ALTER TABLE {eventname} ADD COLUMN name VARCHAR(255)')
        return redirect('/admin')
        

    return render_template('createevent.html', form = form)


@app.route('/deleteevent', methods=['GET','POST'])
def delevent():
    form = DeleteForm()
    if form.validate_on_submit():
        mydb = mysql.connection.cursor()
        eventname = form.eventname.data
        mydb.execute(f'DROP TABLE {eventname}')
        return redirect('/admin')
    return render_template("deleteevent.html", form = form)

@app.route('/insta')
def insta():
    return redirect('https://www.instagram.com')


if __name__ == '__main__':
    app.run(debug=True)
