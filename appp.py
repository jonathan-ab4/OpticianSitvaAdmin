import os
import time,calendar
import json
from pyrebase import pyrebase
from datetime import timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for,session, app

from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)


app.config['SECRET_KEY'] = 'optician_sitva'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=1)

config = {

    "apiKey": "AIzaSyARBIr2OfA_7_xHNvM5VJzhCkx7ullkrM8",
    "authDomain": "optician-sitva-gcp.firebaseapp.com",
    "projectId": "optician-sitva-gcp",
    "storageBucket": "optician-sitva-gcp.appspot.com",
    "messagingSenderId": "552946857203",
     "appId": "1:552946857203:web:3d91953325ef1054af3386",
    "measurementId": "G-B1BT06HZRJ",
    "databaseURL": ""
}

test_email = "jonathanidiculla4@gmail.com"

doc_id = str()

is_logged_in = False



firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


cred = credentials.Certificate("serviceAccountKey.json")
default_app = initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('doctor')

@app.route('/', methods=['GET', 'POST'])
def login():

    uns = "Invalid user or registered user"

    m = "Sign in with registered username and password"

    if request.method == 'POST':
        email = request.form['name']
        password = request.form['pass']
        try:

            auth.create_user_with_email_and_password(email, password)

            user = auth.sign_in_with_email_and_password(email, password)
            auth.send_email_verification(user["idToken"])
            data = { 'email': email , 'verified': False}
            db.collection("admin").document(user["localId"]).set(data)

         
            return redirect(url_for('signin'))

        except:
            
            return render_template('loginpage.html', us=uns)

    return render_template('loginpage.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    global is_logged_in

    session.permanent = True

    is_logged_in = False

    uns = "Please verify your mail"
    inv = "Invalid email or incorrect password"

    if request.method == 'POST':
        email = request.form['name']
        password = request.form['pass']

        try:

            user = auth.sign_in_with_email_and_password(email, password)
            acc = auth.get_account_info(user["idToken"])

            temp = json.dumps(acc)
    
            acc_info = json.loads(temp)

            user_info = acc_info["users"]

            emailVerified = str([sub['emailVerified'] for sub in user_info])


            if(emailVerified.lower() != "[false]"):
                
                is_logged_in = True

                doc_ref = db.collection('admin').document(user["localId"])
                doc = doc_ref.get()
                if doc.exists:
                    db.collection("admin").document(user["localId"]).update({u'verified': True})
                
                else:
                    data = { 'email': email , 'verified': True}
                    db.collection("admin").document(user["localId"]).set(data)
            
                return redirect(url_for('user'))
	            
    
            else:
                return  render_template('signinpage.html', us=uns)

                
        except:
             return render_template('signinpage.html',msg=inv)
    else:
        if is_logged_in == True:
            return redirect(url_for('user'))
        else:
            return render_template('signinpage.html')



@app.route('/reset', methods=['GET', 'POST'])
def reset():

    uns = "Please enter details"

    uns2 = "Password reset link sent"

    if request.method == 'POST':

        emailreset = request.form['email']

        try:


            auth.send_password_reset_email(emailreset)

            return render_template('loginpage.html',s=uns2)

            
        except:

            return render_template('reset.html', us=uns)

    return render_template('reset.html')



@app.route('/user', methods=['GET'])
def user():
    if is_logged_in == True:
        return render_template('user.html')
    else:
        return redirect(url_for('signin'))

@app.route('/userDetails', methods=['POST'])
def appointment():

    m = "User not found"

    if request.method == 'POST':

        email = request.form['email']
        doc = {}

        doc_t = []

        res2 = []

        doc_id = str()


        docs = db.collection(u'user').where(u'email', u'==', email.lower()).stream()

        for doc in docs:
            userList = doc.to_dict()
            doc_id = doc.id

    

        appoint = db.collection(u'appointment').where(u'user_id', u'==', doc_id).stream()

        if not doc:

            return render_template("user.html",msg=m)

        else:

            for doc in appoint:
            # print(f'{doc.id} => {doc.to_dict()}')
                appointment = doc.to_dict()
                doc_t.append(appointment)

            res = [sub['epoch'] for sub in doc_t]

            for res1 in res:
                stored_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(res1 / 1000))
                res2.append(stored_time)


            if (not doc_t):
                return render_template("userDetails.html", user = userList,uid=doc_id)

            else:
                return render_template("userDetails.html", us=res2, uid=doc_id,user = userList)
   


