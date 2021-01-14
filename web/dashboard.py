# -*- coding: utf-8 -*-
from flask import Flask, abort, request, render_template, g, Response, send_from_directory, redirect, session, escape, url_for
from flask_session import Session
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
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
import random
import pty
import select
import termios
import struct
import fcntl
import shlex


def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8')

def check_pid(pid):
  try:
    os.kill(pid, 0)
  except OSError:
    return False
  else:
    return True


logging.basicConfig(level=logging.DEBUG)
template_dir = os.path.abspath('./')
upload_dir = os.path.abspath('./img')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
#FLASKSECRETKEY = bash('grep FLASKSECRETKEY /var/cld/creds/creds | cut -d = -f 2').replace('\n', '')
DOCKERHOST = bash('grep DOCKERHOST /var/cld/creds/creds | cut -d = -f 2').replace('\n', '')

#async_mode = None
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, cors_allowed_origins='https://dev-panel.classicdeploy.com')
app.config['UPLOAD_FOLDER'] = upload_dir
#app.secret_key = FLASKSECRETKEY
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
#accesslist = set(line.strip() for line in open('../creds/accesslist'))

#@app.before_request

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return remote_addr





#socketio
#app.config["fd"] = None
#app.config["child_pid"] = None
def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

@app.route("/tool/<cldutility>")
def tool(cldutility):
  if 'username' in session:
    cmd_args = ''
    try:
        cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except:
        pass
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    socketid = ''
    for c in range(16):
       socketid += random.choice(chars)
    return render_template("html/socket.html", socketid=socketid, cldutility=cldutility, cmd_args=cmd_args)

@app.route("/socket")
def socket():
  if 'username' in session:
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    socketid = ''
    for c in range(8):
       socketid += random.choice(chars)
    return render_template("html/socket.html", socketid=socketid)

def read_and_forward_pty_output(socketid, sessfd, subprocpid, child_pid):
    max_read_bytes = 1024 * 20
    while True:
      socketio.sleep(0.01)
      if check_pid(subprocpid) != True:
          print("exit due child pid not exist", flush=True)
          socketio.emit("pty-output", {"output"+socketid: "Process exited"}, namespace="/pty")
          socketio.disconnect()
          sys.exit(0)
          os.kill(child_pid, 9)
          return
      if sessfd:
          timeout_sec = 0
          (data_ready, _, _) = select.select([sessfd], [], [], timeout_sec)
          if data_ready:
              output = os.read(sessfd, max_read_bytes).decode()
              socketio.emit("pty-output", {"output"+socketid: output}, namespace="/pty")

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
  if 'username' in session:
    socketid=request.args.get('socketid')
    if socketid in app.config["shell"]:
      os.write(app.config["shell"][socketid], data["input"+socketid].encode())

@socketio.on("resize", namespace="/pty")
def resize(data):
  if 'username' in session:
    socketid=request.args.get('socketid')
    if socketid in app.config["shell"]:
      set_winsize(app.config["shell"][socketid], data["rows"], data["cols"])

@socketio.on("connect", namespace="/pty")
def connect():
  if 'username' in session:
    socketid=request.args.get('socketid')
    cldutility=''
    try: cldutility=request.args.get('cldutility')
    except: pass
    user = session["username"]
    if cldutility == 'bash': shellcmd = '/bin/bash'
    else: shellcmd = bash('''grep ' '''+cldutility+'''=' /home/'''+user+'''/.bashrc | cut -d "'" -f 2''')
    if shellcmd == "": 
      return socketio.emit("pty-output", {"output"+socketid: "Access denied: check request is correct and access rights for the user"}, namespace="/pty")
    print(socketid, flush=True)
    try: app.config["shell"]
    except:  app.config["shell"] = {}
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
      app.config["shell"]["child"+socketid] = child_pid
      subprocess.run("TERM=xterm /usr/bin/sudo -u "+user+" "+shellcmd, shell=True, executable='/bin/bash')
    else:
      subprocpid = int(bash('ps axf -o pid,command | grep -v grep | grep -A1 "^'+str(child_pid)+' " | cut -d " " -f 1 | tail -1 | tr -d "\n"'))
      app.config["shell"]["subprocpid"+socketid] = subprocpid
      app.config["shell"][socketid] = fd
      app.config["shell"]["child"+socketid] = child_pid
      print("subprocpid is: "+str(subprocpid), flush=True)
      set_winsize(fd, 50, 50)
      socketio.start_background_task(read_and_forward_pty_output, socketid, fd, subprocpid, child_pid)
      app.config["shell"]["run"+socketid] = "1"


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
  return render_template('html/login.html') 
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
    bash('echo /var/cld/bin/cld-xterm '+cloudid+' '+sessid+' '+username+' >> /var/log/cld/cmd.log')
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
    return render_template('html/index.html', username=username)

