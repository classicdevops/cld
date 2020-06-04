#!/bin/bash
grep --color=always -s "^$1" /var/cld/modules/dns/data/{cf,ibs}/`TZ=Europe/Moscow date +%F`/{cf,ibs}_dns_list
tail -n 999 /var/cld/modules/dns/data/{cf,ibs}/`TZ=Europe/Moscow date +%F`/*$1* 2>/dev/null | grep -v "\;\;" | ack --color --passthru $1 | less -R | cat
