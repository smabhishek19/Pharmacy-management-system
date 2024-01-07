from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,login_user,login_manager,logout_user,LoginManager
from flask_login import login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
import random
from datetime import date


#my DB connection
local_server= True
app = Flask(__name__)
app.secret_key='abhi1234'

#this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#app.config['SQLAlchemy_DATABASE_URI']='mysql://username:password@Localhost/database_table_name'

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@Localhost/pms'
db=SQLAlchemy(app) #connecting with db


#here we will create db models(tables) 

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20))
    email=db.Column(db.String(30),unique=True)
    password=db.Column(db.String(1000))

class Inventory(db.Model):
    pid=db.Column(db.String(15),primary_key=True)
    pname=db.Column(db.String(20))
    quantity=db.Column(db.Integer)
    type=db.Column(db.String(20))
    expdate=db.Column(db.String(50),nullable=False)
    fprice=db.Column(db.Integer)
    mrp=db.Column(db.Integer)
    pdate=db.Column(db.String(50),nullable=False)
    disname=db.Column(db.String(20))

class Stock(db.Model):
    pname=db.Column(db.String(20),primary_key=True)
    quantity=db.Column(db.Integer)
    mrp=db.Column(db.Integer)	   
    uid=db.Column(db.Integer)	

class Customer(db.Model):
    cid=db.Column(db.String(15),primary_key=True)
    cname=db.Column(db.String(20))
    cphone=db.Column(db.Integer)
    uid=uid=db.Column(db.Integer)	

class Sales(db.Model):
    sid=db.Column(db.String(15),primary_key=True)
    pname=db.Column(db.String(20))
    sdate=db.Column(db.String(50),nullable=False)
    quantity=db.Column(db.Integer)	   
    cid=db.Column(db.String(10))
    totalcost=db.Column(db.Integer)
"""
class Total(db.Model):
    totalcost=db.Column(db.Integer)
    sdate=db.Column(db.String(50),nullable=False)
"""    
gpid=10
gcid=10
gsid=10
tcost=0

@app.route("/")
def index():
    return render_template('login.html')
 
@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST" :   #to get values from frontend( that is from 'form' )
        email=request.form.get('email')
        password=request.form.get('password')
        #print(User.query.filter_by(email=email))
        user1=User.query.filter_by(email=email).first() 
        
        if user1 and check_password_hash(user1.password,password):
            login_user(user1)
            flash("Login successfull","primary")
            return redirect(url_for('home'))
        else:
            flash("invalid email or password","danger")
            return render_template("/login.html")

    return render_template('login.html')


def checkString( cpass ) :
	flagl = False
	flag2 = False
	for i in cpass :
		if i.isalpha():
			flagl = True
		if i.isdigit():
			flag2 = True
	return flagl and flag2


@app.route("/signup",methods=["POST","GET"])
def signup(): 
    if request.method == "POST" :   #to get values from frontend( that is from 'form' )
        username1=request.form.get('username')
        email1=request.form.get('email')
        password1=request.form.get('password')
        if checkString(password1) and len(password1)>=8:
            user1=User.query.filter_by(email=email1).first() 
            if user1 :
                flash("email already exist","primary")
                return render_template('/signup.html')
            encpassword=generate_password_hash(password1)
            new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username1}','{email1}','{encpassword}')")
            return render_template('/login.html')
        else:
            flash("password should contain atleast one character, one number and minimum 8 characters","danger")
            return render_template('/signup.html')
    return render_template('signup.html')

@app.route("/logout")
@login_required
def logout():
    logout_user
    flash("logout Sucessfull","success")
    return redirect(url_for('login'))


@app.route("/home")
@login_required
def home():
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else:
         query=db.engine.execute(f"SELECT `sales`.`sdate` AS `sdate`,SUM( `sales`.`totalcost`) AS `totalcost` FROM ( `sales` JOIN `customer` ON ( `sales`.`cid` = `customer`.`cid` AND `customer`.`uid` = {current_user.id} AND `sales`.`sdate` = CURRENT_DATE))")    
         query1=db.engine.execute(f"SELECT SUM(`inventory`.`fprice`) AS mrp FROM `inventory` INNER JOIN `user` ON `inventory`.`uid` = {current_user.id} AND `inventory`.`pdate`=CURRENT_DATE AND `user`.`id`={current_user.id}")
         return render_template('home.html',username=current_user.username,query=query,query1=query1)


