@bot.message_handler(commands=["getdns"])
def cmd_getdns(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  if re.findall(r'([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+[A-Za-z0-9.*=@-]+)?', message.text):
    dnsargs = re.search('([a-z0-9.*-]+\.[a-z0-9.-]+)(\s+[A-Za-z0-9.*=@-]+)?', message.text)
    dnszone = dnsargs.group(1)
    dnscontent = ''
    dnscontent = str(dnsargs.group(2)).replace('None', '')
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-getdns '+str(dnszone)+' '+str(dnscontent))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="DNS zone or DNS content is not defined, please use format:\n`/getdns example.com 1.2.3.4`", parse_mode='Markdown')

@bot.message_handler(commands=["setdns"])
def cmd_setdns(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  if re.findall(r'([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_ -]+|[A-Za-z0-9.*=@/_ -]+)', message.text):
    dnsargs = re.search('([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*=@/_-]+)(\s+[A-Za-z0-9.*@/_ -]+|\s+[A-Za-z0-9.*=@/_ -]+)?', message.text)
    dnstype = dnsargs.group(1)
    dnszone = dnsargs.group(2)
    dnscontent = ''
    dnscontent = str(dnsargs.group(3)).replace('None', '')
    dnsothers = ''
    try:
      dnsothers = str(dnsargs.group(4)).replace('None', '')
    except:
      pass
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-setdns '+str(dnstype)+' '+str(dnszone)+' '+str(dnscontent)+' '+str(dnsothers))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="DNS type, zone or content is not defined, please use format:\n`/setdns A example.com 1.2.3.4`", parse_mode='Markdown')

@bot.message_handler(commands=["deldns"])
def cmd_deldns(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  if re.findall(r'([a-zA-Z]+)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_-]+)', message.text):
    dnsargs = re.search('(A|AAAA|CNAME|TXT|SRV|LOC|MX|NS|SPF|CERT|DNSKEY|DS|NAPTR|SMIMEA|SSHFP|TLSA|URI|a|aaaa|cname|txt|srv|loc|mx|ns|spf|cert|dnskey|ds|naptr|smimea|sshfp|tlsa|uri)\s+([a-z0-9.*-]+\.[a-z0-9.-]+)\s+([A-Za-z0-9.*@/_=-]+)', message.text)
    dnstype = dnsargs.group(1)
    dnszone = dnsargs.group(2)
    dnscontent = ''
    dnscontent = str(dnsargs.group(3)).replace('None', '')
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-deldns '+str(dnstype)+' '+str(dnszone)+' '+str(dnscontent))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="DNS type, zone or content is not defined, please use format:\n`/deldns A example.com 1.2.3.4`", parse_mode='Markdown')

@bot.message_handler(commands=["getip"])
def cmd_getip(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  if re.findall(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|all)', message.text):
    ipargs = re.search('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}|all)', message.text)
    ipaddr = ipargs.group(1)
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-getip '+str(ipaddr))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="DNS type, zone or content is not defined, please use format:\n`/getip 1.2.3.4`", parse_mode='Markdown')

@bot.message_handler(commands=["whois"])
def cmd_whois(message):
  if re.findall(r'([A-z0-9.-]+\.[A-z]+)', message.text):
    domainargs = re.search('([A-z0-9.-]+\.[A-z]+)', message.text)
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-whois '+str(domainargs.group(1)))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="DNS zone is not defined, please use format:\n`/whois example.com`", parse_mode='Markdown')

@bot.message_handler(commands=["geo"])
def cmd_geo(message):
  if re.findall(r'([A-z0-9.:-]+(\.|\:)[A-z0-9]+)', message.text):
    domainargs = re.search('([A-z0-9.:-]+(\.|\:)[A-z0-9]+)', message.text)
    cmdoutput = bash('/var/cld/modules/dns/bin/cld-geo '+str(domainargs.group(1)))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="IP or DNS zone is not defined, please use format:\n`/geo 1.2.3.4`", parse_mode='Markdown')

@bot.message_handler(commands=["nslookup"])
def cmd_nslookup(message):
  if re.findall(r'([A-z0-9.-]+\.[0-9A-z]+)', message.text):
    domainargs = re.search('([A-z0-9.-]+\.[A-z0-9]+)', message.text)
    cmdoutput = bash('''/usr/bin/nslookup '''+str(domainargs.group(1)+''' 8.8.8.8 | grep -v 'Non-authoritative' | awk '{print "`"$0"`"}' '''))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="IP or DNS zone is not defined, please use format:\n`/nslookup example.com`", parse_mode='Markdown')

@bot.message_handler(commands=["ping"])
def cmd_ping(message):
  if re.findall(r'([A-z0-9.-]+\.[0-9A-z]+)', message.text):
    domainargs = re.search('([A-z0-9.-]+\.[A-z0-9]+)', message.text)
    cmdoutput = bash('''ping '''+str(domainargs.group(1)+''' -c5 | awk '{print "`"$0"`"}' '''))
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')
  else:
    bot.send_message(message.chat.id, text="IP or DNS zone is not defined, please use format:\n`/getwhois example.com`", parse_mode='Markdown')

@bot.message_handler(commands=["getmodule"])
def cmd_getmodule(message):
  if checkmoduleperms(cldmodule, message.chat.id, message.from_user.id, message.from_user.username) != "granted":
    return
  bot.send_message(message.chat.id, cldmodule, parse_mode='Markdown')