@app.route('/terminal')
def terminal():
  if 'username' in session:
    username = session['username']
    # ext_do_list_file = open("../creds/ext_do_list", "r")
    # ext_do_list = ext_do_list_file.readlines()
    # ext_do_list_file.close()
    init_list = ['id', 'fullname']
    srv_list = bash('''/var/cld/bin/cld-allowed '''+username+''' | xargs -I {} awk "/{}/" /var/cld/creds/id_list''').split('\n')
    for n, i in enumerate(srv_list):
      srv_list[n] = {k:v for k,v in zip(init_list,srv_list[n].split(' '))}
    return render_template('html/terminal.html', username=username, srv_list=srv_list)

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
      grouptype = bash('grep -qs "1" /var/cld/access/groups/'+group+'/type && echo -n "parsing" || echo -n "manual"').replace('\n', '')
      groupusers = bash('echo -n $(grep -l "'+group+'" /var/cld/access/users/*/groups | cut -d / -f 6)').replace(' ', ',')
      cloudcount = bash('wc -l /var/cld/access/groups/'+group+'/clouds | cut -d \  -f 1').replace('\n', '')
      groups.append(group+";"+groupusers+";"+cloudcount+";"+grouptype)
    init_group = ['group', 'groupusers', 'cloudcount', 'grouptype']
    for n, i in enumerate(groups):
      groups[n] = {k:v for k,v in zip(init_group,groups[n].split(';'))}
    return render_template('html/admin.html', username=username, users=users, groups=groups)

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
    grouplist = bash('echo -n $(ls /var/cld/access/groups/ | cat)').split(' ')
    groups = list()
    for group in name:
      grouptype = bash('grep -qs "1" /var/cld/access/groups/'+group+'/type && echo -n "parsing" || echo -n "manual"').replace('\n', '')
      groupfuncs = bash('grep -qs "1" /var/cld/access/groups/'+group+'/funcs && echo -n "custom" || echo -n "default"').replace('\n', '')
      groupusers = bash('echo -n $(grep -l "'+group+'" /var/cld/access/users/*/groups | cut -d / -f 6)').replace(' ', ',')
      cloudcount = bash('wc -l /var/cld/access/groups/'+group+'/clouds | cut -d \  -f 1').replace('\n', '')
      groups.append(group+";"+groupusers+";"+cloudcount+";"+grouptype+";"+groupfuncs)
    init_group = ['group', 'groupusers', 'cloudcount', 'grouptype', 'groupfuncs']
    for n, i in enumerate(groups):
      groups[n] = {k:v for k,v in zip(init_group,groups[n].split(';'))}
    allusers = [os.path.basename(name) for name in os.listdir('/var/cld/access/users/') if os.path.isdir('/var/cld/access/users/'+name)]
    # allowedclouds = bash('cat /var/cld/access/groups/'+request.args["name"]+'/clouds').split('\n')[:-1]
    allowedclouds = bash("cut -d _ -f -4 /var/cld/access/groups/"+request.args['name']+"/clouds | tr -d '\001' | grep -vh '^$\|^#'").split('\n')
    #[:-1]
    disallowedclouds = bash('/var/cld/bin/cld-disallowed-group '+request.args['name']).split('\n')[:-1]
    parsingscript = bash('cat /var/cld/access/groups/'+group+'/parsingscript')
    groupfuncvars = bash('cat /var/cld/access/groups/'+group+'/funcvars || cat /var/cld/bin/include/defaultvars')
    groupfuncterm = bash('cat /var/cld/access/groups/'+group+'/functerm || cat /var/cld/bin/include/defaultterm')
    groupfuncmount = bash('cat /var/cld/access/groups/'+group+'/funcmount || cat /var/cld/bin/include/defaultmount')
    groupfuncumount = bash('cat /var/cld/access/groups/'+group+'/funcumount || cat /var/cld/bin/include/defaultumount')
    return render_template('html/group.html', username=username, allusers=allusers, groups=groups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds, parsingscript=parsingscript, groupfuncvars=groupfuncvars, groupfuncterm=groupfuncterm, groupfuncmount=groupfuncmount, groupfuncumount=groupfuncumount)

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