@app.route("/inventory/<string:fi>",methods=['POST','GET'])
def inventory(fi):
 #  doct=db.engine.execute("SELECT * FROM `inventory`")
    em=current_user.id 
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html") 
    
    if fi=="today":          
         query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} AND `pdate` =CURRENT_DATE ORDER BY `inventory`.`pdate` ASC")
         return render_template("/inventory.html",query=query)
    
    elif fi=="month":          
         query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} AND `pdate` BETWEEN MONTH(NOW())-1 AND CURRENT_DATE ORDER BY `inventory`.`pdate` ASC")
         return render_template("/inventory.html",query=query)
 
    elif fi=="preyear":
         query=db.engine.execute(f" SELECT * FROM `inventory` WHERE `uid`={em} AND YEAR(`pdate`)  BETWEEN YEAR(NOW())-2 AND YEAR(NOW())-1 ORDER BY `inventory`.`pdate` ASC")
         return render_template("/inventory.html",query=query)

    else :
         query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} ORDER BY `inventory`.`pdate` DESC")
         return render_template("/inventory.html",query=query)


@app.route("/sales/<string:sa>",methods=['POST','GET'])
@login_required
def sales(sa):
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    if sa=="today":
         query=db.engine.execute(f"SELECT `sales`.`sid`,`sales`.`sdate`,`sales`.`quantity`,`sales`.`totalcost` ,`customer`.`cname`,`sales`.`pname` FROM `sales` INNER JOIN `customer` ON `sales`.`cid`=`customer`.`cid` AND `customer`.`uid`={current_user.id} AND `sdate` =CURRENT_DATE ORDER BY `sales`.`sdate` DESC")
    elif sa=="month":
         query=db.engine.execute(f"SELECT `sales`.`sid`,`sales`.`sdate`,`sales`.`quantity`,`sales`.`totalcost` ,`customer`.`cname`,`sales`.`pname` FROM `sales` INNER JOIN `customer` ON `sales`.`cid`=`customer`.`cid` AND `customer`.`uid`={current_user.id} AND `sdate` BETWEEN MONTH(NOW())-1 AND CURRENT_DATE ORDER BY `sales`.`sdate` DESC ")
    elif sa=="preyear":
         query=db.engine.execute(f"SELECT `sales`.`sid`,`sales`.`sdate`,`sales`.`quantity`,`sales`.`totalcost` ,`customer`.`cname`,`sales`.`pname` FROM `sales` INNER JOIN `customer` ON `sales`.`cid`=`customer`.`cid` AND `customer`.`uid`={current_user.id} AND YEAR(`sales`.`sdate`) BETWEEN YEAR(NOW())-2 AND YEAR(NOW())-1 ORDER BY `sales`.`sdate` DESC ")
    else :
         query=db.engine.execute(f"SELECT `sales`.`sid`,`sales`.`sdate`,`sales`.`quantity`,`sales`.`totalcost` ,`customer`.`cname`,`sales`.`pname` FROM `sales` INNER JOIN `customer` ON `sales`.`cid`=`customer`.`cid` AND `customer`.`uid`={current_user.id} ORDER BY `sales`.`sdate` DESC ")
         print("hi")
    return render_template("/sales.html",query=query)




@app.route("/cart",methods=['POST','GET'])
def cart():
    global gsid,tcost
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else :
         query5=db.engine.execute(f"SELECT * FROM `sales` WHERE cid='{gcid}'")
         print(gcid)
         return render_template("/cart.html",query=query5,cost=tcost)

       

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    em=current_user.id 
    posts=Inventory.query.filter_by(pid=pid).first()
    if request.method=="POST":
             gpid=posts.pid
             pname=request.form.get('pname')
             quantity=request.form.get('quantity')
             type=request.form.get('type')
             expdate=request.form.get('expdate')
             fprice=request.form.get('fprice')
             mrp=request.form.get('mrp')
             pdate=request.form.get('pdate')
             disname=request.form.get('disname')
             user3=Stock.query.filter_by(pname=pname).first() 
             if user3:
                 db.engine.execute(f"UPDATE `inventory` SET `pname` = '{pname}', `quantity` = '{quantity}',`type`='{type}', `expdate` = '{expdate}', `fprice` = '{fprice}', `mrp` = '{mrp}', `pdate` = '{pdate}', `disname` = '{disname}' WHERE `inventory`.`pid` = '{gpid}'")
                 qua=Stock.query.filter(Stock.pname == pname).first().quantity
                 quantity=int(qua) + int(quantity)
                 querey3=db.engine.execute(f"UPDATE `stock` SET `quantity` = '{quantity}' WHERE `stock`.`pname` = '{pname}'")
                 flash("Inventory is updated","success")
                 query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} ORDER BY `inventory`.`pdate` DESC")
                 return render_template("/inventory.html",query=query)
             else:
                 query2=db.engine.execute(f"INSERT INTO `stock` (`pname`, `quantity`, `mrp`, `uid`) VALUES ('{pname}', '{quantity}', '{mrp}', '{current_user.id}');")
                 db.engine.execute(f"UPDATE `inventory` SET `pname` = '{pname}', `quantity` = '{quantity}',`type`='{type}', `expdate` = '{expdate}', `fprice` = '{fprice}', `mrp` = '{mrp}', `pdate` = '{pdate}', `disname` = '{disname}' WHERE `inventory`.`pid` = '{gpid}'")
                 flash("Inventory is updated","success")
                 query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} ORDER BY `inventory`.`pdate` DESC")
                 return render_template("/inventory.html",query=query)
    return render_template('edit.html',posts=posts)



