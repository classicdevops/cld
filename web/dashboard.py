# -*- coding: utf-8 -*-
from flask import Flask, abort, request, render_template, g, Response, send_from_directory, redirect, escape, url_for, session, cli
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, close_room
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import re
import os
import subprocess
import datetime
import pam
import time
import sys
import random
import pty
import select
import termios
import struct
import fcntl
import threading
import json
from engineio.payload import Payload
    
def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

def vld(cld_variable):
  return re.match('(^[A-z0-9.,@=/_ -]+?$|^$)', cld_variable).string

def stream_file(filepath, chunksize=8192):
  with open(filepath, "rb") as f:
    while True:
      chunk = f.read(chunksize)
      if chunk:
        yield chunk
      else:
        break

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['path'] = path
        d['dirs'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['path'] = path
        d['type'] = "file"
        d['content'] = open(path).read()
    return d

def check_pid(pid):
  try:
    os.kill(pid, 0)
  except OSError:
    return False
  else:
    return True

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return re.match("[A-z0-9.:]+", remote_addr)[0]

def accesslist():
  return bash("cat /var/cld/modules/access/data/myips /var/cld/modules/access/data/enabledips | cut -d _ -f 1 | uniq").split('\n')

def allowmoduleusers(cldmodule):
  return set(bash('''awk -F ":" '{print $1":"$4}' /var/cld/creds/passwd | grep "'''+vld(cldmodule)+'''\|ALL" | cut -d : -f 1''').split('\n'))

def allowutilityusers(cldutility):
  return set(bash('''awk -F ":" '{print $1":"$5}' /var/cld/creds/passwd | grep "'''+vld(cldutility)+'''\|ALL" | cut -d : -f 1''').split('\n'))

def uservisiblemodules(user):
  usermodules = bash('''awk -F ":" '{print $1":"$4}' /var/cld/creds/passwd | grep "^'''+vld(user)+''':" | cut -d : -f 2''').split(',')
  webmodules = bash('ls /var/cld/modules/*/web.py 2>/dev/null | rev | cut -d / -f 2 | rev').split('\n')
  if "ALL" in usermodules:
    if os.path.isfile('/var/cld/access/users/'+vld(user)+'/showonlymodules'):
      modulesinfile = open('/var/cld/access/users/'+vld(user)+'/showonlymodules').read().strip().split('\n')
      return [x for x in modulesinfile if x in webmodules]
    else:
      return webmodules
  else:
    userwebmodules = [x for x in usermodules if x in webmodules]
    if os.path.isfile('/var/cld/access/users/'+vld(user)+'/showonlymodules'):
      modulesinfile = open('/var/cld/access/users/'+vld(user)+'/showonlymodules').read().strip().split('\n')
      return [x for x in modulesinfile if x in userwebmodules]
    else:
      return userwebmodules

def getusermodules(user):
  usermodules = bash('''awk -F ":" '{print $1":"$4}' /var/cld/creds/passwd | grep "^'''+vld(user)+''':" | cut -d : -f 2''').split(',')
  webmodules = bash('ls /var/cld/modules/*/web.py 2>/dev/null | rev | cut -d / -f 2 | rev').split('\n')
  if "ALL" in usermodules:
    return webmodules
  else:
    return [x for x in webmodules if x in usermodules]


def usertools(user):
  tools = bash('''awk -F ":" '/^'''+vld(user)+''':/{print $1":"$5}' /var/cld/creds/passwd | cut -d : -f 2''').split(',')
  if "ALL" in tools:
    return open('/var/cld/creds/tools_list').read().strip().split(',')
  else:
    return tools

def userisadmin(user):
  if bash('''awk -F ":" '/^'''+vld(user)+''':/{print $1":"$4":"$5}' /var/cld/creds/passwd | cut -d : -f 2-''') == "ALL:ALL":
    return True
  else:
    return False

def apitokenbyuser(user):
  return bash('''awk -F ":" '/^'''+vld(user)+''':/{print $3}' /var/cld/creds/passwd''')

def checkperms(cldmodule, cldutility, user):
  cldmodule=str(cldmodule)
  cldutility=str(cldutility)
  if user in allowmoduleusers(cldmodule) or user in allowutilityusers(cldutility):
    return ["granted", user]
  else:
    return ["denied", "DENIED"]

def checkpermswhiteip(cldmodule, cldutility, user, remoteaddr):
  user=re.match("[A-z0-9_.-]+", user)[0]
  cldmodule=str(re.match("[A-z0-9_.-]+", cldmodule)[0])
  cldutility=str(re.match("[A-z0-9_.-]+", cldutility)[0])
  if cldutility == 'bash' and remoteaddr in accesslist() and user in bash("awk -F ':' '{print $1}' /var/cld/creds/passwd").split('\n'):
    return ["granted", user]
  elif user in allowmoduleusers(cldmodule) and remoteaddr in accesslist():
    return ["granted", user]
  elif user in allowutilityusers(cldutility) and remoteaddr in accesslist():
    return ["granted", user]
  else:
    return ["denied", "DENIED"]

cld_domain = bash('''grep CLD_DOMAIN /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' ''')
cld_ip = bash('''grep CLD_IP /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' ''')
logging.basicConfig(level=logging.DEBUG)
template_dir = os.path.abspath('./')
upload_dir = os.path.abspath('./img')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
cli.show_server_banner = lambda *_: None
Payload.max_decode_packets = 64
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, cors_allowed_origins=['https://'+cld_domain, 'https://'+cld_ip], threading=threading, threaded=True)
app.config['UPLOAD_FOLDER'] = upload_dir
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def logged_in(f):
  @wraps(f)
  def decorated_func(*args, **kwargs):
    if session.get("username"):
      return f(*args, **kwargs)
    else:
      return redirect('/', code=302)
    return decorated_func

