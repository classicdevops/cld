@app.route('/myip')
def myip():
  if 'token' in request.args:
    token = re.fullmatch(r'[a-z0-9]+', request.args['token']).string
    output = bash('/var/cld/modules/access/bin/activate_token '+str(remoteaddr())+' '+token)
    resp = Response(output, status=200, mimetype='application/json')
    return resp
  else:
    return 403

@app.route('/banip')
def banip():
  if remoteaddr() in accesslist and request.args['token'] in tokenlist:
    black_ip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', request.args['ip']).group(1)
    black_cmnt = re.search('([A-z0-9]+)', request.args['comment']).group(1)
    cmdoutput = bash('/var/cld/modules/access/bin/blackip_add '+str(black_ip)+' '+str(black_cmnt))
    resp = Response(cmdoutput, status=200, mimetype='application/json')
    return resp
  else:
    return 403