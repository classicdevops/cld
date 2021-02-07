@app.route('/myipinit')
def myip():
  if 'token' in request.args:
    token = re.fullmatch(r'[a-z0-9]+', request.args['token']).string
    output = bash('FROM=API /var/cld/modules/access/bin/cld-activateapitemptoken '+str(remoteaddr())+' '+token)
    resp = Response(output, status=200, mimetype='application/json')
    return resp
  else:
    return 403