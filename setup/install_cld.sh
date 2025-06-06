#!/bin/bash

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/cld-install.log
}

# Ensure log directory exists
mkdir -p /var/log || true

# Bash configuration
bash_conf() {
    log "Configuring bash environment"
    localedef -i en_US -f UTF-8 en_US.UTF-8 2>/dev/null || true
    export LC_ALL="en_US.UTF-8"

    # Backup existing i18n file
    mkdir -p /root/backup/etc/sysconfig/ || true
    if [ -f /etc/sysconfig/i18n ]; then
        cp /etc/sysconfig/i18n "/root/backup/etc/sysconfig/i18n.$(date +%Y-%m-%d_%H-%M)" || true
    fi

    # Set locale configuration
    cat > /etc/sysconfig/i18n << EOL
LANG="en_US.UTF-8"
SUPPORTED="en_US.UTF-8:en_US:ru"
SYSFONT="latarcyrheb-sun16"
EOL

    # Configure bash prompt
    cat > /etc/profile.d/bash.sh << EOL
PS1='\[\033[01;31m\]\u\[\033[01;33m\]@\[\033[01;36m\]\H \[\033[01;33m\]\w \[\033[01;35m\]\$ \[\033[00m\] '
TERM=xterm
EOL

    # Modify sudoers safely
    sed -i 's/Defaults\    requiretty/#Defaults\    requiretty/g' /etc/sudoers 2>/dev/null || true

    # Configure screen
    cat << 'EOSCREEN' > /root/.screenrc
vbell off
defscrollback 5000
hardstatus alwayslastline
hardstatus string '%{gk}[ %{G}%H %{g}][%{= kw}%-w%{= BW}%n %t%{-}%+w][%= %{=b kR}(%{W} %h%?(%u)%?%{=b kR} )%{= kw}%=][%{Y}%l%{g}]%{=b C}[ %d.%m.%Y %c ]%{W}'
defutf8 on
shell -\$SHELL
termcapinfo xterm Z0=\E[?3h:Z1=\E[?3l:is=\E[r\E[m\E[2J\E[H\E[?7h\E[?1;4;6l
EOSCREEN
    cp /root/.screenrc /etc/skel/.screenrc 2>/dev/null || true
}

# System control configuration
sysctl_setup() {
    log "Configuring sysctl parameters"
    local sysctl_file="/etc/sysctl.conf"
    local temp_file="/etc/sysctl.new"
    local backup_file="/etc/sysctl.old"

    # Define sysctl parameters
    local settings=(
        "net.netfilter.nf_conntrack_max=99999999"
        "fs.inotify.max_user_watches=524288"
        "net.ipv4.tcp_max_tw_buckets=99999999"
        "net.ipv4.tcp_max_tw_buckets_ub=65535"
        "net.ipv4.ip_forward=1"
        "net.ipv4.tcp_syncookies=1"
        "net.ipv4.tcp_max_syn_backlog=65536"
        "net.core.somaxconn=65535"
        "fs.file-max=99999999"
        "kernel.sem=1000 256000 128 1024"
        "vm.dirty_ratio=5"
        "fs.aio-max-nr=262144"
        "kernel.panic=1"
        "net.ipv4.conf.all.rp_filter=1"
        "kernel.sysrq=1"
        "net.ipv4.conf.default.send_redirects=1"
        "net.ipv4.conf.all.send_redirects=0"
        "net.ipv4.ip_dynaddr=1"
        "kernel.msgmni=1024"
        "fs.inotify.max_user_instances=1024"
        "kernel.msgmnb=65536"
        "kernel.msgmax=65536"
        "kernel.shmmax=4294967295"
        "kernel.shmall=268435456"
        "kernel.shmmni=4096"
        "net.ipv4.tcp_keepalive_time=15"
        "net.ipv4.tcp_keepalive_intvl=10"
        "net.ipv4.tcp_keepalive_probes=5"
        "net.ipv4.tcp_fin_timeout=30"
        "net.ipv4.tcp_window_scaling=0"
        "net.ipv4.tcp_sack=0"
        "net.ipv4.tcp_timestamps=0"
        "vm.swappiness=10"
        "vm.overcommit_memory=1"
    )

    # Backup existing sysctl.conf
    cp "$sysctl_file" "$backup_file" 2>/dev/null || true

    # Write settings to temporary file
    : > "$temp_file"
    for setting in "${settings[@]}"; do
        echo "$setting" >> "$temp_file"
    done

    # Remove duplicates and clean up
    awk '!seen[$0]++' "$temp_file" > "$sysctl_file" 2>/dev/null || true
    rm -f "$temp_file" 2>/dev/null || true

    # Apply sysctl settings
    sysctl -p 2>/dev/null || true

    # Configure limits
    cat > /etc/security/limits.d/nofile.conf << EOL
root      soft    nofile           1048576
root      hard    nofile           1048576
*         soft    nofile           1048576
*         hard    nofile           1048576
*         hard    core             0
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

    # Set ulimits
    ulimit -n 1048576 2>/dev/null || true
    ulimit -i 386519 2>/dev/null || true
    ulimit -u unlimited 2>/dev/null || true
    ulimit -s unlimited 2>/dev/null || true
}

# Common system setup for CentOS
centos_common_setup() {
    log "Performing common CentOS setup"
    sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config 2>/dev/null || true
    setenforce 0 2>/dev/null || true
    systemctl stop firewalld 2>/dev/null || true
    systemctl disable firewalld 2>/dev/null || true

    # Clear iptables
    iptables -P INPUT ACCEPT 2>/dev/null || true
    iptables -P FORWARD ACCEPT 2>/dev/null || true
    iptables -P OUTPUT ACCEPT 2>/dev/null || true
    iptables -t nat -F 2>/dev/null || true
    iptables -t mangle -F 2>/dev/null || true
    iptables -F 2>/dev/null || true
    iptables -X 2>/dev/null || true

    # Install nginx repository
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
}

# CentOS 7 setup
system_setup_c7() {
    log "Setting up CentOS 7"
    centos_common_setup
    yum install -y https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm 2>/dev/null || true
    yum install -y epel-release remi-release-8.rpm 2>/dev/null || true
    yum install -y pwgen sshpass deltarpm psmisc e2fsprogs net-tools openssl yum-utils wget nano ntpdate patch telnet bind-utils expect nscd which ltrace mc sudo iftop ncdu htop ntp zip unzip pigz iotop sysstat lsof fuse fuse-sshfs strace atop multitail apg yum-plugin-replace mailx bash-completion git jq ansifilter certbot sipcalc openvpn nginx screen python3 python3-pip python*-crypto python*-cryptography certbot 2>/dev/null || true
    pip3 install flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml certbot certbot-dns-cloudflare cryptography==3.2 zope.interface==5.3.0a1 2>/dev/null || true
    yum install -y https://kojipkgs.fedoraproject.org//packages/whatmask/1.2/27.fc34/x86_64/whatmask-1.2-27.fc34.x86_64.rpm 2>/dev/null || true
}

# CentOS 8 setup
system_setup_c8() {
    log "Setting up CentOS 8"
    centos_common_setup
    yum config-manager --set-enabled powertools 2>/dev/null || true
    yum install -y http://dl.fedoraproject.org/pub/epel/8/Everything/x86_64/Packages/e/epel-release-8-10.el8.noarch.rpm remi-release-8.rpm 2>/dev/null || true
    yum install -y pwgen sshpass deltarpm psmisc e2fsprogs net-tools openssl yum-utils wget nano ntpdate patch telnet bind-utils expect nscd which ltrace mc sudo iftop ncdu htop ntp zip unzip pigz iotop sysstat lsof fuse fuse-sshfs strace atop multitail apg yum-plugin-replace mailx bash-completion git wget jq ansifilter certbot screen sipcalc openvpn nginx python39 python39-pip python*-crypto python*-cryptography certbot python3-certbot-dns-cloudflare --skip-broken 2>/dev/null || true
    pip3.9 install cryptography flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml certbot certbot-dns-cloudflare zope.interface 2>/dev/null || true
    dnf install -y https://kojipkgs.fedoraproject.org//packages/whatmask/1.2/27.fc34/x86_64/whatmask-1.2-27.fc34.x86_64.rpm 2>/dev/null || true
    dnf group install "Development Tools" -y 2>/dev/null || true
    install_ansifilter
    ln -fs /usr/bin/python3.9 /usr/bin/python3 2>/dev/null || true
    ln -fs /usr/bin/pip3.9 /usr/bin/pip3 2>/dev/null || true
}

# CentOS 9 setup
system_setup_c9() {
    log "Setting up CentOS 9"
    centos_common_setup
    dnf config-manager --set-enabled powertools 2>/dev/null || true
    dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm https://rpms.remirepo.net/enterprise/remi-release-9.rpm 2>/dev/null || true
    dnf install -y pwgen sshpass deltarpm psmisc e2fsprogs net-tools openssl yum-utils wget nano ntpdate patch telnet bind-utils expect nscd which ltrace mc sudo iftop ncdu htop ntp zip unzip pigz iotop sysstat lsof fuse fuse-sshfs strace atop multitail apg yum-plugin-replace mailx bash-completion git wget jq ansifilter certbot screen sipcalc openvpn nginx python39 python39-pip python*-crypto python*-cryptography certbot python3-certbot-dns-cloudflare --skip-broken 2>/dev/null || true
    pip3.9 install cryptography flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml certbot certbot-dns-cloudflare zope.interface 2>/dev/null || true
    dnf install -y https://kojipkgs.fedoraproject.org//packages/whatmask/1.2/27.fc34/x86_64/whatmask-1.2-27.fc34.x86_64.rpm 2>/dev/null || true
    dnf group install "Development Tools" -y 2>/dev/null || true
    install_ansifilter
    ln -fs /usr/bin/python3.9 /usr/bin/python3 2>/dev/null || true
    ln -fs /usr/bin/pip3.9 /usr/bin/pip3 2>/dev/null || true
}

# Debian common setup
debian_common_setup() {
    log "Performing common Debian setup"
    apt update 2>/dev/null || true
    apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg2 git curl fuse sshfs sshpass screen jq python3 python3-pip certbot nginx sipcalc uuid-runtime openvpn expect 2>/dev/null || true
    pip3 install flask redis python-pam Image flask_session flask_socketio pytelegrambotapi lxml 2>/dev/null || true
    install_ansifilter
    install_whatmask
}

# Debian 9 setup
system_setup_d9() {
    log "Setting up Debian 9"
    debian_common_setup
}

# Debian 10 setup
system_setup_d10() {
    log "Setting up Debian 10"
    debian_common_setup
}

# Install ansifilter
install_ansifilter() {
    log "Installing ansifilter"
    cd /usr/src || return
    git clone https://github.com/andre-simon/ansifilter.git 2>/dev/null || true
    cd ansifilter || return
    make 2>/dev/null && make install 2>/dev/null || true
}

# Install whatmask
install_whatmask() {
    log "Installing whatmask"
    cd /usr/src || return
    wget -q http://downloads.laffeycomputer.com/current_builds/whatmask/whatmask-1.2.tar.gz 2>/dev/null || return
    tar zxvf whatmask-1.2.tar.gz 2>/dev/null || return
    cd whatmask-1.2 || return
    ./configure 2>/dev/null && make 2>/dev/null && make install 2>/dev/null || true
}

# CLD installation
cld_install() {
    log "Installing CLD"
    # Generate self-signed certificates
    mkdir -p /etc/ssl/certs /etc/ssl/private || true
    openssl req -x509 -nodes -days 3650 -newkey rsa:4096 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/C=GB/ST=London/L=London/O=Global Security/OU=IT Department/CN=example.com" 2>/dev/null || true

    # Install CLD
    cd /var || return
    git clone https://github.com/achendev/cld.git 2>/dev/null || true
    cd cld || return

    # Sync files
    rsync -avz --no-perms /var/cld/setup/etc/ /etc/ 2>/dev/null || true
    rsync -avz --no-perms /var/cld/setup/access /var/cld/ 2>/dev/null || true
    rsync -avz --no-perms /var/cld/setup/creds /var/cld/ 2>/dev/null || true

    # Set path
    sed -i '/PATH/d' /root/.bashrc 2>/dev/null || true
    cat >> /root/.bashrc << 'EOBASHRC'
export CLD_PATH="/var/cld/bin:$(echo -n "$(ls -d /var/cld/modules/*/bin 2>/dev/null)" | tr "\n" :)"
PATH="$PATH:$CLD_PATH"
EOBASHRC

    # Configure CLD
    HOSTIP=$(wget -qO- ip.cldcloud.com 2>/dev/null || echo "localhost")
    sed -i "s#your.host.or.ip#${HOSTIP}#g" /var/cld/creds/creds 2>/dev/null || true
    /var/cld/bin/init-main 2>/dev/null || true
    echo "admin:::ALL:ALL:default" >> /var/cld/creds/passwd 2>/dev/null || true
    /var/cld/bin/cld-update 2>/dev/null || true

    # Set environment
    export CLD_PATH="/var/cld/bin:$(echo -n "$(ls -d /var/cld/*/bin /var/cld/modules/*/bin 2>/dev/null)" | tr "\n" :)"
    PATH="$PATH:$CLD_PATH"

    # Enable IP access
    mytty="$(tty | cut -d / -f 3-)"
    myip="$(w | grep "$mytty" | awk '{print $3}' || echo 'localhost')"
    /var/cld/modules/access/bin/cld-enableip "$myip" user_install_ip 2>/dev/null || true

    # Display deployment information
    CLD_DOMAIN=$(grep "CLD_DOMAIN=" /var/cld/creds/creds | cut -d = -f 2 | tr -d '"' || echo "localhost")
    cat << DEPLOYOUTPUT
Thanks for choosing the CLD!
CLD Dashboard is available at:
"https://${CLD_DOMAIN}" (recommended - ensure correct DNS record, SSL will be issued automatically)
"https://${HOSTIP}" (some features may not be available with self-signed certificate)

user: Admin
password: $(cat /home/admin/.cldusercreds 2>/dev/null || echo "check /home/admin/.cldusercreds")
DEPLOYOUTPUT
}

# Main installation logic
main() {
    log "Starting CLD installation"
    if grep -q 'stretch' /etc/*-release; then
        sysctl_setup
        bash_conf
        system_setup_d9
        cld_install
    elif grep -q 'buster' /etc/*-release; then
        sysctl_setup
        bash_conf
        system_setup_d10
        cld_install
    elif grep -q 'Linux release 7' /etc/*-release; then
        system_setup_c7
        sysctl_setup
        bash_conf
        cld_install
    elif grep -q 'CentOS Linux 8\|CentOS Stream 8' /etc/*-release; then
        sysctl_setup
        bash_conf
        system_setup_c8
        cld_install
    elif grep -q 'CentOS Stream 9\|AlmaLinux 9' /etc/*-release; then
        sysctl_setup
        bash_conf
        system_setup_c9
        cld_install
    else
        log "Unsupported operating system"
        echo "Operation system is not supported"
        exit 1
    fi
    log "CLD installation completed"
}

main