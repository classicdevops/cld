# Introduction
CLD is a system for differentiating access to servers and scripts with the ability to quick and unify develop custom modules and automation tools based on this functionality.
This project does not set itself the goal of replacing any existing automation tool or CI/CD/deployment/etc, to the contrary, it is designed to combine everything in one centralized self-documenting place, with secure, transparent and logged access to any server and tool, simultaneously through several available user interfaces.

The main components of the system are bash-based utilities, API, chat bots and web interface are just additional data validators and access rights for broadcasting to these bash scripts.
To access any tool, several factor validation operates for the user, at the application/web server and/or operating system level (sudoers file generated based on the CLD access permissions matrix), so any new module and script can be shared for execution for certain users via any interface (CLI, API, Chat bot, Web), excluding direct access to their content as well as to the entire application directory.

<details open>
<summary>Show animation</summary>

![cld_intro](https://classicdeploy.com/gif/cld_intro.gif)
</details>

# Support policy

Please do not ask your questions in github issues. Such format is not suitable for storing FAQ. 
Depending on the type of your question go to **ServerFault** or **StackOverflow** and please ask it there:
1) Question about **installation/configuration/using/tweaking/etc** ask it on **[ServerFault](https://serverfault.com/questions/ask)**
2) Question about some kind of **development** tool/modules/integration ask it on **[StackOverflow](https://stackoverflow.com/questions/ask)**

Tag your question with **`cld`** and **`classicdeploy`** tags (both at once).

We are continuously parsing full list of questions by these tags and will answer as soon as possible. Make your experience available for other users!

[GitHub](https://github.com/classicdeploy/cld/issues) issues are for confirmed bugs/feature requests now. If you have feature idea - please describe it from user experience point of view. Describe how'd you gonna to configure CLD for desired result.

# Terms

## CLD server
Server based on OS Linux with installed copy of CLD `Open source` or CLD `Basic`/`Business`/`Premium`/`Enterprise` software

## Instance
Linux-based server added to the CLD group as a string by the default delimeter '\_' `example.example_1.2.3.4_22_user`, the delimeter can be configured for individual groups with appropriate changes to the supported custom functions

## User
PAM user on the CLD server created through the `cld-useradd` utility, file-related to cld (`/var/cld/creds/passwd`, `/var/cld/access/users/${CLD_USER}/`)
  Regardless of the role, it can contain:
- list of available groups `/var/cld/access/users/${CLD_USER}/groups`
- individual list of instances `/var/cld/access/users/${CLD_USER}/clouds` (optional)

## User role
Roles:
- admin - full access to modules and all tools, the role is defined in the access matrix by the presence of the ALL pattern in columns 4 (modules) and 5 (tools) (userexample:::ALL:ALL)
- user - configurable access to modules and individual tools (userexample:::dns,doc,note:cld,cldmount,cld-modules)
The role depends on the access matrix /var/cld/creds/passwd

## Group
CLD Instance Group
Contains
- list of instances `/var/cld/access/groups/${CLD_GROUP}/clouds`
- specifying the type `/var/cld/access/groups/${CLD_GROUP}/type` - optional, default 0 `static`, 1 is `parsing` type
- switch of used functions for instances of `/var/cld/access/groups/${CLD_GROUP}/funcs` - optional, default 0 (functions from the framework)
- custom functions `/var/cld/access/groups/${CLD_GROUP}/func *` (body of custom function in each file)

## Group type
- static, set as type 0 in the file - default value
Contains a static list of instances
- parsing, specified as type 1 in the file
Has a generated list of instances by the script in the file `/var/cld/access/groups/${CLD_GROUP}/parsingscript`

## Group functions
Functions of the main actions when working with an instance:
- definition of variables based on parsing the instance string (`hostname`, ` ip`, `port`, ` user`) - by default, custom groups can have any set of variables used later by other functions
- connecting to the terminal of the instance via SSH
- mounting the instance file system to the user directory on the CLD server
- unmounting the file system of the instance
- deploy with forced tty - similar function to the terminal, has a timeout for execution, we accept input for execution on the instance, the exit command is required at the end of the input
- deploy without forced tty - accepts input for execution on an instance, has a timeout for execution

The default functions are defined in the main framework library `/var/cld/bin/include/cldfuncs`

### Group custom functions
Activation of custom functions is specified in the file `/var/cld/access/groups/${CLD_GROUP}/funcs`
- default, in the job file as type 0 - default value
- custom, specified as type 1 in the file

List of custom function files:
- `/var/cld/access/groups/${CLD_GROUP}/funcvars`
- `/var/cld/access/groups/${CLD_GROUP}/functerm`
- `/var/cld/access/groups/${CLD_GROUP}/funcmount`
- `/var/cld/access/groups/${CLD_GROUP}/funcumount`
- `/var/cld/access/groups/${CLD_GROUP}/funcdeploy`
- `/var/cld/access/groups/${CLD_GROUP}/funcdeploynotty`

## Module
Module of additional CLD functionality, modules are located along the path `/var/cld/modules/`, the module may contain:
- tools `bin/cld-*`
- custom methods of the interfaces `./{api,bot,web}.py`
- custom WEB interface files `./web/${module}.html`, `./web/content/somefile.{css,js,svg}` and so on
- documentation file `./README.md`
- data of custom modules is recommended to be stored in the directory `./data`

A module with demo data/scripts can be created in the web interface using the `Create module` item or with the interactive CLI command `cld-createmodule`

## Tool/Script
CLI tool - is a script of the main/additional or custom module, named `cld-${TOOL}`
The script is also translated for use through the rest of the interfaces available in the CLD.
Detailed information on the available scripts included in the modules "from the box" is available at https://classicdeploy.com/documentation

## Interface
CLD interfaces are methods of using tools or any additional functionality
CLD standard interfaces:
- CLI - the main working interface, the use of the interface is available through the shell Linux console, the connection is made via SSH, it is also possible to use it via a web terminal as part of the WEB interface
- API - interface for accessing non-interactive scripts, access to scripts is validated by access lists and the user's personal token, additional arguments are translated as is, an example of use is `curl -s" https://yourcld.server.com/api/modules?token=y0urUserT0keN&args=-json"`, endpoints like `/api/all/` do not have validation by access lists, for example, they are used in `cld-myip`
- BOT - an interface in the chat bot format for accessing non-interactive scripts, convenient for using when managing DNS, access lists, and so on, an example of use is `/setdns a subdomain.example.com 1.2.3.4`, at the moment only `Telegram` bots supported, `Discord`, `Mattermost` and `Slack` bot interfaces under developing
- WEB - interface for access to any, including interactive scripts (using a web terminal), as well as to additional methods of system management, access is validated by access ip lists and by PAM for CLD users, the interface is available at the address - `https://yourcld.server.com/`

## Framework
As per definition from wikipedia
`Framework - a software platform that defines the structure of a software system; software that facilitates the development and integration of different components of a large software project.`
The project is a kind of access and automation framework.
To ensure the standard structure of the tools is used, the main bash library `/var/cld/bin/include/cldfuncs`, connected in all the tools "from the box", through the functions of this library, help unification is organized and, accordingly, general autodocumentation using the doc module for generating json and rendering via Redoc, as well as various auxiliary functions, access control, security, etc.


# Centralized access system
The basis of the project is a centralized system of SSH access based on PAM:
- all CLD users work according to the internal access matrix and have customizable permissions, they can be assigned personal telegram account id, as well as API token
- each user is authorized on the server to his PAM account
- access to allowed servers is carried out using a single private SSH key or password
- the list of servers allowed for connection to the user is determined both by specifying specific instances and according to the groups to which the user belongs
- SSH-key and passwords, with the help of which authorization takes place on remote nodes - are not available to the user, respectively, this data is reliably protected and cannot be compromised
- access to the CLD management server (as well as to other nodes connected to the system) can be limited by the list of allowed ip addresses (access lists)
- the formation of lists of IP addresses allowed for access is carried out using the telegram bot using the API, or through the built-in CLI utility
- in the process of working through the CLD, when connecting to the server, its root file system is mounted in `~/mnt/$instance`, this provides file access to the user to any available server through a single SFTP connection, as well as transfer and synchronization of files between servers without the need to create new ones direct connections
- servers are divided into groups, available group types: manual and parsing
- groups of type manual contain servers added manually
- groups of the parsing type contain servers updated through an automatic parsing script that works via API, or in another way, for example, supported from aws, digitalocean, google cloud deployments, or parsing KVM/LXC containers of a group of available hypervisors
- for any group of servers, the functions of connecting to the terminal, mounting the file system and deployment can be separately configured
- currently 2 roles are available:
  - **admin** - `unlimited access` to all CLD components and modules.
  - **user** - `customizable access` to servers, server groups, utilities and modules.
- the console output of all connections to the system's servers is logged into the session log, it is possible to track what the user performed, as well as what he saw in the console at any time in any session, the ability to view current sessions is also available, this allows you to see on the screen the same thing that he sees user, for example it can be useful for L3/L2 engineers to help L2/L1 engineers with technical questions.

# Interfaces:
- **CLI**  
  The main interface for working with the CLD system, many main scripts have support for working in an interactive mode designed to work through the CLI
  - CLI launch is validated by user aliases in `~/.bashrc`
  - Each alias contains sudo launch
  - List of aliases and allowed CLD utilities in `/etc/sudoers` - generated by the `cld-initpasswd` utility according to the access matrix `/var/cld/creds/passwd`
  - When a module is enabled for a user, all the utilities of the module are added to the aliases and `/etc/sudoers` of this user

- **API**  
  Interface for accessing non-interactive tools via Web API:
  - The interface code is written in `Python`, using the `Flask` framework
  - Request example: `https://cld.example.com/api/${TOOL}?token=${USER_TOKEN}&args=${ARGUMENTS}`
  - User tokens are stored in the file `/var/cld/creds/passwd` and are available to each user in the profile section of the web interface
  - At the time of the request, the execution of the utility is initiated with the arguments provided in the request
  - Output from the execution of the utility is performed in streaming mode as it is - you can watch the progress in real time
  - Custom endpoint and API functions available
  - When starting the API interface (`systemd` service `cld-api`), the following is executed:
    - Search for all available utilities and generate code for each utility with the appropriate endpoint (truncated by "cld-" in the name)
    - Search for api.py files in the root of each module, this code is executed as is, as part of the entire interface
  - An example of using custom endpoints and functions can be viewed in the access module - file `/var/cld/modules/access/api.py`
  - Location `/api/`:
  - Available only at addresses allowed through the access module in the system
    - Endpoint autogeneration for utilities occurs for this location
    - The file with allowed ip addresses for `nginx` is generated in the file `/etc/nginx/accesslist`
  - Location `/api/all/`:
    - Available for all types of addresses, except those in the prohibited list:
    - Can only be used for custom endpoints
      - An example of use is presented in the above api.py access module file
    - The number of requests for location `/api/all/` has a limit of `60 requests per minute`

- **Bot**  
  Telegram chat bot interface for executing utilities in non-interactive mode:
  - Interface code in `Python`, using the `pytelegrambotapi` module as a basis
  - When sending a command to the chat/bot, it is directly executed with the passed arguments
  - Example of command execution: `/command arguments`
  - Access at the application level is validated based on the telegram id of users specified in the file/var/cld/creds/passwd
  - Output from the utility execution is made in real time by updating the bot's response message
  - When starting the BOT interface (`systemd` service `cld-bot`), the following is executed:
     - Search for all available utilities and generate code for each utility with the corresponding command (by analogy with the API, "cld-" in the name is truncated)
    - Search for bot.py files in the root of each module, this code is executed as is, as part of the whole interface
  - Custom commands and functions of the Bot interface are available
  - An example of using custom commands and functions can be viewed in the access module - file `/var/cld/modules/access/bot.py`
  - To share individual modules/utilities for a whole chat, you need to create a separate user in the CLD and assign it the chat id of this group

- **Web**  
  Auxiliary interface for working with the system
  - The interface code is written in `Python` using the `Flask` framework as well as the `SocketIO` module
  - Provides many system management functions
  - Has access to all CLI elements including interactively
    - Web terminal in the browser is implemented using `XtermJS` and `SocketIO`
  - Allows you to work with the system via web terminal without using SSH client at all
  - When starting the WEB interface (`systemd` service `cld-web`), the following is executed:
    - Search for all available utilities and generate code for each utility with the corresponding endpoint
    - Search for web.py files in the root of each module, this code is executed as is, as part of the whole interface
      - When web.py is found at the root of a module, a symlink is created to the `/var/cld/web/modules/${MODULE}/web` directory along the path `/var/cld/web/modules/${MODULE}` to access the static files of the module outside the Flask directory of the application
  - Each displayed block of the module on the main page of the interface is generated when web.py is detected and leads to the index endpoint specified by web.py in the module code
    - The name and description of modules are read from the properties of the webmodule object specified in the web.py file of each module, you can see an example in the module documentation file `/var/cld/modules/doc/web.py`
    - The module logo is displayed if found at `/var/cld/web/modules/${MODULE}/content/logo.svg`, otherwise a standard image is displayed

## Access validation factors for each interface:
- **CLI** - `PAM authorization`, `access module`, `access matrix` and `sudoers`
- **API** - `token/access module`, `access list` at the nginx level, `access matrix` and `sudoers`
- **Telegram bot** - `userid`, `permissions matrix` and `sudoers`
- **Web** - `cookie`, `access module`, `access list` at the nginx level, `access matrix` and `sudoers`

Thus, the main priorities of CLD are the safety of users and maintained servers, unprecedented transparency work of engineers, increasing the efficiency of personnel, as well as automation of processes and work scenarios.

# Modular concept
The internal structure of the CLD includes a system of modules that allows you to significantly expand the basic functionality and provide the ability to quickly integrate with external services. Below is a list and brief description of several modules that are included in the CLD:
- `access` - control access to network ports by allowed/denied address lists on all servers
- `cm` - create/manage/migrate KVM to Proxmox Virtual Environment
- `deploy` - deploy bash scripts with support for backups, tests and everything you need to deploy thousands of servers
- `dns` - cloudflare integration and DNS management across multiple accounts
- `doc` - core of self-documenting system concept - generating documentation based on parsing readme files and help information of all existing modules and scripts
- `etcbackup` - backup of CLD instances configuration

The system is designed in such a way that the addition of new functional modules for any purpose occurs as quickly as possible due to unification and automatic code generation for API and telegram bot, already now in production on a number of projects up to 50 local modules are used that provide the most diverse functionality and automation, in including complex CI/CD.
Access to modules via CLI, bot telegram, API and via the web interface is separately configured for each user.

# Framework
`ClassicDeploy` is home to all your infrastructure scripts where they are always at hand

CLD framework script is:
- Available through various CLI, API, Telegram bot, Web - in accordance with the `access matrix` and `allowed lists` of ip addresses
- Has a generated help for all interfaces from one or more variables specified at the beginning of the script (`HELP_DESC`, `HELP_ARGS`, `HELP_EXAMPLES`)
- Safely shared separately or as part of the entire module for any user (including telegram user or telegram chat)
- Easily used in API for example for build/deployment in the pipeline (API works in stream mode - new lines are displayed in the response as they are executed)
- Over time, new scripts of local modules are developed faster and faster using a similar structure and framework functions
- Works reliably and safely - due to unification and security features, there is no need for hardcode even with tight deadlines
- The script can be in any language (including compiled ones) - it will also be available through any interface (do not forget to write help available through the -h argument for access through the web interface)
- Can be set to cron, for example, to update groups of instances (centralized release and further renewal of certificates on balancers), as well as for monitoring/parsing and sequential start/restart of various services on groups of instances in complex systems with a regulated startup protocol)

# Installation
### Recommended system requirements:
Virtualization: `KVM`/`Bare metal`
Supported OS: `Centos` 7/8, `Debian` 9/10
CPU: `2` cores
RAM: `2` Gb
Disk space: `20` Gb
Direct public ip address

### Data required for interfaces and modules
Before the installation process, you should prepare the following information:
- For interfaces **(**to use tools through any available interfaces**)**:
	- `Web` - DNS name for WEB/API (cld.example.com)
	- `Chat bot` - Telegram bot token (Bot can be created via http://t.me/BotFather)

- For modules **(**to use modules functionality like create/resize/migrate KVM, create/delete/update DNS records, etc**)**:
	- `cm` - API credentials of supported bare metal hosting providers `OVH`/`Online.net`/`Hetzner`
	- `dns` - Credentianals of CloudFlare account (`login`, `API key`, `user ID`)
	- `zabbix` - Zabbix access credentials (`login`, `password`, `domain`, `link for Zabbix API`)

### Quick start
ClassicDeploy should be installing on a **clean** OS, it is recommended to use `Centos` 8, because work in this distribution is very well tested in production
The installation is starting with the command:
```bash
bash -x <(wget -qO- "https://raw.githubusercontent.com/achendev/cld/master/setup/install_cld.sh")
```

During the installation process, all init scripts of the system and modules will be executed, for each of them in interactive mode, you will need to specify the initialization data necessary for the operation of the system and modules
An example input will be provided for each type of data requested

Upon completion of the installation, a `password` for the `admin` user and a `link` to the `web interface` will be provided in console.