webmodule["filemanager"] = {}
webmodule["filemanager"]["homename"] = "Filemanager"
webmodule["filemanager"]["desc"] = "Classic file manager"
@app.route("/filemanager")
def filemanager_index():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    try: currentdir = request.args['dir']
    except: currentdir = "/var/cld/modules/"
    files = [f for f in os.listdir(currentdir) if os.path.isfile(f)]
    dirs = [d for d in os.listdir(currentdir) if os.path.isdir(d)]
    return render_template('modules/filemanager/filemanager.html', username=user, currentdir=currentdir, files=files, dirs=dirs)

@app.route("/filemanager/getfiles", methods=['POST'])
def filemanager_getfiles():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    currentdir = request.form["currentdir"]
    files = [f for f in os.listdir(currentdir) if os.path.isfile(currentdir+f)]
    files.sort()
    return Response(json.dumps(files), status=200, mimetype='application/json')

@app.route("/filemanager/getdirs", methods=['POST'])
def filemanager_getdirs():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    print(dict(request.form), flush=True)
    currentdir = request.form["currentdir"]
    dirs = [d for d in os.listdir(currentdir) if os.path.isdir(currentdir+d)]
    dirs.sort()
    return Response(json.dumps(dirs), status=200, mimetype='application/json')

@app.route("/filemanager/getfile", methods=['POST'])
def filemanager_getfile():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    file = request.form["file"]
    content = open(file, 'r').read()
    filedict = {"file": file, "content": content}
    return Response(json.dumps(filedict), status=200, mimetype='application/json')
