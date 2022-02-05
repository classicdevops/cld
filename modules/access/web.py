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
    req_files = ['/etc/cron.d/cld_access']
    os.makedirs('/var/cld/modules/access/data', mode = 0o700, exist_ok=True)
    for req_file in req_files:
      if os.path.exists(req_file):
          os.utime(req_file, None)
          os.open('filepath', os.O_CREAT | os.O_WRONLY, 0o600)
      else:
          open(req_file, 'a').close()
    if os.stat("/etc/cron.d/cld_access").st_size == 0:
      open("/etc/cron.d/cld_access", "a").write('#* * * * * root bash -lc /var/cld/modules/access/bin/cld-accesslistdeploy --all --groups=default --allowedgroups=default" &>/dev/null # uncomment this cron to enable access lists deploy\n#* * * * * root bash -lc /var/cld/modules/access/bin/cld-sshkeysdeploy --all --groups=default" &>/dev/null # uncomment this cron to enable SSH keys deploy\n')
    files = {}
    for file in req_files:
      if file != '':
        if os.path.exists(file):
            os.utime(file, None)
        else:
            open(file, 'a').close()
        files[file] = open(file).read()
    bash('''[ -d /var/cld/modules/access/data/groups ] || mkdir -p /var/cld/modules/access/data/groups ; [ -d /var/cld/modules/access/data/instances ] || mkdir -p /var/cld/modules/access/data/instances''')
    instances_files = path_to_dict('/var/cld/modules/access/data/instances')
    groups_files = path_to_dict('/var/cld/modules/access/data/groups')
    configs = {"instances": instances_files, "groups": groups_files}
    cld_instances = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --all').split('\n')
    cld_groups = [os.path.basename(name) for name in os.listdir("/var/cld/access/groups/") if os.path.isdir('/var/cld/access/groups/'+name)]
    examples = [os.path.basename(name) for name in os.listdir("/var/cld/modules/access/examples/") if os.path.isfile('/var/cld/modules/access/examples/'+name)]
    ipfiles = ['/var/cld/modules/access/data/myips', '/var/cld/modules/access/data/enabledips', '/var/cld/modules/access/data/banips']
    ipconfigs = { "name": " Access IP lists", "dirs": [] }
    ipconfigs["dirs"] = [path_to_dict(ipfile) for ipfile in ipfiles]
    defaultfiles = ['/var/cld/creds/protected_ports', '/var/cld/creds/local_nets', '/var/cld/creds/local_nets6']
    defaultsettings = { "name": " Default settings", "dirs": [] }
    defaultsettings["dirs"] = [path_to_dict(defaultfile) for defaultfile in defaultfiles]
    tokenfiles = ['/var/cld/modules/access/data/myip_tokens', '/var/cld/modules/access/data/myip_token_chats', '/var/cld/modules/access/data/myvpn_tokens', '/var/cld/modules/access/data/myvpn_token_chats']
    tokenlists = { "name": " Stored token lists", "dirs": [] }
    tokenlists["dirs"] = [path_to_dict(tokenfile) for tokenfile in tokenfiles]
    tabsets = [ipconfigs, defaultsettings, tokenlists]
    return render_template('modules/access/access.html', username=user, files=files, cld_instances=cld_instances, cld_groups=cld_groups, examples=examples, configs=configs, tabsets=tabsets)

@app.route("/access/example/<example>")
def access_get_file(example):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return Response(open('/var/cld/modules/access/examples/'+vld(example)).read(), status=200, mimetype='text/plain')