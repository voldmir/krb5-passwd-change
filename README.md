# krb5-passwd-change

apt-get install libkrb5-devel -y
apt-get install python3-dev -y
apt-get install gcc -y

cd lib/krb5
python3 setup.py build_ext -i

$(python3-config --includes --ldflags) -fPIC -shared -o krb5.o krb5.c

apt-get install python3-module-flask -y
apt-get install krb5-kinit -y

