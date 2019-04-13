# -*- coding: utf-8 -*-
from flask import Flask, abort, request, render_template, g, Response, send_from_directory, redirect, session, escape, url_for
from werkzeug import secure_filename
#import json
import re
import os
import subprocess
#import redis
import datetime
#import random
import pam
import time
#from io import StringIO

template_dir = os.path.abspath('./')
upload_dir = os.path.abspath('./img')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
FLASKSECRETKEY = subprocess.Popen('grep FLASKSECRETKEY /var/cld/creds/creds | cut -d = -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf8').replace('\n', '')
DOCKERHOST = subprocess.Popen('grep DOCKERHOST /var/cld/creds/creds | cut -d = -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf8').replace('\n', '')

app = Flask(__name__, template_folder=template_dir)
app.config['UPLOAD_FOLDER'] = upload_dir
app.secret_key = FLASKSECRETKEY

#accesslist = set(line.strip() for line in open('../creds/accesslist'))

#@app.before_request

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return remote_addr

# def sessionparse(value):
#   sessionid = re.fullmatch(r'[A-Za-z0-9]+', request.cookies.get('SESSIONID')).string
#   phpsession = re.search(r'.*?username:\"([A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*).*?memberID:\"([0-9]+).*', re.sub('\|\w+\:\d+\:', ':', redis.Redis().get("PHPREDIS_SESSION:"+sessionid).decode(encoding='UTF-8')))
#   if value == 'username':
#     return phpsession.group(1)
#   elif value == 'clientid':
#     return phpsession.group(2)

#@app.after_request

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/')
def index():
   if 'username' in session:
      username = session['username']
      return 'Logged in as ' + username + '<br>' + \
      "<b><a href = '/logout'>click here to log out</a></b>"
   return "You are not logged in <br><a href = '/login'></b>" + \
      "click here to log in</b></a>"

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    try:
      if pam.pam().authenticate(request.form['username'], request.form['password']):
        session['username'] = request.form['username']
        return redirect(url_for('dashboard'))
    except:
      pass
  if 'username' in session:
      username = session['username']
      return 'Logged in as ' + username + '<br>' + \
      "<b><a href = '/logout'>click here to log out</a></b>"
  return render_template('html/login.html',) 
#   return '''
#    <form action = "/login" method = "post">
# <input type=text name="username"><br>
# <input type=text name="password"><br>
# <input type=submit value="Login">
#    </form>
#    '''

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/xactivate')
def xactivate():
  if 'username' in session:
    username = session['username']
    sessid = str(request.cookies.get('session'))
    cloudid = str(request.args['cloudid'])
    test1 = subprocess.Popen('/var/cld/bin/cld-xterm '+cloudid+' '+sessid+' '+username, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    print('/var/cld/bin/cld-xterm '+cloudid+' '+sessid+' '+username)
    return redirect('http://'+DOCKERHOST+'/xterm/'+cloudid, code=302)

@app.route('/factivate')
def factivate():
  if 'username' in session:
    username = session['username']
    sessid = str(request.cookies.get('session'))
    cloudid = str(request.args['cloudid'])
    subprocess.Popen("while :; do ps ax | grep -v grep | grep 'cld\-xterm' | grep -q "+cloudid+" && break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    subprocess.Popen("while :; do ps ax | grep -v grep | grep 'cld\-xterm' | grep -q "+cloudid+" || break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    targetport = subprocess.Popen('grep "'+sessid+'" /var/cld/docker/xtermnginx/etc/nginx/conf.d/sessid  | grep "'+cloudid+'" | tail -1 | egrep -o "XTERMPORT [0-9]{5}" | cut -d \  -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf8').replace('\n', '')
    # print('sudo -u '+username+' sudo /var/cld/bin/cldxmount '+cloudname)
    subprocess.Popen("while :; do wget --server-response --spider http://172.17.0.250:"+targetport+" 2>&1 | grep -q '200 OK' && break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    # print('screen -dm timeout 30m python3 /var/cld/flaskfilemanager/cldapp/app.py --targetpath=/home/'+username+'/mnt/'+cloudname)
    #return redirect('http://'+DOCKERHOST+'/files/'+cloudid+'/fm/index.html', code=302)
    return redirect('http://'+DOCKERHOST+'/files/'+cloudid+'/files/filemanager', code=302)

@app.route('/panel/')
def dashboard():
  if 'username' in session:
    username = session['username']
    # ext_do_list_file = open("../creds/ext_do_list", "r")
    # ext_do_list = ext_do_list_file.readlines()
    # ext_do_list_file.close()
    init_list = ['id', 'hostname', 'fullname']
    do_list = subprocess.Popen('''cat /var/cld/creds/id_list | awk '{print "echo "$1" $(echo "$2" | cut -d _ -f 1) "$2}' | bash''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].decode('utf8').split('\n')
    for n, i in enumerate(do_list):
      do_list[n] = {k:v for k,v in zip(init_list,do_list[n].split(' '))}
    return render_template('html/index.html', username=username, do_list=do_list)

@app.route('/admin')
def admin():
  if 'username' in session:
    username = session['username']
    return render_template('html/admin.html', username=username)

@app.route('/settings')
def settings():
  if 'username' in session:
    username = session['username']
    return render_template('html/settings.html', username=username)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
