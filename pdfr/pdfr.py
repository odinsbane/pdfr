#!/usr/bin/env python
from functools import wraps
from pdfr_config import loadParameters
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import dblib

app = Flask(__name__)
parameters = loadParameters(app)

DATABASE = parameters['DATABASE']
DEBUG = parameters['DEBUG']
SECRET_KEY = parameters['SECRET_KEY']
USERNAMES = parameters['USERNAMES']
PASSWORD = parameters['PASSWORD']
SITE = parameters['SITE']
DESCRIPTION = parameters['DESCRIPTION']
TITLE = parameters['TITLE']

app.config.from_object(__name__)

@app.template_filter('simple_time')
def simple_time(str_time):
    """
      cuts off extra info time.strftime("%a, %d %b %Y %H:%M:%S %Z")
    """
    chunks = str_time.split(' ')
    
    return " ".join([chunks[2], chunks[1]])

#app.jinja_env.filters['simple_time'] = simple_time

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
  

@app.before_request
def before_request():
    g.dbadapter = dblib.getSqliteAdapter(app)
    g.dbadapter.connect()

@app.teardown_request
def teardown_request(exception):
    g.dbadapter.close()
    
@app.route('/docr/')
@login_required
def show_entries():
    entries = g.dbadapter.getEntries()
    if len(entries)==11:
        next_link = "<a href=\"%s\">next</a>"%url_for('show_entries_page', page_id=1)
    else:
        print len(entries)
        next_link = ""
    links = {
        "next":next_link, 
        "previous":"", 
        "all":"<a href=\"%s\">all</a>"%url_for('show_entries_all')
        
        }
    return render_template('show_documents.html',entries=entries[0:10], links=links)

@app.route('/docr/<int:page_id>')
@login_required
def show_entries_page(page_id):
    entries = g.dbadapter.getEntries(offset = page_id*10)
    if len(entries)==11:
        next_link = "<a href=\"%s\">next</a>"%url_for('show_entries_page', page_id=page_id+1)
    else:
        next_link = ""
    if page_id>0:
        previous_link = "<a href=\"%s\">previous</a>"%url_for('show_entries_page', page_id=page_id-1)
    else:
        previous_link = ""
    all_link =  "<a href=\"%s\">all</a>"%url_for('show_entries_all')
    links = {"next":next_link, "previous":previous_link, "all":all_link}
    return render_template('show_documents.html',entries=entries[0:10], links=links)

@app.route('/docr/all')
@login_required
def show_entries_all():
    entries = g.dbadapter.getEntries(limit=-1)
    links = {
        "next":"", 
        "previous":"", 
        "all":""
        }
    return render_template('show_documents.html',entries=entries, links=links)


@app.route('/docr/add', methods=['POST'])
@login_required
def add_entry():
    g.dbadapter.newEntry(request.form)
    if len(g.dbadapter.errors)==0:
        flash('New entry was successfully posted')
    else:
        for error in g.dbadapter.errors:
            flash(error)        
    return redirect(url_for('show_entries'))

@app.route('/docr/login', methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        if not request.form['username'] in app.config['USERNAMES']:
            error = 'login failed'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'login failed'
        else:
            session['logged_in'] = True
            session['username']=request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
@app.route('/docr/show/<int:doc_id>', methods=['POST','GET'])
@login_required
def show(doc_id):
    if request.method == 'POST':
        g.dbadapter.updateEntry(doc_id,request.form)
    entry = g.dbadapter.getEntry(doc_id)        
    return render_template('show.html',entry=entry)


@app.route('/docr/delete/<int:doc_id>', methods=['POST','GET'])
@login_required
def delete(doc_id):
    if request.method == 'GET':
        return render_template('delete.html',entry=g.dbadapter.getEntry(doc_id))
    else:
        g.dbadapter.deleteEntry(doc_id)
        flash('%s successfully deleted'%doc_id)
    return redirect(url_for('show_entries'))

@app.route('/docr/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/docr/xml')
def getXml():
    feed = dict( title=app.config['TITLE'], link=app.config['SITE'], description=app.config['DESCRIPTION'])
    entries=g.dbadapter.getEntries()
    return render_template('feed.xml',feed=feed, entries=entries)
    
def restartDb():
    adapter = dblib.getSqliteAdapter(app)
    adapter.init_db()
    

if __name__=='__main__':
    app.run()
