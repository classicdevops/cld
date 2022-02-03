Module for managing hosts checking the availability of web sites by url (periodic access to a remote server by domain), as well as monitoring and checking the validity of SSL certificates, domain expiration dates.
- Templates and scripts for Zabbix server are in `/var/cld/modules/zabbix/zbx/`

The functional of the zabbix module implements functions that allow you to quickly and conveniently add URLs to monitoring and automatically check its availability, the correctness of the response code and much more, if the CLD was initialized with Zabbix support. The zabbix module allows you to significantly speed up the process of adding domain names to the monitoring system through popular corporate messengers, since CLD is deeply integrated into Slack, Mattermost, Discord, Telegram and others.
The main functionality that the zabbix module provides:
- Adding a URL to the monitoring system using a command for the bot. When adding, it is possible to specify a pattern that will be checked when responding to the page. A pattern can include a piece of content, a search word, or a combination. If the pattern is not specified when adding, only the page response code will be checked, which is 200 by default.
- Removing the URL from the monitoring system. You can always remove one or more hosts from monitoring if their further monitoring is not required. Removal is also performed using a command via a bot in a corporate messenger.
- It is also possible to get a complete list of hosts that are being monitored at the moment.

Below is a list of the Zabbix-module initial variables.

| Variable | Description |
| ------ | ----------- |
| ZABBIX | variable responsible for initializing the Zabbix module. |
| ZABBIX_USER | Zabbix username through which hosts will be added to monitoring. |
| ZABBIX_PASS | Zabbix user password. |
| ZABBIX_SERVER | the address of the Zabbix server with which the checks will be performed. |
| ZABBIX_API | Zabbix API key for CLD interaction of Zabbix module. |
