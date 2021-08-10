# -*- coding: utf-8 -*-
import telebot
import random
from lxml import html
import requests
import subprocess
import re
import sys
import os
from time import sleep
types = telebot.types

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

def vld(cld_variable):
  return re.match('(^[A-z0-9.,@=/_ -]+?$|^$)', cld_variable).string

def bot_bash_stream(cmd, message):
    openmessage = bot.send_message(message.chat.id, '`initializing`', parse_mode='Markdown', disable_web_page_preview='true')
    if os.path.exists('/var/cld/tmp') != True: bash('chattr -i /var/cld ; mkdir /var/cld/tmp ; chattr +i /var/cld')
    chars = 'abcdefjhgkmnopqrstuvwxyz1234567890'
    cmdid = ''
    for c in range(7):
      cmdid += random.choice(chars)
    prev_cmd_file_size = 0
    with open('/var/cld/tmp/bot_cmd_'+cmdid, 'a'): os.utime('/var/cld/tmp/bot_cmd_'+cmdid, None)
    with subprocess.Popen(cmd+' | tee -a /var/cld/tmp/bot_cmd_'+cmdid+'; touch /var/cld/tmp/bot_cmd_'+cmdid+'_end', shell=True, stdout=subprocess.PIPE, universal_newlines=True, executable='/bin/bash') as p:
      while p.stdout:
        cmd_file_size = os.path.getsize('/var/cld/tmp/bot_cmd_'+cmdid)
        if cmd_file_size != prev_cmd_file_size:
          try: bot.edit_message_text(chat_id=openmessage.chat.id, message_id=openmessage.message_id, text='```'+os.linesep+bash('tail -c 4090 /var/cld/tmp/bot_cmd_'+cmdid)+os.linesep+'```', parse_mode='Markdown')
          except: 
            pass
          sleep(1.9)
        sleep(0.1)
        prev_cmd_file_size = cmd_file_size
        if os.path.exists('/var/cld/tmp/bot_cmd_'+cmdid+'_end'):
          break
    cmd_file_size = os.path.getsize('/var/cld/tmp/bot_cmd_'+cmdid)
    if cmd_file_size != prev_cmd_file_size:
      try: bot.edit_message_text(chat_id=openmessage.chat.id, message_id=openmessage.message_id, text='```'+os.linesep+bash('tail -c 4090 /var/cld/tmp/bot_cmd_'+cmdid)+os.linesep+'```', parse_mode='Markdown')
      except: pass
    elif cmd_file_size == 0:
      try: bot.edit_message_text(chat_id=openmessage.chat.id, message_id=openmessage.message_id, text='`command returned null output`', parse_mode='Markdown')
      except: pass
    bash('rm -f /var/cld/tmp/bot_cmd_'+cmdid+' /var/cld/tmp/bot_cmd_'+cmdid+'_end')
    return print('Command '+cmd+' completed', flush=True)

def arg(arg, message):
  return re.search('[A-z0-9.=-]+', message.text.split()[arg])[0]

telegram_bot_token = bash('''grep TELEGRAM_BOT_TOKEN /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' ''')
bot = telebot.TeleBot(telegram_bot_token)
api_domain = bash('''grep CLD_DOMAIN /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' | head -c -1''').replace('\n', '')

# Generate password
@bot.message_handler(commands=["passwd"])
def cmd_passwd(message):
    passlen = 21
    try:
        print(str(message.text.split()[1:][0]), flush=True)
        passlen = int(re.match('[0-9]{1,3}', str(message.text.split()[1:][0])).string)
    except:
        pass
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    password = ''
    for c in range(passlen):
       password += random.choice(chars)
    return bot.send_message(message.chat.id, password)

@bot.message_handler(commands=["wazzup"])
def cmd_wazzup(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="WAZZZUUUP!", callback_data="wazup")
    keyboard.add(callback_button)
    return bot.send_message(message.chat.id, "wazzup?", reply_markup=keyboard)

@bot.callback_query_handler(lambda query: query.data == "wazup")
def wazzup_callback(query):
    chat_id=query.message.chat.id
    message_id=query.message.message_id
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text="WAZZZUUUP!")
    return bot.send_document(chat_id, 'CgADAgADrAEAAlTmaEtekoBhNWqh5QI')

# getid
@bot.message_handler(commands=["getid"])
def cmd_getid(message):
    message_chat_id = 'null'
    try:
      message_chat_id = str(message.chat.id)
    except:
      pass
    return bot.send_message(message.chat.id, 'chat_id: '+message_chat_id+', user_id: '+str(message.from_user.id))

def allowmodule(cldmodule):
  return set(bash('''awk -F ":" '{print $2":"$4}' /var/cld/creds/passwd | grep "'''+vld(cldmodule)+'''\|ALL" | grep -v "^:" | cut -d : -f 1 | cut -d ',' -f 1''').split('\n'))

def allowutility(cldutility):
  return set(bash('''awk -F ":" '{print $2":"$5}' /var/cld/creds/passwd | grep "'''+vld(cldutility)+'''\|ALL" | grep -v "^:" | cut -d : -f 1 | cut -d ',' -f 1''').split('\n'))

def checkperms(cldmodule, cldutility, user_id, chat_id, user_name):
  user_id_str=str(user_id)
  chat_id_str=str(chat_id)
  if user_id_str in allowmodule(cldmodule) or user_id_str in allowutility(cldutility):
    return ["granted", user_id_str]
  elif chat_id_str in allowmodule(cldmodule) or chat_id_str in allowutility(cldutility):
    return ["granted", chat_id_str]
  else:
    bot.send_message(chat_id_str, str("user id is "+user_id_str+", access denied for "+user_name))
    return ["denied", "DENIED"]

cldm={}
for botfile in bash("ls /var/cld/modules/*/bot.py").split('\n'):
  cldmodule=bash('echo '+vld(botfile)+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(botfile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

exec(bash('''
for CLD_FILE in $(find /var/cld/bin/ /var/cld/modules/*/bin/ /var/cld/cm/bin/ /var/cld/deploy/bin/ -type f -maxdepth 1 -name 'cld*')
do
CLD_MODULE=$(rev <<< ${CLD_FILE} | cut -d / -f 3 | rev)
CLD_UTIL=$(rev <<< ${CLD_FILE} | cut -d / -f 1 | rev)
cat << EOL
@bot.message_handler(commands=["${CLD_UTIL/cld-/}"])
def cmd_${CLD_UTIL//[.-]/_}(message):
    checkresult = checkperms("${CLD_MODULE}", "${CLD_UTIL}", message.from_user.id, message.chat.id, message.from_user.username)
    if checkresult[0] != "granted": return
    user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1 | tr -d "\\n"')
    cmd_args=''
    try:
        for arg in message.text.split()[1:]:
            cmd_args=cmd_args+" "+str(re.match('^[A-z0-9.,@=/:_-]+$', arg).string
    except:
        pass
    print('sudo -u '+user+' sudo FROM=BOT ${CLD_FILE} '+cmd_args, flush=True)
    return bot_bash_stream("sudo -u "+user+" sudo FROM=BOT "+vld('${CLD_FILE}')+" "+cmd_args, message)
    # cmdoutput = bash("sudo -u "+user+" sudo FROM=BOT '+vld("${CLD_FILE}")+' "+cmd_args+" | tr -d '\`' | awk -v F='\`' '{print F\$0F}'")
    # bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')

EOL
done
'''))

bash("/var/cld/modules/doc/bin/cld-tgcmdgen")

if __name__ == '__main__':
     bot.polling(none_stop=True)
