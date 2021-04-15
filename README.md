# Introduction
cld - сlassical architecture deployment and management system

- Secure, convenient and centralized access system from one point, it is not required to store the key of each user on each server, now there is only one key
- Transparent and flexible deployment that is limited only by your imagination
- Cloud maker platform - create and manage kvm virtual machines as easy as never before
- Modular system for any functionality, but if this is not enough, you can create and integrate it with the system, support for third-party modules is included
- Control as you like, CLI, web, API or chat bot, wherever you are, anytime

The main components of the system are bash-based utilities, API, telegram bot and web interface are just additional data validators and access rights for broadcasting to these bash scripts.
To access any tool, two (sometimes three) factor validation operates for the user, at the application/web server and/or operating system level (sudoers file generated based on the cld access rights matrix), so any new module and script can be shared for execution for certain users via any interface (CLI, API, bot, web), excluding direct access to their content as well as to the entire application directory.

## Access validation factors for each interface:
- **CLI** - `PAM authorization`, `access module`, `access matrix` and `sudoers`
- **API** - `token/access module`, `white list` at the nginx level, `access matrix` and `sudoers`
- **Telegram bot** - `userid`, `permissions matrix` and `sudoers`
- **Web** - `cookie`, `access module`, `white list` at the nginx level, `access matrix` and `sudoers`

# Centralized access system
The basis of the project is a centralized system of SSH access based on PAM:
- all CLD users work according to the internal access matrix and have customizable permissions, they can be assigned personal telegram account id, as well as API token
- each user is authorized on the server to his PAM account
- access to allowed servers is carried out using a single private SSH key or password
- the list of servers allowed for connection to the user is determined both by specifying specific instances and according to the groups to which the user belongs
- SSH-key and passwords, with the help of which authorization takes place on remote nodes - are not available to the user, respectively, this data is reliably protected and cannot be compromised
- access to the CLD management server (as well as to other nodes connected to the system) can be limited by the list of allowed ip addresses (whitelists)
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

Thus, the main priorities of CLD are the safety of users and maintained servers, unprecedented transparency work of engineers, increasing the efficiency of personnel, as well as automation of processes and work scenarios.

# Modular concept
The internal structure of the CLD includes a system of modules that allows you to significantly expand the basic functionality and provide the ability to quickly integrate with external services. Below is a list and brief description of several modules that are included in the CLD:
- `access` - control access to network ports by allowed/denied address lists on all servers
- `cm` - create/manage/migrate KVM to Proxmox Virtual Environment
- `deploy` - deploy bash scripts with support for backups, tests and everything you need to deploy thousands of servers
- `dns` - cloudflare integration and DNS management across multiple accounts
- `etcbackup` - backup of server configurations

The system is designed in such a way that the addition of new functional modules for any purpose occurs as quickly as possible due to unification and automatic code generation for API and telegram bot, already now in production on a number of projects up to 50 local modules are used that provide the most diverse functionality and automation, in including complex CI/CD.
Access to modules via CLI, bot telegrams, API and via the web interface is separately configured for each user.

# Framework
`Classic deploy` is home to all your infrastructure scripts where they are always at hand
CLD framework script:
- Available through various CLI, API, Telegram bot, Web - in accordance with the access matrix and allowed address lists
- Has a generated help for all interfaces from one or more variables specified at the beginning of the script (HELP_DESC, HELP_ARGS, HELP_EXAMPLES)
- Safely shared separately or as part of the entire module for any user (including user telegrams or chat telegrams)
- Easily used in API for example for build/deployment in the pipeline (API works in stream mode - new lines are displayed in the response as they are executed)
- Over time, new scripts of local modules are developed faster and faster using a similar structure and framework functions
- Works reliably and safely - due to unification and security features, there is no need for hardcode even with tight deadlines
- The script can be in any language (including compiled one) - it will also be available through any interface (do not forget to write help available through the -h argument for access through the web interface)
- Can be set to cron, for example, to update groups of instances (centralized release and further renewal of certificates on balancers), as well as for monitoring/parsing and sequential start/restart of various services on groups of instances in complex systems with a regulated startup protocol)

# Installation
### Recommended system requirements:
Virtualization: `KVM`/`Bare metal`
Supported OS: `Centos` 7/8, `Debian` 9/10
CPU: `2` cores
RAM: `2` Gb
Disk space: `20` Gb
Direct white ip address

### Data required for interfaces and modules
Before the installation process, you should prepare the following information:
- For interfaces:
	- `Web` - DNS name for WEB/API (cld.example.com)
	- `Chat bot` - Telegram bot token (Bot can be created via http://t.me/BotFather)

- For modules:
	- `cm` - Api credentials of supported bare metal hosting providers OVH/Online.net/Hetzner
	- `dns` - Requisites of access to your CloudFlare account (`login`, `api key`, `user ID`)
	- `zabbix` - Zabbix access credentials (user, password, domain, link for zabbix api)

### Quick start
Classic deploy should be installing on a **clean** OS, it is recommended to use `Centos` 8, because work in this distribution is very well tested in production
The installation is starting with the command:
``` bash
bash -x <(wget -qO- "https://raw.githubusercontent.com/achendev/cld/master/setup/install_cld.sh")
```

During the installation process, all init scripts of the system and modules will be executed, for each of them in interactive mode, you will need to specify the initialization data necessary for the operation of the system and modules
An example input will be provided for each type of data requested

Upon completion of the installation, a `password` for the `admin` user and a `link` to the `web interface` will be provided