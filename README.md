# Introduction
CLD is a system for differentiating access to servers and scripts with the ability to quick and unify develop custom modules and automation tools based on this functionality.
This project does not set itself the goal of replacing any existing automation tool or CI/CD/deployment/etc, to the contrary, it is designed to combine everything in one centralized self-documenting place, with secure, transparent and logged access to any server and tool, simultaneously through several available user interfaces.

The main components of the system are bash-based utilities, API, chat bots and web interface are just additional data validators and access rights for broadcasting to these bash scripts.
To access any tool, several factor validation operates for the user, at the application/web server and/or operating system level (sudoers file generated based on the CLD access permissions matrix), so any new module and script can be shared for execution for certain users via any interface (CLI, API, Chat bot, Web), excluding direct access to their content as well as to the entire application directory.

# Use cases
Here are a few of the many use cases with a brief description to visualize the application of the system.

The CLD usage example screencasts below use the following software:
- Termius as an SSH client
- Chromium based browser
- Telegram messenger client

## Centralized access system
The basis of the project is a centralized system of SSH access based on PAM:

<details open>
<summary>Centralized access system demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151917199-abbd03e3-8bbc-4c10-81b6-b528ccb53ce3.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- all CLD users work according to the internal access matrix and have customizable permissions, they can be assigned personal Messenger account id, as well as API token
- each user is authorized on the server to his PAM account
- access to allowed servers is carried out using a single private SSH key or instance password
- the list of servers allowed for connection for the user is determined both by specifying specific instances and according to the groups which shared for a user
- SSH-key and passwords, with the help of which authorization takes place on remote nodes are not available to the user, respectively, this data is reliably protected and cannot be compromised

This video example shows how a user tries to access instances, demonstrates how admin using a dashboard shares one instance for the user, and then a group of instances, also demonstrates the operation of an interactive SSH gate


## Protection of all servers on any hosting
Access to all servers is protected by trusted IP address lists

<details open>
<summary>Protection of all servers on any hosting demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151851153-cf9e00df-aa21-4832-849f-c019f8b57c46.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- access to the CLD management server (as well as to all instances connected to the system) can be limited by the list of allowed ip addresses (access lists)
- the access module provides the ability to update user addresses using a bot in messengers (telegram, discord, mattermost, slack)
- users can generate their personal VPN key to access the CLD server and instances
- trusted lists are deployed by cron, as well as by watcher after changes in the lists on the CLD server
- the list of protected ports is configurable, and separate port lists can be configured for any group or instances

This demonstration shows a user trying to connect to the server, the connection is refused until the user adds his ip address through the bot in the messenger using the link in the api containing the generated one-time token


## CloudFlare integration
DNS management for domain zones simultaneously in multiple accounts

<details>
<summary>CloudFlare integration demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151921860-df302a18-c4f0-48e2-a8a9-e327a245adc9.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- Viewing, editing and deleting DNS records of any domain with the ability to enable proxying at any CLD interface
- Ability to set any CloudFlare settings for the domain, as well as reset the CDN cache
- Backing up DNS zones of all connected accounts
- Bulk domains switching from one IP address to another with auto detection of which domains are directed to the current IP address
- Support tools for viewing geo and whois
- Tool for mass issuance of wildcard certificates for all domains in all connected CloudFlare accounts

In order to demonstrate the equivalent use of different interfaces, a user views value of DNS record for a domain in terminal, then deletes it in a messenger using chat bot and sets DNS record to a different type of address in the terminal

## SFTP single access point
Users able to get filesystem access of any available instance

<details>
<summary>SFTP single access point demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151921929-6993b796-bbd9-4fc0-b43a-2a4f3f820ff9.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>

- All file operations performed by the user are logged to `/var/cld/log/session/$user/$date/$instance_sftp_$time.gz`
- There are 2 utilities, cld-mount (interactive) and cldxmount (the first instance is selected after filtering)
- Custom mount functions provide file access for any kind of servers, containers, and so on by any protocols
- This tool provides the ability to copy / sync / move data between servers without direct access in between

The current example shows how the user mounts the file system of the remote server, checks the mount status in the command line interface and checks the access to files through the SFTP client connected to the CLD server

## Instance list parsing groups
Parsing public cloud providers, hypervisors, container orchestration systems or anything else to group instance list with custom parsing scripts

