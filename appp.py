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



firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


cred = credentials.Certificate("/Users/jonathanabraham/Downloads/Personal/Zutawa/OpticianSitvaNew/optician-sitva-gcp-firebase-adminsdk-rvhx3-37c3683916.json")
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

    uns1 = "Enter email"

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



@app.route('/check',methods =['GET','POST'])
def check():

    doc={}

    doc_t=[]

    res2=[]

    appoint1=()

    

    docs = db.collection(u'user').where(u'email', u'==', test_email).stream()


    for doc in docs:
        doc1 = doc.to_dict()
        doc_id = doc.id

    appoint = db.collection(u'appointment').where(u'user_id', u'==', doc_id).stream()

    

    if(not doc):
               
        return "nothing"

    else:

        for doc in appoint:
            # print(f'{doc.id} => {doc.to_dict()}')
            appointment = doc.to_dict()
            doc_t.append(appointment)

        res = [ sub['epoch'] for sub in doc_t ] 

        for res1 in res:
            stored_time = time.strftime("%d-%m-%Y %H:%M:%S",time.localtime(res1/1000))
            res2.append(stored_time)

        print(res2)

        if(not doc_t):
            return "Nothing2.0"

        else:

            return render_template("base.html",us=res2,uid=doc_id)
   

@app.route('/check/appointment/user=<uid>/app_id=<epoch>',methods =['GET','POST'])
def checkepoch(uid,epoch):

    get_epoch = time.mktime(time.strptime(epoch, '%d-%m-%Y %H:%M:%S')) * 1000

    appoint = db.collection(u'appointment').where(u'user_id', u'==', uid).stream()

    doc_t = []

  

    for doc in appoint:
            # print(f'{doc.id} => {doc.to_dict()}')
            appointment = doc.to_dict()
            doc_t.append(appointment)

    for e in doc_t:

        if(e['epoch']==get_epoch):

            epoch_app = e
            return jsonify(epoch_app)

    return f'{get_epoch}'



    
        



@app.route('/signin', methods=['GET', 'POST'])
def signin():

    uns = "Please verify your mail"

    if request.method == 'POST':
        email = request.form['name']
        password = request.form['pass']
        # try:

        user = auth.sign_in_with_email_and_password(email, password)
        acc = auth.get_account_info(user["idToken"])

        temp = json.dumps(acc)
    
        acc_info = json.loads(temp)

        user_info = acc_info["users"]

        emailVerified = str([sub['emailVerified'] for sub in user_info])


        if(emailVerified.lower() == "[false]"):
	        return  render_template('signinpage.html', us=uns)
    
        else:

            doc_ref = db.collection('admin').document(user["localId"])
            doc = doc_ref.get()
            if doc.exists:
                db.collection("admin").document(user["localId"]).update({u'verified': True})
                
            else:
                data = { 'email': email , 'verified': True}
                db.collection("admin").document(user["localId"]).set(data)
            
            return "Home Page"
        # except:
        #     return user["email"]

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


