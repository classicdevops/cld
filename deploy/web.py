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

@app.route("/deploy/<deploytype>/<deploy>")
def deploy_files(deploytype, deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return Response(json.dumps(bash('{ DEPLOY_FILES=$(ls /var/cld/deploy/'+deploytype+'/'+deploy+') ; for CLD_FILE in vars script clouds ; do grep -s "^$CLD_FILE" <<< "$DEPLOY_FILES" ; done ; grep -v "^vars\|^script\|^clouds" <<< "$DEPLOY_FILES" ; }').split('\n')), status=200, mimetype='application/json')

@app.route("/deploy/templates/<template>/<file>")
def deploy_template_file(template, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return Response(bash('cat /var/cld/deploy/templates/'+template+'/'+file), status=200, mimetype='text/plain')

@app.route("/deploy/deploys/<deploy>/<file>")
def deploy_deploy_file(deploy, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return Response(bash('cat /var/cld/deploy/deploys/'+deploy+'/'+file), status=200, mimetype='text/plain')

@app.route("/template/delete/<template>")
def template_delete(template):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/deploy/bin/cld-deploy --list --json'))
    if template in user_allowed_deploys[0]['content']:
        bash('rm -f /var/cld/deploy/templates/'+template+'/* /var/cld/deploy/templates/'+template+'/*/* &>/dev/null ; rmdir /var/cld/deploy/templates/'+template)
        return Response("Template deleted", status=200, mimetype='text/plain')
    else:
        return Response("Template not found", status=404, mimetype='text/plain')

@app.route("/deploy/delete/<deploy>")
def deploy_delete(deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/deploy/bin/cld-deploy --list --json'))
    if deploy in user_allowed_deploys[1]['content']:
        bash('rm -f /var/cld/deploy/deploys/'+deploy+'/* /var/cld/deploy/deploys/'+deploy+'/*/* &>/dev/null ; rmdir /var/cld/deploy/deploys/'+deploy)
        return Response("Deploy deleted", status=200, mimetype='text/plain')
    else:
        return Response("Deploy not found", status=404, mimetype='text/plain')

@app.route("/deploy/save/<deploytype>/<deploy>", methods=['POST'])
def deploy_save(deploytype, deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        deployfiles = dict(request.form)
        for deployfile in deployfiles:
            print(str(deployfiles[deployfile]), flush=True)
        return Response(deploytype[:-1].capitalize()+" saved", status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')