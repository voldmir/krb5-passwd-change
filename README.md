# krb5-passwd-change

apt-get install libkrb5-devel -y
apt-get install python3-dev -y
apt-get install gcc -y

cd lib/krb5
python3 setup.py build_ext -i

 $(python3-config --includes --ldflags) -fPIC -shared -o krb5.o krb5.c


apt-get install python3-module-flask -y
apt-get install krb5-kinit -y


scp -r -i H:\\ssh\\cit\\id_rsa_ansible ../krb5-passwd-change citadmin-ansible@10.2.124.27:/opt/service

 curl -c ~/cookie --location --request POST 'http://127.0.0.1:5000/api/username' --form 'username="kbst" ' --form 'password="dger5$$*"'
 curl -b ~/cookie --location --request PATCH 'http://127.0.0.1:5000/api/username'  --form 'password_new="ssd**D54df4"'
 curl -b ~/cookie --location --request PUT 'http://127.0.0.1:5000/api/username' --form 'password_new="vfd)gf8*"'
