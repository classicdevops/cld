import json, yaml
import subprocess, os
def bash(cmd):
  return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, executable='/bin/bash').communicate()[0].decode('utf8').strip()

initjson = json.loads('''{"openapi":"3.0.0","info":{},"tags":[],"paths":{},"components":{"schemas":{},"examples":{}}}''')

title = 'CLD documentation'
description = open('/var/cld/README.md', 'r').read().replace('\n', '  \n')

initjson['info']['title'] = title
initjson['info']['description'] = description
initjson['info']['x-logo'] = {}
initjson['info']['x-logo']['url'] = '/img/cld_h.svg'
initjson['info']['x-logo']['href'] = '/'
initjson['info']['x-logo']['altText'] = 'ClassicDeploy logo'

modules = bash("find /var/cld/ /var/cld/{cm,deploy} /var/cld/modules/*/ -maxdepth 1 -type d -name 'bin' -o -name 'README.md'").split('\n')

itter = 0
for modulepath in modules:
  module = modulepath.split('/')[-2]
  print('module: '+module)
  print('modulepath: '+modulepath)
  if module == "cld":
    if os.path.isfile(modulepath.replace('/bin', '/')+"CORE.md"):
      module_desc = open(modulepath.replace('/bin', '/')+'CORE.md', 'r').read().replace('\n', '  \n')
  else:
    if os.path.isfile(modulepath.replace('/bin', '/')+"README.md"):
      module_desc = open(modulepath.replace('/bin', '/')+'README.md', 'r').read().replace('\n', '  \n')
    else:
      module_desc = 'CLD third party module'
  initjson['tags'].append({})
  initjson['tags'][itter]['name'] = module
  initjson['tags'][itter]['description'] = module_desc
  itter += 1
  toolpaths = bash("find "+modulepath+" -maxdepth 1 -type f -name 'cld*' | sort").split('\n')
  print(toolpaths)
  if toolpaths != ['']:
    for toolpath in toolpaths:
      try: del tool
      except: pass
      try: del toolinfo
      except: pass
      try: del tool_desc
      except: pass
      try: del tool_args
      except: pass
      try: del tool_usage
      except: pass
      tool = toolpath.split('/')[-1]
      print('tool: '+tool)
      print('toolpath: '+toolpath)
      toolinfo = yaml.load(bash("grep -q '/var/cld/bin/include/cldfuncs' "+toolpath+" && HELPYAML=1 "+toolpath+" --help"))
      try: tool_desc = toolinfo['Description']
      except: pass
      try: tool_args = toolinfo['Arguments']
      except: pass
      try: tool_usage = toolinfo['Usage examples']
      except: pass
      initjson['paths'][tool] = {}
      initjson['paths'][tool]['options'] = {}
      initjson['paths'][tool]['options']['summary'] = tool
      initjson['paths'][tool]['options']['tags'] = [module]
      initjson['paths'][tool]['options']['responses'] = {}
      initjson['paths'][tool]['options']['operationId'] = tool
      initjson['paths'][tool]['options']['description'] = ''
      try: initjson['paths'][tool]['options']['description'] += 'Description: <pre>'+tool_desc+'</pre>'
      except: pass
      try: initjson['paths'][tool]['options']['description'] += 'Arguments: <pre>'+tool_args+'</pre>'
      except: pass
      xitter = 0
      initjson['paths'][tool]['options']['x-codeSamples'] = []
      try:
        for interface in tool_usage:
          initjson['paths'][tool]['options']['x-codeSamples'].append({})
          initjson['paths'][tool]['options']['x-codeSamples'][xitter]['lang'] = interface
          initjson['paths'][tool]['options']['x-codeSamples'][xitter]['source'] = tool_usage[interface]
          xitter += 1
      except:
        pass

if os.path.isdir('/var/cld/modules/doc/data') != True:
  bash('mkdir -p /var/cld/modules/doc/data &>/dev/null')
open('/var/cld/modules/doc/data/doc.json', 'w').write(json.dumps(initjson))