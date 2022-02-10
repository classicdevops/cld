# -*- coding: utf-8 -*-
import re
import random
from lxml import html
import requests
import subprocess
import sys
import os
import json
import asyncio
from time import sleep
from discord.ext import commands

def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

def vld(cld_variable):
  return re.match('(^[A-z0-9.,@:=/_ -]+?$|^$)', str(cld_variable)).string

discord_bot_token = bash('''grep DISCORD_BOT_TOKEN= /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' ''')

async def bot_bash_stream(cmd, chat):
  message = await chat.send('```\ninitializing\n```')
  if os.path.exists('/var/cld/tmp/dcstream') != True: bash('chattr -i /var/cld ; mkdir -p /var/cld/tmp/dcstream ; chattr +i /var/cld')
  chars = 'abcdefjhgkmnopqrstuvwxyz1234567890'
  COMMAND_ID = ''
  for c in range(7):
    COMMAND_ID += random.choice(chars)
  STREAM_FILE = '/var/cld/tmp/dcstream/cmd_'+COMMAND_ID
  STREAM_DIR = str(os.path.dirname(STREAM_FILE))
  with open('/var/cld/tmp/dcstream/cmd_'+COMMAND_ID, 'a'): os.utime('/var/cld/tmp/dcstream/cmd_'+COMMAND_ID, None)
  subprocess.Popen(cmd+' | tee -a /var/cld/tmp/dcstream/cmd_'+COMMAND_ID+'; touch '+STREAM_FILE+'_done', shell=True, stdout=subprocess.PIPE, universal_newlines=True, executable='/bin/bash')
  MAX_LENGTH=1900
  PREV_FILE="/var/cld/tmp/dcstream/xaaa"+COMMAND_ID
  PREV_FILE_SIZE=0
  STREAM_DONE = 0
  while True:
    if os.path.isfile(STREAM_FILE+'_done'): STREAM_DONE = 1
    STREAM_FILE_SIZE = os.stat(STREAM_FILE).st_size
    if STREAM_FILE_SIZE != 0: 
      bash("cd "+STREAM_DIR+" ; split --line-bytes="+str(MAX_LENGTH)+" --additional-suffix="+COMMAND_ID+" --suffix-length=3 "+STREAM_FILE)
      LAST_FILE = bash("ls "+STREAM_DIR+"/* | grep "+COMMAND_ID+" | tail -1")
      PREV_FILE_CURRENT_SIZE = os.stat(PREV_FILE).st_size
      if LAST_FILE != PREV_FILE:
        if PREV_FILE_CURRENT_SIZE != PREV_FILE_SIZE:
          await message.edit(content=f'```\n{open(PREV_FILE).read()}\n```')
          FILES_LAST_TO_CURRENT = bash('ls /var/cld/tmp/dcstream/x* | grep '+COMMAND_ID+' | grep -A1000 "'+PREV_FILE+'" | tail -n +2').split('\n')
        for SEND_FILE in FILES_LAST_TO_CURRENT:
          message = await chat.send(f'```\n{open(SEND_FILE).read()}\n```')
          PREV_FILE = SEND_FILE
          sleep(2)
        PREV_FILE_SIZE = os.stat(PREV_FILE).st_size
      elif LAST_FILE == PREV_FILE:
        if PREV_FILE_CURRENT_SIZE != PREV_FILE_SIZE:
          PREV_FILE_SIZE = PREV_FILE_CURRENT_SIZE
          await message.edit(content=f'```\n{open(PREV_FILE).read()}\n```')
          sleep(2)
    if STREAM_DONE == 1: break
    sleep(0.1)
  if STREAM_FILE_SIZE == 0:
    await message.edit(content=f'```\nCommand returned null output\n```')
  bash('rm -f /var/cld/tmp/dcstream/*'+COMMAND_ID+'* /var/cld/tmp/dcstream/cmd_'+COMMAND_ID+'_done')
  return print('Command '+cmd+' completed', flush=True)

