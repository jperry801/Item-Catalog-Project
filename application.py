from flask import Flask, render_template, request
from flask import redirect, url_for, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, ToyNames, Inventory, User
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

engine = create_engine('sqlite:///appwithusers.db?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Declare client_id
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# State token to prevent request forgery
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Login user function
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't make a new one
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                    'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserId(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except ImportError:
        return None


# Logout user
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
            'Current user is no longer connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    output = ''
    output += 'username'
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps(
            'User Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view the Toybox Items #
@app.route('/toybox/<int:toy_id>/menu/JSON/')
def ListToyItemsJSON(toy_id):
    allToys = session.query(ToyNames).filter_by(id=toy_id).one()
    allInv = session.query(Inventory).filter_by(toynames_id=toy_id).all()
    return jsonify(Inventory=[a.serialize for a in allInv])


# Homepage
@app.route('/')
@app.route('/toybox/')
def index():
    allToys = session.query(ToyNames).all()
    allInventory = session.query(Inventory).all()
    currentUsers = session.query(User).filter_by(name=User.name).one
    if 'username' not in login_session:
        return render_template('publicIndex.html', allToys=allToys)
    else:
        return render_template('index.html', currentUsers=currentUsers,
                               allToys=allToys, allInventory=allInventory)


# Adding a toy
@app.route('/toybox/new/', methods=['GET', 'POST'])
def addToy():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        addingToy = ToyNames(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(addingToy)
        session.commit()
        flash('New toy created!')
        return redirect(url_for('index'))
    else:
        return render_template('addToy.html', addToy=addToy)


# Edit existing toy
@app.route('/toybox/<int:toy_id>/edit/', methods=['GET', 'POST'])
def editToy(toy_id):
    if 'username' not in login_session:
        return redirect('/login')
    if editToyName.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized to edit toy');}</script>"
    editToyName = session.query(ToyNames).filter_by(id=toy_id).one()
    editingToy = session.query(Inventory).filter_by(id=toy_id).all()
    if request.method == 'POST':
        if request.form['name']:
            editToyName.name = request.form['name']
        session.add(editToyName)
        session.commit()
        flash('Toy Edited')
        return redirect(url_for('index'))
    else:
        return render_template('editToy.html', toy_id=toy_id,
                               editToyName=editToyName, e=editingToy)


# Delete existing toy
@app.route('/toybox/<int:toy_id>/delete/', methods=['GET', 'POST'])
def deleteToy(toy_id):
    toyToDelete = session.query(ToyNames).filter_by(id=toy_id).one()
    if request.method == 'POST':
        session.delete(toyToDelete)
        session.commit()
        flash('Toy Deleted!!')
        return redirect(url_for('index'))
    else:
        return render_template('deleteToy.html', t=toyToDelete)


# Show menu of selected toy
@app.route('/toybox/<int:toy_id>/')
@app.route('/toybox/<int:toy_id>/menu/')
def ListToyItems(toy_id):
    ListofToys = session.query(ToyNames).filter_by(id=toy_id).one()
    creator = getUserInfo(ListofToys.user_id)
    ListofInventory = session.query(Inventory).filter_by(
        toynames_id=toy_id).all()
    if 'username' not in login_session or creator.id != login_session[
     'user_id']:
        return render_template('publicCurrentList.html', ListofToys=ListofToys,
                               ListofInventory=ListofInventory)
    else:
        return render_template('currentList.html', ListofToys=ListofToys,
                               ListofInventory=ListofInventory,
                               creator=creator)


# New toy item
@app.route('/toybox/<int:toy_id>/menu/new/', methods=['GET', 'POST'])
def AddToyItem(toy_id):
    addToyNames = session.query(ToyNames).filter_by(id=toy_id).one()
    if request.method == 'POST':
        newItem = Inventory(name=request.form['name'],
                            description=request.form['description'],
                            toynames_id=toy_id)
        session.add(newItem)
        session.commit()
        flash('Toy Item Added!')
        return redirect(url_for('ListToyItems', toy_id=addToyNames.id))
    else:
        return render_template('addToyItem.html', addToyNames=addToyNames)


# Edit selected toy
@app.route('/toybox/<int:toy_id>/menu/<int:inventory_id>/edit/',
           methods=['GET', 'POST'])
def EditToyItem(toy_id, inventory_id):
    if 'username' not in login_session:
        return redirect('/login')
    if editToyItem.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized to edit item');}</script>"
    editToyItem = session.query(ToyNames).filter_by(id=toy_id).one()
    editingToyItem = session.query(Inventory).filter_by(id=inventory_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editingToyItem.name = request.form['name']
        if request.form['description']:
            editingToyItem.description = request.form['description']
        session.add(editingToyItem)
        session.commit()
        flash('Toy Item Edited')
        return redirect(url_for('ListToyItems', toy_id=editToyItem.id))
    else:
        return render_template('editToyItem.html', editToyItem=editToyItem,
                               e=editingToyItem)


# Delete selected toy from list
@app.route('/toybox/<int:toy_id>/menu/<int:inventory_id>/delete/',
           methods=['GET', 'POST'])
def DeleteToyItem(toy_id, inventory_id):
    if 'username' not in login_session:
        return redirect('/login')
    delToyName = session.query(ToyNames).filter_by(id=toy_id).one()
    delToyItem = session.query(Inventory).filter_by(id=inventory_id).one()
    if request.method == 'POST':
        session.delete(delToyItem)
        session.commit()
        flash('Toy Item Deleted!!')
        return redirect(url_for('ListToyItems', toy_id=delToyName.id))
    else:
        return render_template('deleteToyItem.html',
                               delToyName=delToyName, d=delToyItem)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = 'super_secret_key'
    app.run(host='0.0.0.0', port=8000)