@app.route('/addgroup', methods=['POST'])
def addgroup():
  if 'username' in session:
    newgroup = request.form['newgroup']
    bash('/var/cld/bin/cld-groupadd '+newgroup).replace('\n', ' ')
    return redirect('/admin', code=302)

@app.route('/delgroup', methods=['GET'])
def delgroup():
  if 'username' in session:
    delgroup = request.args['name']
    bash('/var/cld/bin/cld-groupdel '+delgroup).replace('\n', ' ')
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

@app.route('/userclouds', methods=['GET','POST'])
def userclouds():
  if 'username' in session:
    user = request.args['name']
    clouds = str(request.form).replace('ImmutableMultiDict','').replace('([(','').replace(')])','').replace('), (','').replace("'allowclouds', ","").replace("''","','").replace("'","").split(',')
    # return str(str(request.form).replace('ImmutableMultiDict','').replace('([(','').replace(')])','').replace('), (','').replace("'allowclouds', ","").replace("''","','").replace("'","").split(','))
    # print(dir(request.form))
    # sys.stdout.flush()
    # return str(clouds)
    if str(clouds) == "['([])']":
      bash('truncate -s 0 /var/cld/access/users/'+user+'/clouds')
    else:
      usersfile = open('/var/cld/access/users/'+user+'/clouds', 'w')
      usersfile.write("\n".join(clouds))
      usersfile.close()
    return redirect('/admin', code=302)

@app.route('/groupusers', methods=['GET','POST'])
def groupusers():
  if 'username' in session:
    group = request.args['name']
    users = ",".join(list(request.form.to_dict())).split(',')
    # return str(",".join(groups).split(','))
    denyusers = [os.path.basename(name) for name in os.listdir("/var/cld/access/users/") if os.path.isdir('/var/cld/access/users/'+name) and name not in users]
    for user in users:
      if user != '':
        bash('grep '+group+' /var/cld/access/users/'+user+'/groups || echo -e "\n'+group+'" >> /var/cld/access/users/'+user+'/groups')
    for denyuser in denyusers:
      if denyuser != '':
        bash("sed -i '/"+group+"/d' /var/cld/access/users/"+denyuser+"/groups")
    return redirect('/admin', code=302)

@app.route('/groupclouds', methods=['GET','POST'])
def groupclouds():
  if 'username' in session:
    group = request.args['name']
    clouds = str(request.form).replace('ImmutableMultiDict','').replace('([(','').replace(')])','').replace('), (','').replace("'allowclouds', ","").replace("''","','").replace("'","").split(',')
    # return str(str(request.form).replace('ImmutableMultiDict','').replace('([(','').replace(')])','').replace('), (','').replace("'allowclouds', ","").replace("''","','").replace("'","").split(','))
    # print(dir(request.form))
    # sys.stdout.flush()
    # return str(clouds)
    if str(clouds) == "['([])']":
      bash('truncate -s 0 /var/cld/access/groups/'+group+'/clouds')
    else:
      groupsfile = open('/var/cld/access/groups/'+group+'/clouds', 'w')
      groupsfile.write("\n".join(clouds))
      groupsfile.close()
    return redirect('/admin', code=302)

@app.route('/grouptype', methods=['GET','POST'])
def grouptype():
  if 'username' in session:
    group = request.args['name']
    grouptype = ''
    try:
      grouptype = request.form['grouptype']
      parsingscript = request.form['parsingscript']
    except:
      pass
    if grouptype == 'on':
      bash('rm -f /var/cld/creds/'+group+'_list /var/cld/access/groups/'+group+'/clouds ; touch /var/cld/creds/'+group+'_list ; ln -s /var/cld/creds/'+group+'_list /var/cld/access/groups/'+group+'/clouds ; echo 1 > /var/cld/access/groups/'+group+'/type')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/access/groups/"+group+"/parsingscript"+os.linesep+parsingscript+os.linesep+'EOPARSINGSCRIPT')
      return redirect('/admin', code=302)
    else:
      bash('rm -f /var/cld/access/groups/'+group+'/clouds ; touch /var/cld/access/groups/'+group+'/clouds ; mv -f /var/cld/creds/'+group+'_list /var/cld/access/groups/'+group+'/clouds ; echo 0 > /var/cld/access/groups/'+group+'/type')
      return redirect('/admin', code=302)

