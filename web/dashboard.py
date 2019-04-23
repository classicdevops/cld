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
import logging
import sys

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf8')

logging.basicConfig(level=logging.DEBUG)
template_dir = os.path.abspath('./')
upload_dir = os.path.abspath('./img')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
FLASKSECRETKEY = bash('grep FLASKSECRETKEY /var/cld/creds/creds | cut -d = -f 2').replace('\n', '')
DOCKERHOST = bash('grep DOCKERHOST /var/cld/creds/creds | cut -d = -f 2').replace('\n', '')

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

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf8')


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
    test1 = subprocess.Popen('/var/cld/bin/cld-xterm '+cloudid+' '+sessid+' '+username, shell=True, stdout=subprocess.PIPE).communicate()
    print('/var/cld/bin/cld-xterm '+cloudid+' '+sessid+' '+username)
    return redirect('http://'+DOCKERHOST+'/xterm/'+cloudid, code=302)

@app.route('/factivate')
def factivate():
  if 'username' in session:
    username = session['username']
    sessid = str(request.cookies.get('session'))
    cloudid = str(request.args['cloudid'])
    subprocess.Popen("while :; do ps ax | grep -v grep | grep 'cld\-xterm' | grep -q "+cloudid+" && break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE).communicate()
    subprocess.Popen("while :; do ps ax | grep -v grep | grep 'cld\-xterm' | grep -q "+cloudid+" || break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE).communicate()
    targetport = bash('grep "'+sessid+'" /var/cld/docker/xtermnginx/etc/nginx/conf.d/sessid  | grep "'+cloudid+'" | tail -1 | egrep -o "XTERMPORT [0-9]{5}" | cut -d \  -f 2').replace('\n', '')
    # print('sudo -u '+username+' sudo /var/cld/bin/cldxmount '+cloudname)
    subprocess.Popen("while :; do wget --server-response --spider http://172.17.0.250:"+targetport+" 2>&1 | grep -q '200 OK' && break ; sleep 0.5s ; done", shell=True, stdout=subprocess.PIPE).communicate()
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
    init_list = ['id', 'fullname']
    srv_list = bash('''/var/cld/bin/cld-allowed '''+username+''' | xargs -I {} awk "/{}/" /var/cld/creds/id_list''').split('\n')
    for n, i in enumerate(srv_list):
      srv_list[n] = {k:v for k,v in zip(init_list,srv_list[n].split(' '))}
    return render_template('html/index.html', username=username, srv_list=srv_list)

@app.route('/admin')
def admin():
  if 'username' in session:
    username = session['username']
    userlist = bash('echo -n $(ls /var/cld/access/users/ | cat)').split(' ')
    users = list()
    for user in userlist:
      userid = bash('grep ^'+user+': /etc/passwd | cut -d : -f 3').replace('\n', '')
      role = bash('cat /var/cld/access/users/'+user+'/role').replace('\n', '')
      groups = bash('echo -n $(cat /var/cld/access/users/'+user+'/groups)').replace(' ', ',')
      status = bash("grep -q '"+user+":!' /etc/shadow && echo -n 0 || echo -n 1")
      lastlogin = bash('''echo -n $(last '''+user+''' -R | head -1 | awk '{$1=$2=""; print $0}')''')
      users.append(userid+";"+user+";"+role+";"+groups+";"+status+";"+lastlogin)
    init_list = ['userid', 'user', 'role', 'groups', 'status', 'lastlogin']
    for n, i in enumerate(users):
      users[n] = {k:v for k,v in zip(init_list,users[n].split(';'))}
    grouplist = bash('echo -n $(ls /var/cld/access/groups/ | cat)').split(' ')
    groups = list()
    for group in grouplist:
      grouptype = bash('ls -l /var/cld/access/groups/'+group+'/clouds | grep -q "\->" && echo -n "parsing" || echo -n "manual"').replace('\n', '')
      groupusers = bash('echo -n $(grep -l "'+group+'" /var/cld/access/users/*/groups | cut -d / -f 6)').replace(' ', ',')
      cloudcount = bash('wc -l /var/cld/access/groups/'+group+'/clouds | cut -d \  -f 1').replace('\n', '')
      groups.append(group+";"+groupusers+";"+cloudcount+";"+grouptype)
    init_group = ['group', 'groupusers', 'cloudcount', 'grouptype']
    for n, i in enumerate(groups):
      groups[n] = {k:v for k,v in zip(init_group,groups[n].split(';'))}
    return render_template('html/admin.html', username=username, users=users, groups=groups)

@app.route('/adduser', methods=['POST'])
def adduser():
  if 'username' in session:
    newuser = request.form['newuser']
    newpassword = request.form['newpass']
    bash('/var/cld/bin/cld-useradd '+newuser+' '+newpassword).replace('\n', ' ')
    return redirect('/admin', code=302)

@app.route('/deluser', methods=['GET'])
def deluser():
  if 'username' in session:
    deluser = request.args['name']
    bash('/var/cld/bin/cld-userdel '+deluser).replace('\n', ' ')
    return redirect('/admin', code=302)

@app.route('/enableuser', methods=['GET'])
def enableuser():
  if 'username' in session:
    enableuser = request.args['name']
    bash('passwd --unlock '+enableuser).replace('\n', ' ')
    return redirect('/admin', code=302)

@app.route('/disableuser', methods=['GET'])
def disableuser():
  if 'username' in session:
    disableuser = request.args['name']
    bash('passwd --lock '+disableuser).replace('\n', ' ')
    return redirect('/admin', code=302)

@app.route('/user')
def user():
  if 'username' in session:
    username = session['username']
    name = [str(request.args['name'])]
    users = list()
    for user in name:
      userid = bash('grep ^'+user+': /etc/passwd | cut -d : -f 3').replace('\n', '')
      role = bash('cat /var/cld/access/users/'+user+'/role').replace('\n', '')
      groups = bash('echo -n $(cat /var/cld/access/users/'+user+'/groups)').replace(' ', ',')
      status = bash("grep -q '"+user+":!' /etc/shadow && echo -n 0 || echo -n 1")
      lastlogin = bash('''echo -n $(last '''+user+''' -R | head -1 | awk '{$1=$2=""; print $0}')''')
      users.append(userid+";"+user+";"+role+";"+groups+";"+status+";"+lastlogin)
    init_list = ['userid', 'user', 'role', 'groups', 'status', 'lastlogin']
    for n, i in enumerate(users):
      users[n] = {k:v for k,v in zip(init_list,users[n].split(';'))}
    allgroups = [os.path.basename(name) for name in os.listdir("/var/cld/access/groups/") if os.path.isdir('/var/cld/access/groups/'+name)]
    allowedclouds = bash('/var/cld/bin/cld-allowed '+request.args['name']).split('\n')[:-1]
    disallowedclouds = bash('/var/cld/bin/cld-disallowed '+request.args['name']).split('\n')[:-1]
    return render_template('html/user.html', username=username, users=users, allgroups=allgroups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds)

@app.route('/group')
def group():
  if 'username' in session:
    username = session['username']
    name = [str(request.args['name'])]
    users = list()
    for user in name:
      userid = bash('grep ^'+user+': /etc/passwd | cut -d : -f 3').replace('\n', '')
      role = bash('cat /var/cld/access/users/'+user+'/role').replace('\n', '')
      groups = bash('echo -n $(cat /var/cld/access/users/'+user+'/groups)').replace(' ', ',')
      status = bash("grep -q '"+user+":!' /etc/shadow && echo -n 0 || echo -n 1")
      lastlogin = bash('''echo -n $(last '''+user+''' -R | head -1 | awk '{$1=$2=""; print $0}')''')
      users.append(userid+";"+user+";"+role+";"+groups+";"+status+";"+lastlogin)
    init_list = ['userid', 'user', 'role', 'groups', 'status', 'lastlogin']
    for n, i in enumerate(users):
      users[n] = {k:v for k,v in zip(init_list,users[n].split(';'))}
    allgroups = [os.path.basename(name) for name in os.listdir("/var/cld/access/groups/") if os.path.isdir('/var/cld/access/groups/'+name)]
    return render_template('html/group.html', username=username, users=users, allgroups=allgroups)

@app.route('/usergroups', methods=['GET','POST'])
def usergroups():
  if 'username' in session:
    user = request.args['name']
    groups = list(request.form.to_dict())
    # print(dir(request.form))
    # sys.stdout.flush()
    groupsfile = open('/var/cld/access/users/'+user+'/groups', 'w')
    groupsfile.write("\n".join(groups))
    groupsfile.close()
    return redirect('/admin', code=302)

@app.route('/settings')
def settings():
  if 'username' in session:
    username = session['username']
    return render_template('html/settings.html', username=username)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
