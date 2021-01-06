@bot.message_handler(commands=["myip"])
def cmd_myip(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  if re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', message.text):
    myip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', message.text).group(1)
    cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/myip '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown')
  else:
    myip = 'TOKEN'
    cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/myip '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown', disable_web_page_preview='true')