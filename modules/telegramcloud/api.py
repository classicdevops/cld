@app.route('/tcloud/<telegram_file_id>/<file_name>')
@app.route('/all/tcloud/<telegram_file_id>/<file_name>')
def telegramclouddownload(telegram_file_id, file_name):
	try:
		tg_file_path = json.loads(requests.get("https://api.telegram.org/bot"+telegram_bot_token+"/getFile?file_id="+telegram_file_id).content)['result']['file_path']
	except:
		return requests.get("https://api.telegram.org/bot"+telegram_bot_token+"/getFile?file_id="+telegram_file_id).content
	return requests.get("https://api.telegram.org/file/bot"+telegram_bot_token+"/"+tg_file_path).content, {'Content-Type': 'application/octet-stream'}

@app.route('/cldcloud/<filename>')
@app.route('/all/cldcloud/<filename>')
def cldclouddownload(filename):
    if os.path.exists('/var/cld/modules/telegramcloud/data/all/'+str(filename)) != True:
      return Response('404', status=404, mimetype='text/plain')
    return Response(stream_file('/var/cld/modules/telegramcloud/data/all/'+str(filename)), status=200, mimetype='application/octet-stream')
