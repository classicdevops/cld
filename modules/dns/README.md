The module allows you to quickly integrate and manage DNS zones of domains simultaneously in multiple CloudFlare (CF) accounts, back up DNS records of all domains, as well as track rps using the nginx log to enable “Under Attack” mode in CF

The module has a number of useful areas of application that implement the functionality that provides not only a convenient system for managing DNS records, but also backing up all DNS records (A \ AAAA \ CNAME \ MX \ TXT \ SPF \ PTR and others) for each domain under CLD control. This measure allows you to reliably store information about all DNS records, track changes over a long period of time, and in the event of a failure or loss of a record, it is easy to restore the state for the required period of time.
In addition, the DNS module allows you to manage additional functionality of CloudFlare (CF), such as working with the cache (dumping cached data), which is relevant at certain stages of development and not only. The functionality of this module is quite extensive, here are some of the most useful functions for you:
+ Full control over domain names even at the stage of adding. Using the DNS module, you can add a domain to the panel literally with one command, as well as register the necessary records, enable or disable proxying for a domain name, and naturally delete records and domain names from the panel.
+ Manage domain parameters in CloudFlare (CF), such as:
  - enable / disable support for HTTP2 / HTTP3,
  - enable / disable automatic https rewrites, change the caching level
  - enable / disable support for TLS1 / TLS2
  - enable / disable the "Always online" mode
  - enable / disable optimization and acceleration parameters Brotli, Minify, Mirage
  - enable / disable Under Attack mode
And many other parameters that you can use every day.
+ Having built-in integration with Zabbix Monitroing, the DNS module is able to automatically respond to parsing, DDOS and other suspicious activity. The functionality allows you to flexibly configure the RPS limit, which is a convenient and effective tool that will automatically turn on the Under Attack mode, and turn it off when the RPS drops below the set mark.
+ If you have front servers balancing and proxying to the backend servers, the DNS module provides a convenient tool that allows you to quickly generate commands to switch DNS records between servers and change ip addresses on the fly.
+ The list of useful and convenient utilities also includes a whole set of commands that allow you to find out all information about the domain (WHOIS) and ip address, show all active DNS records for the specified domain name.

It is important to note that all the above functionality is available not only in the CLD management console, but also successfully integrated into Telegram, Slack, Mattermost and other corporate messengers.

Below is a list of the DNS-module initial variables.

| Variable | Description |
| :------- | :----------- |
| CLOUDFLARE | variable responsible for initializing the DNS module. |
| CFACC | email address of the account connected to the DNS module. |
| CFKEY | API key generated in the CloudFlare panel |
| CF_ACC_ID | Account ID key from CloudFlare panel (common for all domains). |
