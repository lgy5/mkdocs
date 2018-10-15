## openvpn
```
客户端   192.168.1.0/24 
vpn服务端分配 10.8.0.0/24   服务端内网  192.168.9.0/24    一定不能和客户端内网一样

客户端要连服务端内网其他服务器需要加路由
route add -net 10.8.0.0 netmask 255.255.255.0 gw vpn服务器的192.168.9.0/24段的IP

yum install openvpn easy-rsa -y

cd /usr/share/easy-rsa/3
vim vars
export KEY_COUNTRY="CN"
export KEY_PROVINCE="SH"
export KEY_CITY="ShangHai"
export KEY_ORG="Company"
export KEY_EMAIL="liangguangyu@dachuizichan.com"
export KEY_OU="MyOrganization"

source vars

./easyrsa init-pki # 初始化证书目录pki
./easyrsa build-ca nopass # 创建根证书，提示输入Common Name，名称随意，但是不能和服务端证书或客户端证书名称相同
cp pki/ca.crt /etc/openvpn/
./easyrsa gen-dh # 生成Diffle Human参数，它能保证密钥在网络中安全传输
cp pki/dh.pem /etc/openvpn/

./easyrsa build-server-full server nopass # server是服务端证书名称，可以用其它名称

./easyrsa build-client-full npt02 nopass # client是客户端名称 每个客户端生成一个
./easyrsa build-client-full nix02 nopass
./easyrsa build-client-full nix22 nopass  名字和/etc/openvpn/ccd 里面文件对应

cd pki/private/ && cp * /etc/openvpn/ 已经有的可以不覆盖
cd ../../pki/issued && cp * /etc/openvpn/ 
cp /usr/share/doc/openvpn-2.4.5/sample/sample-config-files/server.conf /etc/openvpn/
cat /etc/openvpn/server.conf
local ip # 填服务器真实IP
port 1194
proto tcp
dev tun
ca /etc/openvpn/ca.crt
cert /etc/openvpn/server.crt
key /etc/openvpn/server.key
dh /etc/openvpn/dh.pem
server 10.8.0.0 255.255.255.0 # 给客户端分配的IP段

client-config-dir /etc/openvpn/ccd
route 192.168.69.0 255.255.255.0
route 192.168.73.0 255.255.255.0
route 192.168.81.0 255.255.255.0
push "route 192.168.69.0 255.255.255.0" # 重定向客户端网关
push "route 192.168.73.0 255.255.255.0" # 重定向客户端网关
push "route 192.168.81.0 255.255.255.0" # 重定向客户端网关
#duplicate-cn 允许客户使用一样的client.key client.crt

client-to-client
keepalive 10 120
comp-lzo
max-clients 10
user nobody
group nobody
persist-key
persist-tun
status /var/log/openvpn-status.log
log /var/log/openvpn.log
verb 3 # 日志等级

cat /etc/openvpn/ccd/npt02   #客户端网络信息
iroute 192.168.69.0 255.255.255.0
cat /etc/openvpn/ccd/nix02
iroute 192.168.73.0 255.255.255.0
cat /etc/openvpn/ccd/npt22
iroute 192.168.81.0 255.255.255.0



net.ipv4.ip_forward = 1  /etc/sysctl.conf   sysctl -p   要内网互通每个都需要配置ip转发
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE  tun0的数据转发到eth0（192.168.9.0/24）
service iptables save
/etc/init.d/openvpn start

客户端
从服务器拷贝ca.crt nix02.crt  nix02.key  到客户端.每个客户端的 nix02.crt  nix02.key不通
dacui.ovpn 内容： 
client
proto tcp
dev tun
remote 服务器ip 11947
persist-key
persist-tun
comp-lzo
ca ca.crt
cert nix02.crt
key nix02.key
verb 3

windows客户端 C:\Program Files\OpenVPN\config\目录下

启动客户端
```



## pptpd
```
yum install ppp pptpd

/etc/pptpd.conf
localip 10.0.0.1
remoteip 10.0.0.100-200
上面的IP地址是可以随便填的，ABC三类的内网地址都可以，主要兼顾其他地方的IP配置，不要出现IP冲突就可以了，后面的remoteip，
默认从第一个10.0.0.100开始分配给客户，localip表示分配给服务器的内部网关地址。

/etc/ppp/pptpd-options
ms-dns 202.96.128.86
ms-dns 202.96.128.166
这里配置成客户端所在地的DNS就好了

/etc/ppp/chap-secrets
依次为：账号，协议，密码，ip地址
chap-secret

service pptpd start
chkconfig pptpd on
日志 在 /var/log/messages


net.ipv4.ip_forward = 1
sysctl -p

pptp需要用到的端口
pptp使用到的端口只有一个，那就是1723，网上有很多误人子弟的文章还说要开47端口，真是坑爹，因为GRE协议号是47，并不代表需要开47端口，
因此如果是要映射端口的话，1723就完全够了，不要信网上的某些教程,如果使用了iptable来作为防火墙，需要加入规则
iptables -A INPUT -p tcp --dport 1723 -j ACCEPT
iptables -A INPUT -p 47 -j ACCEPT
如果是在内网中，需要网关转发，那么网关需要如下配置：
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 1723 -j DNAT --to SERVER_IP
iptables -t nat -A PREROUTING -i eth0 -p 47 -j DNAT --to SERVER_IP

配置防火墙转发
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
或
iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j SNAT --to 115.115.115.115
其中第一种比较简单，自动伪装ip，第二种的10.0.0.0/24指的是VPN虚拟内网，而115.115.115.115代表外网地址，进行NAT。如果VPN服务器是
用来代理上网的，仅有上面的配置会出现访问网站缓慢的情况，需要手动修改一下转发包的mss
iptables -A FORWARD -p tcp --syn -s 10.0.0.0/24 -j TCPMSS --set-mss 1356

这样就不会出现打不开网页的问题了，最后可以保存一下防火墙。

访问限制
iptables -A FORWARD -p tcp -s 10.0.0.0/24 -d 180.97.163.157 -j ACCEPT  只允许访问180.97.163.157
iptables -A FORWARD -p tcp -s 10.0.0.0/24 -j DROP
```

## shadowsocks
https://copr.fedorainfracloud.org/coprs/librehat/shadowsocks/

centos6

```
[librehat-shadowsocks]
name=Copr repo for shadowsocks owned by librehat
baseurl=https://copr-be.cloud.fedoraproject.org/results/librehat/shadowsocks/epel-6-$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/librehat/shadowsocks/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1
```

centos7

```
[librehat-shadowsocks]
name=Copr repo for shadowsocks owned by librehat
baseurl=https://copr-be.cloud.fedoraproject.org/results/librehat/shadowsocks/epel-7-$basearch/
type=rpm-md
skip_if_unavailable=True
gpgcheck=1
gpgkey=https://copr-be.cloud.fedoraproject.org/results/librehat/shadowsocks/pubkey.gpg
repo_gpgcheck=0
enabled=1
enabled_metadata=1
```