@app.route('/editUser/uid=<uid>', methods=['GET', 'POST'])
def editUser(uid):
    try:
        
        addr = request.form['addr']
        name = request.form['uname']

        
        
        db.collection(u'user').document(uid).update({'name': name, 'address_google_map': addr})

        return render_template('user.html')

    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route('/update/doctor_id=<id>/<u>', methods=['GET'])
def update(id,u):
   
    try:
        
        if(u == 'a'):

            todo_ref.document(id).update({
            'status': '1'})

        else:

            todo_ref.document(id).update({
            'status': '0'})

        return redirect(url_for('doctor'))

    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/delete/doctor_id=<id>', methods=['GET'])
def delete(id):
   
    try:
        
        todo_ref.document(id).delete()

        return redirect(url_for('doctor'))

    except Exception as e:
        return f"An Error Occured: {e}"


          

@app.route('/customer', methods=['GET'])
def customer():
    return render_template('customerSupport.html')


@app.route('/doctor', methods=['GET'])
def doctor():
    if is_logged_in == True:
        return render_template('doctor.html')
    else:
        return redirect(url_for('signin'))
    





@app.route('/logout')
def logout():
    is_logged_in = False
    return redirect(url_for('signin'))



@app.route('/approvedDoctor', methods=['GET'])
def approved():
    query = db.collection('doctor').where(u'status', u'==', '1').stream()
    doc = []

    for docs in query:
        appointment = docs.to_dict()
        doc.append(appointment)

    return render_template('approvedAppoint.html', data=doc)

@app.route('/appointDetails/user=<uid>/epoch=<epoch>', methods=['GET', 'POST'])
def checkepoch(uid, epoch):
   
    get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000


    appoint = db.collection(u'appointment').where(u'doctor_id', u'==', uid).where(u'epoch', u'==',
                                                                                  int(get_epoch)).stream()

    doc_t = []

    for doc in appoint:
        appointment = doc.to_dict()
        doc_id = doc.id

    return render_template('doctorAppointment.html', data=appointment, date=epoch, uid=doc_id)


@app.route('/uappointDetails/user=<uid>/epoch=<epoch>', methods=['GET', 'POST'])
def uappoint(uid, epoch):
    
    get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000


    appoint = db.collection(u'appointment').where(u'user_id', u'==', uid).where(u'epoch', u'==',
                                                                                int(get_epoch)).stream()

    doc_t = []

    for doc in appoint:
        appointment = doc.to_dict()
        doc_id = doc.id

    return render_template('userAppointment.html', data=appointment, date=epoch, uid=doc_id)

@app.route('/appointments/uid=<uid>/epoch=<epoch>',methods=['GET','POST'])
def view_app(uid,epoch):
    get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000
    appoint = db.collection(u'appointment').where(u'user_id', u'==', uid).stream()
    doc_t = []
    for doc in appoint:
            appointment = doc.to_dict()
            doc_t.append(appointment)

    for e in doc_t:

            if(e['epoch']== get_epoch):

                epoch_app = e
                
                return render_template('base.html',data=e)
            

