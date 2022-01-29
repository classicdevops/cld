@bot.command(name='myip')
async def cmd_myip(message, *args):
  checkresult = checkresult = checkperms(cldmodule, "cld-myipbot", message.author.id, message.channel.id)
  if checkresult[0] != "granted": return await message.reply("user id is "+str(message.author.id)+", access denied for "+str(message.author).replace('#','-'))
  cmd_args=''
  try:
    for arg in args: cmd_args=cmd_args+" "+re.match('^[A-z0-9.,@=/:_-]+$', arg).string
  except: pass
  user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1')
  if re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', cmd_args):
    myip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', cmd_args).group(1)
    cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+str(message.author.id)+' '+str(message.author).replace('#','-')+' '+str(myip))
    await message.send('`'+cmdoutput+'`')
  else:
    myip = 'TOKEN'
    cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myipbot '+str(message.author.id)+' '+str(message.author).replace('#','-')+' '+str(myip))
    await message.send(cmdoutput)

@bot.command(name='myvpn')
async def cmd_myvpn(message, *args):
  checkresult = checkresult = checkperms(cldmodule, "cld-myvpnbot", message.author.id, message.channel.id)
  if checkresult[0] != "granted": return await message.reply("user id is "+str(message.author.id)+", access denied for "+str(message.author).replace('#','-'))
  cmd_args=''
  try:
    for arg in args: cmd_args=cmd_args+" "+re.match('^[A-z0-9.,@=/:_-]+$', arg).string
  except: pass
  user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1')
  cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT /var/cld/modules/access/bin/cld-myvpnbot '+str(message.author.id)+' '+str(message.author).replace('#','')+' '+cmd_args)
  await message.send(cmdoutput)