def is_admin(f):
  @wraps(f)
  def decorated_func(*args, **kwargs):
    if session.get("username"):
      if userisadmin(session['username']) == True:
        return f(*args, **kwargs)
      else:
        session.pop('username', None)
        return redirect('/', code=302)
    else:
      return redirect('/', code=302)
    return decorated_func

webmodule = {}
#include code from web.py of modules
cldm={}
for webfile in bash("ls /var/cld/modules/*/web.py 2>/dev/null").split('\n'):
  cldmodule=bash('echo '+vld(webfile)+' | rev | cut -d / -f 2 | rev')
  cldm[cldmodule]=cldmodule
  print(cldmodule, flush=True)
  exec(open(webfile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

#recreate symlinks to templates in external directories for this dashboard.py
bash('''
rm -f /var/cld/web/modules/*
mkdir /var/cld/web/modules &>/dev/null
rm -f /var/cld/web/html/include/cld_tier.html
ln -s /var/cld/creds/cld_tier /var/cld/web/html/include/cld_tier.html
for WEB_TEMPLATE_PATH in $(ls -d /var/cld/modules/*/web 2>/dev/null)
do
WEB_MODULE=$(rev <<< ${WEB_TEMPLATE_PATH} | cut -d / -f 2 | rev)
ln -s ${WEB_TEMPLATE_PATH} /var/cld/web/modules/${WEB_MODULE}
done
''')

#generate help endpoints for each CLD tool
exec(bash('''
for CLD_FILE in $(find /var/cld/bin/ /var/cld/modules/*/bin/ -type f -maxdepth 1 -name 'cld*')
do
CLD_MODULE=$(rev <<< ${CLD_FILE} | cut -d / -f 3 | rev)
CLD_UTIL=$(rev <<< ${CLD_FILE} | cut -d / -f 1 | rev)
cat << EOL
@app.route('/help/${CLD_UTIL}')
def help_${CLD_UTIL//[.-]/_}():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip("${CLD_MODULE}", "${CLD_UTIL}", user, remoteaddr()) 
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    print('sudo -u '+user+' sudo FROM=CLI ${CLD_FILE} --help', flush=True)
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=API '+vld("${CLD_FILE}")+' --help')
    resp = Response(cmdoutput, status=200, mimetype='application/json')
    return resp

EOL
done
'''))

ansifiltercheck = bash('which ansifilter &>/dev/null && echo 0 || echo 1')
if ansifiltercheck == "0":
  outputinterpreter = bash('which ansifilter') + ' -Hf'
else:
  outputinterpreter = bash('which cat')
  print('''ansifilter IS NOT INSTALLED IN THE SYSTEM - API OUTPUT WILL NOT FILTERED - https://github.com/andre-simon/ansifilter
  cd /usr/src
  git clone https://github.com/andre-simon/ansifilter.git
  cd ansifilter/
  make
  make install
  ''')

#generate webapi endpoints for each CLD tool
exec(bash('''
for CLD_FILE in $(find /var/cld/bin/ /var/cld/modules/*/bin/ -type f -maxdepth 1 -name 'cld*')
do
CLD_MODULE=$(rev <<< ${CLD_FILE} | cut -d / -f 3 | rev)
CLD_UTIL=$(rev <<< ${CLD_FILE} | cut -d / -f 1 | rev)
cat << EOL
@app.route('/webapi/tool/${CLD_UTIL}')
@app.route('/webapi/tool/${CLD_UTIL}/')
@app.route('/webapi/tool/${CLD_UTIL}/<args>')
def webapi_${CLD_UTIL//[.-]/_}(args=None):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip("${CLD_MODULE}", "${CLD_UTIL}", user, remoteaddr()) 
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
    except: cmd_args = ''
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except: pass
    try:
      if request.args['output'] == 'html':
        print('sudo -u '+user+' sudo FROM=CLI ${CLD_FILE} '+cmd_args+' | '+outputinterpreter, flush=True)
        cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=API '+vld("${CLD_FILE}")+' '+cmd_args+' | '+outputinterpreter)
        return Response('<pre>'+cmdoutput+'</pre>', status=200, mimetype='text/html')
    except:
      pass
    print('sudo -u '+user+' sudo FROM=CLI ${CLD_FILE} '+cmd_args, flush=True)
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=WEB '+vld("${CLD_FILE}")+' '+cmd_args)
    return Response(cmdoutput, status=200, mimetype='text/plain')

EOL
done
'''))

#socketio
app.config["shell"] = {}
app.config["shell"]["childpid"] = {}
app.config["shell"]["keepalive"] = {}

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

@app.route("/tool/cldx/<args>")
def cldx(args):
  if 'username' in session:
    user = session['username']
    cldutility = 'cldx'
    cldfile = "/var/cld/bin/cldx"
    cldmodule = bash('rev <<< '+vld(cldfile)+' | cut -d / -f 3 | rev | tr -d "\n"')
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
    except: cmd_args = ''
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except: pass
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    socketid = ''
    for c in range(16):
       socketid += random.choice(chars)
    return render_template("html/cldx.html", socketid=socketid, cldutility=cldutility, cmd_args=cmd_args)

@app.route("/tool/<cldutility>")
@app.route("/tool/<cldutility>/")
@app.route("/tool/<cldutility>/<args>")
def tool(cldutility, args=None):
  if 'username' in session:
    user = session['username']
    cldutility = str(re.match('^[A-z0-9.,@=/_ -]+', cldutility)[0])
    if cldutility != 'bash':
      cldfile = bash('''grep ' '''+vld(cldutility)+'''=' /home/'''+vld(user)+'''/.bashrc | cut -d ' ' -f 4 | tr -d "'"''').replace('\n', '')
    else:
      cldfile = '/bin/bash'
    if cldfile != '/bin/bash': cldmodule = bash('rev <<< '+vld(cldfile)+' | cut -d / -f 3 | rev | tr -d "\n"')
    else: cldmodule = "bash"
    if os.path.exists(cldfile) != True:
      return Response('File not exist', status=403, mimetype='text/plain')
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
    except: cmd_args = ''
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except: pass
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    socketid = ''
    for c in range(16):
       socketid += random.choice(chars)
    return render_template("html/socket.html", socketid=socketid, cldutility=cldutility, cmd_args=cmd_args)

@app.route("/getfile/<instance>")
def getfile(instance):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip('NONE', 'cldxmount', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    instance = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --json '+vld(instance)))[0]['clouds'][0]
    filepath = str(re.match('^/[A-z0-9.,@=/_-]+$', request.args['filepath']).string)
    mountpath = '/home/'+user+'/mnt/'+instance
    fullfilepath = mountpath+filepath
    filename = os.path.basename(filepath)
    if os.path.ismount(mountpath) != True:
      bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cldxmount '+vld(instance))
      time.sleep(3)
    if os.path.ismount(mountpath) != True:
      return Response('Instance directory mount failed', status=403, mimetype='text/plain')
    if os.path.exists(fullfilepath) != True or os.path.isfile(fullfilepath) != True:
      return Response('File not exist', status=403, mimetype='text/plain')
    return Response(stream_file(fullfilepath), status=200, mimetype='application/octet-stream', headers={'Content-Disposition': f'attachment; filename={filename}'})

@app.route("/uploadfile/<instance>", methods=['GET','POST'])
def uploadfile(instance):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip('NONE', 'cldxmount', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    instance = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --json '+vld(instance)))[0]['clouds'][0]
    try: filepath = str(re.match('^/[A-z0-9.,@=/_-]+$', request.form['filepath']).string)
    except: filepath = '/tmp'
    mountpath = '/home/'+user+'/mnt/'+instance
    file = request.files['file']
    filename = secure_filename(file.filename)
    fullfilepath = mountpath+filepath
    if os.path.ismount(mountpath) != True:
      bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cldxmount '+vld(instance))
      time.sleep(3)
    if os.path.ismount(mountpath) != True:
      return Response('Instance directory mount failed', status=403, mimetype='text/plain')
    if os.path.isdir(fullfilepath) != True:
      return Response('Directory not exist', status=403, mimetype='text/plain')
    file.save(fullfilepath+'/'+filename)
    print(fullfilepath+'/'+filename, flush=True)
    return Response('File uploaded', status=200, mimetype='text/plain')

def keepalive_shell_session(socketid, child_pid, room, subprocpid, fd):
    app.config["shell"]["keepalive"][socketid] = int(time.time())+60
    print("keepalive_shell_session started for socketid: "+socketid, flush=True)
    while True:
        time.sleep(10)
        try:
          current_timestamp = int(time.time())
          socket_timestamp = app.config["shell"]["keepalive"][socketid]
          print
          if current_timestamp > socket_timestamp:
              print("started terminating task for socket "+socketid, flush=True)
              print("exit due "+socketid+" not connected", flush=True)
              socketio.emit("output", {"output": "Process exited"}, namespace="/cld", room=room, sid=socketid)
              socketio.emit("disconnect", {"disconnect": socketid}, namespace="/cld", room=room, sid=socketid)
              try: socketio.close_room(room)
              except: print("socketio.close_room exception", flush=True)
              if check_pid(subprocpid) == True:
                bash('kill -9 '+str(subprocpid))
              return #bash('kill -9 '+str(child_pid))
        except:
          pass

def read_and_forward_pty_output(socketid, sessfd, subprocpid, child_pid, room):
    max_read_bytes = 1024 * 20
    if check_pid(subprocpid) != True:
      print(bash('ps axfu | grep '+vld(subprocpid)), flush=True)
    while True:
      socketio.sleep(0.05)
      if check_pid(subprocpid) != True:
          print("exit due subprocpid not exist", flush=True)
          socketio.emit("output", {"output": "Process exited"}, namespace="/cld", room=room, sid=socketid)
          socketio.emit("disconnect", {"disconnect": socketid}, namespace="/cld", room=room, sid=socketid)
          return
      if sessfd:
          timeout_sec = 0
          (data_ready, _, _) = select.select([sessfd], [], [], timeout_sec)
          if data_ready:
              output = os.read(sessfd, max_read_bytes).decode()
              socketio.emit("output", {"output": output}, namespace="/cld", room=room, sid=socketid)
      else:
          return socketio.emit("disconnect", namespace="/cld", room=room, sid=socketid)


@socketio.on("input", namespace="/cld")
def pty_input(data):
  if 'username' in session:
    socketid=request.sid
    if socketid in app.config["shell"]:
      os.write(app.config["shell"][socketid], data["input"].encode())

@socketio.on("keepalive", namespace="/cld")
def pty_keepalive():
  if 'username' in session:
    socketid=request.sid
    print("received keepalive data from: "+socketid, flush=True)
    app.config["shell"]["keepalive"][socketid] = int(time.time())+15

@socketio.on("resize", namespace="/cld")
def resize(data):
  if 'username' in session:
    socketid=request.sid
    if socketid in app.config["shell"]:
      set_winsize(app.config["shell"][socketid], data["rows"], data["cols"])

#@socketio.on("disconnect", namespace="/cld")
#def socket_disconnect():
#  if 'username' in session:
#    socketid=request.sid
#    sid = request.sid
#    leave_room(socketid)
#    close_room(socketid)
#    disconnect(sid)

@socketio.on("connect", namespace="/cld")
def connect():
   if 'username' not in session: return redirect('/login', code=302)
   elif 'username' in session:
    user = session['username']
    cldutility=request.args.get('cldutility')
    if cldutility != 'bash':
      cldfile = bash('''grep ' '''+vld(cldutility)+'''=' /home/'''+vld(user)+'''/.bashrc | cut -d ' ' -f 4 | tr -d "'"''').replace('\n', '')
    else:
      cldfile = '/bin/bash'
    print('cldfile is: '+str(cldfile), flush=True)
    if cldfile != '/bin/bash': cldmodule = bash('rev <<< '+vld(cldfile)+' | cut -d / -f 3 | rev | tr -d "\n"')
    else: cldmodule = "bash"
    print('cldmodule is: '+str(cldmodule), flush=True)
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    print('checkresult is: '+str(checkresult), flush=True)
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    socketid=request.sid
    sid=request.sid
    #try: app.config["shell"][socketid]
    #except: pass
    #else: return
    cmd_args = ''
    try: cmd_args = str(re.match('^[A-z0-9.,@=/: -]+$', request.args.get('args')).string)+" "
    except: cmd_args = " "
    user = session["username"]
    if cldutility == 'bash': shellcmd = '/bin/bash'
    else: shellcmd = bash('''grep ' '''+vld(cldutility)+'''=' /home/'''+vld(user)+'''/.bashrc | cut -d "'" -f 2 | tr -d "\n" ''')
    join_room(socketid)
    room = socketid
    if shellcmd == "": 
      socketio.emit("output", {"output": "Access denied: check request is correct and access rights for the user"}, namespace="/cld", room=room, sid=socketid)
      return socketio.emit("disconnect", namespace="/cld", room=room, sid=socketid)
    else:
      child_pid = None
      (child_pid, fd) = pty.fork()
      time.sleep(0.05)
      if child_pid == 0:
        #print("command is: TERM=xterm /usr/bin/sudo -u "+user+" "+shellcmd+" "+cmd_args, flush=True)
        subprocess.run("TERM=xterm /usr/bin/sudo -u "+vld(user)+" "+vld(shellcmd)+" "+cmd_args+" ; sleep 0.5s", shell=True, cwd=str('/home/'+user), executable='/bin/bash')
      elif isinstance(child_pid, int):
        app.config["shell"]["childpid"][socketid] = child_pid
        try: subprocpid
        except NameError: 
          subprocpid = ''
          count = 0
        while subprocpid == '' and count != 30:
          subprocpid = bash('ps axf -o pid,command | grep -v grep | sed "s/^ *//g" | grep -A1 "^'+str(child_pid)+' " | cut -d " " -f 1 | tail -1').replace('\n', '')
          count+=1
          time.sleep(0.1)
        app.config["shell"][socketid] = fd
        app.config["shell"]["subprocpid"+socketid] = int(subprocpid)
        set_winsize(fd, 50, 50)
        socketio.start_background_task(read_and_forward_pty_output, socketid, fd, int(subprocpid), child_pid, room)
        print(str(socketid), str(fd), str(subprocpid), str(child_pid), str(room), flush=True)
        threading.Thread(target=keepalive_shell_session, args=(socketid, child_pid, room, int(subprocpid), fd)).start()

#@app.after_request

@app.route('/test')
def testip():
  return remoteaddr()

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/modules/<module>/content/<path:path>')
def send_module_content(module, path):
    return send_from_directory('modules/'+module+'/content', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/font/<path:path>')
def send_font(path):
    return send_from_directory('font', path)

@app.route('/favicon.ico')
def send_favicon():
    return send_from_directory('img', 'favicon.ico')

@app.route('/')
def index():
    if 'username' not in session: return redirect('/login', code=302)
    user = session['username']
    isadmin = userisadmin(session['username'])
    modulelist = uservisiblemodules(user)
    if modulelist != ['']:
      modulelist = list(uservisiblemodules(user))
      modules = {}
      for module in modulelist:
        name = module
        if os.path.isfile('modules/'+module+'/content/logo.svg'):
          webmodule[module]['logo'] = 'modules/'+module+'/content/logo.svg'
        else:
          webmodule[module]['logo'] = 'img/module.svg'
        try: webmodule[module]['desc']
        except: webmodule[module]['desc'] = "module "+module
        try: webmodule[module]['homename']
        except: webmodule[module]['homename'] = module.capitalize().replace('.local', '')
        try: webmodule[module]['adminonly']
        except: webmodule[module]['adminonly'] = False
        modules[module] = webmodule[module]
      print(str(modules), flush=True)
      return render_template('html/index.html', username=user, modules=modules, isadmin=isadmin)
    else:
      return render_template('html/index.html', username=user, isadmin=isadmin)

@app.route('/panel/')
def dashboard():
  return redirect('/', code=302)

@app.route('/login', methods = ['GET', 'POST'])
def login():
  if request.method == 'POST':
    if 'username' not in session:
      if os.path.isdir('/var/cld/access/users/'+request.form['username']):
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

@app.route('/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/terminal')
def terminal():
  if 'username' in session:
    username = session['username']
    cld_instances = json.loads(bash('sudo -u '+vld(username)+' sudo FROM=CLI /var/cld/bin/cld --list --json'))
    return render_template('html/terminal.html', username=username, cld_instances=cld_instances)

@app.route('/password', methods=['POST'])
def changepassword():
  if 'username' in session:
    username = session['username']
    newpassword = request.form['password']
    chars = 'ABCDEFJHGKLMNPQRSTUVWXYZ'
    randomid = ''
    for c in range(16): randomid += random.choice(chars)
    cmdoutput = bash(f'''
cat << '{randomid}' | passwd {vld(username)}
{newpassword}
{newpassword}
{randomid}
''')
    return Response(cmdoutput.replace('\n','<br>')+'<script>window.setTimeout(function(){window.location.href="/profile";},2000);</script>', status=200, mimetype='text/html')

@app.route('/toolkit')
def toolkit():
  if 'username' in session:
    username = session['username']
    cld_tools = json.loads(bash('sudo -u '+vld(username)+' sudo FROM=CLI /var/cld/bin/cld-modules --json'))
    utils = bash('''grep alias /home/'''+vld(username)+'''/.bashrc | grep -v "^#" | cut -d "'" -f 2 | cut -d ' ' -f 3 | rev | cut -d / -f 1 | rev''').split('\n')
    return render_template('html/toolkit.html', username=username, utils=utils, cld_tools=cld_tools)

@app.route('/admin')
@logged_in
def admin():
  if 'username' in session:
    username = session['username']
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    userlist = bash('ls /var/cld/access/users/').split('\n')
    users = list()
    for user in userlist:
      userid = bash('grep ^'+vld(user)+': /etc/passwd | cut -d : -f 3')
      role = bash('cat /var/cld/access/users/'+vld(user)+'/role').replace('\n', '')
      groups = bash('grep "^'+vld(user)+':" /var/cld/creds/passwd | cut -d : -f 6')
      status = bash("grep -q '"+vld(user)+":!' /etc/shadow && echo -n 0 || echo -n 1")
      lastlogin = bash('''last '''+vld(user)+''' -R | head -1 | awk '{$1=$2=""; print $0}' ''')
      users.append(userid+";"+user+";"+role+";"+groups+";"+status+";"+lastlogin)
    init_list = ['userid', 'user', 'role', 'groups', 'status', 'lastlogin']
    for n, i in enumerate(users):
      users[n] = {k:v for k,v in zip(init_list,users[n].split(';'))}
    grouplist = bash('ls /var/cld/access/groups/').split('\n')
    groups = list()
    for group in grouplist:
      grouptype = bash('grep -qs "1" /var/cld/access/groups/'+vld(group)+'/type && echo -n "parsing" || echo -n "manual"')
      groupusers = bash('egrep "[:,]'+vld(group)+'([:,]|$)" /var/cld/creds/passwd | cut -d : -f 1').replace('\n', ',')
      cloudcount = bash('grep -v "^#\|^$" /var/cld/access/groups/'+vld(group)+'/clouds | wc -l')
      groups.append(group+";"+groupusers+";"+cloudcount+";"+grouptype)
    init_group = ['group', 'groupusers', 'cloudcount', 'grouptype']
    for n, i in enumerate(groups):
      groups[n] = {k:v for k,v in zip(init_group,groups[n].split(';'))}
    file_list = ['/var/cld/creds/passwd', '/etc/cron.d/cld', '/var/cld/creds/creds', '/var/cld/creds/creds', '/var/cld/creds/protected_ports', '/var/cld/creds/local_nets']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    return render_template('html/admin.html', username=username, users=users, groups=groups, files=files)


@app.route('/admin/savefile', methods=['POST'])
def adminsavefile():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    elif userisadmin(session['username']) == True:
      file = request.form['file']
      filename = os.path.basename(file)
      filedir = os.path.dirname(file)
      if os.path.exists(filedir) != True:
        os.makedirs(filedir, mode=0o700, exist_ok=False)
      content = request.form['content']
      open(file, "w", newline='\n').write(content.replace('\r', ''))
      if re.match('(^cld-[A-za-z0-9]+$)', filename):
        os.chmod(file, 0o700)
      return Response("file "+file+" saved", status=200, mimetype='text/plain')

@app.route('/admin/deletefile', methods=['POST'])
def admindeletefile():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    elif userisadmin(session['username']) == True:
      file = request.form['file']
      os.remove(file)
      filedir = os.path.dirname(file)
      try: os.rmdir(filedir)
      except: pass
      return Response("file "+file+" deleted", status=200, mimetype='text/plain')

@app.route('/admin/user/<name>')
def user(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    username = session['username']
    clduser = str(re.match('^[A-z0-9.,@=/_ -]+$', name).string)
    name = [str(clduser)]
    users = list()
    for user in name:
      userid = bash('grep "^'+vld(user)+':" /etc/passwd | cut -d : -f 3').replace('\n', '')
      role = bash('cat /var/cld/access/users/'+vld(user)+'/role').replace('\n', '')
      modules = bash('grep "^'+vld(user)+':" /var/cld/creds/passwd | cut -d : -f 4')
      tools = bash('grep "^'+vld(user)+':" /var/cld/creds/passwd | cut -d : -f 5')
      groups = bash('grep "^'+vld(user)+':" /var/cld/creds/passwd | cut -d : -f 6')
      status = bash("grep -q '^"+vld(user)+":!' /etc/shadow && echo -n 0 || echo -n 1")
      lastlogin = bash('''last '''+vld(user)+''' -R | head -1 | awk '{$1=$2=""; print $0}' ''')
      users.append(userid+";"+user+";"+role+";"+modules+";"+tools+";"+groups+";"+status+";"+lastlogin)
    init_list = ['userid', 'user', 'role', 'modules', 'tools', 'groups', 'status', 'lastlogin']
    for n, i in enumerate(users):
      users[n] = {k:v for k,v in zip(init_list,users[n].split(';'))}
    allmodules = open('/var/cld/creds/modules_list').read().strip().split(',')
    alltools = open('/var/cld/creds/tools_list').read().strip().split(',')
    allgroups = [os.path.basename(name) for name in os.listdir("/var/cld/access/groups/") if os.path.isdir('/var/cld/access/groups/'+name)]
    allowedclouds = bash('grep -v "^#" /var/cld/access/users/'+vld(user)+'/clouds').split('\n')
    disallowedclouds = bash('/var/cld/bin/cld --list --all | sort -u').split('\n')
    bash('if ! [ -d "/home/'+vld(clduser)+'/.ssh" ]; then mkdir -p /home/'+vld(clduser)+'/.ssh ; fi; chown -R '+vld(clduser)+': /home/'+vld(clduser)+'/.ssh ; chmod 700 /home/'+vld(clduser)+'/.ssh')
    file_list = ['/var/cld/access/users/'+clduser+'/clouds', '/var/cld/access/users/'+clduser+'/kvms', '/home/'+clduser+'/.ssh/authorized_keys']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    return render_template('html/user.html', username=username, users=users, allmodules=allmodules, alltools=alltools, allgroups=allgroups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds, files=files)

@app.route('/admin/group/<name>')
def group(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    username = session['username']
    cldgroup = name
    name = [str(cldgroup)]
    grouplist = bash('ls /var/cld/access/groups/').split('\n')
    groups = list()
    for group in name:
      grouptype = bash('grep -qs "1" /var/cld/access/groups/'+vld(group)+'/type && echo -n "parsing" || echo -n "manual"').replace('\n', '')
      groupfuncs = bash('grep -qs "1" /var/cld/access/groups/'+vld(group)+'/funcs && echo -n "custom" || echo -n "default"').replace('\n', '')
      groupusers = bash('egrep "[:,]'+vld(group)+'([:,]|$)" /var/cld/creds/passwd | cut -d : -f 1').replace('\n', ',')
      cloudcount = bash('grep -v "^#\|^$" /var/cld/access/groups/'+vld(group)+'/clouds | wc -l')
      groups.append(group+";"+groupusers+";"+cloudcount+";"+grouptype+";"+groupfuncs)
    init_group = ['group', 'groupusers', 'cloudcount', 'grouptype', 'groupfuncs']
    for n, i in enumerate(groups):
      groups[n] = {k:v for k,v in zip(init_group,groups[n].split(';'))}
    allusers = [os.path.basename(name) for name in os.listdir('/var/cld/access/users/') if os.path.isdir('/var/cld/access/users/'+name)]
    allowedclouds = bash('/var/cld/bin/cld --groups='+cldgroup+' --list --all | sort -u').split('\n')
    disallowedclouds = bash('/var/cld/bin/cld --list --all | sort -u').split('\n')
    parsingscript = bash('cat /var/cld/access/groups/'+vld(group)+'/parsingscript')
    groupfuncvars = bash('cat /var/cld/access/groups/'+vld(group)+'/funcvars || cat /var/cld/access/groups/default/default_funcvars')
    groupfuncterm = bash('cat /var/cld/access/groups/'+vld(group)+'/functerm || cat /var/cld/access/groups/default/default_functerm')
    groupfuncmount = bash('cat /var/cld/access/groups/'+vld(group)+'/funcmount || cat /var/cld/access/groups/default/default_funcmount')
    groupfuncumount = bash('cat /var/cld/access/groups/'+vld(group)+'/funcumount || cat /var/cld/access/groups/default/default_funcumount')
    groupfuncdeploy = bash('cat /var/cld/access/groups/'+vld(group)+'/funcdeploy || cat /var/cld/access/groups/default/default_funcdeploy')
    groupfuncdeploynotty = bash('cat /var/cld/access/groups/'+vld(group)+'/funcdeploynotty || cat /var/cld/access/groups/default/default_funcdeploynotty')
    file_list = ['/var/cld/access/groups/'+cldgroup+'/clouds', '/var/cld/access/groups/'+cldgroup+'/kvms']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    return render_template('html/group.html', username=username, allusers=allusers, groups=groups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds, parsingscript=parsingscript, groupfuncvars=groupfuncvars, groupfuncterm=groupfuncterm, groupfuncmount=groupfuncmount, groupfuncumount=groupfuncumount, groupfuncdeploy=groupfuncdeploy, groupfuncdeploynotty=groupfuncdeploynotty, files=files)

@app.route('/admin/adduser', methods=['POST'])
def adduser():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    newuser = request.form['newuser']
    newpassword = request.form['newpass']
    bash('/var/cld/bin/cld-useradd '+vld(newuser)+' '+vld(newpassword))
    return redirect('/admin', code=302)

@app.route('/admin/deluser', methods=['GET'])
def deluser():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    deluser = request.args['name']
    bash('/var/cld/bin/cld-userdel '+vld(deluser))
    return redirect('/admin', code=302)

@app.route('/admin/addgroup', methods=['POST'])
def addgroup():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    newgroup = request.form['newgroup']
    bash('/var/cld/bin/cld-groupadd '+vld(newgroup))
    return redirect('/admin', code=302)

@app.route('/admin/delgroup', methods=['GET'])
def delgroup():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    delgroup = request.args['name']
    bash('/var/cld/bin/cld-groupdel '+vld(delgroup))
    return redirect('/admin', code=302)

@app.route('/admin/enableuser', methods=['GET'])
def enableuser():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    enableuser = request.args['name']
    bash('passwd --unlock '+vld(enableuser))
    return redirect('/admin', code=302)

@app.route('/admin/disableuser', methods=['GET'])
def disableuser():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    disableuser = request.args['name']
    bash('passwd --lock '+vld(disableuser))
    return redirect('/admin', code=302)

@app.route('/admin/usergroups/<name>', methods=['GET','POST'])
def usergroups(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    groups = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --groups='+vld(','.join(list(filter(None, groups)))))
    return Response('User groups saved', status=200, mimetype='text/plain')

@app.route('/admin/usermodules/<name>', methods=['GET','POST'])
def usermodules(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    modules = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --modules='+vld(','.join(list(filter(None, modules)))))
    return Response('User modules saved', status=200, mimetype='text/plain')

@app.route('/admin/usertools/<name>', methods=['GET','POST'])
def usertools(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    tools = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --tools='+vld(','.join(list(filter(None, tools)))))
    return Response('User tools saved', status=200, mimetype='text/plain')

@app.route('/admin/userclouds/<name>', methods=['GET','POST'])
def userclouds(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    clouds = [vld(cloud) for cloud in list(request.form.to_dict())]
    print(clouds, flush=True)
    open('/var/cld/access/users/'+name+'/clouds', 'w').write("\n".join(list(filter(None, clouds))))
    return Response('User clouds saved', status=200, mimetype='text/plain')

@app.route('/admin/groupusers/<name>', methods=['GET','POST'])
def groupusers(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    group = name
    users = ",".join(list(request.form.to_dict())).split(',')
    denyusers = [os.path.basename(name) for name in os.listdir("/var/cld/access/users/") if os.path.isdir('/var/cld/access/users/'+name) and name not in users]
    for user in users:
      if user != '':
        user = user
        currentgroups = bash('/var/cld/bin/cld-getpasswd --user='+user+' --groups').split(',')
        if group not in currentgroups:
          currentgroups.append(group)
          bash('/var/cld/bin/cld-setpasswd --user='+user+' --groups='+vld(','.join(list(filter(None, currentgroups)))))
    for denyuser in denyusers:
      if denyuser != '':
        currentgroups = bash('/var/cld/bin/cld-getpasswd --user='+denyuser+' --groups').split(',')
        if group in currentgroups:
          currentgroups = [x for x in currentgroups if x != group]
          bash('/var/cld/bin/cld-setpasswd --user='+denyuser+' --groups='+vld(','.join(list(filter(None, currentgroups)))))
    return Response('Group users saved', status=200, mimetype='text/plain')

@app.route('/admin/groupclouds/<name>', methods=['GET','POST'])
def groupclouds(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    group = name
    clouds = [vld(cloud) for cloud in list(request.form.to_dict())]
    print(clouds, flush=True)
    open('/var/cld/access/groups/'+group+'/clouds', 'w').write("\n".join(list(filter(None, clouds))))
    return Response('Group clouds saved', status=200, mimetype='text/plain')

@app.route('/admin/grouptype/<name>', methods=['GET','POST'])
def grouptype(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    group = name
    grouptype = ''
    try:
      grouptype = request.form['grouptype']
      parsingscript = request.form['parsingscript']
    except:
      pass
    if grouptype == 'on':
      bash('rm -f /var/cld/creds/'+vld(group)+'_list /var/cld/access/groups/'+vld(group)+'/clouds ; touch /var/cld/creds/'+vld(group)+'_list ; ln -s /var/cld/creds/'+vld(group)+'_list /var/cld/access/groups/'+vld(group)+'/clouds ; echo 1 > /var/cld/access/groups/'+vld(group)+'/type')
      open("/var/cld/access/groups/"+vld(group)+"/parsingscript", "w", newline='\n').write(parsingscript.replace('\r', ''))
    else:
      bash('rm -f /var/cld/access/groups/'+vld(group)+'/clouds ; touch /var/cld/access/groups/'+vld(group)+'/clouds ; mv -f /var/cld/creds/'+vld(group)+'_list /var/cld/access/groups/'+vld(group)+'/clouds ; echo 0 > /var/cld/access/groups/'+vld(group)+'/type')
    return Response('Group type saved', status=200, mimetype='text/plain')

@app.route('/admin/groupfuncs/<name>', methods=['GET','POST'])
def groupfuncs(name):
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    group = name
    groupfuncs = ''
    try: groupfuncs = request.form['groupfuncs']
    except: pass
    try: groupfuncvars = request.form['groupfuncvars']
    except: pass
    try: groupfuncterm = request.form['groupfuncterm']
    except: pass
    try: groupfuncmount = request.form['groupfuncmount']
    except: pass
    try: groupfuncumount = request.form['groupfuncumount']
    except: pass
    try: groupfuncdeploy = request.form['groupfuncdeploy']
    except: pass
    try: groupfuncdeploynotty = request.form['groupfuncdeploynotty']
    except: pass
    if groupfuncs == 'on':
      bash('echo 1 > /var/cld/access/groups/'+vld(group)+'/funcs')
      open("/var/cld/access/groups/"+vld(group)+"/funcvars", "w", newline='\n').write(groupfuncvars.replace('\r', ''))
      open("/var/cld/access/groups/"+vld(group)+"/functerm", "w", newline='\n').write(groupfuncterm.replace('\r', ''))
      open("/var/cld/access/groups/"+vld(group)+"/funcmount", "w", newline='\n').write(groupfuncmount.replace('\r', ''))
      open("/var/cld/access/groups/"+vld(group)+"/funcumount", "w", newline='\n').write(groupfuncumount.replace('\r', ''))
      open("/var/cld/access/groups/"+vld(group)+"/funcdeploy", "w", newline='\n').write(groupfuncdeploy.replace('\r', ''))
      open("/var/cld/access/groups/"+vld(group)+"/funcdeploynotty", "w", newline='\n').write(groupfuncdeploynotty.replace('\r', ''))
    else:
      bash('echo 0 > /var/cld/access/groups/'+vld(group)+'/funcs')
    return Response('Group functions saved', status=200, mimetype='text/plain')

@app.route('/profile')
def profile():
  if 'username' in session:
    username = session['username']
    clouds=bash('sudo -u '+vld(username)+' sudo /var/cld/bin/cld --list')
    visiblemodules = uservisiblemodules(username)
    modules = getusermodules(username)
    perms=bash('grep "^'+vld(username)+':" /var/cld/creds/passwd').split(':')
    return render_template('html/profile.html', username=username, clouds=clouds, perms=perms, visiblemodules=visiblemodules, modules=modules)

@app.route('/profile/usermodules/<name>', methods=['GET','POST'])
def profile_set_visible_modules(name):
  if 'username' in session:
    user = session['username']
    modules = list(request.form.to_dict())
    open('/var/cld/access/users/'+vld(name)+'/showonlymodules', 'w').write("\n".join(modules))
    return Response('User groups saved', status=200, mimetype='text/plain')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8080)