@bot.message_handler(func=lambda message: message.caption == '/upload', content_types=['document'])
def tcloud_get_file(message):
  checkresult = checkperms(cldmodule, "tcloud_get_file", message.from_user.id, message.chat.id, message.from_user.username)
  if checkresult[0] != "granted": return
  user = bash('grep ":'+checkresult[1]+':" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
  answer = "downloadlink:\n`https://"+api_domain+"/api/all/tcloud/"+message.document.file_id+"/"+message.document.file_name+"`"
  return bot.send_message(message.chat.id, answer, parse_mode='Markdown')