@app.route('/groupfuncs', methods=['GET','POST'])
def groupfuncs():
  if 'username' in session:
    group = request.args['name']
    groupfuncs = ''
    try:
      groupfuncs = request.form['groupfuncs']
    except:
      pass
    try:
      groupfuncvars = request.form['groupfuncvars']
    except:
      pass
    try:  
      groupfuncterm = request.form['groupfuncterm']
    except:
      pass
    try:  
      groupfuncmount = request.form['groupfuncmount']
    except:
      pass
    try:  
      groupfuncumount = request.form['groupfuncumount']
    except:
      pass
    if groupfuncs == 'on':
      bash('echo 1 > /var/cld/access/groups/'+group+'/funcs')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/access/groups/"+group+"/funcvars"+os.linesep+groupfuncvars+os.linesep+'EOPARSINGSCRIPT')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/access/groups/"+group+"/functerm"+os.linesep+groupfuncterm+os.linesep+'EOPARSINGSCRIPT')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/access/groups/"+group+"/funcmount"+os.linesep+groupfuncmount+os.linesep+'EOPARSINGSCRIPT')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/access/groups/"+group+"/funcumount"+os.linesep+groupfuncumount+os.linesep+'EOPARSINGSCRIPT')
      return redirect('/admin', code=302)
    else:
      bash('echo 0 > /var/cld/access/groups/'+group+'/funcs')
      return redirect('/admin', code=302)

@app.route('/cloudadd')
def cloudadd():
  if 'username' in session:
    username = session['username']
    groups = bash('''source <(awk '{print "grep -q 0 /var/cld/access/groups/"$1"/type && echo "$1}' /var/cld/access/users/'''+username+'''/groups) 2>/dev/null''').split('\n')[:-1]
    # return str(groups)
    return render_template('html/cloudadd.html', username=username, groups=groups)

@app.route('/addcloud', methods=['GET','POST'])
def addcloud():
  if 'username' in session:
    username = session['username']
    cloudname = request.form['cloudname']
    cloudip = request.form['cloudip']
    cloudport = request.form['cloudport']
    clouduser = request.form['clouduser']
    cloudpassword = request.form['cloudpassword']
    if cloudport == '':
      cloudport='22'
    if clouduser == '':
      clouduser='root'
    if cloudpassword != '':
      cloudpassword='_'+cloudpassword
    cloudgroup = request.form['cloudgroup']
    bash('echo "'+cloudname+'_'+cloudip+'_'+cloudport+'_'+clouduser+cloudpassword+'" >> /var/cld/access/groups/'+cloudgroup+'/clouds')
    # return str(groups)
    return redirect('/admin', code=302)
  
@app.route('/settings')
def settings():
  if 'username' in session:
    username = session['username']
    return render_template('html/settings.html', username=username)

