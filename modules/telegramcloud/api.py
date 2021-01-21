@app.route('/tcloud/<telegram_file_id>/<file_name>')
def telegramclouddownload(telegram_file_id, file_name):
	tg_file_path = json.loads(request.get("https://api.telegram.org/bot"+telegram_bot_token+"/getFile?file_id="+telegram_file_id).content)['result']['file_path']
	return request.get("https://api.telegram.org/file/bot"+tgtoken+"/"+tg_file_path).content