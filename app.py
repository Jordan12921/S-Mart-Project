import pandas as pd
from flask import Flask,render_template, request, session, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import column,select,insert, inspect, create_engine, MetaData, Table, Column, Integer, String, Date, Float
import os



from werkzeug.utils import secure_filename

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
class UserModel(db.Model):
    __tablename__ = "user"
    StaffID = db.Column(db.Integer, primary_key=True)
    StaffName = db.Column(db.String, unique=True, nullable=False)
    StaffEmail = db.Column(db.String, nullable=False)
    Password = db.Column(db.String, nullable=False)
    Role = db.Column(db.String, nullable=False)

    def __init__(self,StaffID = None,StaffName = 'user_test', StaffEmail = 'test@example.com', Password = 'password',Role = 'staff'):
        if StaffID:
            self.StaffID = StaffID
        
        self.StaffName = StaffName
        self.StaffEmail = StaffEmail
        self.Password = Password
        self.Role = Role
    
    def __rer__(self):
        return f'<UserModel {self.StaffName!r}'
    
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

class TBL_Config(db.Model):
    __tablename__ = "Table_Config"
    tbConfig_ID = db.Column(db.Integer, nullable=False, primary_key=True)
    tbConfig_TABLE_NAME = db.Column(db.String, nullable=False)
    tbConfig_TB_NAME = db.Column(db.String, nullable=False)
    tbConfig_COLNUMBER = db.Column(db.Integer, nullable=True)
    tbConfig_STATUS = db.Column(db.String, nullable=False)

    def __init__(self,tbConfig_TABLE_NAME,tbConfig_TB_NAME,tbConfig_COLNUMBER,tbConfig_STATUS):

        self.tbConfig_TABLE_NAME = tbConfig_TABLE_NAME
        self.tbConfig_TB_NAME = tbConfig_TB_NAME
        self.tbConfig_COLNUMBER = tbConfig_COLNUMBER
        self.tbConfig_STATUS = tbConfig_STATUS

    def __rer__(self):
        return f'<Table_Config Model {self.tbConfig_TABLE_NAME!r}'

#ensures that the code inside this block has access to current app configurations, like the database setup.
with app.app_context():
    #Create database
    db.create_all()
    if not db.session.query(UserModel).filter(UserModel.StaffName == 'user_test').count():
        # delete old record
        db.session.query(UserModel).filter(UserModel.StaffName == 'user_test').delete()
        db.session.commit()
        print("Inserted User")
        # Insert the new record
        db.session.add(UserModel())
        db.session.commit()


@app.route("/")
def index():
    return render_template("index.html", info_message = None)

#Login feature
@app.route("/login", methods=["GET","POST"])
def user_list():
    info_message = None
    url_direction = "users/login.html"
    if request.method == "GET":
        return render_template("users/login.html")
    
    if request.method == "POST":
        # users = db.session.execute(db.select(User).order_by(User.StaffName)).scalars()
        user = db.session.execute(db.select(UserModel).filter_by(StaffEmail=request.form["email"],Password=request.form["password"])).scalar()
        if not user:
            info_message = "Invalid Email or Password!"
            return render_template(f"{url_direction}", info_message = info_message)
        else:
            url_direction = "excel-import-form.html"
            return redirect(url_for('index'))
    # return render_template(f"{url_direction}", info_message = info_message)


#Create Account
@app.route("/user/create", methods=["GET", "POST"])
def user_create():
    
    if request.method == "GET":
        return render_template("users/register.html")

    if request.method == "POST":
        user = UserModel(
            StaffName=request.form["username"],
            Password = request.form["password"],
            StaffEmail=request.form["email"],
            Role = request.form["role"]

        )
        db.session.add(user)
        db.session.commit()
        # return redirect(url_for("user_detail", id=user.id))
        return render_template("users/register.html",error = "register successfully" )
    


@app.route('/users')
@app.route('/users/')
def RetrieveUserList():
    # users = db.session.execute(db.select(User)).all()
    # users = db.session.execute(db.select(User)).scalars().all()
    # employees = EmployeeModel.query.all()

    users = db.session.execute(db.select(UserModel)).scalars()
    column_names = UserModel.metadata.tables['user'].columns.keys()
    column_names = [column for column in UserModel.metadata.tables['user'].columns.keys() if column != 'Password' and column != 'StaffID']
    # print(type(column_names))
    # # Use the Inspector to get information about the 'user' table
    # inspector = inspect(db.engine)
    # columns = inspector.get_columns('user')  # Replace 'user' with your actual table name


    return render_template("users/userlist.html", users=users, column_names = column_names)


