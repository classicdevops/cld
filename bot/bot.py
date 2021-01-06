# -*- coding: utf-8 -*-
import telebot
import random
from lxml import html
import requests
import subprocess
import re
import sys
types = telebot.types

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8')

def arg(arg, message):
  return re.search('[A-z0-9.=-]+', message.text.split()[arg])[0]

bot = telebot.TeleBot(bash("grep ACCESS_BOT_TOKEN /var/cld/creds/creds_security_system | cut -d = -f 2").strip())

# Generate password
@bot.message_handler(commands=["passwd"])
def cmd_passwd(message):
    chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
    password = ''
    for c in range(21):
       password += random.choice(chars)
    bot.send_message(message.chat.id, password)

@bot.message_handler(commands=["wazzup"])
def cmd_wazzup(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Вазааап!", callback_data="wazup")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "wazzup?", reply_markup=keyboard)

# System date of bot host with button
@bot.message_handler(commands=["date"])
def cmd_date(message):
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="To know date", callback_data="date")
    keyboard.add(callback_button)
    bot.send_message(message.chat.id, "Do you want to know the date?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    chat_id=call.message.chat.id
    message_id=call.message.message_id
    if call.message:
        if call.data == "date":
            cmdoutput = subprocess.Popen("date", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=cmdoutput.communicate())
        elif call.data == "wazup":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="WAZZZUUUP!")
            bot.send_document(chat_id, 'CgADAgADrAEAAlTmaEtekoBhNWqh5QI')

# getid
@bot.message_handler(commands=["getid"])
def cmd_getid(message):
    message_chat_id = 'null'
    try:
      message_chat_id = str(message.chat.id)
    except:
      pass
    bot.send_message(message.chat.id, 'chat_id: '+message_chat_id+', user_id: '+str(message.from_user.id))

def allowmoduleusers(moduleperm):
  return set(bash('''awk -F ":" '{print $2":"$4}' /var/cld/creds/passwd | grep "'''+moduleperm+'''\|ALL" | cut -d : -f 1 | grep -v "^-" | head -c -1 | tr "\n" ","''').strip().split(','))

def allowmodulegroups(moduleperm):
  return set(bash('''awk -F ":" '{print $2":"$4}' /var/cld/creds/passwd | grep "'''+moduleperm+'''\|ALL" | cut -d : -f 1 | grep "^-" | head -c -1 | tr "\n" ","''').strip().split(','))

def checkmoduleperms(moduleperm, chat_id, user_id, user_name):
  chat_id_str=str(chat_id)
  user_id_str=str(user_id)
  if chat_id_str in allowmodulegroups(moduleperm) or user_id_str in allowmoduleusers(moduleperm):
    return "granted"
  else:
    bot.send_message(chat_id_str, str("user id is "+user_id_str+", access denied for "+user_name))
    return "denied"

cldm={}
for botfile in bash("ls /var/cld/modules/*/bot.py").strip().split('\n'):
  cldmodule=bash('echo '+botfile+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(botfile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

exec(bash('''
for CLD_FILE in $(find /var/cld/modules/*/bin/ -type f -name 'cld-*')
do
CLD_MODULE=$(cut -d / -f 5 <<< ${CLD_FILE})
CLD_UTIL=$(cut -d / -f 7 <<< ${CLD_FILE})
cat << EOL
@bot.message_handler(commands=["${CLD_UTIL/cld-/}"])
def cmd_${CLD_UTIL//-/_}(message):
    if checkmoduleperms("${CLD_MODULE}", message.chat.id, message.from_user.id, message.from_user.username) != "granted": return
    cmd_args=''
    try:
        for arg in message.text.split()[1:]: cmd_args=cmd_args+" "+str(arg)
        cmd_args = str(re.match('^[A-z0-9.,@=/ -]+\$', cmd_args).string)
    except:
        pass
    cmdoutput = bash('${CLD_FILE} '+cmd_args)
    bot.send_message(message.chat.id, cmdoutput, parse_mode='Markdown')

EOL
done
'''))

if __name__ == '__main__':
     bot.polling(none_stop=True)
