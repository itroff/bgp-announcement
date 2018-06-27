# bgp-announcement
Python 2.7 based script for announce and withdraw routes with Exabgp from file.
New route announce (withdraw) when file (net.txt) changed

RUN

/usr/local/bin/exabgp /home/bgp/exabgp.conf -f /home/bgp/ -e /home/bgp/exabgp.env

INSTALL README
1. sudo apt install python-minimal python-pip
2. sudo locale-gen "ru_RU.UTF-8"
3. sudo dpkg-reconfigure locales
4. git clone https://github.com/Exa-Networks/exabgp.git
5. git checkout 3.4.13
6. python2.7 ./setup.py build
7. sudo python2.7 ./setup.py install 
8. git clone **bgp-announcement**
9. su bgp
10. pip install netaddr
11. exabgp -f /home/bgp/bgp-announcement -e /home/bgp/bgp-announcement/exabgp.env /home/bgp/bgp-announcement/exabgp.conf