@app.route("/user/<int:id>",methods=["GET", "POST"])
def user_detail(id):
    if request.method == "GET":
        user = db.get_or_404(UserModel, id)
        return render_template("users/user-detail.html", user=user)
    
    if request.method == "POST":
        user = UserModel.query.filter_by(StaffID=id).first()
        if user:
            # db.session.delete(user)
            # db.session.commit()

            # name = request.form['name'] if request.form['name'] else user.StaffName
            # email = request.form['email'] if request.form['email'] else user.StaffEmail
            # password = request.form['password'] if request.form['password'] else user.Password
            # role = request.form['position'] if request.form['position'] else user.Role
            # user = UserModel(StaffID = user.StaffID, StaffName = name, StaffEmail = email,Password = password, Role = role)
            # db.session.add(user)

            user.StaffName = user.StaffName if not request.form['name'] else request.form['name']
            user.StaffEmail = user.StaffEmail if not request.form['email'] else request.form['email']
            user.Password = user.Password if not request.form['password'] else request.form['password']
            user.Role = user.Role if not request.form['position'] else request.form['position']

            db.session.commit()
            return redirect(f'/user/{id}')
        return f"User with id = {id} Does not exist"




@app.route("/user/<int:id>/delete",methods=['Get','POST'])
def user_delete(id):
    if request.method =='GET':
        return render_template("users/userlist.html",  delete_confirmation = True)
    if request.method =='POST':
        user = db.get_or_404(UserModel, id)
        if user:
            db.session.delete(user)
            db.session.commit()
        
        return redirect('/users')

def crea_dynamic_table(table_name, column_names, datatypes):
    # Ensure table object is created within the context
    inspector = inspect(db.engine)  # Use inspector for table existence check

    if not inspector.has_table(table_name):
        print(f"Table '{table_name}' does not exist, creating it...")
        # Create the table here
        with app.app_context():
            table = db.Table(table_name, db.metadata,db.Column('id', db.Integer, primary_key=True,nullable=False))  # Add primary key column
            for column_name, datatype in zip(column_names, datatypes):
                if datatype == 'string':
                    table.append_column(db.Column(column_name, db.String,nullable=False))
                elif datatype == 'integer':
                    table.append_column(db.Column(column_name, db.Integer,nullable=False))
                elif datatype == 'date':
                    table.append_column(db.Column(column_name, db.Date,nullable=False))
                elif datatype == 'double':
                    table.append_column(db.Column(column_name, db.Float,nullable=False))  # Use Float for double precision
                else:
                    # Handle unsupported datatypes gracefully
                    print(f"Unsupported datatype: {datatype}")

            db.metadata.create_all(bind=db.engine)  # Create the table with all columns
            db.session.commit()
    else:
        print(f"Table '{table_name}' already exists.")



# Schema Builder
@app.route('/tablebuilder', methods=['GET','POST'])
def tablebuilder(info = None):

    column_names = [column.name for column in TBL_Config.__table__.columns]
    # table = db.session.execute(db.select(TBL_Config)).scalars()
    table = db.session.query(TBL_Config.tbConfig_ID,TBL_Config.tbConfig_TB_NAME).all()
    print('Table_Config: ', table)
    table_detail = None

    if request.method == "POST":
        if 'get_form_detail' in request.form:
            id = request.form.get('select-id') or request.args.get('select-id')
            table_detail = TBL_Config.query.filter_by(tbConfig_ID = id).first()
            # table =db.session.execute(db.select(TBL_Config).filter_by(tbConfig_ID=id)).scalar_one()
            # column_names = table.__table__.columns.keys()

        if 'form_edit_columns' in request.form:
            column_names = request.form.getlist('field-data')
            datatypes = request.form.getlist('datatype')
            print('you submitted form 2')
            print(column_names,datatypes)
            table_name = request.form['tablename']
            print(request.form)
            crea_dynamic_table(table_name,column_names,datatypes)
            
    return render_template("/admin/schema-builder.html",tables = table, table_detail = table_detail)