@app.route('/doctorDetails', methods=['GET', 'POST'])
def dotor():

    m = "Doctor not found"
    global doc_id
    if request.method == 'POST':

        email = request.form['email']

        doc = {}

        doc_u = []
        doc_p = []
        total = []

        appointment = {}

        res2 = []
        res_up = []
        res_pa = []

        appoint1 = ()

        docs = db.collection(u'doctor').where(u'email', u'==', email).stream()

        for doc in docs:
            userList = doc.to_dict()
            doc_id = doc.id

        print(int(round(time.time() * 1000)))

        appoint_up = db.collection(u'appointment').where(u'doctor_id', u'==', doc_id).where(u'test_status', u'==',
                                                                                        '0').stream()
        appoint_pa = db.collection(u'appointment').where(u'doctor_id', u'==', doc_id).where(u'test_status', u'==',
                                                                                        '1').stream()

        if not doc:

            return render_template("doctor.html",msg=m)

        else:

            for doc in appoint_up:
                
                appointment = doc.to_dict()
                doc_u.append(appointment)
            for doc in appoint_pa:
                appointment = doc.to_dict()
                doc_p.append(appointment)
        

            res_u = [sub['epoch'] for sub in doc_u]
            res_p = [sub['epoch'] for sub in doc_p]

            for res1 in res_u:
                stored_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(res1 / 1000))
                res_up.append(stored_time)

            for res1 in res_p:
                stored_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(res1 / 1000))
                res_pa.append(stored_time)

            if not appointment:
                return render_template("doctorDetails.html",user=userList,uid=doc_id)

            else:

                return render_template("doctorDetails.html", tot=total, up=res_up, past=res_pa, time=res2, uid=doc_id,
                                   user=userList)

@app.route('/order', methods=['GET'])
def order():
    if is_logged_in == True:
        return render_template('order.html')
    else:
        return redirect(url_for('signin'))

@app.route('/orderDetails/oid=<oid>')
def orderList(oid):
    order_list = db.collection(u'orders').where(u'order_id', u'==', oid).stream()
    for doc in order_list:
            order_dict = doc.to_dict()

    return render_template("orderDetails.html",orderSel=order_dict)




@app.route('/orderDetails',methods=['POST'])
def orderDet():

    m = "No orders present!"

    if request.method == 'POST':

        email = request.form['email']
        doc={}
        doc_o = []

        doc_t = []

        res2 = []

        doc_id = str()

        if "@" in email:

            docs = db.collection(u'orders').where(u'email', u'==', email.lower()).stream()
        else:
            docs = db.collection(u'orders').where(u'order_id', u'==', email.lower()).stream()




        for doc in docs:
            userList = doc.to_dict()
            doc_id = doc.id
            if "@" in email:
                doc_t.append(userList)
            else:
                doc_o.append(userList)



        if doc:

            if "@" in email:
               
                return render_template("orderDetails.html",orderList=doc_t)

            else:
                return render_template("orderDetails.html",orderDet=userList)
        
            
        return render_template("order.html",msg=m)

@app.route('/editDoctor/uid=<uid>', methods=['GET', 'POST'])
def editDoctor(uid):
    try:

        addr = request.form['addr']
        name = request.form['uname']
        db.collection(u'doctor').document(uid).update({'name': name, 'address_google_map': addr})

        return render_template('doctor.html')

    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route('/dAppoint/uid=<uid>', methods=['GET', 'POST'])
def dappoint(uid):
    try:
        pname = request.form['pname']
        dname = request.form['dname']
        db.collection(u'appointment').document(uid).update({'user_name': pname, 'dotor_name': dname})

        return render_template('doctor.html')

    except Exception as e:
        return f"An Error Occurred: {e}"

@app.route('/uAppoint/uid=<uid>', methods=['GET', 'POST'])
def appoint(uid):
    try:
        pname = request.form['pname']
        dname = request.form['dname']
        db.collection(u'appointment').document(uid).update({'user_name': pname, 'dotor_name': dname})

        return render_template('user.html')

    except Exception as e:
        return f"An Error Occurred: {e}"


@app.route('/pendingDoctor', methods=['GET'])
def pending():
    query = db.collection('doctor').where(u'status', u'==', '0').stream()
    doc = []

    for docs in query:
        appointment = docs.to_dict()
        doc.append(appointment)

    return render_template('pendingAppoint.html', data=doc)






# @app.before_request
# def make_session_permanent():
#     print("before_request is running!")
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(seconds=5)

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)
    # app.run(debug=True)


