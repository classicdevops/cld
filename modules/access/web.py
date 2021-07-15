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
    file_list = bash('find /var/cld/modules/access/data -maxdepth 2 -type f | grep -v ovpn | sort').split('\n') + ['/var/cld/creds/protected_ports', '/var/cld/creds/local_nets']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    return render_template('modules/access/access.html', username=user, files=files)