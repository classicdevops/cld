webmodule["infraconfig"] = {}
webmodule["infraconfig"]["homename"] = "Infra config"
webmodule["infraconfig"]["desc"] = "Collect instance configuration"

@app.route("/infraconfig")
def infraconfig_index():
  if 'username' in session:
    if userisadmin(session['username']) != True:
      session.pop('username', None)
      return redirect('/', code=302)
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    cld_instances = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/bin/cld --list --all').split('\n')
    cld_groups = [os.path.basename(name) for name in os.listdir('/var/cld/access/groups/') if os.path.isdir('/var/cld/access/groups/'+name)]
    return render_template('modules/infraconfig/infraconfig.html', username=user, cld_instances=cld_instances, cld_groups=cld_groups)