<details>
<summary>Instance list parsing groups demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151921967-b62c11c9-6987-4f86-9276-d76c0e3c1e75.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- Group type "parsing" have custom script, it will continuously synchronize instance list to group, so you always have single point access to all your infrastructure instances wherever it are
- Parsing any public cloud providers fully customizable - it can use API or CLI third party tools installed on CLD server, parsing script have not limited at all
- Built-in parsing groups: AWS cloud, Google cloud, Hetzner cloud, DigitalOcean, Azure cloud, Scaleway cloud, OVH cloud, Proxmox LXC containers, Docker containers, Kubernetes containers
- The group parsing model combines well with various automation and security tools, as well as with continuously trusted IP lists deploy and SSH authorized keys deploy

The video demonstrates how the user checks the list of instances in the Hetzner group, then activates the group type parsing with the corresponding script in the CLD admin panel, creates a new cloud in the Hetzner Cloud panel, once the server is created, it can be accessed from the CLD

## KVM Cloud management
Creation, management and migration of KVM clouds on PVE hypervisors

<details>
<summary>KVM Cloud management demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151922026-5055929b-856d-4fe5-a02d-fb798a5bd7e9.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- Interactive creation of KVM clouds with a choice of operating system, processor cores, amount of RAM, amount of disk space and network configuration
- Single point management of clouds on all hypervisors (it does not matter if they are not in a cluster, in different DCs, and so on), commands are available: start, stop, pause, resume and delete
- PVE hypervisor deployment script with network configuration (vmbr0 and vmbr1 bridging), storage configuration - support for 3 types of storages: ZFS, LVM, QCOW2, and so on
- Interactive cloud migration between hypervisors via pve-zsync, preliminary phased synchronization before switching (automatic migration of type addresses is supported for some hosting providers)
- Parsing the availability of backups for all hypervisors with a clear daily report in the messenger

The video demonstrates interactive creation using the CLD web terminal, after creation, the user checks the status of the cloud, gets SSH access through the web interface and checks the settings and resources specified during creation

## Custom modules for any functionality
Support of custom modules to expand the capabilities of the system

<details>
<summary>Custom modules for any functionality demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151922104-18a715f7-670d-44f9-950c-68dea607b611.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- Interactive creation of a module template, with a custom API method, a module editing web page and an example of a shell tool
- Modules are located along the path /var/cld/modules/, a module may contain:
  - tools `bin/cld-*`
  - custom methods of the interfaces `./{api,bot,web}.py`
  - custom WEB interface files `web/${module}.html`, `web/content/somefile.{css,js,svg}` and so on
  - documentation file `./README.md`
  - data of custom modules is recommended to be stored in the directory ./data
- Custom methods of the module interfaces can be related to each other, for example, as it is implemented in the built-in access module
- Module tools can be written in any programming language, including compiled ones
- The CLD interfaces code for the standard launch of the module's tools is generated automatically when the systemd interfaces services are restarted, as well as the code of the user methods is parsing and loading into the interfaces automatically

The video demonstrates how the administrator creates a new module, then makes a new tool for complex application deployment and launches it using the chat bot interface in the messenger

## Backup for any case
Organizing backup system for configurations, files, and databases

<details>
<summary>Backup for any case demo screencast (click to expand)</summary>
<table style="max-width: 700px; margin: 30px auto">
  <tr style="border:none">
    <td width="60%" style="border:none">
      <video src="https://user-images.githubusercontent.com/45525349/151922168-665d0df7-44c9-493b-ad7c-7f9e04389501.mp4" type="video/mp4" loop="" autoplay="" muted="" playsinline="true" style="min-width:289px;width:100%;box-shadow:0 6px 15px 0 rgb(69 65 78 / 15%);border-radius:10px"></video>
    </td>
  </tr>
</table>
</details>


