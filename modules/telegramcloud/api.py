@app.route('/tcloud/<telegram_file_id>/<file_name>')
def telegramclouddownload(telegram_file_id, file_name):
	tg_file_path = json.loads(requests.get("https://api.telegram.org/bot"+telegram_bot_token+"/getFile?file_id="+telegram_file_id).content)['result']['file_path']
	return requests.get("https://api.telegram.org/file/bot"+telegram_bot_token+"/"+tg_file_path).content, {'Content-Type': 'application/octet-stream'}