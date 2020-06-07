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

for apifile in bash("ls /var/cld/modules/*/api.py").strip().split('\n'):
  exec(open(apifile).read())

@app.route('/test')
def index():
  return remoteaddr()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=50025)

