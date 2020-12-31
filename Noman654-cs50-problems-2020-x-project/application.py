from flask import Flask, render_template, request, redirect , flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from tempfile import mkdtemp
from collections import defaultdict
from functools import wraps
from flask_session import Session


app = Flask(__name__)
db = SQL("sqlite:///database.db")

# maake sure template are auto reload
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
# set session file
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# set user id into session dictionary
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# give me a apology or detaial about error
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route('/')
def home():
    return render_template('home.html')


# ENTRY FOR NEW USER
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        email = request.form.get('email');
        name = request.form.get('name')
        password = request.form.get('password')
        password = generate_password_hash(password)
        # check the email is present or not
        row = db.execute("select email from users where email = ?",email)
        if len(row) != 0 :
            return render_template("error.html",name = "email is already present")
        db.execute("insert into users(email, name, password) values(:email, :name ,:password)",email = email, name = name, password = password)
        row = db.execute("select id from users where email = ?",email)
        session["user_id"] = row[0]['id']
        flash(f"hello {name} you are successfully registered ")
        return redirect('/')

# CREATE A LOGIN INFO AND CHECK
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        check= db.execute("select password from users where email = ?",email)
        if len(check) != 1 or not check_password_hash(check[0]['password'],password):
            return render_template('error.html',name = "invalid username ")
        row = db.execute("select id from users where email = ?",email)
        session["user_id"] = row[0]['id']
        flash("Successfully login ")
        return redirect('/')
    else :
        return render_template('login.html')

# def buy_sell books
@app.route("/buy-sell", methods=["GET", "POST"])
@login_required
def sell_buy():
    if request.method == 'GET':
        return render_template('buy-sell.html')


@app.route('/books')
def books_list():
    return render_template('books.html')

@app.route('/stores')
def stores():
    name = db.execute("select name,book_type from stores join books on books.id = stores.id")
    books = defaultdict(list)
    for row in name:
        books[row['name']].append(row['book_type'])
    return render_template('stores.html', stores = books)

# for logout
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
