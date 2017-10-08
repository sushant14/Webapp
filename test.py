from flask import Flask, render_template, request,session,jsonify,flash,redirect,url_for
from functools import wraps
import stripe
import string
from prettytable import PrettyTable
import smtplib,string
import sqlite3 as sql
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

order_no=random.randint(111,999)
app = Flask(__name__)
app.secret_key = 'my precious'
STRIPE_PUBLISHABLE_KEY = 'pk_test_BEaOg6TITP2isrwvxMpgw2bv'  
STRIPE_SECRET_KEY = 'sk_test_TVy6hPJMNJN3nscryI0xWrPM'
stripe.api_key = STRIPE_SECRET_KEY



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('home'))
    return wrap
@app.route('/')
def home():
   return render_template('home.html')

@login_required
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('home'))

@login_required
@app.route('/payment/<ordered_items>/<amount>/<user_name>')
def payment(ordered_items,amount,user_name):
   return render_template('pay.html',ordered_items=ordered_items,amount=amount,user_name=user_name)

@app.route('/signup')
def signup():
	return render_template('studentii.html')
@app.route('/login')
def login():
   return render_template('login1.html')

@app.route('/adduser',methods = ['POST', 'GET'])
def adduser():
   if request.method == 'POST':
      try:
         roll = request.form['roll']
         email = request.form['email']
         password = request.form['password']
         mobile = request.form['mobile']
         
         with sql.connect("test.db") as con:
            cur = con.cursor()
            
            cur.execute("INSERT INTO users (rollno,email,password,mobileno) VALUES (?,?,?,?)",(roll,email,password,mobile) )
            
            con.commit()
            msg = "Record successfully added"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         return render_template("result.html",msg = msg)
         con.close()


@app.route('/logincheck',methods = ['POST', 'GET'])
def logincheck():
  roll = request.form['roll']
  password = request.form['password']
  conn = sql.connect("test.db")
  cur = conn.cursor()
  t = (roll,password )
  cur.execute('SELECT 1 FROM users WHERE rollno = ? AND password = ?',t)
  if cur.fetchone():	
    session['logged_in'] = True
    reply = "Welcome" + " " + roll
    con = sql.connect("test.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select * from items")
    rows = cur.fetchall(); 
    return render_template("WELCOME.html",reply = reply,rows = rows,user_name=roll)
  else:
		mesg = "Sorry,You have entered Wrong user or Wrong Password"
 		return render_template("result1.html",mesg = mesg)
  con.close()

@login_required
@app.route('/abc/<xyz>/<amount>/<user_name>')
def  abc(xyz,amount,user_name):
  s=xyz
  s1=xyz
  s=s.split(',')
  length = len(s)
  i=0
  list1=[];
  while(i<length):
    list1.append([s[i],s[i+1],s[i+2]])
    i=i+3
  #return jsonify(list1)
  return render_template("file1.html",data=list1,amount=amount,user_name=user_name,s1=s1)

@login_required
@app.route('/byyyy/<ordered_items>/<hhh>/<user_name>')
def  byyyy(ordered_items,hhh,user_name):
  user_id=user_name
  final_amount=hhh
  s=ordered_items
  s=s.split(',')
  length = len(s)
  i=0
  list1=[];
  while(i<length):
    list1.append([s[i],s[i+1],s[i+2]])
    i=i+3
  con=sql.connect("test.db")
  cur=con.cursor()
  cur.execute('SELECT mobileno FROM users WHERE rollno = ?',(user_id,))
  mobile_number=cur.fetchone()[0]
  cur.execute('SELECT email FROM users WHERE rollno = ?',(user_id,))
  email_id=cur.fetchone()[0]
  con.close()
  con1=sql.connect("test.db")
  cur1=con1.cursor()
  cur1.execute("INSERT INTO payment_history (order_no,User,payment,mobileno,emailid) VALUES (?,?,?,?,?)",(order_no,user_id,final_amount,mobile_number,email_id) )
  con1.commit()          
  con1.close()
  file_name=str(order_no)
  file_name=file_name+".txt"
  f=open(file_name,"w")
  t=PrettyTable(['S.NO','ITEM NAME','QUANTITY'])
  len1=len(list1)
  j=1
  i=0
  while(i<len1):
    t.add_row([list1[i][0],list1[i][1],list1[i][2]])
    i=i+1
  r=str(t)
  f.write("\nCU-PAL\n\n")
  f.write("User Name %s"%user_id)
  f.write("\nEmail-id %s"%email_id)
  f.write("\n Your Order has been placed and your order number is %s\n"%order_no)
  f.write(r)
  f.write("\nTOTAL AMOUNT PAYED %s" % final_amount)
  f.write("\n Please go to the counter and collect you order\nTHANK YOU!!")
  f.close()
  fromaddr = "earn4800@gmail.com"
  toaddr = email_id
  msg = MIMEMultipart()
  msg['From'] = fromaddr
  msg['To'] = toaddr
  msg['Subject'] = "CU-PAL(YOUR ORDER HAS BEEN PLACED)"
  body = "\nThank You for using our application\nYour Order Number is %s \nRegards\nCU-PAL"%order_no
  msg.attach(MIMEText(body, 'plain'))
  filename = file_name
  path="/home/sushant/Desktop/flask_test/"+file_name
  attachment = open(path, "rb")
  p = MIMEBase('application', 'octet-stream')
  p.set_payload((attachment).read())
  encoders.encode_base64(p)
  p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
  msg.attach(p)
  s = smtplib.SMTP('smtp.gmail.com', 587)
  s.starttls()
  s.login(fromaddr, "sushant123")
  text = msg.as_string()
  s.sendmail(fromaddr, toaddr, text)
  s.quit()
  return render_template('bye.html')


























#ADMINNNN DETAILS****************************************************************************************************************************
@app.route('/admin')
def admin():
  return render_template("a.html")

@app.route('/admin_items')
def admin_items():
  con = sql.connect("test.db")
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("select * from items")
  rows = cur.fetchall(); 
  return render_template("c.html",rows = rows)
  con.close()


@app.route('/admin_payment')
def admin_payment():
  con = sql.connect("test.db")
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("select * from payment_history")
  rows = cur.fetchall(); 
  return render_template("d.html",rows = rows)
  con.close()

@app.route('/admin_users')
def admin_users():
  return render_template("e.html")







if __name__ == '__main__':
   app.run(debug = True)




