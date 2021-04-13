@app.route('/all/myipinit')
def myip():
  if 'token' in request.args:
    token = re.fullmatch(r'[a-z0-9]+', request.args['token']).string
    output = bash('FROM=API /var/cld/modules/access/bin/cld-activateapitemptoken '+str(remoteaddr())+' '+token)
    resp = Response(output, status=200, mimetype='text/plain')
    return resp
  else:
    return 403