def allowmodule(cldmodule):
  return set(bash('''grep -v "^#\|^$" /var/cld/creds/passwd | awk -F ":" '{print $2":"$4}' | grep "'''+vld(cldmodule)+'''\|ALL" | grep -v "^:" | cut -d : -f 1 | tr ',' '\n' ''').split('\n'))

def allowutility(cldutility):
  return set(bash('''grep -v "^#\|^$" /var/cld/creds/passwd | awk -F ":" '{print $2":"$5}' | grep "'''+vld(cldutility)+'''\|ALL" | grep -v "^:" | cut -d : -f 1 | tr ',' '\n' ''').split('\n'))

def checkperms(cldmodule, cldutility, user_id, chat_id, server_id):
  user_id_str=str(user_id)
  chat_id_str=str(chat_id)
  if server_id == None:
    botsource = "direct"
  else:
    botsource = "group"
  if user_id_str in allowmodule(cldmodule) or user_id_str in allowutility(cldutility):
    return ["granted", user_id_str, botsource]
  elif chat_id_str in allowmodule(cldmodule) or chat_id_str in allowutility(cldutility):
    return ["granted", chat_id_str, botsource]
  else:
    return ["denied", "DENIED"]

bot = commands.Bot(command_prefix='/')

cldm={}
for botfile in bash("ls /var/cld/modules/*/dcbot.py").split('\n'):
  cldmodule=bash('echo '+vld(botfile)+' | rev | cut -d / -f 2 | rev | tr -d "\n"')
  cldm[cldmodule]=cldmodule
  print(cldmodule)
  exec(open(botfile).read().replace('cldmodule', 'cldm["'+cldmodule+'"]'))

exec(bash('''
for CLD_FILE in $(find /var/cld/bin/ /var/cld/modules/*/bin/ -maxdepth 1 -type f -name 'cld*')
do
CLD_MODULE=$(rev <<< ${CLD_FILE} | cut -d / -f 3 | rev)
CLD_UTIL=$(rev <<< ${CLD_FILE} | cut -d / -f 1 | rev)
cat << EOL
@bot.command(name='${CLD_UTIL/cld-/}')
async def cmd_${CLD_UTIL//[.-]/_}(message, *args):
  try: server_id = message.guild.id
  except: server_id = None
  cmd_args=''
  try: 
    for arg in args: cmd_args=cmd_args+" "+re.match('^[A-z0-9.,@=/:_-]+$', arg).string
  except: pass
  checkresult = checkperms("${CLD_MODULE}", "${CLD_UTIL}", message.author.id, message.channel.id, server_id)
  if checkresult[0] != "granted": return await message.reply(str("user id is "+str(message.author.id)+", access denied for "+str(message.author).replace('#','-')))
  user = bash('grep "[:,]'+checkresult[1]+'[:,]" /var/cld/creds/passwd | cut -d : -f 1 | head -1')
  await bot_bash_stream("sudo -u "+user+" sudo FROM=BOT BOTSOURCE="+checkresult[2]+" "+vld('${CLD_FILE}')+" "+cmd_args, message)

EOL
done
'''))

@bot.command(name='passwd')
async def cmd_passwd(message, *args):
  cmd_args=''
  try:
    for arg in args: cmd_args=cmd_args+" "+re.match('^[A-z0-9.,@=/:_-]+$', arg).string
  except: pass
  passlen = 21
  try: passlen = int(re.findall('[0-9]{1,3}', str(cmd_args))[0])
  except: pass
  chars = 'abcdefjhgkmnopqrstuvwxyzABCDEFJHGKLMNPQRSTUVWXYZ1234567890'
  password = ''
  for c in range(passlen):
    password += random.choice(chars)
  await message.send("`"+password+"`")

@bot.command(name='getid', help='Current identifier information')
async def cmd_getid(message, *args):
    try: server_id = message.guild.id
    except: server_id = None
    await message.reply(f'''```
User:        {message.author}
User id:     {message.author.id}
Channel:     {message.channel}
Channel id:  {message.channel.id}
Server:      {message.guild}
Server id:   {server_id}
```''')

bot.run(discord_bot_token)