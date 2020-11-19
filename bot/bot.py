# -*- coding: utf-8 -*-
import telebot
import random
from lxml import html
import requests
import subprocess
import re
types = telebot.types

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8')

bot = telebot.TeleBot(bash("grep ACCESS_BOT_TOKEN /var/cld/creds/creds_security_system | cut -d = -f 2").strip())

def allowusers():
  return set(bash("grep ALLOW_USER_IDS /var/cld/creds/creds_security_system | cut -d = -f 2").strip().split(','))

def allowgroups():
  return set(bash("grep ALLOW_GROUP_IDS /var/cld/creds/creds_security_system | cut -d = -f 2").strip().split(','))

# Generate password
@bot.message_handler(commands=["passwd"])
def cmd_passwd(message):
    chars = 'abcdefjhigkmnopqrstuvwxyzABCDEFJHGKLMNOPQRSTUVWXYZ1234567890'
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

cldm={}
for botfile in bash("ls /var/cld/modules/*/bot.py").strip().split('\n'):
  cldmodule=bash('echo '+botfile+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(botfile).read().replace('cldmodule', 'cldm['+cldmodule+']'))

if __name__ == '__main__':
     bot.polling(none_stop=True)
