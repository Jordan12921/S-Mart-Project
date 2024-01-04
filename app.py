from flask import Flask,render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy

# create the extension
db = SQLAlchemy()
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:\\Users\\jorda\\Desktop\\flask-project-main\\flask-project-main\\project.db"
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

@app.route("/")
def hello_world():
    return "<p>Hello, Worlds!ssa</p>"

#Login feature
@app.route("/login", methods=["GET","POST"])
def user_list():
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

#Create Account
@app.route("/register", methods=["GET", "POST"])
def user_create():
    error = None
    if request.method == "POST":
        user = User(
            StaffName=request.form["username"],
            Password = request.form["password"],
            StaffEmail=request.form["email"]
        )
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for("user_detail", id=user.id))
        return render_template("users/register.html",error = "register successfully" )

    return render_template("users/register.html",error = error )

@app.route("/user/<int:id>")
def user_detail(id):
    user = db.get_or_404(User, id)
    return render_template("user/detail.html", user=user)

@app.route("/user/<int:id>/delete", methods=["GET", "POST"])
def user_delete(id):
    user = db.get_or_404(User, id)

    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("user_list"))

    return render_template("user/delete.html", user=user)