@bot.message_handler(commands=["myip"])
def cmd_myip(message):
  checkresult = checkperms(cldmodule, "cld-myipbot", message.from_user.id, message.chat.id, message.from_user.username)
  if checkresult[0] != "granted": return
  user = bash('grep ":'+checkresult[1]+':" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
  if re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', message.text):
    myip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', message.text).group(1)
    cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip))
    last_message = bot.send_message(message.chat.id, '`'+cmdoutput+'`', parse_mode='Markdown')
    sleep(10)
    return bot.delete_message(last_message.chat.id, last_message.message_id)
  else:
    myip = 'TOKEN'
    cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip))
    last_message = bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown', disable_web_page_preview='true')
    open("/var/cld/modules/access/data/myip_token_chats", "a").write(cmdoutput.split('=')[1]+"_"+str(last_message.message_id)+"_"+str(message.chat.id)+"\n")
    sleep(10)
    return bot.delete_message(last_message.chat.id, last_message.message_id)


@bot.message_handler(commands=["myvpn"])
def cmd_myvpn(message):
  checkresult = checkperms(cldmodule, "cld-myvpnbot", message.from_user.id, message.chat.id, message.from_user.username)
  if checkresult[0] != "granted": return
  user = bash('grep ":'+checkresult[1]+':" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
  cmd_args=''
  try:
      for arg in message.text.split()[1:]: cmd_args=cmd_args+" "+str(arg)
      cmd_args = str(re.match('^[A-z0-9.,@=/ -]+\$', cmd_args).string)
  except:
      pass
  cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myvpnbot '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+cmd_args)
  last_message = bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown', disable_web_page_preview='true')
  open("/var/cld/modules/access/data/myvpn_token_chats", "a").write(cmdoutput.split('=')[1]+"_"+str(last_message.message_id)+"_"+str(message.chat.id)+"\n")
  sleep(10)
  return bot.delete_message(last_message.chat.id, last_message.message_id)