@app.route("/cartedit/<string:si>/<string:pn>",methods=['POST','GET'])
@login_required
def cartedit(si,pn):
    global gcid,tcost
    posts=Sales.query.filter_by(sid=si,pname=pn).first()
    posts1=Customer.query.filter_by(cid=posts.cid).first()
    print('post :',posts.cid)
    print('hello')
    if request.method=="POST":
             print('hello1')
             sid=si
             gcid=posts.cid
             cname=request.form.get('cname')
             cphone=request.form.get('cphone')
             pname=request.form.get('pname')
             quantity=request.form.get('quantity')
             sdate=request.form.get('sdate')
             mrp=request.form.get('mrp')
             db.engine.execute(f"UPDATE `customer` SET `cname` = '{cname}', `cphone` = '{cphone}' WHERE `customer`.`cid` = '{gcid}'")
             db.engine.execute(f"UPDATE `sales` SET `pname` = '{pname}', `sdate` = '{sdate}', `quantity` = '{quantity}', `totalcost` = '{mrp}' WHERE `sales`.`sid` = '{sid}' AND `sales`.`pname` = '{pn}'")
             flash("cart is updated","success")
             query5=db.engine.execute(f"SELECT * FROM `sales` WHERE cid='{gcid}'")
             return render_template("/cart.html",query=query5,cost=tcost)
    return render_template('/cartedit.html',posts=posts,posts1=posts1)



@app.route("/addproduct",methods=['POST','GET'])
@login_required
def addproduct():
    global gcid,gsid,tcost
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else:
        if request.method=="POST":
             cname=request.form.get('cname')
             cid=gcid
             print(cid)
             sid=gsid  
             pname1=request.form.get('pname')
             quantity=request.form.get('quantity')
             sdate=request.form.get('sdate')
             totalcost=request.form.get('mrp')
             tcost=int(totalcost)+tcost
             query1=db.engine.execute(f"INSERT INTO `sales` (`sid`, `pname`, `sdate`, `quantity`, `cid`,`totalcost`) VALUES ('{sid}', '{pname1}', '{sdate}', '{quantity}', '{cid}','{totalcost}')")
             flash("Cart is updated successfully","info")
             return redirect(url_for('cart'))     
        return render_template('/addproduct.html')




@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    db.engine.execute(f"DELETE FROM `inventory` WHERE `inventory`.`pid`='{pid}'")
    flash("Slot Deleted Successful","danger")
    return render_template('/inventory.html')

@app.route("/cartdelete/<string:si>/<string:pn>/<int:tc>",methods=['POST','GET'])
@login_required
def cartdelete(si,pn,tc):
    global tcost
    tcost=tcost-tc
    db.engine.execute(f"DELETE FROM `sales` WHERE `sales`.`sid` = '{si}' AND `sales`.`pname` = '{pn}'")
    flash("Slot Deleted Successful","danger")
    return redirect(url_for('cart'))


