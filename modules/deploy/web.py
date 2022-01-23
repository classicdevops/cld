webmodule["deploy"] = {}
webmodule["deploy"]["homename"] = "Deploy"
webmodule["deploy"]["desc"] = "Classic deploy"
@app.route("/deploy")
def deploy_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    userapitoken = apitokenbyuser(user)
    deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    return render_template('modules/deploy/deploy.html', username=user, deploys=deploys, cld_domain=cld_domain, userapitoken=userapitoken)

@app.route("/deploy/<deploytype>/<deploy>/files")
def deploy_files(deploytype, deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.exists('/var/cld/modules/deploy/'+deploytype+'/'+deploy) != True:
        if deploytype == "templates":
            bash('/var/cld/modules/deploy/bin/cld-template --template='+vld(deploy))
        elif deploytype == "deploys":
            bash('/var/cld/modules/deploy/bin/cld-template --template='+vld(deploy)+' ; /var/cld/modules/deploy/bin/cld-template --template='+vld(deploy)+' --deploy='+vld(deploy))
    user_allowed_deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        deploy_file_list = bash('{ DEPLOY_FILES=$(ls /var/cld/modules/deploy/'+vld(deploytype)+'/'+vld(deploy)+') ; for CLD_FILE in script vars clouds ; do grep -s "^$CLD_FILE" <<< "$DEPLOY_FILES" ; done ; grep -v "^vars\|^script\|^clouds" <<< "$DEPLOY_FILES" ; }').split('\n')
        deploy_file_dict = {}
        for deploy_file in deploy_file_list:
            deploy_file_dict[deploy_file] = open('/var/cld/modules/deploy/'+deploytype+'/'+deploy+'/'+deploy_file, 'r').read()
        return Response(json.dumps(deploy_file_dict), status=200, mimetype='application/json')

@app.route("/deploy/<deploytype>/<deploy>/<file>")
def deploy_get_file(deploytype, deploy, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        return Response(bash('cat /var/cld/modules/deploy/'+vld(deploytype)+'/'+vld(deploy)+'/'+vld(file)), status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')

@app.route("/deploy/delete/<deploytype>/<deploy>/<file>")
def deploy_delete_file(deploytype, deploy, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        os.remove('/var/cld/modules/deploy/'+deploytype+'/'+deploy+'/'+file)
        return Response("File: "+file+" deleted", status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')

@app.route("/deploy/save/<deploytype>/<deploy>", methods=['POST'])
def deploy_save(deploytype, deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        deployfiles = dict(request.form)
        for deployfile in deployfiles:
            open("/var/cld/modules/deploy/"+vld(deploytype)+"/"+vld(deploy)+"/"+vld(deployfile), "w", newline='\n').write(deployfiles[deployfile].replace('\r', ''))
        return Response(deploytype[:-1].capitalize()+" saved", status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')

@app.route("/deploy/delete/<deploytype>/<deploy>")
def deploy_delete(deploytype, deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user_allowed_deploys = json.loads(bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        bash('rm -f /var/cld/modules/deploy/'+vld(deploytype)+'/'+vld(deploy)+'/* /var/cld/modules/deploy/'+vld(deploytype)+'/'+vld(deploy)+'/*/* &>/dev/null ; rmdir /var/cld/modules/deploy/'+vld(deploytype)+'/'+vld(deploy))
        return Response(deploytype[:-1].capitalize()+" deleted", status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')

@app.route("/deploy/action/<deploy>")
def actions(deploy):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'cld-action', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    actions = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-action --deploy='+vld(deploy)).split('\n')
    actions_dict = []
    itter = 0
    for action in actions:
        action_content = bash('sudo -u '+vld(user)+' sudo FROM=CLI /var/cld/modules/deploy/bin/cld-action --deploy='+vld(deploy)+' --action='+vld(action)+'  | ansifilter').split('\n')
        actions_dict.append({})
        actions_dict[itter]["action"] = action
        actions_dict[itter]["clouds"] = action_content[0]
        actions_dict[itter]["tests"] = action_content[1]
        actions_dict[itter]["status"] = action_content[2]
        itter += 1
    return Response(json.dumps(actions_dict), status=200, mimetype='application/json')