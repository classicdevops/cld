webmodule["cm"] = {}
webmodule["cm"]["homename"] = "Cloud manager"
webmodule["cm"]["desc"] = "Virtual environment control"
@app.route("/cm")
def cm_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTUTILITY', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    return render_template("modules/cm/index.html")