@app.route("/addsales",methods=['POST','GET'])
@login_required
def addsales():
    global gcid,gsid,tcost
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else:
        if request.method=="POST":
             uid=current_user.id
             cname=request.form.get('cname')
             gcid="c"+ current_user.username + str(current_user.id) + str((random.randint(100,999)))  
             print(gcid)
             gsid="s" + str(current_user.id) + str((random.randint(100,999)))  
             print(gsid)
             cphone=request.form.get('cphone')
             pname1=request.form.get('pname')
             quantity=request.form.get('quantity')
             sdate=request.form.get('sdate')
             totalcost=int(request.form.get('mrp'))
             tcost=int(totalcost)+tcost
             user1=Stock.query.filter_by(pname=pname1).first() 
             if user1 :
                 query1=db.engine.execute(f"INSERT INTO `customer` (`cid`, `cname`, `cphone`, `uid`) VALUES ('{gcid}', '{cname}', '{cphone}', '{uid}')")
                 query1=db.engine.execute(f"INSERT INTO `sales` (`sid`, `pname`, `sdate`, `quantity`, `cid`,`totalcost`) VALUES ('{gsid}', '{pname1}', '{sdate}', '{quantity}', '{gcid}','{tcost}')")
                 flash("Inventory added successfully","info")    
                 return redirect(url_for('cart'))
             else :
                 flash("Product not available","info")
        return render_template('/addsales.html')


@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def sedit(pid):
    posts=Inventory.query.filter_by(pid=pid).first()
    if request.method=="POST":
             gpid=posts.pid
             pname=request.form.get('pname')
             quantity=request.form.get('quantity')
             type=request.form.get('type')
             expdate=request.form.get('expdate')
             fprice=request.form.get('fprice')
             mrp=request.form.get('mrp')
             pdate=request.form.get('pdate')
             disname=request.form.get('disname')

             db.engine.execute(f"UPDATE `inventory` SET `pname` = '{pname}', `quantity` = '{quantity}', `expdate` = '{expdate}', `fprice` = '{fprice}', `mrp` = '{mrp}', `pdate` = '{pdate}', `disname` = '{disname}' WHERE `inventory`.`pid` = '{gpid}'")
             flash("Inventory is updated","success")
             return redirect(url_for('inventory'))
    return render_template('edit.html',posts=posts)



@app.route("/addinventory",methods=['POST','GET'])
@login_required
def addinventory():
    em=current_user.id 
    global gpid
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else:
        if request.method=="POST":
             uid=current_user.id
             gpid="P" + str(current_user.id) + str((random.randint(1000,9999)))  
             pname1=request.form.get('pname')
             quantity=request.form.get('quantity')
             type=request.form.get('type')
             expdate=request.form.get('expdate')
             fprice=request.form.get('fprice')
             mrp=request.form.get('mrp')
             pdate=request.form.get('pdate')
             disname=request.form.get('disname')
             query1=db.engine.execute(f"INSERT INTO `inventory` (`pid`,`pname`, `quantity`, `type`, `expdate`, `fprice`, `mrp`, `pdate`, `disname`,`uid`) VALUES ('{gpid}','{pname1}', '{quantity}', '{type}', '{expdate}', '{fprice}', '{mrp}', '{pdate}', '{disname}','{uid}')")
             user3=Stock.query.filter_by(pname=pname1).first() 
             if user3:
                 qua=Stock.query.filter(Stock.pname == pname1).first().quantity
                 quantity=int(qua) + int(quantity)
                 querey3=db.engine.execute(f"UPDATE `stock` SET `quantity` = '{quantity}' WHERE `stock`.`pname` = '{pname1}'")
                 
                 query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} ORDER BY `inventory`.`pdate` DESC")
                 return render_template("/inventory.html",query=query)
             else:
                 query2=db.engine.execute(f"INSERT INTO `stock` (`pname`, `quantity`, `mrp`, `uid`) VALUES ('{pname1}', '{quantity}', '{mrp}', '{uid}');")
                 flash("Inventory added successfully","info")
                 query=db.engine.execute(f"SELECT * FROM `inventory` WHERE `uid`={em} ORDER BY `inventory`.`pdate` DESC")
                 return render_template("/inventory.html",query=query)
        return render_template('/addinventory.html')



@app.route("/bill")
@login_required
def bill():
    if not User.is_authenticated:
        flash("Login to access this page","danger")
        return render_template("/login.html")
    else:
         print('hello')
         """global gcid,gsid
          today = date.today()
     print(gsid,gcid)
    posts=Sales.query.filter_by(sid=gsid,pname=gcid).first()
    posts1=Customer.query.filter_by(cid=gcid).first()
         """
         flash("updated sale","success")
         redirect(url_for('home'))




app.run(debug=True)

"""try:
        Test.query.all()
        return render_template('index.html')
    except:
        return "DB not connected" """