@app.route('/devops')
def devops():
  if 'username' in session:
    username = session['username']
    templatelist = bash('ls /var/cld/devops/templates/ | cat').split('\n')[:-1]
    templates = list()
    for template in templatelist:
      templatedesc = bash('cat /var/cld/devops/templates/'+template+'/description').replace('\n', ' ')
      templatesync = bash('cat /var/cld/devops/templates/'+template+'/sync').replace('\n', '')
      templatedebug = bash('cat /var/cld/devops/templates/'+template+'/debug').replace('\n', '')
      templatebackup = bash('cat /var/cld/devops/templates/'+template+'/backup').replace('\n', '')
      templates.append(template+";"+templatedesc+";"+templatesync+";"+templatebackup+";"+templatedebug)
    init_template = ['name', 'description', 'sync', 'backup', 'debug']
    for n, i in enumerate(templates):
      templates[n] = {k:v for k,v in zip(init_template,templates[n].split(';'))}
    deploylist = bash('ls -t /var/cld/devops/deploys/ | cat').split('\n')[:-1]
    deploys = list()
    for deploy in deploylist:
      deploytemplate = bash('''echo '''+deploy+''' | awk -F _ '{print $1}' ''').replace('\n', '')
      deploycloudcount = bash('wc -l /var/cld/devops/deploys/'+deploy+'/clouds | cut -d \  -f 1').replace('\n', '')
      deploygroupcount = bash('wc -l /var/cld/devops/deploys/'+deploy+'/groups | cut -d \  -f 1').replace('\n', '')
      deploysync = bash('cat /var/cld/devops/deploys/'+deploy+'/sync').replace('\n', ' ')
      deploycron = bash('cat /var/cld/devops/deploys/'+deploy+'/cron').replace('\n', ' ')
      deploydebug = bash('cat /var/cld/devops/deploys/'+deploy+'/debug').replace('\n', ' ')
      deploybackup = bash('cat /var/cld/devops/deploys/'+deploy+'/backup').replace('\n', ' ')
      deploycreated = bash('''stat /var/cld/devops/deploys/'''+deploy+''' | tr . ' ' | awk '/Modify/ {print $2" "$3}' ''').replace('\n', ' ')
      deploys.append(deploy+";"+deploytemplate+";"+deploycloudcount+";"+deploygroupcount+";"+deploysync+";"+deploycron+";"+deploydebug+";"+deploybackup+";"+deploycreated)
    init_deploy = ['name', 'template', 'cloudcount', 'groupcount', 'sync', 'cron', 'debug', 'backup', 'created']
    for n, i in enumerate(deploys):
      deploys[n] = {k:v for k,v in zip(init_deploy,deploys[n].split(';'))}
    actionlist = bash('ls -t /var/cld/devops/actions/ | cat').split('\n')[:-1]
    actions = list()
    for action in actionlist:
      actiondeploy = bash('''echo '''+action+''' | awk -F _ '{print $1"_"$2}' ''').replace('\n', '')
      actioncloudcount = bash('wc -l /var/cld/devops/actions/'+action+'/clouds | cut -d \  -f 1').replace('\n', '')
      actiongroupcount = bash('wc -l /var/cld/devops/actions/'+action+'/groups | cut -d \  -f 1').replace('\n', '')
      actionsync = bash('cat /var/cld/devops/actions/'+action+'/sync').replace('\n', ' ')
      actiondebug = bash('cat /var/cld/devops/actions/'+action+'/debug').replace('\n', ' ')
      actionbackup = bash('cat /var/cld/devops/actions/'+action+'/backup').replace('\n', ' ')
      actioncreated = bash('''stat /var/cld/devops/actions/'''+action+''' | tr . ' ' | awk '/Modify/ {print $2" "$3}' ''').replace('\n', ' ')
      actiondone = bash('cat /var/cld/devops/actions/'+action+'/done').replace('\n', ' ')
      actions.append(action+";"+actiondeploy+";"+actioncloudcount+";"+actiongroupcount+";"+actionsync+";"+actiondebug+";"+actionbackup+";"+actioncreated+";"+actiondone)
    init_action = ['name', 'deploy', 'cloudcount', 'groupcount', 'sync', 'debug', 'backup', 'created', 'done']
    for n, i in enumerate(actions):
      actions[n] = {k:v for k,v in zip(init_action,actions[n].split(';'))}
    return render_template('html/devops.html', username=username, templates=templates, deploys=deploys, actions=actions)

@app.route('/devops/template')
def devopstemplate():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/template.html', username=username)

@app.route('/devops/templateadd')
def devopstemplateadd():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/templateadd.html', username=username)

@app.route('/devops/addtemplate', methods=['GET','POST'])
def adddevopstemplate():
  if 'username' in session:
    username = session['username']
    templatename = request.form['templatename']
    description = request.form['description']
    cloudscript = request.form['cloudscript']
    bash('mkdir /var/cld/devops/templates/'+templatename+' &>/dev/null')
    bash('echo "'+description+'" > /var/cld/devops/templates/'+templatename+'/description')
    bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/script"+os.linesep+cloudscript+os.linesep+'EOPARSINGSCRIPT')
    backupstate=''
    try:
      backupstate = request.form['backupstate']
    except:
      pass
    if backupstate == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/backup')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/backup')
    backupfilelist=''
    try:
      backupfilelist = request.form['backupfilelist']
    except:
      pass
    bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/backup_files"+os.linesep+backupfilelist+os.linesep+'EOPARSINGSCRIPT')
    custombackupstate=''
    try:
      custombackupstate = request.form['custombackupstate']
    except:
      pass
    try: 
      custombackupscript = request.form['custombackupscript']
    except:
      pass
    try: 
      customrestorescript = request.form['customrestorescript']
    except:
      pass
    if custombackupstate == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/custombackup')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/custom_backup_script"+os.linesep+custombackupscript+os.linesep+'EOPARSINGSCRIPT')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/custom_restore_script"+os.linesep+customrestorescript+os.linesep+'EOPARSINGSCRIPT')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/custombackup')
    sync=''
    try:
      sync = request.form['sync']
    except:
      pass
    if sync == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/sync')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/sync')
    debug=''
    try:
      debug = request.form['debug']
    except:
      pass
    if debug == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/debug')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/debug')
    cron=''
    try: 
      cron = request.form['cron']
    except:
      pass
    try:  
      crontime = request.form['crontime']
    except:
      pass
    if cron == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/cron')
      bash("echo '"+crontime+"' > /var/cld/devops/templates/"+templatename+"/cron_time")
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/cron')
    return redirect('/devops', code=302)

