# -*- coding: utf-8 -*-
from flask import Flask, abort, request, render_template, Response
import json
import re
import subprocess
import random
import os
import shutil
from glob import glob
from pathlib import Path

def bash(cmd):
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

def customattr(s, n, v):
    class a(type(s)):
        def ttr(self, n, v):
            setattr(self, n, v)
            return self
    return a(s).ttr(n, v)

def bashapi(cmd):
    initproc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash')
    return customattr(initproc.communicate()[0].decode('utf8').strip(), 'status', initproc.returncode)

def vld(cld_variable):
    return re.match('(^[A-z0-9.,@:=/_ -]+?$|^$)', str(cld_variable)).string

# Check for ansifilter using Python
ansifilter_path = shutil.which('ansifilter')
if ansifilter_path:
    outputinterpreter = ansifilter_path
    ansifiltercheck = "0"
else:
    outputinterpreter = shutil.which('cat') or '/bin/cat'
    ansifiltercheck = "1"
    print("ansifilter IS NOT INSTALLED IN THE SYSTEM - API OUTPUT WILL NOT FILTERED - https://github.com/andre-simon/ansifilter")

def stream_file(filepath, chunksize=8192):
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break

def bashstream(cmd, format="plain"):
    addopentag = ""
    addclosetag = ""
    outputargs = ""
    if format == "html" and ansifiltercheck == "0":
        outputargs = " -Hf"
        addopentag = "<pre>"
        addclosetag = "</pre>"
    elif format == "plain" and ansifiltercheck == "0":
        outputargs = " -Tf"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash')
    yield ''.join(addopentag)
    for line in process.stdout:
        yield ''.join(bash("echo -e $(cat << 'EOHTML' | "+outputinterpreter+outputargs+os.linesep+line.decode('utf8')+os.linesep+"EOHTML"+os.linesep+")")+'\n')
    yield ''.join(addclosetag)

def remoteaddr():
    if request.headers.getlist("X-Forwarded-For"):
        remote_addr = request.headers.getlist("X-Forwarded-For")[0]
    else:
        remote_addr = request.remote_addr
    return re.match("[A-z0-9.:]+", remote_addr)[0]

def accesslist():
    try:
        with open('/var/cld/api/accesslist', 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

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

def checkperms(cldmodule, cldutility, token):
    token = re.match("[A-z0-9_.-]+", token)[0]
    cldmodule = str(cldmodule)
    cldutility = str(cldutility)
    if token in allowmoduleusers(cldmodule) or token in allowutilityusers(cldutility):
        return ["granted", token]
    return ["denied", "DENIED"]

def checkpermswhiteip(cldmodule, cldutility, token, remoteaddr):
    token = re.match("[A-z0-9_.-]+", token)[0]
    cldmodule = str(cldmodule)
    cldutility = str(cldutility)
    if token in allowmoduleusers(cldmodule) and remoteaddr in accesslist():
        return ["granted", token]
    elif token in allowutilityusers(cldutility) and remoteaddr in accesslist():
        return ["granted", token]
    return ["denied", "DENIED"]

def userbytoken(token):
    try:
        with open('/var/cld/creds/passwd', 'r') as f:
            for line in f:
                fields = line.strip().split(':')
                if len(fields) >= 3 and fields[2] == vld(token):
                    return fields[0]
    except FileNotFoundError:
        pass
    return ''

# Read creds file using Python
cld_domain = ''
telegram_bot_token = ''
creds_file = '/var/cld/creds/creds'
if os.path.exists(creds_file):
    with open(creds_file, 'r') as f:
        for line in f:
            if line.startswith('CLD_DOMAIN='):
                cld_domain = line.split('=', 1)[1].strip().strip('"')
            elif line.startswith('TELEGRAM_BOT_TOKEN='):
                telegram_bot_token = line.split('=', 1)[1].strip().strip('"')

template_dir = '/var/cld/api'
app = Flask(__name__, template_folder=template_dir)

# Create symlinks for module API templates using Python
modules_dir = Path('/var/cld/api/modules')
if modules_dir.exists():
    shutil.rmtree(modules_dir)
modules_dir.mkdir(parents=True, exist_ok=True)
for web_template_path in Path('/var/cld/modules').glob('*/api'):
    web_module = web_template_path.parent.name
    target = modules_dir / web_module
    os.symlink(web_template_path, target)

# Load module API files using Python
cldm = {}
for apifile in Path('/var/cld/modules').glob('*/api.py'):
    cldmodule = apifile.parent.name
    cldm[cldmodule] = cldmodule
    print(cldmodule)
    with open(apifile, 'r') as f:
        code = f.read().replace('cldmodule', f'cldm["{cldmodule}"]')
        exec(code)

# Dynamic endpoint generation for cld tools using Python
from pathlib import Path

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

@app.route('/<cldutility>')
def cmd_tool(cldutility):
    # Reconstruct full utility name with 'cld-' prefix if needed
    cld_util = f'cld-{cldutility}' if not cldutility.startswith('cld-') else cldutility
    # Sanitize cldutility
    cld_util = str(re.match('^[A-z0-9.,@=/_ -]+', cld_util)[0])
    # Determine cldfile
    cldfile = CLD_UTILITIES.get(cld_util, '')
    # Check if file exists
    if not cldfile or not Path(cldfile).is_file():
        return Response('File not exist', status=403, mimetype='text/plain')
    # Get module name
    cldmodule = Path(cldfile).parent.parent.name if Path(cldfile).parent.name == 'bin' and Path(cldfile).parent.parent.parent == Path('/var/cld/modules') else ''
    # Check permissions using token
    token = request.args.get('token', '')
    checkresult = checkpermswhiteip(cldmodule, cld_util, token, remoteaddr())
    if checkresult[0] != "granted":
        return Response("403", status=403, mimetype='application/json')
    # Get user from token
    user = userbytoken(token)
    # Handle output format
    output = 'plain'
    try:
        output = str(re.match('^[a-z]+$', request.args['output']).string)
    except:
        pass
    # Sanitize command arguments
    cmd_args = ''
    try:
        cmd_args = str(re.match('^[A-z0-9.,@=/: -]+$', request.args['args']).string)
    except:
        pass
    # Handle Telegram output
    tgout = ''
    try:
        tgout = f' | /var/cld/modules/telegramcloud/bin/cld-tcloud-stream --chatid={vld(request.args["tgout"])}'
    except:
        pass
    # Handle background execution
    bg = ''
    try:
        if str(int(request.args['bg'])) == '1':
            bg = ' &>/dev/null &'
    except:
        pass
    # Handle execution mode
    mode = 'stream'
    try:
        mode = str(re.match('^[a-z]+$', request.args['mode']).string)
    except:
        pass
    # Execute command
    print(f'sudo -u {user} sudo FROM=API {cldfile} {cmd_args}{bg}', flush=True)
    if mode == "track":
        cmdoutput = bashapi(f'sudo -u {user} sudo FROM=API {vld(cldfile)} {cmd_args}{tgout}{bg}')
        respstatus = 200 if cmdoutput.status == 0 else 500
        return Response(cmdoutput, status=respstatus, mimetype='text/plain')
    else:
        return Response(bashstream(f'sudo -u {user} sudo FROM=API {vld(cldfile)} {cmd_args}{tgout}{bg}', output), status=200, mimetype=f'text/{output}')

@app.route('/all/ip')
def index():
    return remoteaddr()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8085)