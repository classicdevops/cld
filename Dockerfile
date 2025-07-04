FROM almalinux:9

RUN dnf -y install epel-release \
    && dnf -y install \
        openssh-server nginx supervisor python3 python3-pip cronie screen certbot \
    && dnf clean all

RUN mkdir -p /var/run/sshd /var/log/nginx /var/cld /root/sbin

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm -f /tmp/requirements.txt

COPY supervisord.conf /etc/supervisord.conf
COPY docker/nginx/cld.conf /etc/nginx/conf.d/cld.conf
COPY docker/nginx/sslgen.conf /etc/nginx/sslgen.conf
RUN touch /etc/nginx/accesslist /etc/nginx/deny.conf

COPY docker/scripts/lets_auto_sign /root/sbin/lets_auto_sign
COPY docker/scripts/lets_renew /root/sbin/lets_renew
COPY docker/scripts/lets_clean_subdomains /root/sbin/lets_clean_subdomains
COPY docker/scripts/lets_auto_gen /etc/cron.d/lets_auto_gen
COPY docker/init_creds.sh /docker/init_creds.sh
RUN chmod 700 /root/sbin/lets_auto_sign /root/sbin/lets_renew /root/sbin/lets_clean_subdomains \
    && chmod 644 /etc/cron.d/lets_auto_gen \
    && screen -m /root/sbin/lets_clean_subdomains

COPY docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
EXPOSE 22 80 443
VOLUME ["/var/cld"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
