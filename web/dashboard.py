# -*- coding: utf-8 -*-
from flask import Flask, abort, request, render_template, g, Response, send_from_directory, redirect, escape, url_for, session, cli
from flask_session import Session
from flask_socketio import SocketIO, join_room, leave_room, close_room
from werkzeug.utils import secure_filename
from functools import wraps
import logging
import os, re, pwd, subprocess, shutil
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
from glob import glob
from pathlib import Path

def bash(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

def vld(cld_variable):
    return re.match('(^[A-z0-9.,@=/_ -]+?$|^$)', cld_variable).string

def stream_file(filepath, chunksize=8192):
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk: yield chunk
            else: break

def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['path'] = path
        d['dirs'] = [path_to_dict(os.path.join(path, x)) for x in os.listdir(path)]
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
    return True

def remoteaddr():
    if request.headers.getlist("X-Forwarded-For"):
        remote_addr = request.headers.getlist("X-Forwarded-For")[0]
    else:
        remote_addr = request.remote_addr
    return re.match("[A-z0-9.:]+", remote_addr)[0]

def accesslist():
    ip_set = set()
    files = ['/var/cld/modules/access/data/myips', '/var/cld/modules/access/data/enabledips']
    for file in files:
        try:
            with open(file, 'r') as f:
                for line in f:
                    ip = line.strip().split('_')[0]
                    ip_set.add(ip)
        except FileNotFoundError:
            print(f"Warning: File {file} not found.")
    return list(ip_set)

def allowmoduleusers(cldmodule):
    allowed_users = set()
    with open('/var/cld/creds/passwd', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                parts = line.split(':')
                if len(parts) >= 4:
                    username, module_info = parts[0], parts[3]
                    if cldmodule in module_info or 'ALL' in module_info:
                        allowed_users.add(username)
    return allowed_users

def allowutilityusers(cldutility):
    allowed_users = set()
    with open('/var/cld/creds/passwd', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Skip empty lines and comments
                parts = line.split(':')
                if len(parts) >= 5:
                    username, utility_info = parts[0], parts[4]
                    if cldutility in utility_info or 'ALL' in utility_info:
                        allowed_users.add(username)
    return allowed_users

def uservisiblemodules(user):
    if not user or not isinstance(user, str):
        return []
    usermodules = []
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 5 and parts[0] == user:
                    usermodules = parts[3].split(',') if parts[3] else []
                    break
    except FileNotFoundError:
        return []
    webmodules = [module for module in os.listdir('/var/cld/modules') if os.path.isfile(os.path.join('/var/cld/modules', module, 'web.py'))]
    if "ALL" in usermodules:
        showonly_path = f'/var/cld/access/users/{user}/showonlymodules'
        if os.path.isfile(showonly_path):
            try:
                with open(showonly_path, 'r') as f:
                    modulesinfile = [x.strip() for x in f.read().strip().split('\n') if x.strip()]
                return [x for x in modulesinfile if x in webmodules]
            except (FileNotFoundError, PermissionError):
                return []
        return webmodules
    else:
        userwebmodules = [x for x in usermodules if x in webmodules]
        showonly_path = f'/var/cld/access/users/{user}/showonlymodules'
        if os.path.isfile(showonly_path):
            try:
                with open(showonly_path, 'r') as f:
                    modulesinfile = [x.strip() for x in f.read().strip().split('\n') if x.strip()]
                return [x for x in modulesinfile if x in userwebmodules]
            except (FileNotFoundError, PermissionError):
                return userwebmodules
        return userwebmodules

def getusermodules(user):
    if not user or not isinstance(user, str):
        return []
    usermodules = []
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 5 and parts[0] == user:
                    usermodules = parts[3].split(',') if parts[3] else []
                    break
    except FileNotFoundError:
        return []
    webmodules = [module for module in os.listdir('/var/cld/modules') if os.path.isfile(os.path.join('/var/cld/modules', module, 'web.py'))]
    if "ALL" in usermodules:
        return webmodules
    return [x for x in webmodules if x in usermodules]

def usertools(user):
    if not user or not isinstance(user, str):
        return []
    tools = []
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 6 and parts[0] == user:
                    tools = parts[4].split(',') if parts[4] else []
                    break
    except FileNotFoundError:
        return []
    if "ALL" in tools:
        try:
            with open('/var/cld/creds/tools_list', 'r') as f:
                return [x.strip() for x in f.read().strip().split(',') if x.strip()]
        except FileNotFoundError:
            return []
    return tools

def userisadmin(user):
    if not user or not isinstance(user, str):
        return False
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 6 and parts[0] == user:
                    modules = parts[3] if len(parts) > 3 else ""
                    tools = parts[4] if len(parts) > 4 else ""
                    return modules == "ALL" and tools == "ALL"
    except FileNotFoundError:
        return False
    return False

def apitokenbyuser(user):
    if not user or not isinstance(user, str):
        return ""
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 4 and parts[0] == user:
                    return parts[2] if len(parts) > 2 else ""
    except FileNotFoundError:
        return ""
    return ""

def checkperms(cldmodule, cldutility, user):
    cldmodule = str(cldmodule)
    cldutility = str(cldutility)
    if user in allowmoduleusers(cldmodule) or user in allowutilityusers(cldutility):
        return ["granted", user]
    return ["denied", "DENIED"]

def checkpermswhiteip(cldmodule, cldutility, user, remoteaddr):
    # Sanitize inputs, allowing empty cldmodule
    user = re.match("[A-z0-9_.-]+", user)[0] if re.match("[A-z0-9_.-]+", user) else "DENIED"
    cldmodule = str(cldmodule) if cldmodule and re.match("[A-z0-9_.-]+", str(cldmodule)) else ""
    cldutility = str(re.match("[A-z0-9_.-]+", cldutility)[0]) if re.match("[A-z0-9_.-]+", cldutility) else "DENIED"
    usernames = [line.split(':')[0] for line in open('/var/cld/creds/passwd') if line.strip() and not line.startswith('#')] if os.path.exists('/var/cld/creds/passwd') else []
    if cldutility == 'bash' and remoteaddr in accesslist() and user in usernames:
        return ["granted", user]
    elif user in allowmoduleusers(cldmodule) and remoteaddr in accesslist():
        return ["granted", user]
    elif user in allowutilityusers(cldutility) and remoteaddr in accesslist():
        return ["granted", user]
    return ["denied", "DENIED"]

# Parse creds file instead of grep/cut
creds_file = '/var/cld/creds/creds'
cld_domain = cld_ip = ''
if os.path.exists(creds_file):
    with open(creds_file, 'r') as f:
        for line in f:
            if line.startswith('CLD_DOMAIN='):
                cld_domain = line.split('=')[1].strip().strip('"')
            elif line.startswith('CLD_IP='):
                cld_ip = line.split('=')[1].strip().strip('"')

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
        if 'username' in session:
            return f(*args, **kwargs)
        return redirect('/login', code=302)
    return decorated_func

def is_admin(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if 'username' in session:
            if userisadmin(session['username']):
                return f(*args, **kwargs)
            session.pop('username', None)
            return redirect('/', code=302)
        return redirect('/', code=302)
    return decorated_func

webmodule = {}
cldm = {}
for webfile in Path('/var/cld/modules').glob('*/web.py'):
    cldmodule = webfile.parent.name
    cldm[cldmodule] = cldmodule
    print(cldmodule, flush=True)
    with open(webfile, 'r') as f:
        code = f.read().replace('cldmodule', f'cldm["{cldmodule}"]')
        exec(code)

# Create symlinks to templates using Python
web_modules_dir = '/var/cld/web/modules'
html_include_dir = '/var/cld/web/html/include'
os.makedirs(web_modules_dir, exist_ok=True)
for module in Path('/var/cld/modules').glob('*/web'):
    module_name = module.parent.name
    target = os.path.join(web_modules_dir, module_name)
    if os.path.exists(target):
        os.remove(target)
    os.symlink(module, target)
cld_tier_source = '/var/cld/creds/cld_tier'
cld_tier_target = os.path.join(html_include_dir, 'cld_tier.html')
if os.path.exists(cld_tier_target):
    os.remove(cld_tier_target)
os.symlink(cld_tier_source, cld_tier_target)

CLD_UTILITIES = {}

def init_cld_utilities():
    """Initialize the global CLD_UTILITIES dictionary with utilities from /var/cld/bin/ and /var/cld/modules/*/bin/"""
    # Check /var/cld/bin/
    bin_path = '/var/cld/bin/'
    if os.path.exists(bin_path):
        for utility in os.listdir(bin_path):
            full_path = os.path.join(bin_path, utility)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                CLD_UTILITIES[utility] = full_path
    
    # Check /var/cld/modules/*/bin/
    module_bins = glob('/var/cld/modules/*/bin/')
    for module_bin in module_bins:
        for utility in os.listdir(module_bin):
            full_path = os.path.join(module_bin, utility)
            if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                CLD_UTILITIES[utility] = full_path

# Initialize utilities on startup
init_cld_utilities()

@app.route('/help/<cldutility>')
@logged_in
def help_tool(cldutility):
    user = session['username']
    # Sanitize cldutility
    cldutility = str(re.match('^[A-z0-9.,@=/_ -]+', cldutility)[0])
    # Determine cldfile
    cldfile = CLD_UTILITIES.get(cldutility, '')
    # Check if file exists
    if not os.path.exists(cldfile):
        return Response('File not exist', status=403, mimetype='text/plain')
    # Get module name
    cldmodule = Path(cldfile).parent.parent.name if Path(cldfile).parent.name == 'bin' and Path(cldfile).parent.parent.parent == Path('/var/cld/modules') else ''
    # Check permissions
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    if checkresult[0] != "granted":
        return Response("403", status=403, mimetype='application/json')
    # Execute help command
    print(f'sudo -u {user} sudo FROM=CLI {cldfile} --help', flush=True)
    cmdoutput = bash(f'sudo -u {vld(user)} sudo FROM=API {vld(cldfile)} --help')
    return Response(cmdoutput, status=200, mimetype='application/json')

# Check for ansifilter using shutil.which
ansifilter_path = shutil.which('ansifilter')
if ansifilter_path:
    outputinterpreter = f'{ansifilter_path} -Hf'
else:
    outputinterpreter = shutil.which('cat')
    print('''ansifilter IS NOT INSTALLED IN THE SYSTEM - API OUTPUT WILL NOT FILTERED - https://github.com/andre-simon/ansifilter
    cd /usr/src
    git clone https://github.com/andre-simon/ansifilter.git
    cd ansifilter/
    make
    make install
    ''')

@app.route('/webapi/tool/<cldutility>')
@app.route('/webapi/tool/<cldutility>/')
@app.route('/webapi/tool/<cldutility>/<args>')
@logged_in
def webapi_tool(cldutility, args=None):
    user = session['username']
    # Sanitize cldutility
    cldutility = str(re.match('^[A-z0-9.,@=/_ -]+', cldutility)[0])
    # Determine cldfile
    if cldutility != 'bash':
        cldfile = CLD_UTILITIES.get(cldutility, '')
    else:
        cldfile = '/bin/bash'
    # Check if file exists
    if not os.path.exists(cldfile):
        return Response('File not exist', status=403, mimetype='text/plain')
    # Get module name
    cldmodule = os.path.basename(os.path.dirname(os.path.dirname(cldfile))) if cldfile != '/bin/bash' and '/modules/' in cldfile else "bash"
    # Check permissions
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    if checkresult[0] != "granted":
        return Response("403", status=403, mimetype='application/json')
    # Sanitize command arguments
    cmd_args = ''
    try:
        if args:
            cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
    except:
        pass
    try:
        if request.args.get('args'):
            cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except:
        pass
    # Handle output
    try:
        if request.args.get('output') == 'html':
            print(f'sudo -u {user} sudo FROM=CLI {cldfile} {cmd_args} | {outputinterpreter}', flush=True)
            cmdoutput = bash(f'sudo -u {vld(user)} sudo FROM=API {vld(cldfile)} {cmd_args} | {outputinterpreter}')
            return Response(f'<pre>{cmdoutput}</pre>', status=200, mimetype='text/html')
    except:
        pass
    print(f'sudo -u {user} sudo FROM=CLI {cldfile} {cmd_args}', flush=True)
    cmdoutput = bash(f'sudo -u {vld(user)} sudo FROM=WEB {vld(cldfile)} {cmd_args}')
    return Response(cmdoutput, status=200, mimetype='text/plain')

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
        cldmodule = os.path.basename(os.path.dirname(os.path.dirname(cldfile))) if '/modules/' in cldfile else ''
        checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
        if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
        try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
        except: cmd_args = ''
        try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
        except: pass
        chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
        socketid = ''.join(random.choice(chars) for _ in range(16))
        return render_template("html/cldx.html", socketid=socketid, cldutility=cldutility, cmd_args=cmd_args)

@app.route("/tool/<cldutility>")
@app.route("/tool/<cldutility>/")
@app.route("/tool/<cldutility>/<args>")
@logged_in
def tool(cldutility, args=None):
    user = session['username']
    cldutility = str(re.match('^[A-z0-9.,@=/_ -]+', cldutility)[0])
    if cldutility != 'bash':
        if cldutility in CLD_UTILITIES:
            cldfile = CLD_UTILITIES[cldutility]
        else:
            cldfile = ''
    else:
        cldfile = '/bin/bash'
    cldmodule = os.path.basename(os.path.dirname(os.path.dirname(cldfile))) if cldfile != '/bin/bash' and '/modules/' in cldfile else "bash"
    print(cldfile, flush=True)
    if not os.path.exists(cldfile):
        print(f"os.path.exists({cldfile})", flush=True)
        return Response('File not exist', status=403, mimetype='text/plain')
    print(cldfile, flush=True)
    checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', args).string)
    except: cmd_args = ''
    try: cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except: pass
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    socketid = ''.join(random.choice(chars) for _ in range(16))
    return render_template("html/socket.html", socketid=socketid, cldutility=cldutility, cmd_args=cmd_args)

@app.route("/getfile/<instance>")
@logged_in
def getfile(instance):
    user = session['username']
    checkresult = checkpermswhiteip('NONE', 'cldxmount', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    instance = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --json '+vld(instance)))[0]['clouds'][0]
    filepath = str(re.match('^/[A-z0-9.,@=/_-]+$', request.args['filepath']).string)
    mountpath = f'/home/{user}/mnt/{instance}'
    fullfilepath = mountpath + filepath
    filename = os.path.basename(filepath)
    if not os.path.ismount(mountpath):
        bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cldxmount '+vld(instance))
        time.sleep(3)
    if not os.path.ismount(mountpath):
        return Response('Instance directory mount failed', status=403, mimetype='text/plain')
    if not os.path.exists(fullfilepath) or not os.path.isfile(fullfilepath):
        return Response('File not exist', status=403, mimetype='text/plain')
    return Response(stream_file(fullfilepath), status=200, mimetype='application/octet-stream', headers={'Content-Disposition': f'attachment; filename={filename}'})

@app.route("/uploadfile/<instance>", methods=['GET','POST'])
@logged_in
def uploadfile(instance):
    user = session['username']
    checkresult = checkpermswhiteip('NONE', 'cldxmount', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    instance = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --json '+vld(instance)))[0]['clouds'][0]
    try: filepath = str(re.match('^/[A-z0-9.,@=/_-]+$', request.form['filepath']).string)
    except: filepath = '/tmp'
    mountpath = f'/home/{user}/mnt/{instance}'
    file = request.files['file']
    filename = secure_filename(file.filename)
    fullfilepath = mountpath + filepath
    if not os.path.ismount(mountpath):
        bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cldxmount '+vld(instance))
        time.sleep(3)
    if not os.path.ismount(mountpath):
        return Response('Instance directory mount failed', status=403, mimetype='text/plain')
    if not os.path.isdir(fullfilepath):
        return Response('Directory not exist', status=403, mimetype='text/plain')
    file.save(os.path.join(fullfilepath, filename))
    print(os.path.join(fullfilepath, filename), flush=True)
    return Response('File uploaded', status=200, mimetype='text/plain')

def keepalive_shell_session(socketid, child_pid, room, subprocpid, fd):
    app.config["shell"]["keepalive"][socketid] = int(time.time()) + 60
    print("keepalive_shell_session started for socketid: "+socketid, flush=True)
    while True:
        time.sleep(10)
        try:
            current_timestamp = int(time.time())
            socket_timestamp = app.config["shell"]["keepalive"][socketid]
            if current_timestamp > socket_timestamp:
                print("started terminating task for socket "+socketid, flush=True)
                print("exit due "+socketid+" not connected", flush=True)
                socketio.emit("output", {"output": "Process exited"}, namespace="/cld", room=room, sid=socketid)
                socketio.emit("disconnect", {"disconnect": socketid}, namespace="/cld", room=room, sid=socketid)
                try: socketio.close_room(room)
                except: print("socketio.close_room exception", flush=True)
                if check_pid(subprocpid):
                    bash('kill -9 '+str(subprocpid))
                return
        except:
            pass

def read_and_forward_pty_output(socketid, sessfd, subprocpid, child_pid, room):
    max_read_bytes = 1024 * 20
    if not check_pid(subprocpid):
        print(f"Process {subprocpid} not found", flush=True)
    while True:
        socketio.sleep(0.05)
        if not check_pid(subprocpid):
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
        socketid = request.sid
        if socketid in app.config["shell"]:
            os.write(app.config["shell"][socketid], data["input"].encode())

@socketio.on("keepalive", namespace="/cld")
def pty_keepalive():
    if 'username' in session:
        socketid = request.sid
        print("received keepalive data from: "+socketid, flush=True)
        app.config["shell"]["keepalive"][socketid] = int(time.time()) + 15

@socketio.on("resize", namespace="/cld")
def resize(data):
    if 'username' in session:
        socketid = request.sid
        if socketid in app.config["shell"]:
            set_winsize(app.config["shell"][socketid], data["rows"], data["cols"])

@socketio.on("connect", namespace="/cld")
@logged_in
def connect():
    if 'username' in session:
        user = session['username']
        cldutility = request.args.get('cldutility')
        if cldutility != 'bash':
            bashrc_path = f'/home/{vld(user)}/.bashrc'
            cldfile = ''
            if os.path.exists(bashrc_path):
                with open(bashrc_path, 'r') as f:
                    for line in f:
                        if f" {vld(cldutility)}=" in line:
                            cldfile = line.split("'")[1]
                            break
            if not cldfile:
                cldfile = ''
        else:
            cldfile = '/bin/bash'
        cldmodule = os.path.basename(os.path.dirname(os.path.dirname(cldfile))) if cldfile != '/bin/bash' and '/modules/' in cldfile else "bash"
        checkresult = checkpermswhiteip(cldmodule, cldutility, user, remoteaddr())
        if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
        socketid = request.sid
        sid = request.sid
        cmd_args = ''
        try: cmd_args = str(re.match('^[A-z0-9.,@=/: -]+$', request.args.get('args')).string) + " "
        except: cmd_args = " "
        if cldutility == 'bash':
            shellcmd = '/bin/bash'
        else:
            shellcmd = ''
            if os.path.exists(bashrc_path):
                with open(bashrc_path, 'r') as f:
                    for line in f:
                        if f" {vld(cldutility)}=" in line:
                            shellcmd = line.split("'")[1]
                            break
        join_room(socketid)
        room = socketid
        if not shellcmd:
            socketio.emit("output", {"output": "Access denied: check request is correct and access rights for the user"}, namespace="/cld", room=room, sid=socketid)
            return socketio.emit("disconnect", namespace="/cld", room=room, sid=socketid)
        child_pid, fd = pty.fork()
        time.sleep(0.05)
        if child_pid == 0:
            subprocess.run(f"TERM=xterm /usr/bin/sudo -u {vld(user)} {vld(shellcmd)} {cmd_args} ; sleep 0.5s", shell=True, cwd=f'/home/{user}', executable='/bin/bash')
        elif isinstance(child_pid, int):
            app.config["shell"]["childpid"][socketid] = child_pid
            subprocpid = ''
            count = 0
            while not subprocpid and count < 30:
                subprocpid = bash('ps axf -o pid,command | grep -v grep | sed "s/^ *//g" | grep -A1 "^'+str(child_pid)+' " | cut -d " " -f 1 | tail -1').replace('\n', '')
                count += 1
                time.sleep(0.1)
            app.config["shell"][socketid] = fd
            app.config["shell"]["subprocpid"+socketid] = int(subprocpid)
            set_winsize(fd, 50, 50)
            socketio.start_background_task(read_and_forward_pty_output, socketid, fd, int(subprocpid), child_pid, room)
            print(str(socketid), str(fd), str(subprocpid), str(child_pid), str(room), flush=True)
            threading.Thread(target=keepalive_shell_session, args=(socketid, child_pid, room, int(subprocpid), fd)).start()

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
@logged_in
def index():
    user = session['username']
    isadmin = userisadmin(user)
    modulelist = uservisiblemodules(user)
    if modulelist:
        modules = {}
        for module in modulelist:
            name = module
            webmodule[module]['logo'] = f'modules/{module}/content/logo.svg' if os.path.isfile(f'modules/{module}/content/logo.svg') else 'img/module.svg'
            webmodule[module]['desc'] = webmodule.get(module, {}).get('desc', f"module {module}")
            webmodule[module]['homename'] = webmodule.get(module, {}).get('homename', module.capitalize().replace('.local', ''))
            webmodule[module]['adminonly'] = webmodule.get(module, {}).get('adminonly', False)
            modules[module] = webmodule[module]
        print(str(modules), flush=True)
        return render_template('html/index.html', username=user, modules=modules, isadmin=isadmin)
    return render_template('html/index.html', username=user, isadmin=isadmin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' not in session:
            if os.path.isdir(f'/var/cld/access/users/{request.form["username"]}'):
                try:
                    if pam.pam().authenticate(request.form['username'], request.form['password']):
                        session['username'] = request.form['username']
                        return redirect(url_for('index'))
                except:
                    pass
    if 'username' in session:
        return redirect(url_for('index'))
    return render_template('html/login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/terminal')
@logged_in
def terminal():
    username = session['username']
    cld_instances = json.loads(bash('sudo -u '+vld(username)+' sudo FROM=CLI /var/cld/bin/cld --list --json'))
    return render_template('html/terminal.html', username=username, cld_instances=cld_instances)

@app.route('/password', methods=['POST'])
@logged_in
def changepassword():
    username = session['username']
    newpassword = request.form['password']
    try:
        subprocess.run(['chpasswd'], input=f"{vld(username)}:{newpassword}", text=True, check=True)
        return Response('Password changed successfully<script>window.setTimeout(function(){window.location.href="/profile";},2000);</script>', status=200, mimetype='text/html')
    except subprocess.CalledProcessError as e:
        return Response(f'Error changing password: {e}<script>window.setTimeout(function()window.location.href="/profile";,2000);</script>', status=500, mimetype='text/html')

@app.route('/toolkit')
@logged_in
def toolkit():
    username = session['username']
    cld_tools = json.loads(bash('sudo -u '+vld(username)+' sudo FROM=CLI /var/cld/bin/cld-modules --json'))
    utils = []
    bashrc_path = f'/home/{vld(username)}/.bashrc'
    if os.path.exists(bashrc_path):
        with open(bashrc_path, 'r') as f:
            for line in f:
                if line.startswith('alias ') and not line.startswith('#'):
                    parts = line.split("'")
                    if len(parts) > 1:
                        cmd = parts[1].split(' ')[-1]
                        utils.append(os.path.basename(cmd))
    return render_template('html/toolkit.html', username=username, utils=utils, cld_tools=cld_tools)

@app.route('/admin/')
@app.route('/admin')
@is_admin
def admin():
    username = session['username']
    users = []
    for user in os.listdir('/var/cld/access/users/'):
        user_path = os.path.join('/var/cld/access/users/', user)
        if os.path.isdir(user_path):
            try:
                user_info = pwd.getpwnam(user)
                userid = str(user_info.pw_uid)
                role = open(os.path.join(user_path, 'role')).read().strip() if os.path.exists(os.path.join(user_path, 'role')) else ''
                groups = ''
                with open('/var/cld/creds/passwd', 'r') as f:
                    for line in f:
                        if line.startswith(f"{user}:"):
                            groups = line.split(':')[5] if len(line.split(':')) > 5 else ''
                            break
                status = '0' if user_info.pw_passwd == '!' else '1'
                lastlogin = ''
                try:
                    lastlogin_lines = subprocess.check_output(['last', user, '-R'], text=True).splitlines()
                    lastlogin = ' '.join(lastlogin_lines[0].split()[2:]) if lastlogin_lines else ''
                except subprocess.CalledProcessError:
                    lastlogin = 'N/A'
                users.append({
                    'userid': userid,
                    'user': user,
                    'role': role,
                    'groups': groups,
                    'status': status,
                    'lastlogin': lastlogin
                })
            except KeyError:
                continue
    groups = []
    for group in os.listdir('/var/cld/access/groups/'):
        group_path = os.path.join('/var/cld/access/groups/', group)
        if os.path.isdir(group_path):
            type_file = os.path.join(group_path, 'type')
            grouptype = 'parsing' if os.path.exists(type_file) and open(type_file).read().strip() == '1' else 'manual'
            groupusers = ','.join(line.split(':')[0] for line in open('/var/cld/creds/passwd').readlines() if group in line.split(':')[5].split(',') and line.strip())
            clouds_file = os.path.join(group_path, 'clouds')
            cloudcount = sum(1 for line in open(clouds_file).readlines() if line.strip() and not line.startswith('#')) if os.path.exists(clouds_file) else 0
            groups.append({
                'group': group,
                'groupusers': groupusers,
                'cloudcount': str(cloudcount),
                'grouptype': grouptype
            })
    file_list = ['/var/cld/creds/passwd', '/etc/cron.d/cld', '/var/cld/creds/creds', '/var/cld/creds/protected_ports', '/var/cld/creds/local_nets']
    files = {file: open(file).read() if os.path.exists(file) else (open(file, 'a').close() or '') for file in file_list}
    return render_template('html/admin.html', username=username, users=users, groups=groups, files=files)

@app.route('/admin/savefile', methods=['POST'])
@is_admin
def adminsavefile():
    file = request.form['file']
    filename = os.path.basename(file)
    filedir = os.path.dirname(file)
    if not os.path.exists(filedir):
        os.makedirs(filedir, mode=0o700, exist_ok=True)
    content = request.form['content']
    with open(file, "w", newline='\n') as f:
        f.write(content.replace('\r', ''))
    if re.match('(^cld-[A-za-z0-9]+$)', filename):
        os.chmod(file, 0o700)
    return Response(f"file {file} saved", status=200, mimetype='text/plain')

@app.route('/admin/deletefile', methods=['POST'])
@is_admin
def admindeletefile():
    file = request.form['file']
    os.remove(file)
    filedir = os.path.dirname(file)
    try: os.rmdir(filedir)
    except: pass
    return Response(f"file {file} deleted", status=200, mimetype='text/plain')

@app.route('/admin/user/<name>')
@is_admin
def user(name):
    username = session['username']
    clduser = re.match('^[A-z0-9.,@=/_ -]+$', name).string
    users = []
    try:
        user_info = pwd.getpwnam(vld(clduser))
        userid = str(user_info.pw_uid)
        role = Path(f'/var/cld/access/users/{vld(clduser)}/role').read_text().strip() if Path(f'/var/cld/access/users/{vld(clduser)}/role').exists() else ''
        modules, tools, groups = '', '', ''
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                if line.startswith(f'{vld(clduser)}:'):
                    fields = line.strip().split(':')
                    modules, tools, groups = fields[3:6] if len(fields) > 5 else ('', '', '')
                    break
        status = '0' if user_info.pw_passwd == '!' else '1'
        try:
            lastlogin = subprocess.check_output(['last', vld(clduser), '-R'], text=True).splitlines()[0].split()[2:] or ['']
            lastlogin = ' '.join(lastlogin)
        except subprocess.CalledProcessError:
            lastlogin = ''
        users.append(f"{userid};{clduser};{role};{modules};{tools};{groups};{status};{lastlogin}")
    except KeyError:
        pass
    users = [{k: v for k, v in zip(['userid', 'user', 'role', 'modules', 'tools', 'groups', 'status', 'lastlogin'], i.split(';'))} for i in users]
    allmodules = Path('/var/cld/creds/modules_list').read_text().strip().split(',') if Path('/var/cld/creds/modules_list').exists() else []
    alltools = Path('/var/cld/creds/tools_list').read_text().strip().split(',') if Path('/var/cld/creds/tools_list').exists() else []
    allgroups = [name for name in os.listdir('/var/cld/access/groups') if os.path.isdir(f'/var/cld/access/groups/{name}')]
    allowedclouds = Path(f'/var/cld/access/users/{vld(clduser)}/clouds').read_text().splitlines() if Path(f'/var/cld/access/users/{vld(clduser)}/clouds').exists() else []
    disallowedclouds = subprocess.check_output(['/var/cld/bin/cld', '--list', '--all'], text=True).strip().split('\n') or []
    disallowedclouds.sort()
    ssh_dir = f'/home/{vld(clduser)}/.ssh'
    if not os.path.exists(ssh_dir):
        os.makedirs(ssh_dir, mode=0o700)
        user_info = pwd.getpwnam(vld(clduser))
        os.chown(ssh_dir, user_info.pw_uid, user_info.pw_gid)
    file_list = [f'/var/cld/access/users/{clduser}/{x}' for x in ['clouds', 'kvms']] + [f'/home/{clduser}/.ssh/authorized_keys']
    files = {f: (Path(f).touch() or Path(f).read_text()) for f in file_list if not Path(f).exists() or True}
    return render_template('html/user.html', username=username, users=users, allmodules=allmodules, alltools=alltools, allgroups=allgroups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds, files=files)

@app.route('/admin/group/<name>')
@is_admin
def group(name):
    username = session['username']
    cldgroup = name
    grouplist = [d for d in os.listdir('/var/cld/access/groups') if os.path.isdir(f'/var/cld/access/groups/{d}')]
    groups = []
    for group in [cldgroup]:
        type_file = Path(f'/var/cld/access/groups/{vld(group)}/type')
        grouptype = 'manual'
        if type_file.exists():
            try:
                grouptype = 'parsing' if type_file.read_text().strip() == '1' else 'manual'
            except FileNotFoundError:
                pass
        funcs_file = Path(f'/var/cld/access/groups/{vld(group)}/funcs')
        groupfuncs = 'default'
        if funcs_file.exists():
            try:
                groupfuncs = 'custom' if funcs_file.read_text().strip() == '1' else 'default'
            except FileNotFoundError:
                pass
        groupusers = ','.join([fields[0] for fields in [line.strip().split(':') for line in open('/var/cld/creds/passwd').readlines()] if len(fields) > 5 and re.search(f'[:,]{vld(group)}([:,]|$)', fields[5])] if Path('/var/cld/creds/passwd').exists() else [])
        clouds_file = Path(f'/var/cld/access/groups/{vld(group)}/clouds')
        cloudcount = 0
        if clouds_file.exists():
            try:
                cloudcount = sum(1 for line in clouds_file.read_text().splitlines() if line.strip() and not line.startswith('#'))
            except FileNotFoundError:
                pass
        groups.append(f"{group};{groupusers};{cloudcount};{grouptype};{groupfuncs}")
    groups = [{k: v for k, v in zip(['group', 'groupusers', 'cloudcount', 'grouptype', 'groupfuncs'], i.split(';'))} for i in groups]
    allusers = [name for name in os.listdir('/var/cld/access/users') if os.path.isdir(f'/var/cld/access/users/{name}')]
    allowedclouds = subprocess.check_output(['/var/cld/bin/cld', f'--groups={vld(cldgroup)}', '--list', '--all'], text=True).strip().split('\n') or []
    allowedclouds.sort()
    disallowedclouds = subprocess.check_output(['/var/cld/bin/cld', '--list', '--all'], text=True).strip().split('\n') or []
    disallowedclouds.sort()
    group_files = {
        'parsingscript': f'/var/cld/access/groups/{vld(group)}/parsingscript',
        'groupfuncvars': f'/var/cld/access/groups/{vld(group)}/funcvars',
        'groupfuncterm': f'/var/cld/access/groups/{vld(group)}/functerm',
        'groupfuncmount': f'/var/cld/access/groups/{vld(group)}/funcmount',
        'groupfuncumount': f'/var/cld/access/groups/{vld(group)}/funcumount',
        'groupfuncdeploy': f'/var/cld/access/groups/{vld(group)}/funcdeploy',
        'groupfuncdeploynotty': f'/var/cld/access/groups/{vld(group)}/funcdeploynotty'
    }
    defaults = {k: f'/var/cld/access/groups/default/default_{k}' for k in ['funcvars', 'functerm', 'funcmount', 'funcumount', 'funcdeploy', 'funcdeploynotty']}
    file_contents = {}
    for k, v in group_files.items():
        file_path = Path(v)
        default_path = Path(defaults.get(k, '/nonexistent'))  # Use a non-existent path as fallback
        content = ''
        if file_path.exists() and file_path.is_file():
            try:
                content = file_path.read_text()
            except FileNotFoundError:
                pass
        elif default_path.exists() and default_path.is_file():
            try:
                content = default_path.read_text()
            except FileNotFoundError:
                pass
        file_contents[k] = content
    file_list = [f'/var/cld/access/groups/{cldgroup}/{x}' for x in ['clouds', 'kvms']]
    files = {}
    for f in file_list:
        file_path = Path(f)
        try:
            if not file_path.exists():
                file_path.touch()
            files[f] = file_path.read_text()
        except FileNotFoundError:
            files[f] = ''
    return render_template('html/group.html', username=username, allusers=allusers, groups=groups, allowedclouds=allowedclouds, disallowedclouds=disallowedclouds, **file_contents, files=files)

@app.route('/admin/adduser', methods=['POST'])
@is_admin
def adduser():
    newuser = request.form['newuser']
    newpassword = request.form['newpass']
    bash('/var/cld/bin/cld-useradd '+vld(newuser)+' '+vld(newpassword))
    return redirect('/admin', code=302)

@app.route('/admin/deluser', methods=['GET'])
@is_admin
def deluser():
    deluser = request.args['name']
    bash('/var/cld/bin/cld-userdel '+vld(deluser))
    return redirect('/admin', code=302)

@app.route('/admin/addgroup', methods=['POST'])
@is_admin
def addgroup():
    newgroup = request.form['newgroup']
    bash('/var/cld/bin/cld-groupadd '+vld(newgroup))
    return redirect('/admin', code=302)

@app.route('/admin/delgroup', methods=['GET'])
@is_admin
def delgroup():
    delgroup = request.args['name']
    bash('/var/cld/bin/cld-groupdel '+vld(delgroup))
    return redirect('/admin', code=302)

@app.route('/admin/enableuser', methods=['GET'])
@is_admin
def enableuser():
    clduser = request.args['name']
    shadow_file = '/etc/shadow'
    if os.path.exists(shadow_file):
        with open(shadow_file, 'r') as f:
            lines = f.readlines()
        with open(shadow_file, 'w') as f:
            for line in lines:
                if line.startswith(f'{vld(clduser)}:'):
                    f.write(line.replace(f'{vld(clduser)}:!!', f'{vld(clduser)}:'))
                else:
                    f.write(line)
    return redirect('/admin', code=302)

@app.route('/admin/disableuser', methods=['GET'])
@is_admin
def disableuser():
    clduser = request.args['name']
    shadow_file = '/etc/shadow'
    if os.path.exists(shadow_file):
        with open(shadow_file, 'r') as f:
            lines = f.readlines()
        with open(shadow_file, 'w') as f:
            for line in lines:
                if line.startswith(f'{vld(clduser)}:'):
                    f.write(line.replace(f'{vld(clduser)}:', f'{vld(clduser)}:!!'))
                else:
                    f.write(line)
    return redirect('/admin', code=302)

@app.route('/admin/usergroups/<name>', methods=['GET','POST'])
@is_admin
def usergroups(name):
    groups = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --groups='+vld(','.join(list(filter(None, groups)))))
    return Response('User groups saved', status=200, mimetype='text/plain')

@app.route('/admin/usermodules/<name>', methods=['GET','POST'])
@is_admin
def usermodules(name):
    modules = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --modules='+vld(','.join(list(filter(None, modules)))))
    return Response('User modules saved', status=200, mimetype='text/plain')

@app.route('/admin/usertools/<name>', methods=['GET','POST'])
@is_admin
def usertools(name):
    tools = list(request.form.to_dict())
    bash('/var/cld/bin/cld-setpasswd --user='+vld(name)+' --tools='+vld(','.join(list(filter(None, tools)))))
    return Response('User tools saved', status=200, mimetype='text/plain')

@app.route('/admin/userclouds/<name>', methods=['GET','POST'])
@is_admin
def userclouds(name):
    clouds = [vld(cloud) for cloud in list(request.form.to_dict())]
    print(clouds, flush=True)
    with open(f'/var/cld/access/users/{name}/clouds', 'w') as f:
        f.write("\n".join(list(filter(None, clouds))))
    return Response('User clouds saved', status=200, mimetype='text/plain')

@app.route('/admin/groupusers/<name>', methods=['GET','POST'])
@is_admin
def groupusers(name):
    group = name
    users = ",".join(list(request.form.to_dict())).split(',')
    denyusers = [os.path.basename(name) for name in os.listdir("/var/cld/access/users/") if os.path.isdir(f'/var/cld/access/users/{name}') and name not in users]
    for user in users:
        if user:
            currentgroups = bash(f'/var/cld/bin/cld-getpasswd --user={user} --groups').split(',')
            if group not in currentgroups:
                currentgroups.append(group)
                bash(f'/var/cld/bin/cld-setpasswd --user={user} --groups={vld(",".join(list(filter(None, currentgroups))))}')
    for denyuser in denyusers:
        if denyuser:
            currentgroups = bash(f'/var/cld/bin/cld-getpasswd --user={denyuser} --groups').split(',')
            if group in currentgroups:
                currentgroups = [x for x in currentgroups if x != group]
                bash(f'/var/cld/bin/cld-setpasswd --user={denyuser} --groups={vld(",".join(list(filter(None, currentgroups))))}')
    return Response('Group users saved', status=200, mimetype='text/plain')

@app.route('/admin/groupclouds/<name>', methods=['GET','POST'])
@is_admin
def groupclouds(name):
    group = name
    clouds = [vld(cloud) for cloud in list(request.form.to_dict())]
    print(clouds, flush=True)
    with open(f'/var/cld/access/groups/{group}/clouds', 'w') as f:
        f.write("\n".join(list(filter(None, clouds))))
    return Response('Group clouds saved', status=200, mimetype='text/plain')

@app.route('/admin/grouptype/<name>', methods=['GET','POST'])
@is_admin
def grouptype(name):
    group = name
    grouptype = request.form.get('grouptype', '')
    parsingscript = request.form.get('parsingscript', '')
    group_list_file = f'/var/cld/creds/{vld(group)}_list'
    clouds_file = f'/var/cld/access/groups/{vld(group)}/clouds'
    type_file = f'/var/cld/access/groups/{vld(group)}/type'
    if grouptype == 'on':
        if os.path.exists(group_list_file):
            os.remove(group_list_file)
        if os.path.exists(clouds_file):
            os.remove(clouds_file)
        with open(group_list_file, 'w') as f:
            pass  # touch equivalent
        os.symlink(group_list_file, clouds_file)
        with open(type_file, 'w') as f:
            f.write('1')
        with open(f"/var/cld/access/groups/{vld(group)}/parsingscript", 'w', newline='\n') as f:
            f.write(parsingscript.replace('\r', ''))
    else:
        if os.path.exists(clouds_file):
            os.remove(clouds_file)
        with open(clouds_file, 'w') as f:
            pass  # touch equivalent
        if os.path.exists(group_list_file):
            os.rename(group_list_file, clouds_file)
        with open(type_file, 'w') as f:
            f.write('0')
    return Response('Group type saved', status=200, mimetype='text/plain')

@app.route('/admin/groupfuncs/<name>', methods=['GET','POST'])
@is_admin
def groupfuncs(name):
    group = name
    groupfuncs = request.form.get('groupfuncs', '')
    groupfuncvars = request.form.get('groupfuncvars', '')
    groupfuncterm = request.form.get('groupfuncterm', '')
    groupfuncmount = request.form.get('groupfuncmount', '')
    groupfuncumount = request.form.get('groupfuncumount', '')
    groupfuncdeploy = request.form.get('groupfuncdeploy', '')
    groupfuncdeploynotty = request.form.get('groupfuncdeploynotty', '')
    funcs_file = f'/var/cld/access/groups/{vld(group)}/funcs'
    if groupfuncs == 'on':
        with open(funcs_file, 'w') as f:
            f.write('1')
        for fname, content in [
            ('funcvars', groupfuncvars),
            ('functerm', groupfuncterm),
            ('funcmount', groupfuncmount),
            ('funcumount', groupfuncumount),
            ('funcdeploy', groupfuncdeploy),
            ('funcdeploynotty', groupfuncdeploynotty)
        ]:
            with open(f"/var/cld/access/groups/{vld(group)}/{fname}", 'w', newline='\n') as f:
                f.write(content.replace('\r', ''))
    else:
        with open(funcs_file, 'w') as f:
            f.write('0')
    return Response('Group functions saved', status=200, mimetype='text/plain')

@app.route('/profile')
@logged_in
def profile():
    username = session['username']
    clouds = bash('sudo -u '+vld(username)+' sudo /var/cld/bin/cld --list')
    visiblemodules = uservisiblemodules(username)
    modules = getusermodules(username)
    perms = []
    with open('/var/cld/creds/passwd', 'r') as f:
        for line in f:
            if line.startswith(f'{vld(username)}:'):
                perms = line.strip().split(':')
                break
    return render_template('html/profile.html', username=username, clouds=clouds, perms=perms, visiblemodules=visiblemodules, modules=modules)

@app.route('/profile/usermodules/<name>', methods=['GET','POST'])
@logged_in
def profile_set_visible_modules(name):
    user = session['username']
    modules = list(request.form.to_dict())
    with open(f'/var/cld/access/users/{vld(name)}/showonlymodules', 'w') as f:
        f.write("\n".join(modules))
    return Response('User modules saved', status=200, mimetype='text/plain')

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8080)