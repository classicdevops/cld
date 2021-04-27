webmodule["access"] = {}
webmodule["access"]["homename"] = "Access"
webmodule["access"]["desc"] = "Classic firewall"
webmodule["access"]["adminonly"] = True
@app.route("/access")
def access_index():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    file_list = ['/var/cld/modules/access/data/myips', '/var/cld/modules/access/data/enabledips', '/var/cld/modules/access/data/blackips', '/var/cld/modules/access/data/myip_tokens']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    return render_template('modules/access/access.html', username=user, files=files)