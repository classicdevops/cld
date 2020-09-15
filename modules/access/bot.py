
# myip
@bot.message_handler(commands=["myip"])
def cmd_myip(message):
   valid_id = str(message.chat.id)
   valid_id2 = str(message.from_user.id)
   if valid_id in allowgroups() or valid_id2 in allowusers():
     if re.findall(r'[\d]+\.[\d]+\.[\d]+\.[\d]+', message.text):
        myip = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)', message.text).group(1)
        cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/myip_add '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown')
     else:
        myip = 'TOKEN'
        cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/myip_add '+str(message.from_user.id)+' '+str(message.from_user.username)+' '+str(myip), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown', disable_web_page_preview='true')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)

# enableip
@bot.message_handler(commands=["enableip"])
def cmd_enableip(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([\d]+\.[\d]+\.[\d]+\.[\d]+)\s(.+)', message.text):
        enableipargs = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)\s+(.+)', message.text)
        enable_ip = enableipargs.group(1)
        enable_cmnt = enableipargs.group(2)
        cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/enableip_add '+str(enable_ip)+' '+str(enable_cmnt), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="ip address or comment is not defined, please use format:\n`/enableip 1.1.1.1 AccessReason`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)

# blackip
@bot.message_handler(commands=["blackip"])
def cmd_blackip(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([\d]+\.[\d]+\.[\d]+\.[\d]+)\s(.+)', message.text):
        blackipargs = re.search('([\d]+\.[\d]+\.[\d]+\.[\d]+)\s+(.+)', message.text)
        black_ip = blackipargs.group(1)
        black_cmnt = blackipargs.group(2)
        cmdoutput = subprocess.Popen('/var/cld/modules/access/bin/blackip_add '+str(black_ip)+' '+str(black_cmnt), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bot.send_message(message.chat.id, cmdoutput.communicate(), parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="ip address or comment is not defined, please use format:\n`/blackip 1.1.1.1 BlackReason`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)