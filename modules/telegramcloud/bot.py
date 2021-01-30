@bot.message_handler(content_types=['document'])
def tcloud_get_file(message):
    checkresult = checkperms(cldmodule, "tcloud_get_file", message.from_user.id, message.chat.id, message.from_user.username)
    if checkresult[0] != "granted": return
    user = bash('grep ":'+checkresult[1]+':" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
    cmd_args=''
    try:
        for arg in message.text.split()[1:]: cmd_args=cmd_args+" "+str(arg)
        cmd_args = str(re.match('^[A-z0-9.,@=/ -]+\$', cmd_args).string)
    except:
        pass
    answer = "downloadlink:\n`https://"+api_domain+"/api/tcloud/"+message.document.file_id+"/"+message.document.file_name+"`"
#    cmdoutput = bash('sudo -u '+user+' sudo FROM=BOT ${CLD_FILE} '+cmd_args)
    bot.send_message(message.chat.id, answer, parse_mode='Markdown')