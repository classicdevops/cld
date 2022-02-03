#!/bin/bash
DOMAIN=$1
expr \( `echo|openssl s_client -connect ${DOMAIN}:443 -servername ${DOMAIN} 2>/dev/null|openssl x509 -noout -enddate|cut -d'=' -f2|xargs -I ^ date +%s -d "^"` - `date +%s` \) / 24 / 3600
