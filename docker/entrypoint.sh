#!/bin/bash
set -e
mkdir -p /var/cld/creds

# If an existing creds file is present from a non-containerized setup, convert
# it into creds_static so future runs use symlinks.
if [ -f /var/cld/creds/creds ] && [ ! -L /var/cld/creds/creds ]; then
    [ -f /var/cld/creds/creds_static ] || mv /var/cld/creds/creds /var/cld/creds/creds_static
fi

# If environment variables prefixed with CLD_CFG_ are provided,
# write them into creds_env and use it. Otherwise fall back to creds_static.
if env | grep -q '^CLD_CFG_' ; then
    CREDS_ENV=/var/cld/creds/creds_env
    : > "$CREDS_ENV"
    for VAR in $(env | grep '^CLD_CFG_' | sort); do
        KEY=${VAR%%=*}
        VALUE=${VAR#*=}
        KEY=${KEY#CLD_CFG_}
        echo "${KEY}=${VALUE}" >> "$CREDS_ENV"
    done
    ln -sf creds_env /var/cld/creds/creds
else
    # Ensure a static credentials file exists. If a plain creds file exists from
    # a previous setup, move it so future runs use the symlink.
    if [ -f /var/cld/creds/creds ] && [ ! -L /var/cld/creds/creds ]; then
        [ -f /var/cld/creds/creds_static ] || mv /var/cld/creds/creds /var/cld/creds/creds_static
    fi
    [ -f /var/cld/creds/creds_static ] || touch /var/cld/creds/creds_static
    ln -sf creds_static /var/cld/creds/creds
fi

exec /usr/bin/supervisord -c /etc/supervisord.conf
