@app.route("/deploy/<deploytype>/<deploy>/<file>")
def deploy_get_file(deploytype, deploy, file):
    checkresult = checkpermswhiteip(cldmodule, "NONE", request.args['token'],  remoteaddr()) 
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    user = userbytoken(checkresult[1])
    user_allowed_deploys = json.loads(bash('sudo -u '+user+' sudo FROM=CLI /var/cld/deploy/bin/cld-deploy --list --json'))
    if deploytype == "templates":
        deploys = user_allowed_deploys[0]['content']
    elif deploytype == "deploys":
        deploys = user_allowed_deploys[1]['content']
    if deploy in deploys:
        return Response(open('/var/cld/deploy/'+deploytype+'/'+deploy+'/'+file).read(), status=200, mimetype='text/plain')
    else:
        return Response(deploytype[:-1].capitalize()+" not found", status=404, mimetype='text/plain')