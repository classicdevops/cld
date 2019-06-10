#!/bin/bash
install_cld()
{
#install base soft
apt update
apt install apt-transport-https ca-certificates curl software-properties-common gnupg2 git curl fuse sshfs sshpass screen supervisor -y

#install docker python
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable"
apt update
apt install docker-ce docker-compose python python3-pip  -y
pip3 install flask redis python-pam

#install yarn nodejs
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt-get update && apt install yarn -y
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
apt-get install -y nodejs

#install cld
cd /var
git clone https://github.com/achendev/cld.git
cd cld

#install wetty.js
git clone https://github.com/achendev/wetty.git
cd wetty
yarn
yarn build
sed -i -r 's#(.*res\.setHeader.*)#//\1#g' /var/cld/wetty/node_modules/frameguard/index.js

#install RichFileManager
cd /var/cld
git clone https://github.com/achendev/RichFilemanager-Python3Flask.git
cd RichFilemanager-Python3Flask
pip3 install Image
ip addr add 172.17.0.250/16 dev docker0

#sync files from repo
rsync -avzP /var/cld/setup/etc/ /etc/
rsync -avzP /var/cld/setup/access /var/cld/
rsync -avzP /var/cld/setup/creds /var/cld/

#xtermnginx enable
cd /var/cld/docker/xtermnginx/
touch /var/cld/docker/xtermnginx/etc/nginx/conf.d/sessid
docker-compose up -d

HOSTIP=$(wget -qO- ipinfo.io/ip)
sed -i "s#your.host.or.ip#${HOSTIP}#g" /var/cld/creds/creds

systemctl restart supervisor
systemctl enable supervisor

echo http://${HOSTIP}
/var/cld/bin/cld-useradd admin $(< /dev/urandom tr -dc A-Za-z0-9 | head -c${1:-21})
}
echo;echo;echo;echo;echo
cat /etc/*-release | grep -q stretch && install_cld || echo "OS not is Debian 9"
