## bind
```
yum install bind bind-utils -y

修改主配置

vi /etc/named.conf

listen-on port 53 {any;};

//将监听的地址改为any,监听本机的所有地址。

listen-on-v6 port 53 {any;};

allow-query     { any; };

//改为any,允许任意主机查询

zone "xx.com" IN {   

    type master;

    file "xx.com.zone";

    allow-update { none; };

};

//添加正向解析区域 xx.com

//使用file 参数指出该区域的数据库文件（默认/var/named目录下，根据主配置文件的参数决定）

修改zone文件

cd /var/named

cp named.localhost xx.com.zone

chmod 644 xx.com.zone //使named用户拥有读取的权限

vi xx.com.zone  //编辑数据库文件，设置解析条目


    NS      @

    A       192.168.128.133

    AAAA    ::1


www     A       192.168.128.133

*.ic        A       10.215.105.7

statics.ic    A       10.215.105.7

//格式如图所示。   A 对应 IPv4的解析条目   AAAA对应IPv6的解析条目。

//注意不可缺少


    A       192.168.128.133

    AAAA    ::1


不能缺少没有主机名的这两项，否则会造成服务无法启动。逆向解析数据库也是如此。

创建逆向解析条目和数据库

vi /etc/named.rfc1912.zones  //编辑DNS辅配置文件

//参考末尾的逆向解析条目，创建自己的逆向解析。

zone "128.168.192.in-addr.arpa" IN {

    type master;

    file "128.168.192.zone";

    allow-update { none; };


};

//注意格式问题，比如IP地址点分十进制的格式，每个十进制为一个整体，倒着书写，且不写主机位。

//“.in-addr.arpa” 为逆向解析的固定格式  不能写错。

//数据库文件可以新建，也可以使用正向的数据库，在其中添加逆向的条目。

//注意权限问题。

cd /var/named

cp named.localhost 128.168.192.zone

chmod 644 128.168.192.zone

编辑逆向解析条目

vi 128.168.192.zone

133     PTR www.xx.com.

//此为逆向解析的条目格式

不能缺少没有主机名的这两项，否则会造成服务无法启动。逆向解析数据库也是如此。

重启服务，进行检测

service named restart
```

## bind edns
```
https://blog.gnuers.org/?p=1379

yum install GeoIP GeoIP-devel
./configure --prefix=/usr/local/bind9.12.0 --with-geoip=/usr/share/GeoIP/ --enable-threads
make && make install
./sbin/rndc-confgen -r /dev/urandom > etc/rndc.conf

dig测试 dig在源码编译目录下的 /root/bind-9.12.1-P2/bin/dig/dig
./bin/dig/dig @127.0.0.1 a.test.com +subnet=172.1.1.1/24
含有OPT PSEUDOSECTION表示支持edns

acl zone1 { ecs 10.0.0.0/8;  10.0.0.0/8; };
acl zone2 { ecs 172.0.0.0/8;172.0.0.0/8; };
acl ecs-zone1 { ecs 10.0.0.0/8;  };
acl ecs-zone2 { ecs 172.0.0.0/8;};
view  "ecs-zone1" { match-clients  {ecs-zone1;}; zone "test.org" { type master; file "ecszone/test.org" ;}; };
view  "ecs-zone2" { match-clients  {ecs-zone2;}; zone "test.org" { type master; file "ecszone2/test.org" ;}; };
view  "zone1" { match-clients  {zone1;}; zone "test.org" { type master; file "zone/test.org" ;}; };
view  "zone2" { match-clients  {zone2;}; zone "test.org" { type master; file "zone2/test.org" ;}; };

dig @10.10.0.15 test100.test.org
dig @172.18.0.6 test100.test.org
dig @10.10.0.15 test100.test.org  +subnet=172.1.1.1/24
dig @10.10.0.15 test100.test.org  +subnet=10.1.1.1/24
dig @172.18.0.6 test100.test.org  +subnet=10.1.1.1/24
dig @172.18.0.6 test100.test.org  +subnet=172.1.1.1/24

cat /etc/init.d/named
#!/bin/bash 
# named a network name service. 
# chkconfig: 345 35 75 
# description: a name server

PIDFILE='/var/named/named.pid'
BASEDIR='/usr/local/bind9.12.0'
if [ `id -u` -ne 0 ]; then
	echo "ERROR:For bind to port 53,must run as root." 
	exit 1
fi
case "$1" in
start)
	if [ -x $BASEDIR/sbin/named ]; then
		if [ -e $PIDFILE ]; then
			echo 'BIND9 already started'
		else
			$BASEDIR/sbin/named -u named -c /etc/named.conf  && echo . && echo 'BIND9 server started' 
		fi
	fi
;;
stop)
	if [ -e $PIDFILE ]; then
		/bin/kill -9 `cat $PIDFILE` && echo . && echo 'BIND9 server stopped' 
	else
		echo 'BIND9 already stopped'
	fi
	rm $PIDFILE -f
;;
restart)
	echo . 
	echo "Restart BIND9 server" 
	$0 stop
	sleep 3
	$0 start
;;
reload)
	$BASEDIR/sbin/rndc reload
;;
status)
	$BASEDIR/sbin/rndc status
;;
*)
echo "$0 start | stop | restart |reload |status" 
;;
esac
```
