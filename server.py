from flask import Flask, render_template, request, redirect, url_for, session, flash
from form import SubmitForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1/test_flask'
db.init_app(app)

@app.route('/create-db', methods=['GET', 'POST'])
def create_db():
    if request.method == 'GET':
        return render_template('database.html')
    else:
        with app.app_context():
            db.create_all()
            flash('Database created successfully', 'info')
            return render_template('database.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('isLoggedIn'):
            flash('You are already logged in.', 'info')
            return redirect(url_for('home'))
        return render_template('login.html')
    else:
        return login_user(request.form['username'], request.form['password'])
    
@app.route('/')
def home():
    if session.get('isLoggedIn'):
        get_and_clear_flashed_messages()
    posts = [
        {
            'title': 'Hello World!',
            'content': 'This is my first post on Flask'
        },
        {
            'title': 'Not the Hello World',
            'content': 'This is my second post on Flask'
        }
    ]
    return render_template('home.html', sunny = False, posts=posts)


@app.route('/about')
def about():
    
    if session.get('isLoggedIn'):
        return 'About page'
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return 'Contact page'


@app.route('/users')
def users():
    return users_list()

@app.route('/user/<id>', methods=['GET'])
def user(id=None):
    print(id)
    if request.method == 'GET':
        user = getUser(id)
        return render_template('user.html', user=user)
    
@app.route('/user-edit/<id>', methods=['GET','POST'])
def editUser(id):
    user = getUser(id)
    if request.method == 'GET':
        return render_template('user-edit.html', user=user)
    else:
        if 'username' and 'password' in request.form:
            form = {
                'username': request.form['username'],   
                'password': request.form['password']
            }
            return edit_user(user.id, form)
        
@app.route('/user-delete/<id>')
def deleteUser(id):
    User.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('users'))
            
@app.route('/submit', methods=['GET', 'POST'])
def signup():
    form  = SubmitForm()
    if form.is_submitted():
        result = request.form
        return render_template('success.html', result=result)
    return render_template('submit.html', form=form)

@app.route('/logout')
def logout():
    if 'isLoggedIn' in session:
        session.pop('isLoggedIn', None)
        flash("You are logged out.", 'info')
        return redirect(url_for('login'))
    else: 
        flash('You are already logged out.', 'info')
        return redirect(request.referrer)
    
@app.route('/user/create', methods=['GET','POST'])
def create_user():
    if request.method == 'POST':
        if 'username' in request.form:
            username = request.form['username']
            password = request.form['password']
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            flash('User created successfully', 'info')
            return users_list()
        else:
            flash('Error in creating user', 'error')
            return redirect(url_for('users_list'))
    else:
        return render_template('user-create.html')
    
# get and clear messages
def get_and_clear_flashed_messages():
    messages = get_flashed_messages()
    clear_flashed_messages()
    return messages

#get messages 
def get_flashed_messages():
    return session.get('_flashes', [])


# clear flashed messages
def clear_flashed_messages():
    session.pop('_flashes', None)
    
#create Users table
class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80))
    password: Mapped[str] = mapped_column(String(80))
    
def users_list():
    users = db.session.execute(db.select(User)).scalars()
    return render_template('users.html', users=users)

def login_user(username, password):
    user = db.session.execute(db.select(User).where(User.username == username)).scalar()
    if user and user.password == password:
        session['isLoggedIn'] = True
        return render_template('home.html')
    else:
        flash('Incorrect login details', 'error')
        return redirect(url_for('login'))

def edit_user(id, form):
    user = User.query.get(id)
    user.username = form['username']
    user.password = form['password']
    db.session.commit()    
    
    return redirect(url_for('user', id=id))
    
def getUser(id):
    user = db.session.execute(db.select(User).where(User.id == id)).scalar()
    return user
    
    
if __name__ == '__main__':
    app.run(debug=True)