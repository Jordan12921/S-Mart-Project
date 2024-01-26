from flask import Flask,render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os
from functools import wraps

# create the extension
db = SQLAlchemy()
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///F:\\python project\\S-Mart-Project\\project.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.abspath("project.db")}"
# initialize the app with the extension
db.init_app(app)


####DATABASE
#User table DB
class User(db.Model):
    StaffID = db.Column(db.Integer, primary_key=True)
    StaffName = db.Column(db.String, unique=True, nullable=False)
    StaffEmail = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False)

#class InventoryList DB
class InventoryList(db.Model):
    StockID = db.Column(db.String, nullable=False, primary_key=True)
    StockName = db.Column(db.String, nullable=False)
    Category = db.Column(db.String, nullable=False)
    StockInDate = db.Column(db.Date, nullable=False)
    ExpiryDate = db.Column(db.Date, nullable=False)
    BeginInventoryNum = db.Column(db.Integer, nullable=True)
    ItemPurchasedNum = db.Column(db.Integer, nullable=True)
    ItemSoldNum = db.Column(db.Integer, nullable=True)
    InventoryLeftNum = db.Column(db.Integer, nullable=True)
    CostPrice = db.Column(db.Double, nullable=False)
    CostPricePerItem = db.Column(db.Double, nullable=False)
    RetailPrice = db.Column(db.Double, nullable=False)
    
    
#ensures that the code inside this block has access to current app configurations, like the database setup.
with app.app_context():
    #Create database
    db.create_all()


#Login feature
@app.route("/login", methods=["GET","POST"])
def login():
    info_message = None
    url_direction = "users/login.html"
    if request.method == "POST":
        # users = db.session.execute(db.select(User).order_by(User.StaffName)).scalars()
        user = db.session.execute(db.select(User).filter_by(StaffEmail=request.form["email"],Password=request.form["password"])).scalar()
        if not user:
            info_message = "Invalid Email or Password!"
        else:
            url_direction = "index.html"
    return render_template(f"{url_direction}", info_message = info_message)

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

### This is for ADMIN
#Create Account
@app.route("/register", methods=["GET", "POST"])
def user_create():
    error = None
    if request.method == "POST":
        user = User(
            StaffName=request.form["username"],
            Password = request.form["password"],
            StaffEmail=request.form["email"],
            Role = request.form["role"]

        )
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for("user_detail", id=user.id))
        return render_template("users/register.html",error = "register successfully" )

    return render_template("users/register.html",error = error )

#Staff Management 
@app.route("/staff_management/", methods=["GET","POST"])
@app.route("/staff_management/<int:page_num>", methods=["GET","POST"])
@login_required
def staff_management(page_num):
    staffList = User.query.filter(User.role=="Staff".paginate(per_page=10, page=page_num, error_out=True))
    user = User.query.get(session["logged_in"])
    role = user.role
    
    #To prevent staff from enter the admin page
    if role == "Staff":
        return staff_Home()
    
    if request.method == "POST" and "tag" in request.form:
        tag = request.form["tag"]
        search = "%{}%".format(tag)
        staffList = User.query.filter(User.name.like(search)).paginate(per_page=10, error_out=True)
        return render_template('manageStaff.html',staff=staffList, tag=tag, user=user)
    return render_template('manageStaff.html', staff = staffList,user=user)

#Register staff with CSV file



### This is for STAFF
@app.route('/staffHomepage')
@login_required
def staff_Home():
    user = User.query.filter_by(id=session['logged_in']).first()
    return render_template('/staff_mode/staffHomepage.html', user=user)

###IGNORE FIRST
# @app.route("/user/<int:id>")
# def user_detail(id):
#     user = db.get_or_404(User, id)
#     return render_template("user/detail.html", user=user)

# @app.route("/user/<int:id>/delete", methods=["GET", "POST"])
# def user_delete(id):
#     user = db.get_or_404(User, id)

#     if request.method == "POST":
#         db.session.delete(user)
#         db.session.commit()
#         return redirect(url_for("user_list"))

#     return render_template("user/delete.html", user=user)