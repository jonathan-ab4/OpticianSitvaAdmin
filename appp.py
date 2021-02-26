import os
import time,calendar
import json
from pyrebase import pyrebase
from flask import Flask, request, jsonify, render_template, redirect, url_for

from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

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


@app.route('/update/doctor_id=<id>/<u>', methods=['GET'])
def update(id,u):
   
    try:
        
        if(u == 'a'):

            todo_ref.document(id).update({
            'status': '1'})

        else:

            todo_ref.document(id).update({
            'status': '0'})

        return redirect(url_for('read'))

    except Exception as e:
        return f"An Error Occured: {e}"


@app.route('/delete/doctor_id=<id>', methods=['GET'])
def delete(id):
   
    try:
        
        todo_ref.document(id).delete()

        return redirect(url_for('read'))

    except Exception as e:
        return f"An Error Occured: {e}"

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
                return render_template("userDetails.html", user = userList)

            else:
                return render_template("userDetails.html", us=res2, uid=doc_id,user = userList)
    # else:
    #     return redirect(url_for('user'))


@app.route('/editUser/uid=<uid>', methods=['GET', 'POST'])
def editUser(uid):
    try:
        # if request.method == 'POST':
        mail = request.form['email']
        addr = request.form['addr']
        name = request.form['uname']
        db.collection(u'user').document(uid).update({'name': name})

        doc = {}

        doc_t = []

        res2 = []

        appoint1 = ()

        docs = db.collection(u'user').where(u'email', u'==', mail).stream()

        for doc in docs:
            userList = doc.to_dict()
            doc_id = doc.id

        appoint = db.collection(u'appointment').where(u'user_id', u'==', doc_id).stream()

        if not doc:

            return "nothing"

        else:

            for doc in appoint:
                # print(f'{doc.id} => {doc.to_dict()}')
                appointment = doc.to_dict()
                doc_t.append(appointment)

            res = [sub['epoch'] for sub in doc_t]

            for res1 in res:
                stored_time = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime(res1 / 1000))
                res2.append(stored_time)

            print(res2)

            if (not doc_t):
                return "Nothing2.0"

            else:
                return render_template("userDetails.html", us=res2, uid=doc_id, user=userList)

    except Exception as e:
        return f"An Error Occurred: {e}"



@app.route('/customer', methods=['GET'])
def customer():
    return render_template('customerSupport.html')


@app.route('/doctor', methods=['GET'])
def doctor():
    return render_template('doctor.html')


@app.route('/user', methods=['GET'])
def user():
    if is_logged_in == True:
        return render_template('user.html')
    else:
        return redirect(url_for('signin'))



# @app.route('/check',methods =['GET','POST'])
# def check():

#     doc={}

#     doc_t=[]

#     res2=[]

    
#     docs = db.collection(u'user').where(u'email', u'==', test_email).stream()


#     for doc in docs:
#         doc1 = doc.to_dict()
#         doc_id = doc.id

#     appoint = db.collection(u'appointment').where(u'user_id', u'==', doc_id).stream()

    

#     if(not doc):
               
#         return "nothing"

#     else:

#         for doc in appoint:
#             # print(f'{doc.id} => {doc.to_dict()}')
#             appointment = doc.to_dict()
#             doc_t.append(appointment)

#         res = [ sub['epoch'] for sub in doc_t ] 

#         for res1 in res:
#             stored_time = time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(res1/1000))
#             res2.append(stored_time)

#         print(res2)

#         if(not doc_t):
#             return "Nothing2.0"

#         else:

#             return render_template("base.html",us=res2,uid=doc_id)

@app.route('/appointments',methods=['GET','POST'])
def ap():
    if request.method == 'POST':
        uid = request.form['uid']
        epoch = request.form['epoch']
        print(request.form)
        get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000

        appoint = db.collection(u'appointment').where(u'user_id', u'==', uid).stream()
        doc_t = []

        print(epoch)


        for doc in appoint:
            # print(f'{doc.id} => {doc.to_dict()}')
            appointment = doc.to_dict()
            doc_t.append(appointment)

        for e in doc_t:

            if(e['epoch']==get_epoch):

                epoch_app = e
                print(epoch_app)
                return redirect(url_for('view_app'))
        
        return "hi"


            #return render_template("base.html",us=epoch,uid=uid)

@app.route('/view/appointment')
def view_app():
    return "hi"




   

# @app.route('/check/appointment/user=<uid>/app_id=<epoch>',methods =['GET','POST'])
# def checkepoch(uid,epoch):

#     get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000

#     appoint = db.collection(u'appointment').where(u'user_id', u'==', uid).stream()

#     doc_t = []


#     for doc in appoint:
#             # print(f'{doc.id} => {doc.to_dict()}')
#             appointment = doc.to_dict()
#             doc_t.append(appointment)

#     for e in doc_t:

#         if(e['epoch']==get_epoch):

#             epoch_app = e
#             return jsonify(epoch_app)

#     return f'{get_epoch}'



@app.route('/dash', methods=['GET','POST'])
def dashboard():
    if is_logged_in == True:
         return render_template('dashboard.html')
    else:
        return redirect(url_for('signin'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    global is_logged_in

    is_logged_in == False

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
            
                return redirect(url_for('dashboard'))
	            
    
            else:
                return  render_template('signinpage.html', us=uns)

                
        except:
             return render_template('signinpage.html',msg=inv)
    else:
        if is_logged_in == True:
            return redirect(url_for('dashboard'))
        else:
            return render_template('signinpage.html')

@app.route('/list', methods=['GET'])
def read():
   
    try:
        
        all_todos = [doc.to_dict() for doc in todo_ref.stream()]
        
        return render_template('page.html',t= all_todos)
    except Exception as e:
        return f"An Error Occured: {e}"

port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=port)


