def allowzbxgroups():
  return set(bash("grep ALLOW_ZBX_GROUP_IDS /var/cld/creds/creds_security_system | cut -d = -f 2").strip().split(','))

@bot.message_handler(commands=["webcheckadd"])
def cmd_webcheckadd(message):
  checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username)
  if re.findall(r'([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+?[A-Za-z0-9.*:@\/?&= -]+)?', message.text):
    zbxargs = re.search('([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+?[А-яA-Za-z0-9.*:@\/?&= -]+)?', message.text)
    zbxhost = zbxargs.group(1)
    zbxothers = ''
    try:
      zbxothers = str(zbxargs.group(2)).replace('None', '')
    except:
      pass
    print('/var/cld/modules/zabbixcontrol/bin/cld-zbxwebcheck '+str(zbxhost)+' '+str(zbxothers))
    cmdoutput = bash('/var/cld/modules/zabbixcontrol/bin/cld-zbx-web-check-add '+str(zbxhost)+' '+str(zbxothers))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="web host is not defined, please use format:\n`/webcheck example.com -pattern=testword -url=https://examlpe.com/test?test=test`", parse_mode='Markdown')

@bot.message_handler(commands=["webcheckdel"])
def cmd_webcheckdel(message):
  checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username)
  if re.findall(r'([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+?[A-Za-z0-9.*:@\/?&= -]+)?', message.text):
    zbxargs = re.search('([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+?[A-Za-z0-9.*:@\/?&= -]+)?', message.text)
    zbxhost = zbxargs.group(1)
    zbxothers = ''
    try:
      zbxothers = str(zbxargs.group(2)).replace('None', '')
    except:
      pass
    cmdoutput = bash('/var/cld/modules/zabbixcontrol/bin/cld-zbx-web-check-del '+str(zbxhost)+' '+str(zbxothers))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="web host is not defined, please use format:\n`/webcheck example.com -pattern=testword -url=https://examlpe.com/test?test=test`", parse_mode='Markdown')

@bot.message_handler(commands=["webchecklist"])
def cmd_webchecklist(message):
  checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username)
  zbxargs = ''
  try:
    zbxargs = re.search('\/webchecklist\s([A-Za-z0-9:/@#._-]+)', message.text).group(1)
  except:
    pass
  print('/var/cld/modules/zabbixcontrol/bin/cld-zbx-web-check-list '+str(zbxargs))
  cmdoutput = bash('/var/cld/modules/zabbixcontrol/bin/cld-zbx-web-check-list '+str(zbxargs))
  bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')