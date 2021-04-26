webmodule["note"] = {}
webmodule["note"]["homename"] = "Note"
webmodule["note"]["desc"] = "Security script storage"
@app.route("/note")
def note_index():
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    userapitoken = apitokenbyuser(user)
    notes = bash('find /var/cld/modules/note/data/ -maxdepth 1 -mindepth 1 -type d | cut -d / -f 7').split('\n')
    return render_template('modules/note/note.html', username=user, notes=notes, cld_domain=cld_domain, userapitoken=userapitoken)

@app.route("/note/<note>/files")
def note_files(note):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    note_file_list = bash('ls /var/cld/modules/note/data/'+note).split('\n')
    note_file_dict = {}
    for note_file in note_file_list:
        note_file_dict[note_file] = open('/var/cld/modules/note/data/'+note+'/'+note_file, 'r').read()
    return Response(json.dumps(note_file_dict), status=200, mimetype='application/json')

@app.route("/note/<note>/<file>")
def note_get_file(note, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.isfile('/var/cld/modules/note/data/'+note+'/'+file):
        return Response(bash('cat /var/cld/modules/note/data/'+note+'/'+file), status=200, mimetype='text/plain')
    else:
        return Response("Note not found", status=404, mimetype='text/plain')

@app.route("/note/delete/<note>/<file>")
def note_delete_file(note, file):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.isfile('/var/cld/modules/note/data/'+note+'/'+file):
        os.remove('/var/cld/modules/note/data/'+note+'/'+file)
        return Response("File: "+file+" deleted", status=200, mimetype='text/plain')
    else:
        return Response("Note not found", status=404, mimetype='text/plain')

@app.route("/note/save/<note>", methods=['POST'])
def note_save(note):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.isdir('/var/cld/modules/note/data/'+note) != True:
        os.makedirs('/var/cld/modules/note/data/'+note, mode = 0o700, exist_ok=True)
    notefiles = dict(request.form)
    for notefile in notefiles:
        open("/var/cld/modules/note/data/"+note+"/"+notefile, "w", newline='\n').write(notefiles[notefile].replace('\r', ''))
    return Response("Note saved", status=200, mimetype='text/plain')

@app.route("/note/delete/<note>")
def note_delete(note):
  if 'username' in session:
    user = session['username']
    checkresult = checkpermswhiteip(cldmodule, 'NOTOOL', user, remoteaddr())
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='application/json')
    if os.path.isdir('/var/cld/modules/note/data/'+note):
        bash('rm -f /var/cld/modules/note/data/'+note+'/* /var/cld/modules/note/data/'+note+'/*/* &>/dev/null ; rmdir /var/cld/modules/note/data/'+note)
        return Response("Note deleted", status=200, mimetype='text/plain')
    else:
        return Response("Note not found", status=404, mimetype='text/plain')