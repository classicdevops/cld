# -*- coding: utf-8 -*-
from flask import Flask
from flask import abort, request
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

app = Flask(__name__)

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return remote_addr

try:
  accesslist = set(line.strip() for line in open('/var/cld/modules/access/data/api_accesslist'))
except:
  pass

try:
  tokenlist = set(line.strip() for line in open('/var/cld/modules/access/data/api_tokenlist'))
except:
  pass

def allowmoduleusers(moduleperm):
  return set(bash('''awk -F ":" '{print $3":"$4}' /var/cld/creds/passwd | grep "'''+moduleperm+'''\|ALL" | cut -d : -f 1 | grep -v "^-" | head -c -1 | tr "\n" ","''').strip().split(','))

def allowutilityusers(utilityperm):
  return set(bash('''awk -F ":" '{print $3":"$5}' /var/cld/creds/passwd | grep "'''+utilityperm+'''\|ALL" | cut -d : -f 1 | grep -v "^-" | head -c -1 | tr "\n" ","''').strip().split(','))

def checkmoduleperms(moduleperm, token):
  token=re.match("[A-z0-9_.-]+", token)[0]
  moduleperm=str(moduleperm)
  if token in allowmoduleusers(moduleperm):
    return "granted"
  else:
    return "denied"

def checkutilityperms(cldutility, token):
  token=re.match("[A-z0-9_.-]+", token)[0]
  cldutility=str(cldutility)
  if token in allowutilityusers(cldutility):
    return "granted"
  else:
    return "denied"

def checkutilitypermswhiteip(cldutility, token, remoteaddr):
  token=re.match("[A-z0-9_.-]+", token)[0]
  cldutility=str(cldutility)
  if token in allowutilityusers(cldutility) and remoteaddr in accesslist:
    return "granted"
  else:
    return "denied"

cldm={}
for apifile in bash("ls /var/cld/modules/*/api.py").strip().split('\n'):
  cldmodule=bash('echo '+apifile+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(apifile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

exec(bash('''
for CLD_FILE in $(find /var/cld/modules/*/bin/ -type f -name 'cld-*')
do
CLD_MODULE=$(cut -d / -f 5 <<< ${CLD_FILE})
CLD_UTIL=$(cut -d / -f 7 <<< ${CLD_FILE})
cat << EOL
@app.route('/${CLD_UTIL}')
def cmd_${CLD_UTIL//-/_}():
    if checkutilitypermswhiteip("${CLD_UTIL}", request.args['token'], remoteaddr()) != "granted": return
    user=bash('grep '+request.args['token']+' /var/cld/creds/passwd | cut -d : -f 1')
    cmd_args = ''
    cmd_args = str(re.match('^[A-z0-9.,@=/ -]+$', request.args['args']).string)
    bg = ''
    try:
      if str(int(request.args['bg'])) == '1': bg = ' &>/dev/null &'
    except:
      pass
    cmdoutput = bash('${CLD_FILE} '+cmd_args+bg)
    resp = Response(cmdoutput, status=200, mimetype='application/json')
    return resp

EOL
done
'''))

@app.route('/test')
def index():
  return remoteaddr()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=50025)
