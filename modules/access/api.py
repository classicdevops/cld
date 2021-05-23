@app.route('/all/myipinit')
def myip():
  if 'token' in request.args:
    token = re.fullmatch(r'[A-Za-z0-9]+', request.args['token']).string
    output = bash('FROM=API /var/cld/modules/access/bin/cld-activateiptoken '+str(remoteaddr())+' '+token)
    resp = Response(output, status=200, mimetype='text/plain')
    return resp
  else:
    return 403

@app.route('/myvpnget')
def myvpn():
  if 'token' in request.args:
    token = re.fullmatch(r'[A-Za-z0-9]+', request.args['token']).string
    file_path = bash('FROM=API /var/cld/modules/access/bin/cld-activatevpntoken '+token)
    if os.path.exists(file_path) != True:
      return Response('404', status=404, mimetype='text/plain')
    return Response(stream_file(file_path), status=200, mimetype='application/octet-stream')
  else:
    return Response('403', status=403, mimetype='text/plain')