- Independent backup methods for any instance
- Ability to set unique parameters, such as credentials for databases, paths to backup directories, backup execution time, the number of stored copies, a list of files, excluding extensions and backup server for each method
- Backups are performing at remote backup servers
- Backup process is optimized for multi thread copy data
- Built-in backup methods:
  - ETC Backup: backup of configuration files located in the /etc/ or another configuration directories
  - Files Backup: backup files and entire file directories, allows you to quickly and conveniently configure the backup of the necessary elements
  - MongoDB Backup: flexible, customizable backup of databases of any size powered by MongoDB
  - ClickHouse Backup: flexible custom backup of databases of any size managed by ClickHouse-Server
  - MySQL Backup: flexible, customizable backup of databases of any size running MySQL, In addition, it is possible to perform local and remote backups
  - PostgreSQL Backup: flexible, customizable backup of databases of any size powered by PostgreSQL
- CLD users able to create their own backup methods such as built-in placed at /var/cld/modules/backup/methods

The video demonstrates creating configurations for backup methods for a couple of instances and generating a report in the messenger

# Support policy

Please do not ask your questions in github issues. Such format is not suitable for storing FAQ.

If you have any question, please go to **[ServerFault](https://serverfault.com/questions/ask?tags=cld%20classicdevops)** and ask it there.

Tag your question with **`cld`** and **`classicdevops`** tags (both at once).

We are continuously parsing full list of questions by these tags and will answer as soon as possible. Make your experience available for other users!

[GitHub](https://github.com/classicdevops/cld/issues) issues are for confirmed bugs/feature requests now. If you have feature idea - please describe it from user experience point of view. Describe how'd you gonna to configure CLD for desired result.

# Terms

## CLD server
Server based on OS Linux with installed CLD software

## Instance
Linux-based server added to the CLD group as a string by the default delimeter '\_' `example.example_1.2.3.4_22_user`, the delimeter can be configured for individual groups with appropriate changes to the supported custom functions

## User
PAM user on the CLD server created through the `cld-useradd` utility, file-related to CLD (`/var/cld/creds/passwd`, `/var/cld/access/users/${CLD_USER}/`)
  User passwd string have such format: `Username`:`UserMessangerIds`:`ApiToken`:`Modules`:`Tools`:`Groups`
  Regardless of the role, it can contain:
- individual list of instances `/var/cld/access/users/${CLD_USER}/clouds` (optional)

## User role
Roles:
- admin - full access to modules and all tools, the role is defined in the access matrix by the presence of the ALL pattern in columns 4 (modules) and 5 (tools) (userexample:::ALL:ALL)
- user - configurable access to modules and individual tools (userexample:::dns,doc,note:cld,cld-mount,cld-modules)
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
Detailed information on the available scripts included in the modules "from the box" is available at https://classicdevops.com/documentation

## Interface
CLD interfaces are methods of using tools or any additional functionality
CLD standard interfaces:
- CLI - the main working interface, the use of the interface is available through the shell Linux console, the connection is made via SSH, it is also possible to use it via a web terminal as part of the WEB interface
- API - interface for accessing non-interactive scripts, access to scripts is validated by access lists and the user's personal token, additional arguments are translated as is, an example of use is `curl -s" https://yourcld.server.com/api/modules?token=y0urUserT0keN&args=-json"`, endpoints like `/api/all/` do not have validation by access lists, for example, they are used in `cld-myip`
- BOT - an interface in the chat bot format for accessing non-interactive scripts, convenient for using when managing DNS, access lists, backup reports and so on, an example of use is `/setdns a subdomain.example.com 1.2.3.4`, at the moment are `Telegram`, `Discord`, `MatterMost` and `Slack` integrations are supported
- WEB - interface for access to any, including interactive scripts (using a web terminal), as well as to additional methods of system management, access is validated by access ip lists and by PAM for CLD users, the interface is available at the address - `https://yourcld.server.com/`

## Framework
As per definition from wikipedia
`Framework - a software platform that defines the structure of a software system; software that facilitates the development and integration of different components of a large software project.`
The project is a kind of access and automation framework.
To ensure the standard structure of the tools is used, the main bash library `/var/cld/bin/include/cldfuncs`, connected in all the built-in tools, through the functions of this library, help unification is organized and, accordingly, general autodocumentation using the doc module for generating json and rendering via Redoc, as well as various auxiliary functions, access control, security, etc.


# Centralized access system
The basis of the project is a centralized system of SSH access based on PAM:
- all CLD users work according to the internal access matrix and have customizable permissions, they can be assigned personal messenger account id, as well as API token
- each user is authorized on the server to his PAM account
- access to allowed servers is carried out using a single private SSH key or instance password
- the list of servers allowed for connection for the user is determined both by specifying specific instances and according to the groups which shared for a user
- SSH-key and passwords, with the help of which authorization takes place on remote nodes - are not available to the user, respectively, this data is reliably protected and cannot be compromised
- access to the CLD management server (as well as to other nodes connected to the system) can be limited by the list of allowed ip addresses (access lists)
- the formation of lists of IP addresses allowed for access is carried out using the chat bot together with API, or through the built-in CLI utility
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
## CLI
The main interface for working with the CLD system, many main scripts have support for working in an interactive mode designed to work through the CLI
- CLI launch is validated by user aliases in `~/.bashrc`
- Each alias contains sudo launch
- List of aliases and allowed CLD utilities in `/etc/sudoers` - generated by the `cld-initpasswd` utility according to the access matrix `/var/cld/creds/passwd`
- When a module is enabled for a user, all the utilities of the module are added to the aliases and `/etc/sudoers` of this user

## API 
Interface for accessing non-interactive tools via Web API:
- The interface code is written in `Python`, using the `Flask` framework
- Request example: `https://cld.example.com/api/${TOOL}?token=${USER_TOKEN}&args=${ARGUMENTS}`
- User tokens are stored in the file `/var/cld/creds/passwd` and are available to each user in the profile section of the web interface
- At the time of the request, the execution of the utility is initiated with the arguments provided in the request
- Required get arguments:
  - `token` - API token key of CLD user
- Available get arguments:
  - `args` - command line arguments will pass to the CLD tool as is via symbols regex filter
  - `output` - "plain" or "html" - if "html" value will convert color console output to color html - default is plain
  - `mode` - example `?token=${USER_TOKEN}&args=${ARGUMENTS}&mode=track`
    - "stream" - output will streaming line by line in realtime so you can watch progress but response code will always 200 - default value
    - "track" - output will available only after CLD tool work done, response code depend on CLD tool return code:
      - return code "0" - response code will 200
      - otherwise response code will 500 - can be useful for CI/CD systems to track status of API request
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

## Bot
Telegram/Discord/MatterMost/Slack chat bot interface for executing utilities in non-interactive mode:
- Interface code for each chat bot interface in `Python`.
- When sending a command to the chat/bot, it is directly executed with the passed arguments
- Example of command execution: `/command arguments` (first symbol can be different at MatterMost and Slack)
- Access at the application level is validated based on the messendger id of users specified in the file `/var/cld/creds/passwd`
- Output from the utility execution is made in real time by updating the bot's response message
- When starting the BOT interface (`systemd` service `cld-bot`), the following is executed:
   - Search for all available utilities and generate code for each utility with the corresponding command (by analogy with the API, "cld-" in the name is truncated)
  - Search for bot.py files in the root of each module, this code is executed as is, as part of the whole interface
- Custom commands and functions of the Bot interface are available
- An example of using custom commands and functions can be viewed in the access module - file `/var/cld/modules/access/bot.py`
- To share individual modules/utilities for a whole chat, you need to create a separate user in the CLD and assign it the chat id of this group

## Web
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
  - The name and description of modules are read from the properties of the webmodule object specified in the web.py file of each module, you can see as an example in the documentation module - file `/var/cld/modules/doc/web.py`
  - The module logo is displayed if found at `/var/cld/web/modules/${MODULE}/content/logo.svg`, otherwise a standard image is displayed
- As the text editor in the web interface uses the [Ace Cloud9 Editor](https://github.com/ajaxorg/ace), it comes with the following license:
  <details>
  <summary>Ace Cloud9 Editor license</summary>

  ```
  Copyright (c) 2010, Ajax.org B.V.
  All rights reserved.

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:
      * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
      * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
      * Neither the name of Ajax.org B.V. nor the
        names of its contributors may be used to endorse or promote products
        derived from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  DISCLAIMED. IN NO EVENT SHALL AJAX.ORG B.V. BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  ```

  </details>

## Access validation factors for each interface:
- **CLI** - `PAM authorization`, `access module`, `access matrix` and `sudoers`
- **API** - `token/access module`, `access list` at the nginx level, `access matrix` and `sudoers`
- **Bot** - `userid`, `permissions matrix` and `sudoers`
- **Web** - `cookie`, `access module`, `access list` at the nginx level, `access matrix` and `sudoers`

Thus, the main priorities of CLD are the safety of users and maintained servers, unprecedented transparency work of engineers, increasing the efficiency of personnel, as well as automation of processes and work scenarios.

# Modular concept
The internal structure of the CLD includes a system of modules that allows you to significantly expand the basic functionality and provide the ability to quickly integrate with external services. Below is a list and brief description of several built-in modules:
- `access` - control access to network ports by allowed/denied address lists on all servers
- `backup` - backup of CLD instances files, databases and configurations
- `cm` - create/manage/migrate KVM to Proxmox Virtual Environment
- `deploy` - deploy bash scripts with support for backups, tests and everything you need to deploy thousands of servers
- `dns` - CloudFlare integration and DNS management across multiple accounts
- `doc` - core of self-documenting system concept - generating documentation based on parsing readme files and help information of all existing modules and scripts

The system is designed in such a way that the addition of new functional modules for any purpose occurs as quickly as possible due to unification and automatic code generation for API and messenger bots, already now in production on a number of projects up to one hundred local modules are used that provide the most diverse functionality and automation, in including complex CI/CD.
Access to modules via CLI, Chat bots, API and via the web interface is separately configured for each user.

# Framework
`ClassicDevOps` is home to all your infrastructure scripts where it's always at hand

CLD framework script is:
- Available through various CLI, API, Chat bot, Web - in accordance with the `access matrix` and `allowed lists` of ip addresses
- Has a generated help for all interfaces from one or more variables specified at the beginning of the script (`HELP_DESC`, `HELP_ARGS`, `HELP_EXAMPLES`)
- Securely shared separately or as part of the entire module for any user (including messenger user or group chat)
- Easily used in API for example for build/deployment in the pipeline (API works in stream mode - new lines are displayed in the response as they are executed)
- Over time, new scripts of local modules are developed faster and faster using a similar structure and framework functions
- Works reliably and securely - due to unification and security features, there is no need for hardcode even with tight deadlines
- The script can be in any language (including compiled ones) - it will also be available through any interface (do not forget to write help available through the -h argument for access through the web interface)
- Can be set to cron, for example, to update groups of instances (centralized release and further renewal of certificates on balancers), as well as for monitoring/parsing and sequential start/restart of various services on groups of instances in complex systems with a regulated startup protocol)

# Installation
### Recommended system requirements:
- Virtualization: `KVM`/`Bare metal`
- Supported OS: `Centos` 7/8, `Debian` 9/10
- CPU: `1` cores 
  - `1` more core for every 500 next instances
- RAM: `2` Gb 
  - `1`Gb more RAM for every 500 next instances
- Disk space: `20` Gb 
  - `10`Gb more disk space for every 500 next instances
- Direct public ip address

### Data required for interfaces and modules
Before the installation process, you should prepare the following information:
- For interfaces **(**to use tools through any available interfaces**)**:
	- `Web`/`API` - DNS name for WEB and API (cld.example.com)
	- `Chat bot`:
    - Telegram bot token (http://t.me/BotFather)
    - Discord bot token (https://discord.com/developers/applications)
    - Extended license:
      - MatterMost url, port, team, bot token (https://example.com/yourteam/integrations/bots)
      - Slack app token, bot token (https://example.slack.com/apps/manage)

- For modules **(**to use modules functionality like create/resize/migrate KVM, create/delete/update DNS records, etc**)**:
	- `cm` - API credentials of supported bare metal hosting providers `OVH`/`Online.net`/`Hetzner`
	- `dns` - Credentianals of CloudFlare account (`login`, `API key`, `user ID`)
	- `zabbix` - Zabbix access credentials (`login`, `password`, `domain`, `url for Zabbix API`)

### Quick start
ClassicDevOps should be installing on a **clean** OS, it is recommended to use `Centos` 8 Stream, because work in this distribution is very well tested in production
The installation is starting with the command:
```
bash -x <(wget -qO- "https://raw.githubusercontent.com/classicdevops/cld/master/setup/install_cld.sh")
```

During the installation process, all init scripts of the system and modules will be executed, for each of them in interactive mode, you will need to specify the initialization data necessary for the operation of the system and modules
An example input will be provided for each type of data requested

Upon completion of the installation, a `password` for the `admin` user and a `link` to the `web interface` will be provided in console.