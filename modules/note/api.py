import hashlib
@app.route("/all/note/<note>/<file>")
def note_get_file(note, file):
    apihash = request.args['hash']
    for line in open('/var/cld/creds/passwd').read().strip().split('\n'):
      token = line.split(':')[2]
      checkhash = hashlib.md5(str(note+file+token).encode('utf-8')).hexdigest()
      if checkhash == apihash:
        user = line.split(':')[0]
        break
    try: user
    except: return Response("404", status=403, mimetype='text/plain')
    checkresult = checkperms(cldmodule, "NONE", token)
    if checkresult[0] != "granted": return Response("403", status=403, mimetype='text/plain')
    user = userbytoken(checkresult[1])
    if os.path.isfile('/var/cld/modules/note/data/'+note+'/'+file):
        return Response(open('/var/cld/modules/note/data/'+note+'/'+file).read(), status=200, mimetype='text/plain')
    else:
        return Response(note.capitalize()+" not found", status=404, mimetype='text/plain')