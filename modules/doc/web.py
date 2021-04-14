webmodule["doc"] = {}
webmodule["doc"]["homename"] = "Documentation"
webmodule["doc"]["desc"] = "CLD handbook"
@app.route("/doc")
def doc_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return render_template('modules/doc/doc.html')

@app.route("/doc/doc.json")
def doc_spec():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.isfile('/var/cld/modules/doc/data/doc.json') != True:
    	bash('python3 /var/cld/modules/doc/doc.py &>/dev/null')
    return Response(open('/var/cld/modules/doc/data/doc.json', 'r').read(), status=403, mimetype='application/json')