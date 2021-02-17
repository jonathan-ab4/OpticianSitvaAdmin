import os
from flask import Flask,request,jsonify,render_template,redirect,url_for

from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

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


@app.route('/',methods=['GET'])
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