@app.route('/devops/deploy')
def devopsdeploy():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/deploy.html', username=username)

@app.route('/devops/deployadd')
def devopsdeployadd():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/deployadd.html', username=username)

@app.route('/devops/adddeploy', methods=['GET','POST'])
def adddevopsdeploy():
  if 'username' in session:
    username = session['username']
    templatename = request.form['templatename']
    description = request.form['description']
    cloudscript = request.form['cloudscript']
    bash('mkdir /var/cld/devops/templates/'+templatename+' &>/dev/null')
    bash('echo "'+description+'" > /var/cld/devops/templates/'+templatename+'/description')
    bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/script"+os.linesep+cloudscript+os.linesep+'EOPARSINGSCRIPT')
    backupstate=''
    try:
      backupstate = request.form['backupstate']
    except:
      pass
    if backupstate == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/backup')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/backup')
    backupfilelist=''
    try:
      backupfilelist = request.form['backupfilelist']
    except:
      pass
    bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/backup_files"+os.linesep+backupfilelist+os.linesep+'EOPARSINGSCRIPT')
    custombackupstate=''
    try:
      custombackupstate = request.form['custombackupstate']
    except:
      pass
    try: 
      custombackupscript = request.form['custombackupscript']
    except:
      pass
    try: 
      customrestorescript = request.form['customrestorescript']
    except:
      pass
    if custombackupstate == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/custombackup')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/custom_backup_script"+os.linesep+custombackupscript+os.linesep+'EOPARSINGSCRIPT')
      bash("cat << 'EOPARSINGSCRIPT' | tr -d '\r' > /var/cld/devops/templates/"+templatename+"/custom_restore_script"+os.linesep+customrestorescript+os.linesep+'EOPARSINGSCRIPT')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/custombackup')
    sync=''
    try:
      sync = request.form['sync']
    except:
      pass
    if sync == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/sync')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/sync')
    debug=''
    try:
      debug = request.form['debug']
    except:
      pass
    if debug == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/debug')
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/debug')
    cron=''
    try: 
      cron = request.form['cron']
    except:
      pass
    try:  
      crontime = request.form['crontime']
    except:
      pass
    if cron == 'on':
      bash('echo 1 > /var/cld/devops/templates/'+templatename+'/cron')
      bash("echo '"+crontime+"' > /var/cld/devops/templates/"+templatename+"/cron_time")
    else:
      bash('echo 0 > /var/cld/devops/templates/'+templatename+'/cron')
    return redirect('/devops', code=302)

@app.route('/devops/action')
def devopsaction():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/action.html', username=username)

@app.route('/devops/actionadd')
def devopsactionadd():
  if 'username' in session:
    username = session['username']
    return render_template('html/devops/actionadd.html', username=username)

#Just easy direct pipeline for early dev version, will deleted in the future
@app.route('/backendgitpull')
def backendgitpull():
    bg = ''
    try:
      bg = str(int(request.args['bg']))
      if bg == '1':
        bg = '''&>/dev/null &'''
    except:
      pass
    cmd = bash('(cd /var/cld/ && git reset --hard && git pull origin master && supervisorctl restart cldpanel) ' + bg)
    resp = Response(cmd, status=200, mimetype='text/plain')
    return resp

if __name__ == '__main__':
#    app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('/etc/ssl/certs/nginx-selfsigned.crt', '/etc/ssl/private/nginx-selfsigned.key'))
    #app.run(debug=True, host='0.0.0.0', port=8080)
    socketio.run(app, debug=True, host='0.0.0.0', port=8080)