@app.post('/insert_data')
def insert_data():
    # Read the File using Flask request
    file = request.files['file']
    # save file in local directory
 
    # Parse the data as a Pandas DataFrame type
    data = pd.read_excel(file)
    table_name = 'Metadata'


    data.to_sql(table_name, con=db.engine, index=False, if_exists='append')
    
    # db.session.execute(db.select, data)
    db.session.commit()
    print(data)
    # Return HTML snippet that will render the table
    return data.to_html()





@app.route('/table/add', methods=['POST'])
def table_create():
    if request.method == "POST":
        name = request.form["name"]
        tb_config = TBL_Config(
            
            tbConfig_TABLE_NAME = name,
            tbConfig_TB_NAME = name + "2",
            tbConfig_COLNUMBER = 0,
            tbConfig_STATUS = "Not Created"

        )
        db.session.add(tb_config)
        db.session.commit()
        return redirect(url_for('tablebuilder'))
    return 'You are in table create'

@app.route('/table/create', methods=['POST'])
def create_dynamic_table(table_name, columns):
    metadata = MetaData()
    dynamic_table = Table(table_name, metadata)
    
    for column in columns:
        col_name, col_type = column
        if col_type == 'String':
            dynamic_table.append_column(Column(col_name, String))
        elif col_type == 'Integer':
            dynamic_table.append_column(Column(col_name, Integer))
        elif col_type == 'Date':
            dynamic_table.append_column(Column(col_name, Date))
        elif col_type == 'Double':
            dynamic_table.append_column(Column(col_name, Float))

    return dynamic_table


@app.route('/view', methods=['GET','POST'])
def view_table():
    metadata = db.MetaData()
    metadata.reflect(bind=db.engine)
    if request.method == 'GET':
        return render_template('view.html',metadata = metadata)
    if request.method == 'POST':
        selected_table = request.form.get('choose-table')

        # table = db.Table(selected_table, db.metadata, autoload=True, autoload_with=db.engine)
        # # results = db.session.execute(db.select(table)).scalars().all()
        # results = db.session.execute(db.select(table)).fetchall()
        # first_row_dict = dict(results[0]) 

        # Using the SQLAlchemy session to execute a query
        with db.engine.connect() as connection:
            table = db.Table(selected_table, db.metadata, autoload=True, autoload_with=db.engine)
            result = connection.execute(db.select(table))
            columns = result.keys()
            all_records = [dict(zip(columns, row)) for row in result.fetchall()]
        # You can now use the 'all_records' variable as needed
        for record in all_records:
            print("record",record)

        print("columns",columns)
        print("all_records",all_records)
        # return render_template('view.html',metadata = metadata, results =results,first_row_dict = first_row_dict)
        return render_template('view.html',metadata = metadata,records = all_records)


@app.route('/table/update', methods=['POST'])
def table_update():
    try:
        with db.engine.connect() as connection:
            table = db.Table('Table_Config', db.metadata, autoload=True, autoload_with=db.engine)
            update_data = {
                'tbConfig_TABLE_NAME': 'SecondTable',  # Replace with the actual column name
                # Add other columns and their values as needed
            }
            stmt = db.update(table).where(table.c.tbConfig_ID == 1).values(tbConfig_TABLE_NAME='Second Table')
            connection.execute(stmt)
            connection.commit()
            
        return redirect('/view')
    except Exception as e:
        # Handle any errors appropriately, e.g., log the error and display a user-friendly message
        return render_template('error.html', error_message=str(e))







# ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# @app.route('/file_upload', methods=['GET','POST'])
# def upload_file():
#     if 'file' in request.files:
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             f = request.files['file']
#             data_xls = pd.read_excel(f)
#             # return data_xls.to_html()

#             # return render_template('simple.html',  tables=[data_xls.to_html(classes='data')], titles=data_xls.columns.values)
#             # return render_template('simple.html',  tables=[data_xls.to_html(classes='data', header="true")])
#             return render_template("simple.html", column_names=data_xls.columns.values, row_data=list(data_xls.values.tolist()),
#                            link_column="Patient ID", zip=zip)
#     return 'File upload failed'

@app.route('/create_table', methods=['GET','POST'])
def create_table():
    return render_template('table-create-form.html')

# @app.route("/post", methods=["POST"])
# def submit():
#     #use titles to create table
#     titles = request.form.getlist('field_entity')

#     # ['name','email','role']
#     for data in titles:

#         # 'name'
#         value = request.form.getlist(data)
#         print(data)
#         #use this to insert value
#         for v in value:
#             print(v)
#     # print(data)
#     return render_template('index.html', datatable = data)