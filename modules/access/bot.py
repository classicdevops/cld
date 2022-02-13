@bot.message_handler(commands=["myip"])
def cmd_myip(message):
  checkresult = checkperms(cldmodule, "cld-myipbot", message.from_user.id, message.chat.id, message.from_user.username)
  if checkresult[0] != "granted": return
  user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
  if re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', message.text):
    myip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', message.text).group(1)
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+vld(message.from_user.id)+' '+vld(message.from_user.username)+' '+vld(myip))
    last_message = bot.send_message(message.chat.id, '`'+cmdoutput+'`', parse_mode='Markdown')
    # sleep(10)
    # return bot.delete_message(last_message.chat.id, last_message.message_id)
  elif re.findall(r'(-h|--help)$', message.text):
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot -h')
    return bot.send_message(message.chat.id, '```\n'+cmdoutput+'\n```', parse_mode='Markdown')
  else:
    myip = 'TOKEN'
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+vld(message.from_user.id)+' '+vld(message.from_user.username)+' '+vld(myip))
    last_message = bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown', disable_web_page_preview='true')
    return open("/var/cld/modules/access/data/myip_token_chats", "a").write(cmdoutput.split('=')[1]+"_"+vld(last_message.message_id)+"_"+vld(message.chat.id)+"\n")
    # sleep(10)
    # return bot.delete_message(last_message.chat.id, last_message.message_id)


@bot.message_handler(commands=["myvpn"])
def cmd_myvpn(message):
  checkresult = checkperms(cldmodule, "cld-myvpnbot", message.from_user.id, message.chat.id, message.from_user.username)
  if checkresult[0] != "granted": return
  user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
  cmd_args=''
  try:
      for arg in message.text.split()[1:]: cmd_args=cmd_args+" "+vld(arg)
      cmd_args = vld(re.match('^[A-z0-9.,@=/ -]+\$', cmd_args).string)
  except:
      pass
  if re.findall(r'(-h|--help)$', message.text):
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myvpnbot -h')
    return bot.send_message(message.chat.id, '```\n'+cmdoutput+'\n```', parse_mode='Markdown')
  else:
    cmdoutput = bash('sudo -u '+vld(user)+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myvpnbot '+vld(message.from_user.id)+' '+vld(message.from_user.username)+' '+cmd_args)
    last_message = bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown', disable_web_page_preview='true')
    return open("/var/cld/modules/access/data/myvpn_token_chats", "a").write(cmdoutput.split('=')[1]+"_"+vld(last_message.message_id)+"_"+vld(message.chat.id)+"\n")
  # sleep(10)
  # return bot.delete_message(last_message.chat.id, last_message.message_id)