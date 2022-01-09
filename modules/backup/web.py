webmodule["backup"] = {}
webmodule["backup"]["homename"] = "Backup"
webmodule["backup"]["desc"] = "Classic backup"
@app.route("/backup")
def backup_index():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    file_list = bash('find /var/cld/modules/backup/data -type f | sort').split('\n') + ['/etc/cron.d/cld-backup']
    files = {}
    for file in file_list:
      if os.path.exists(file) != True:
        bash('touch '+vld(file))
      files[file] = open(file).read()
    if os.stat("/etc/cron.d/cld-backup").st_size == 0:
      open("/etc/cron.d/cld-backup", "a").write('#0 0 * * * root bash -lc "/var/cld/modules/backup/bin/cld-backup -a" &>/dev/null')
    if os.stat("/var/cld/modules/backup/data/servers").st_size == 0:
      open("/var/cld/modules/backup/data/servers", "a").write('#backup1.example.com_1.2.3.4_22_root,/backup')
    cld_instances = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --all').split('\n')
    cld_groups = [os.path.basename(name) for name in os.listdir("/var/cld/access/groups/") if os.path.isdir('/var/cld/access/groups/'+name)]
    methods = [os.path.basename(name) for name in os.listdir("/var/cld/modules/backup/methods/") if os.path.isdir('/var/cld/modules/backup/methods/'+name)]
    return render_template('modules/backup/backup.html', username=user, files=files, cld_instances=cld_instances, cld_groups=cld_groups, methods=methods)

@app.route("/backup/method/<method>/example")
def backup_get_file(method):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return Response(open('/var/cld/modules/backup/methods/'+vld(method)+'/example').read(), status=200, mimetype='text/plain')