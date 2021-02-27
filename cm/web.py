webmodule["cm"] = {}
webmodule["cm"]["homename"] = "Cloud manager"
webmodule["cm"]["desc"] = "Virtual environment control"
@app.route("/cm")
def cm_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    cld_clouds = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/cm/bin/cld-cmclouds --json'))
    return render_template('modules/cm/cm.html', username=user, cld_clouds=cld_clouds)
