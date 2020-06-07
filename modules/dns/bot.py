
@bot.message_handler(commands=["getdns"])
def cmd_getdns(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@-]+)', message.text):
        dnsargs = re.search('([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@-]+)', message.text)
        dnszone = dnsargs.group(1)
        dnscontent = dnsargs.group(2)
        cmdoutput = bash('/var/cld/modules/dns/bin/cld-getdns '+str(dnszone)+' '+str(dnscontent))
        bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="DNS zone or DNS content is not defined, please use format:\n`/getdns example.com 1.2.3.4`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)