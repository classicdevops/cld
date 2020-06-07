
@bot.message_handler(commands=["getdns"])
def cmd_getdns(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+[A-Za-z0-9.*@-]+)?', message.text):
        dnsargs = re.search('([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+[A-Za-z0-9.*@-]+)?', message.text)
        dnszone = dnsargs.group(1)
        dnscontent = ''
        dnscontent = str(dnsargs.group(2)).replace('None', '')
        cmdoutput = bash('/var/cld/modules/dns/bin/cld-getdns '+str(dnszone)+' '+str(dnscontent))
        bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="DNS zone or DNS content is not defined, please use format:\n`/getdns example.com 1.2.3.4`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)

@bot.message_handler(commands=["setdns"])
def cmd_setdns(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_-]+)', message.text):
        dnsargs = re.search('([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_-]+)', message.text)
        dnstype = dnsargs.group(1)
        dnszone = dnsargs.group(2)
        dnscontent = ''
        dnscontent = str(dnsargs.group(3)).replace('None', '')
        cmdoutput = bash('/var/cld/modules/dns/bin/cld-setdns '+str(dnstype)+' '+str(dnszone)+' '+str(dnscontent))
        bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="DNS type, zone or content is not defined, please use format:\n`/setdns A example.com 1.2.3.4`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)

@bot.message_handler(commands=["deldns"])
def cmd_deldns(message):
   valid_id = str(message.from_user.id)
   if valid_id in allowusers():
     if re.findall(r'([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_-]+)', message.text):
        dnsargs = re.search('(A|AAAA|CNAME|TXT|SRV|LOC|MX|NS|SPF|CERT|DNSKEY|DS|NAPTR|SMIMEA|SSHFP|TLSA|URI|a|aaaa|cname|txt|srv|loc|mx|ns|spf|cert|dnskey|ds|naptr|smimea|sshfp|tlsa|uri)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_-]+)', message.text)
        dnstype = dnsargs.group(1)
        dnszone = dnsargs.group(2)
        dnscontent = ''
        dnscontent = str(dnsargs.group(3)).replace('None', '')
        cmdoutput = bash('/var/cld/modules/dns/bin/cld-deldns '+str(dnstype)+' '+str(dnszone)+' '+str(dnscontent))
        bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
     else:
        bot.send_message(message.chat.id, text="DNS type, zone or content is not defined, please use format:\n`/deldns A example.com 1.2.3.4`", parse_mode='Markdown')
   else:
      myid_answer = "user id is %s, access denied for %s" % (message.from_user.id, message.from_user.username)
      bot.send_message(message.chat.id, myid_answer)