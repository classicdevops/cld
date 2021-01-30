# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort, request
import requests
from flask import g
from flask import Response
import json
import re
import subprocess
import random
import datetime
from urllib.request import urlopen

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8')

telegram_bot_token = bash("grep ACCESS_BOT_TOKEN /var/cld/creds/creds_security_system | cut -d = -f 2").replace('\n', '')

app = Flask(__name__)

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return re.match("[A-z0-9.:]+", remote_addr)[0]

def accesslist():
  return bash("cat /var/cld/modules/access/data/myips /var/cld/modules/access/data/enabledips | cut -d _ -f 1 | uniq").split('\n')

try:
  tokenlist = set(line.strip() for line in open('/var/cld/modules/access/data/api_tokenlist'))
except:
  pass

def allowmoduleusers(cldmodule):
  return set(bash('''awk -F ":" '{print $3":"$4}' /var/cld/creds/passwd | grep "'''+cldmodule+'''\|ALL" | cut -d : -f 1 | head -c -1 | tr "\n" ","''').strip().split(','))

def allowutilityusers(cldutility):
  return set(bash('''awk -F ":" '{print $3":"$5}' /var/cld/creds/passwd | grep "'''+cldutility+'''\|ALL" | cut -d : -f 1 | head -c -1 | tr "\n" ","''').strip().split(','))

def checkperms(cldmodule, cldutility, token):
  token=re.match("[A-z0-9_.-]+", token)[0]
  cldmodule=str(cldmodule)
  cldutility=str(cldutility)
  if token in allowmoduleusers(cldmodule) or token in allowutilityusers(cldutility):
    return ["granted", token]
  else:
    return ["denied", "DENIED"]

def checkpermswhiteip(cldmodule, cldutility, token, remoteaddr):
  token=re.match("[A-z0-9_.-]+", token)[0]
  cldmodule=str(cldmodule)
  cldutility=str(cldutility)
  if token in allowmoduleusers(cldmodule) and remoteaddr in accesslist():
    return ["granted", token]
  elif token in allowutilityusers(cldutility) and remoteaddr in accesslist():
    return ["granted", token]
  else:
    return ["denied", "DENIED"]

cldm={}
for apifile in bash("ls /var/cld/modules/*/api.py").strip().split('\n'):
  cldmodule=bash('echo '+apifile+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(apifile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

exec(bash('''
for CLD_FILE in $(find /var/cld/modules/*/bin/ /var/cld/cm/bin/ /var/cld/deploy/bin/ -type f -name 'cld-*')
do
CLD_MODULE=$(rev <<< ${CLD_FILE} | cut -d / -f 3 | rev)
CLD_UTIL=$(rev <<< ${CLD_FILE} | cut -d / -f 1 | rev)
cat << EOL
@app.route('/${CLD_UTIL/cld-/}')
def cmd_${CLD_UTIL//-/_}():
    checkresult = checkpermswhiteip("${CLD_MODULE}", "${CLD_UTIL}", request.args['token'], remoteaddr()) 
    if checkresult[0] != "granted":
      return Response("403", status=403, mimetype='application/json')
    user = bash('grep ":'+checkresult[1]+':" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
    cmd_args = ''
    try:
        cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    except:
        pass
    bg = ''
    try:
      if str(int(request.args['bg'])) == '1': bg = ' &>/dev/null &'
    except:
      pass
    print('sudo -u '+user+' sudo FROM=API ${CLD_FILE} '+cmd_args+bg, flush=True)
    cmdoutput = bash('sudo -u '+user+' sudo FROM=API ${CLD_FILE} '+cmd_args+bg)
    resp = Response(cmdoutput, status=200, mimetype='application/json')
    return resp

EOL
done
'''))

@app.route('/test')
def index():
  return remoteaddr()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8081)
