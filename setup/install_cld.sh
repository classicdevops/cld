#!/bin/bash
bash_conf()
{
localedef  -i en_US -f UTF-8 en_US.UTF-8
export LC_ALL="en_US.UTF-8"

mkdir -p /root/backup/etc/sysconfig/
if [ -f /etc/sysconfig/i18n ]; then
cp /etc/sysconfig/i18n /root/backup/etc/sysconfig/i18n.`date +%Y-%m-%d_%H-%M`
fi  

cat > /etc/sysconfig/i18n << EOL
LANG="en_US.UTF-8"
SUPPORTED="en_US.UTF-8:en_US:ru"
SYSFONT="latarcyrheb-sun16"
EOL

cat > /etc/profile.d/bash.sh << EOL
PS1='\[\033[01;31m\]\u\[\033[01;33m\]@\[\033[01;36m\]\H \[\033[01;33m\]\w \[\033[01;35m\]\$ \[\033[00m\] '     
TERM=xterm
EOL

sed -i 's/Defaults\    requiretty/#Defaults\    requiretty/g' /etc/sudoers

cat << 'EOSCREEN' | tee /root/.screenrc /etc/skel/.screenrc 1>/dev/null
vbell off
defscrollback 5000
hardstatus alwayslastline
hardstatus string '%{gk}[ %{G}%H %{g}][%{= kw}%-w%{= BW}%n %t%{-}%+w][%= %{=b kR}(%{W} %h%?(%u)%?%{=b kR} )%{= kw}%=][%{Y}%l%{g}]%{=b C}[ %d.%m.%Y %c ]%{W}'
defutf8 on
shell -$SHELL
termcapinfo  xterm Z0=\E[?3h:Z1=\E[?3l:is=\E[r\E[m\E[2J\E[H\E[?7h\E[?1;4;6l
EOSCREEN
}

sysctl_setup()
{
echo "net.netfilter.nf_conntrack_max=99999999" >> /etc/sysctl.conf
echo "fs.inotify.max_user_watches=99999999" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_tw_buckets=99999999" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_tw_buckets_ub=65535" >> /etc/sysctl.conf
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
echo "net.ipv4.tcp_syncookies=1" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog=65536" >> /etc/sysctl.conf
echo "net.core.somaxconn=65535" >> /etc/sysctl.conf
echo "fs.file-max=99999999" >> /etc/sysctl.conf
echo "kernel.sem=1000 128000 128 512" >> /etc/sysctl.conf
echo "vm.dirty_ratio=5" >> /etc/sysctl.conf
echo "fs.aio-max-nr=262144" >> /etc/sysctl.conf
echo "kernel.panic=1" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.rp_filter=1" >> /etc/sysctl.conf
echo "kernel.sysrq=1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.send_redirects=1" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.send_redirects=0" >> /etc/sysctl.conf
echo "net.ipv4.ip_dynaddr=1" >> /etc/sysctl.conf
echo "kernel.sem=1000 256000 128 1024" >> /etc/sysctl.conf
echo "kernel.msgmni=1024" >> /etc/sysctl.conf
echo "fs.inotify.max_user_watches=524288" >> /etc/sysctl.conf
echo "fs.inotify.max_user_instances=1024" >> /etc/sysctl.conf
echo "kernel.msgmnb=65536" >> /etc/sysctl.conf
echo "kernel.msgmax=65536" >> /etc/sysctl.conf
echo "kernel.shmmax=4294967295" >> /etc/sysctl.conf
echo "kernel.shmall=268435456" >> /etc/sysctl.conf
echo "kernel.shmmni=4096" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_time=15" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_intvl=10" >> /etc/sysctl.conf
echo "net.ipv4.tcp_keepalive_probes=5" >> /etc/sysctl.conf
echo "net.ipv4.tcp_fin_timeout=30" >> /etc/sysctl.conf
echo "net.ipv4.tcp_window_scaling=0" >> /etc/sysctl.conf
echo "net.ipv4.tcp_sack=0" >> /etc/sysctl.conf
echo "net.ipv4.tcp_timestamps=0" >> /etc/sysctl.conf
echo "vm.swappiness=10" >> /etc/sysctl.conf
echo "vm.overcommit_memory=1" >> /etc/sysctl.conf
echo "fs.inotify.max_user_instances=256" >> /etc/sysctl.conf
sed -i 's/.*net.netfilter.nf_conntrack_max.*/net.netfilter.nf_conntrack_max=99999999/g' /etc/sysctl.conf
sed -i 's/.*fs.inotify.max_user_watches.*/fs.inotify.max_user_watches=99999999/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.net.ipv4.tcp_max_tw_buckets.*/net.ipv4.net.ipv4.tcp_max_tw_buckets=99999999/g' /etc/sysctl.conf
sed -i 's/.*tcp_max_tw_buckets_ub.*/net.ipv4.tcp_max_tw_buckets_ub=65535/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_max_tw_buckets_ub.*/net.ipv4.tcp_max_tw_buckets_ub=65535/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.ip_forward.*/net.ipv4.ip_forward=1/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_syncookies.*/net.ipv4.tcp_syncookies=1/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_max_syn_backlog.*/net.ipv4.tcp_max_syn_backlog=65536/g' /etc/sysctl.conf
sed -i 's/.*net.core.somaxconn.*/net.core.somaxconn=65535/g' /etc/sysctl.conf
sed -i 's/.*fs.file-max.*/fs.file-max=99999999/g' /etc/sysctl.conf
sed -i 's/.*kernel.sem.*/kernel.sem=1000 128000 128 512/g' /etc/sysctl.conf
sed -i 's/.*vm.dirty_ratio.*/vm.dirty_ratio=5/g' /etc/sysctl.conf
sed -i 's/.*fs.aio-max-nr.*/fs.aio-max-nr=262144/g' /etc/sysctl.conf
sed -i 's/.*kernel.panic.*/kernel.panic=1/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.conf.all.rp_filter.*/net.ipv4.conf.all.rp_filter=1/g' /etc/sysctl.conf
sed -i 's/.*kernel.sysrq.*/kernel.sysrq=1/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.conf.default.send_redirects.*/net.ipv4.conf.default.send_redirects=1/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.conf.all.send_redirects.*/net.ipv4.conf.all.send_redirects=0/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.ip_dynaddr.*/net.ipv4.ip_dynaddr=1/g' /etc/sysctl.conf
sed -i 's/.*kernel.sem.*/kernel.sem=1000 256000 128 1024/g' /etc/sysctl.conf
sed -i 's/.*kernel.msgmn.*/kernel.msgmn=1024/g' /etc/sysctl.conf
sed -i 's/.*fs.inotify.max_user_watches.*/fs.inotify.max_user_watches=524288/g' /etc/sysctl.conf
sed -i 's/.*fs.inotify.max_user_instances.*/fs.inotify.max_user_instances=1024/g' /etc/sysctl.conf
sed -i 's/.*kernel.msgmnb.*/kernel.msgmnb=65536/g' /etc/sysctl.conf
sed -i 's/.*kernel.msgmax.*/kernel.msgmax=65536/g' /etc/sysctl.conf
sed -i 's/.*kernel.shmmax.*/kernel.shmmax=4294967295/g' /etc/sysctl.conf
sed -i 's/.*kernel.shmall.*/kernel.shmall=268435456/g' /etc/sysctl.conf
sed -i 's/.*kernel.shmmni.*/kernel.shmmni=4096/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_keepalive_time.*/net.ipv4.tcp_keepalive_time=15/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_keepalive_intvl.*/net.ipv4.tcp_keepalive_intvl=10/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_keepalive_probes.*/net.ipv4.tcp_keepalive_probes=5/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_fin_timeout.*/net.ipv4.tcp_fin_timeout=30/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_window_scaling.*/net.ipv4.tcp_window_scaling=0/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_sack.*/net.ipv4.tcp_sack=0/g' /etc/sysctl.conf
sed -i 's/.*net.ipv4.tcp_timestamps.*/net.ipv4.tcp_timestamps=0/g' /etc/sysctl.conf 
sed -i 's/.*vm.swappiness.*/vm.swappiness=10/g' /etc/sysctl.conf 
sed -i 's/.*vm.overcommit_memory.*/vm.overcommit_memory=1/g' /etc/sysctl.conf 

mv -f /etc/sysctl.conf /etc/sysctl.old
cat /etc/sysctl.old | sed 's/ =/=/g' | sed 's/= /=/g' | grep -v -e \# -e ^$ > /etc/sysctl.new
awk '! a[$0]++' /etc/sysctl.new >  /etc/sysctl.conf

sysctl -p

cat > /etc/security/limits.d/nofile.conf << EOL
root      soft    nofile           1048576
root      hard    nofile           1048576
*         soft    nofile           1048576
*         hard    nofile           1048576    
*         hard    core           0
EOL

cat > /etc/security/limits.d/90-nproc.conf << EOL
*       hard    nproc   unlimited
*       soft    nproc   unlimited
root    hard    nproc   unlimited
root    soft    nproc   unlimited
EOL

cat > /etc/security/limits.d/90-stack.conf << EOL
*       hard    stack   unlimited
*       soft    stack   unlimited
root    hard    stack   unlimited
root    soft    stack   unlimited
EOL

ulimit -n 1048576
ulimit -i 386519
ulimit -u unlimited
ulimit -s unlimited
}

system_setup_c7()
{
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
setenforce 0
systemctl stop firewalld
systemctl disable firewalld
iptables -P INPUT ACCEPT ; iptables -P FORWARD ACCEPT ; iptables -P OUTPUT ACCEPT ; iptables -t nat -F  ; iptables -t mangle -F  ; iptables -F ; iptables -X

yum install -y http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-9.noarch.rpm
yum install -y http://rpms.famillecollet.com/enterprise/remi-release-8.rpm
yum install -y pwgen sshpass deltarpm psmisc e2fsprogs net-tools openssl yum-utils wget nano ntpdate patch telnet bind-utils expect nscd which ltrace mc sudo iftop ncdu htop ntp zip unzip pigz iotop sysstat lsof fuse fuse-sshfs strace atop multitail apg yum-plugin-replace mailx bash-completion git wget jq ansifilter certbot sipcalc
cat > /etc/yum.repos.d/nginx.repo << 'EONGINX'
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true

[nginx-mainline]
name=nginx mainline repo
baseurl=http://nginx.org/packages/mainline/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EONGINX
yum install -y nginx
yum install -y screen

yum install python3 python3-pip  -y
pip3 install flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml
}

system_setup_c8()
{
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
setenforce 0
systemctl stop firewalld
systemctl disable firewalld
iptables -P INPUT ACCEPT ; iptables -P FORWARD ACCEPT ; iptables -P OUTPUT ACCEPT ; iptables -t nat -F  ; iptables -t mangle -F  ; iptables -F ; iptables -X
yum config-manager --set-enabled powertools
yum install -y http://dl.fedoraproject.org/pub/epel/8/Everything/x86_64/Packages/e/epel-release-8-10.el8.noarch.rpm
yum install -y http://rpms.famillecollet.com/enterprise/remi-release-8.rpm
yum install -y pwgen sshpass deltarpm psmisc e2fsprogs net-tools openssl yum-utils wget nano ntpdate patch telnet bind-utils expect nscd which ltrace mc sudo iftop ncdu htop ntp zip unzip pigz iotop sysstat lsof fuse fuse-sshfs strace atop multitail apg yum-plugin-replace mailx bash-completion git wget jq ansifilter certbot screen sipcalc --skip-broken
cat > /etc/yum.repos.d/nginx.repo << 'EONGINX'
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true

[nginx-mainline]
name=nginx mainline repo
baseurl=http://nginx.org/packages/mainline/centos/$releasever/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
EONGINX
yum install -y nginx

yum install python3 python3-pip  -y
pip3 install cryptography flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml
}

system_setup_d9()
{
#install base soft
apt update
apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg2 git curl fuse sshfs sshpass screen jq python3 python3-pip certbot nginx
pip3 install flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml sipcalc
}

system_setup_d10()
{
#install base soft
apt update
apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg2 git curl fuse sshfs sshpass screen jq python3 python3-pip certbot nginx
pip3 install flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml sipcalc 
}

cld_install()
{
#generate self signed certificates
mkdir -p /etc/ssl/
mkdir -p /etc/ssl/certs/
mkdir -p /etc/ssl/private/
openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=example.com"
mkdir /var/log/cld &>/dev/null

#install cld
cd /var
git clone https://github.com/achendev/cld.git
cd cld

#sync files from repo
rsync -avzP /var/cld/setup/etc/ /etc/
rsync -avzP /var/cld/setup/access /var/cld/
rsync -avzP /var/cld/setup/creds /var/cld/

#set path
sed -i '/PATH/d' /root/.bashrc ; 
cat >> /root/.bashrc << 'EOBASHRC'
export CLD_PATH="/var/cld/bin:/var/cld/deploy/bin:/var/cld/cm/bin:$(echo -n "$(ls -d /var/cld/modules/*/bin)" | tr "\n" :)"
PATH="$PATH:$CLD_PATH"
EOBASHRC

HOSTIP=$(wget -qO- ipinfo.io/ip)
sed -i "s#your.host.or.ip#${HOSTIP}#g" /var/cld/creds/creds

/var/cld/bin/init-main

echo "admin:::ALL:ALL" >> /var/cld/creds/passwd
/var/cld/bin/cld-initpasswd
echo http://${HOSTIP}
}

if grep --quiet 'stretch' /etc/*-release ; then
sysctl_setup
bash_conf
system_setup_d9
cld_install
elif grep --quiet 'buster' /etc/*-release ; then
sysctl_setup
bash_conf
system_setup_d10
cld_install
elif grep --quiet 'Linux release 7' /etc/*-release ; then
system_setup_c7
sysctl_setup
bash_conf
cld_install
elif grep --quiet 'CentOS Linux 8' /etc/*-release ; then
sysctl_setup
bash_conf
system_setup_c8
cld_install
elif grep --quiet 'xenial\|yakkety' /etc/*-release ; then
sysctl_setup
bash_conf
system_setup_u16
cld_install
elif grep --quiet 'bionic\|cosmic' /etc/*-release ; then
sysctl_setup
bash_conf
system_setup_u18
cld_install
else
echo Operation system is not supported
fi
