from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'X38cXdx10Sd8Xx'

db = SQLAlchemy(app)

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_text = db.Column(db.String, nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    passw = db.Column(db.String, nullable=False)

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session.get('user_id')
        tasks = Tasks.query.filter_by(user_id=user_id).order_by(Tasks.id.desc()).all()
        return render_template("index.html", tasks=tasks)
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get("login")
        passw = request.form.get("passw")
        check_user = db.session.query(Users.id).filter_by(login=login, passw=passw).scalar() is not None
        if check_user:
            session['user_id'] = login
            return redirect('/')
        else:
            error = "Error! Login or Password invalid!"
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/login')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        login = request.form.get("login")
        passw = request.form.get("passw")
        c_passw = request.form.get("c_passw")
        check_user = db.session.query(Users.id).filter_by(login=login).scalar() is not None
        if check_user:
            return "Error! User with same login alredy exist!"
        if passw == c_passw:
            user = Users(login=login, passw=passw)
            try:
                db.session.add(user)
                db.session.commit()
                return redirect('/login')
            except:
                return 'DB error!'
        else:
            return "Error! Passwords do not match!"
    else:
        return render_template("sign_up.html")

@app.route('/get_tasks')
def get_tasks():
    if 'user_id' in session:
        user_id = session.get('user_id')
        tasks = Tasks.query.filter_by(user_id=user_id).order_by(Tasks.id.desc()).all()
        return render_template("task_list.html", tasks=tasks)
    else:
        return redirect('/login')


@app.route('/create_task', methods=['POST'])
def create_task():
    if request.method == 'POST':
        task_text = request.form.get('task_text')
        if len(task_text) >= 3:
            user_login = session.get('user_id')
            task = Tasks(user_id=user_login, task_text=task_text)
            try:
                db.session.add(task)
                db.session.commit()
                return redirect('/')
            except:
                return 'DB error!'
        else:
            return "Error! Min 3 chars"
    return render_template("index.html")

@app.route('/delete_task/<int:id>')
def delete_task(id):
    task = Tasks.query.get_or_404(id)

    try:
        db.session.delete(task)
        db.session.commit()
        return redirect('/')
    except:
        return 'DB error!'



if __name__ == '__main__':
    app.run(debug=True)