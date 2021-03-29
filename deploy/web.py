webmodule["deploy"] = {}
webmodule["deploy"]["homename"] = "Deploy"
webmodule["deploy"]["desc"] = "Classic deploy"
@app.route("/deploy")
def deploy_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    deploys = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/deploy/bin/cld-deploy --list --json'))
    return render_template('modules/deploy/deploy.html', username=user, deploys=deploys)
