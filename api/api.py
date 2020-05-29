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

app = Flask(__name__)
try:
  accesslist = set(line.strip() for line in open('accesslist'))
except:
  pass

def remoteaddr():
  if request.headers.getlist("X-Forwarded-For"):
    remote_addr = request.headers.getlist("X-Forwarded-For")[0]
  else:
    remote_addr = request.remote_addr
  return remote_addr

@app.route('/test')
def index():
  return remoteaddr()

@app.route('/myip')
def myip():
  if 'token' in request.args:
    token = re.fullmatch(r'[a-z0-9]+', request.args['token']).string
    output = subprocess.Popen('/var/cld/bot/bin/activate_token '+str(remoteaddr())+' '+token, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    resp = Response(output, status=200, mimetype='application/json')
    return resp
  else:
    return 403

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=50025)

