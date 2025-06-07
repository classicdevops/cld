webmodule["infraconfig"] = {}
webmodule["infraconfig"]["homename"] = "Infra config"
webmodule["infraconfig"]["desc"] = "Manage parsing settings"

@app.route("/infraconfig")
def infraconfig_index():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    os.makedirs('/var/cld/modules/infraconfig/data', mode = 0o700, exist_ok=True)
    bash('''[ -d /var/cld/modules/infraconfig/data/groups ] || mkdir -p /var/cld/modules/infraconfig/data/groups ; [ -d /var/cld/modules/infraconfig/data/instances ] || mkdir -p /var/cld/modules/infraconfig/data/instances''')
    instances_files = path_to_dict('/var/cld/modules/infraconfig/data/instances')
    groups_files = path_to_dict('/var/cld/modules/infraconfig/data/groups')
    configs = {"instances": instances_files, "groups": groups_files}
    cld_instances = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --all').split('\n')
    cld_groups = [os.path.basename(name) for name in os.listdir('/var/cld/access/groups/') if os.path.isdir('/var/cld/access/groups/'+name)]
    return render_template('modules/infraconfig/infraconfig.html', username=user, cld_instances=cld_instances, cld_groups=cld_groups, configs=configs)

