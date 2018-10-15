## 运维
```
运维的本质是“可控”。运维是一门非常复杂的学问，不像学会两三门语言，设计几个网站应用就可以成为
架构师那样的工作。
他除了技术之外，经验积累、视野、大局观、甚至是心胸都有可能决定成败。优秀的开发者比比皆是，
但是优秀的运维人员少之又少。

原因就是运维内容太复杂了！而我为什么说运维的本质是“可控”，大概有以下几个原因：

第一点：稳定性“可控”

运维不是维护一两台机器，发布代码就好，而是要做成千上万，甚至十几万台的服务器和各种网络设备、
存储设备等专有设备维护，
这些服务器包含webserver，DB，cache，cdn，computing多种类型，如何让这些大量的服务器稳定
的跑在生产环境中，
不因为硬件损坏、发布变更、系统升级而引发的业务系统故障。没有东西是不会坏的，没有系统是
没有bug的。硬件要坏，系统升级，发布变更，
这些都没有关系，但是最重要的，一旦发生这些之后，运维人员知道，这会业务影响多大!?需要多少
时间和工作量恢复?

第二点：性能“可控”

我和DBA一起维护DB多年，DBA最痛苦的地方，不在于“慢”，而在于时快时慢。一个不稳定的性能，
就无法预估承受业务压力需要的系统规模，
这样对于DBA在维护是无异于自杀。很多云计算厂商做设计的时候，往往也会忽略这一点，其实
性能的问题，比最高性能，来的重要的多！
非常漂亮的数字不能解决问题，但是一次性能的不足，可能就引发故障。

第三点：安全“可控”

有没有绝对的安全呢？理论上没有，所以，运维的同学，总要花很多精力在系统安全上，比如控制哪
些用户可以登录系统环境？
哪些用户是可以进行变更？哪些用户甚至可以拿到最高权限？测试和开发隔离，公司内外隔离，都是
因此而生。只要能够控制权限的面积，范围，
就能知道风险，这边是所谓的安全“可控”。

重要如上所示，但是正如一开头所说，运维的内容相当复杂，交付“可控”，变更内容“可控”，效率“
可控”都是可以值得深究的东西，因此，
无论是“可视化”，“大数据”，“运维自动化”等等，都是在为“运维可控”服务的。数据可视化，带来的
是规模可控；运维自动化，带来的是效率可控，
风险可控，如是而已。

每一个点的提升，都是运维的提升，希望所有从事运维的同学，都能感受到，做什么可以让“可控力”
提升，不要再半夜的时候处理故障，
不要和女朋友看电影的时候回公司处理故障，也许我们再次遇到这些问题的时候，可以拿起一杯茶，
做一个优雅的运维。
```



## 360文档
```
360文库复制时总要登陆

开发者工具---console里输入
[...document.getElementsByTagName('*')].forEach(x => x.oncopy = function(){})
```



## teredo
```
@echo off

net start "ip helper"
netsh int ipv6 reset

netsh int teredo set state default
netsh int 6to4 set state disable
netsh int isatap set state disable
::netsh int teredo set state server=teredo.remlab.net
netsh int teredo set state server=teredo.trex.fi
netsh int ipv6 set teredo enterpriseclient
netsh int ter set state enterpriseclient
route DELETE ::/0
netsh int ipv6 add route ::/0 "Teredo Tunneling Pseudo-Interface"
netsh int ipv6 set prefix 2002::/16 30 1
netsh int ipv6 set prefix 2001::/32 5 1

ipconfig /flushdns
route print
netsh int ipv6 show int
netsh int ipv6 show teredo
cmd


win10开启
netsh interface Teredo set state disable
netsh interface Teredo set state type=default
netsh interface teredo set state enterpriseclient server=teredo.remlab.net
ping -6 ipv6.test-ipv6.com
ping -6 [2001:470:1:18::125]
```



## steam下载
```
@echo
color 09
echo 放入steam目录 循环启动Steam
:down
ping 127.0.0.1 -n 1800 >nul
taskkill /f /im Steam.exe
start Steam.exe
goto down
pause

```



## 百度语音
```
# coding=utf-8
# pip install baidu-aip
from aip import AipSpeech

APP_ID = '9953283'
API_KEY = 'p3grxzGIU55uApjDO56vXVNE'
SECRET_KEY = 'sEFXAWrwPDackWSqo4tCsTtNNZlRlBiB'

# 初始化AipSpeech对象
aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


def hecheng(txt):   #语音合成
    result = aipSpeech.synthesis(txt, 'zh', 1, {
    'vol': 5,
    })

    # 识别正确返回语音二进制 错误则返回dict 参照下面错误码
    if not isinstance(result, dict):
        with open('audio.wav', 'wb') as f:
            f.write(result)
    else:
        print result


def shibie(filePath, types='amr', rate=16000): #语音识别
    with open(filePath, 'rb') as fp:
        file = fp.read()
    asr_result = aipSpeech.asr(file, types, rate, {
        'lan': 'zh',
    })
    if asr_result['err_msg'] == "success.":
        # for i in asr_result['result']:
        #     print i
        print asr_result['result'][0]
    else:
        print asr_result

hecheng('你好')
```



## miui
```
https://xiaomi.eu/community/ 选择ROMS DOWNLOAD
https://xiaomi.eu/community/threads/8-3-22.43708/

https://dl.google.com/android/repository/platform-tools-latest-windows.zip

https://jaist.dl.sourceforge.net/project/xiaomi-eu-multilang-miui-roms/xiaomi.eu/  
源地址
http://sourceforge.mirrorservice.org/x/xi/xiaomi-eu-multilang-miui-roms/xiaomi.eu/ 
镜像，下载后验证md5


twrp MD5	1a12d541c2a3d1e95448e62f6a20f4c8
系统 MD5	77e597db85858df9eef057c4fc6f202e

系统放到手机根目录

fastboot flash recovery twrp.img
fastboot boot twrp.img


进入recovery之后，进入到“挂载”界面，里面有个解锁data选项，此步骤不可省略，否则可能会卡白米
点击“清除”，格式化data（不格式化无法挂载data，连接电脑传不了rom包），然后三清或者四清
把下好的包复制到根目录，点安装。安装完之后，不要立刻重启，recovery会提示双清一下，
就先双清再重启
```



## bbr
```
bbr https://www.elrepo.org/

rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-3.el7.elrepo.noarch.rpm
yum --enablerepo=elrepo-kernel install kernel-ml -y  不要安装其他的

rpm -qa | grep kernel  有  kernel-ml-4.xx

egrep ^menuentry /etc/grub2.cfg | cut -f 2 -d \'
CentOS Linux (4.16.2-1.el7.elrepo.x86_64) 7 (Core)   这个第一个，
否则要改启动顺序grub2-set-default 1
CentOS Linux (3.10.0-693.11.6.el7.x86_64) 7 (Core)
CentOS Linux (3.10.0-693.el7.x86_64) 7 (Core)
CentOS Linux (0-rescue-c73a5ccf3b8145c3a675b64c4c3ab1d4) 7 (Core)

重启 查看内核是否为4.16

echo 'net.core.default_qdisc = fq' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf
sysctl -p

检查，以下命令输出都应该有bbr
sysctl -n net.ipv4.tcp_available_congestion_control
sysctl -n net.ipv4.tcp_congestion_control
lsmod | grep bbr

安装bbr后要注意重新关闭selinux


aws可以直接开启bbr
yum remove amazon-ssm-agent postfix rpcbind update-motd irqbalance sysstat -y
echo -e "ListenAddress 0.0.0.0\nPort 17006\nPermitRootLogin yes" >> /etc/ssh/sshd_config
echo 'PS1="[\e[31m\u@\e[36m\d \w]\\$\e[m "' >> /etc/profile
systemctl restart sshd
\cp -f /home/ec2-user/.ssh/authorized_keys .ssh/
\cp -f /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
userdel -r ec2-user
echo 'nohup /root/v2ray/v2ray &' >> /etc/rc.local
chmod +x /etc/rc.d/rc.local

crontab -l
0 0 * * * >/root/v2ray/access.log;find /var/log/ -type f -mtime 1 -exec rm {} \;

```



## chrome
```

到目前为止，Chrome 浏览器主要包括 Stable 正式版、Beta 测试版、DEV 开发版、Canary金丝雀版
以及鼻祖 Chromium 版 。从稳定性方面，
Stable>Beta>DEV>Canary>Chromium，而更新的速度则正好相反 Chromium>Canary>DEV>Beta>Stable


1、Windows 平台 32 位版本：

Stable正式版：https://www.google.com/chrome/browser/
Bata 测试版：https://www.google.com/chrome/browser/beta.html?platform=win
DEV 开发版：https://www.google.com/chrome/browser/index.html?extra=devchannel&platform=win
Canary 金丝雀版：http://www.google.com/chrome/browser/canary.html?platform=win
2、Windows 平台 64 位版本：

Stable正式版：https://www.google.com/chrome/browser/?platform=win64
Bata 测试版：https://www.google.com/chrome/browser/beta.html?platform=win64
DEV 开发版：https://www.google.com/chrome/browser/index.html?extra=devchannel&platform=win64
Canary 金丝雀版：http://www.google.com/chrome/browser/canary.html?platform=win64
3、Windows 平台32位离线安装包：

Canary 金丝雀版：http://www.google.com/chrome/eula.html?platform=win&extra=canarychannel&standalone=1
Dev开发版：http://www.google.com/chrome/eula.html?platform=win&extra=devchannel&standalone=1
Beta测试版：http://www.google.com/chrome/eula.html?platform=win&extra=betachannel&standalone=1
Stable稳定版：http://www.google.com/chrome/eula.html?platform=win&extra=stablechannel&standalone=1
其次是 MAC 平台：

Stable正式版：https://www.google.com/chrome/browser/?platform=mac
Bata 测试版：https://www.google.com/chrome/browser/beta.html?platform=mac&extra=betachannel
DEV 开发版：https://www.google.com/chrome/browser/?platform=mac&extra=devchannel
Canary 金丝雀版：http://www.google.com/chrome/browser/canary.html?platform=mac
第三个 Linux 平台：

Stable 正式版：https://www.google.com/chrome/browser/?platform=linux
Ubuntu/Debian 32-bit Bata 版: https://www.google.com/chrome/browser/beta.html?platform=linux
Ubuntu/Debian 32-bit DEV 版: https://www.google.com/chrome/browser/?platform=linux&extra=devchannel
Ubuntu/Debian 64-bit Bata 版: https://www.google.com/chrome/browser/beta.html?platform=linux
Ubuntu/Debian 64-bit DEV 版: https://www.google.com/chrome/browser/?platform=linux&extra=devchannel
Fedora/OpenSUSE 32-bit Bata 版: https://www.google.com/chrome/browser/beta.html?platform=linux
Fedora/OpenSUSE 32-bit DEV 版: https://www.google.com/chrome/browser/?platform=linux&extra=devchannel
Fedora/OpenSUSE 64-bit Bata 版: https://www.google.com/chrome/browser/beta.html?platform=linux
Fedora/OpenSUSE 64-bit DEV 版: https://www.google.com/chrome/browser/?platform=linux&extra=devchannel
Chromium下载地址：http://commondatastorage.googleapis.com/chromium-browser-continuous/index.html

当然，可能还有一些下载地址，浏览迷暂时没有收集到，欢迎大家踊跃发言，提供更多资料。另外，大家可以收藏下  
http://liulanmi.com/chrome 页面，Chrome 的下载地址浏览迷会随时在此更新补充。
```

## 基本优化
     在运维工作中，我们发现Linux系统安装之后并不能立即投入生产环境使用，往往需要先经过我们运维人员的优化才行。
    下面我就为大家简单讲解几点关于Linux系统安装后的基础优化操作。

    注意：本次优化都是基于CentOS（5.8/6.4）。关于5.8和6.4两者优化时的小区别，我会在文中提及的。

    优化条目：
    修改ip地址、网关、主机名、DNS等
    关闭selinux，清空iptables
    添加普通用户并进行sudo授权管理
    更新yum源及必要软件安装
    定时自动更新服务器时间
    精简开机自启动服务
    定时自动清理/var/spool/clientmqueue/目录垃圾文件，防止inode节点被占满
    变更默认的ssh服务端口，禁止root用户远程连接
    锁定关键文件系统
    调整文件描述符大小
    调整字符集，使其支持中文
    去除系统及内核版本登录前的屏幕显示
    内核参数优化
    1、修改ip地址、网关、主机名、DNS等
    修改IP地址：
    [root@localhost ~]# vi /etc/sysconfig/network-scripts/ifcfg-eth0

    DEVICE=eth0         #网卡名字

    BOOTPROTO=static    #静态IP地址获取状态 如：DHCP表示自动获取IP地址

    IPADDR=192.168.1.113            #IP地址

    NETMASK=255.255.255.0           #子网掩码

    ONBOOT=yes #引导时是否激活

    GATEWAY=192.168.1.1

    [root@localhost ~]# cat /etc/sysconfig/network-scripts/ifcfg-eth0

    DEVICE=eth0

    BOOTPROTO=static

    IPADDR=192.168.1.113

    NETMASK=255.255.255.0

    ONBOOT=yes

    GATEWAY=192.168.1.1

    修改主机名：
    [root@localhost ~]# vi /etc/sysconfig/network

    HOSTNAME=c64     #修改主机名，重启生效

    GATEWAY=192.168.1.1    #修改默认网关,如果上面eth0里面不配置网关的话，默认就使用这里的网关了。

    [root@localhost ~]# cat /etc/sysconfig/network

    HOSTNAME=c64

    GATEWAY=192.168.1.1

    我们也可以用  hostname c64  来临时修改主机名，重新登录生效

    修改DNS
    [root@localhost ~]# vi /etc/resolv.conf   #修改DNS信息

    nameserver 114.114.114.114

    nameserver 8.8.8.8

    [root@localhost ~]# cat /etc/resolv.conf  #查看修改后的DNS信息

    nameserver 114.114.114.114

    nameserver 8.8.8.8

    [root@localhost ~]# service network restart   #重启网卡，生效

    重启网卡，也可以用下面的命令

    [root@localhost ~]# /etc/init.d/network restart

    2、关闭selinux，清空iptables
    关闭selinux
    [root@c64 ~]# sed –i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config   #修改配置文件则永久生效，
    但是必须要重启系统。

    [root@c64 ~]# grep SELINUX=disabled /etc/selinux/config

    SELINUX=disabled     #查看更改后的结果

    [root@c64 ~]# setenforce 0   #临时生效命令

    [root@c64 ~]# getenforce      #查看selinux当前状态

    Permissive

    清空iptables
    [root@c64 ~]# iptables –F     #清理防火墙规则

    [root@c64 ~]# iptables –L     #查看防火墙规则

    Chain INPUT (policy ACCEPT)

    target     prot opt source               destination

    Chain FORWARD (policy ACCEPT)

    target     prot opt source               destination

    Chain OUTPUT (policy ACCEPT)

    target     prot opt source               destination

    [root@c64 ~]#/etc/init.d/iptables save   #保存防火墙配置信息

    3、添加普通用户并进行sudo授权管理
    [root@c64 ~]# useradd sunsky

    [root@c64 ~]# echo "123456"|passwd --stdin sunsky&&history –c

    [root@c64 ~]# visudo

    在root    ALL=(ALL)    ALL此行下，添加如下内容

    sunsky    ALL=(ALL)    ALL

    4、更新yum源及必要软件安装
    yum安装软件，默认获取rpm包的途径从国外官方源，改成国内的源。

    国内较快的两个站点：搜狐镜像站点、网易镜像站点

    法1：自己配置好安装源配置文件，然后上传到linux。

    法2：使用镜像站点配置好的yum安装源配置文件

    [root@c64 ~]# cd /etc/yum.repos.d/

    [root@c64 yum.repos.d]# /bin/mv CentOS-Base.repo CentOS-Base.repo.bak

    [root@c64 yum.repos.d]# wget http://mirrors.163.com/.help/CentOS6-Base-163.repo

    接下来执行如下命令，检测yum是否正常

    [root@c64 yum.repos.d]# yum clean all  #清空yum缓存

    [root@c64 yum.repos.d]# yum makecache  #建立yum缓存

    然后使用如下命令将系统更新到最新

    [root@c64 yum.repos.d]# rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY*       #导入签名KEY到RPM

    [root@c64 yum.repos.d]# yum  upgrade -y     #更新系统内核到最新

    接下来就要安装几个必要的软件了

    [root@c64 yum.repos.d]# yum install lrzsz ntpdate sysstat -y

    lrzsz：是一个上传下载的软件
    ntpdate：是用来与远程时间服务器进行时间更新的软件
    sysstat：是用来检测系统性能及效率的工具 
    5、定时自动更新服务器时间
    [root@c64 ~]# echo '*/5 * * * * /usr/sbin/ntpdate time.windows.com >/dev/null 2 >&1' >>/var/spool/cron/root

    [root@c64 ~]# echo '*/10 * * * * /usr/sbin/ntpdate time.nist.gov >/dev/null 2>&1' >>/var/spool/cron/root

    提示：CentOS 6.4的时间同步命令路径不一样

    6是/usr/sbin/ntpdate

    5是/sbin/ntpdate

    扩展：在机器数量少时，以上定时任务同步时间就可以了。如果机器数量大时，可以在网内另外部署一台时间同步服务器NTP Server。
    此处仅提及，不做部署。

    6、精简开机自启动服务
    刚装完操作系统可以只保留crond，network，syslog，sshd这四个服务。（Centos6.4为rsyslog）

    [root@c64 ~]# for sun in `chkconfig --list|grep 3:on|awk '{print $1}'`;do chkconfig --level 3 $sun off;done

    [root@c64 ~]# for sun in crond rsyslog sshd network;do chkconfig --level 3 $sun on;done

    [root@c64 ~]# chkconfig --list|grep 3:on

    crond           0:off   1:off   2:on    3:on    4:on    5:on    6:off

    network         0:off   1:off   2:on    3:on    4:on    5:on    6:off

    rsyslog         0:off   1:off   2:on    3:on    4:on    5:on    6:off

    sshd            0:off   1:off   2:on    3:on    4:on    5:on    6:off

    7、定时自动清理/var/spool/clientmqueue/目录垃圾文件，放置inode节点被占满
    本优化点，在6.4上可以忽略不需要操作即可！

    [root@c64 ~]# mkdir /server/scripts -p

    [root@c64 ~]# vi /server/scripts/spool_clean.sh

    #!/bin/sh

    find /var/spool/clientmqueue/ -type f -mtime +30|xargs rm -f

    然后将其加入到crontab定时任务中

    [root@c64 ~]# echo '*/30 * * * * /bin/sh /server/scripts/spool_clean.sh >/dev/null 2>&1'>>/var/spool/cron/root

    8、变更默认的ssh服务端口，禁止root用户远程连接
    [root@c64 ~]# cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

    [root@c64 ~]# vim /etc/ssh/sshd_config

    Port 52113 #ssh连接默认的端口

    PermitRootLogin no   #root用户黑客都知道，禁止它远程登录

    PermitEmptyPasswords no #禁止空密码登录

    UseDNS no            #不使用DNS

    [root@c64 ~]# /etc/init.d/sshd reload    #从新加载配置

    [root@c64 ~]# netstat -lnt     #查看端口信息

    [root@c64 ~]# lsof -i tcp:52113

    9、锁定关键文件系统
    [root@c64 ~]# chattr +i /etc/passwd

    [root@c64 ~]# chattr +i /etc/inittab

    [root@c64 ~]# chattr +i /etc/group

    [root@c64 ~]# chattr +i /etc/shadow

    [root@c64 ~]# chattr +i /etc/gshadow

    使用chattr命令后，为了安全我们需要将其改名

    [root@c64 ~]# /bin/mv /usr/bin/chattr /usr/bin/任意名称

    10、调整文件描述符大小
    [root@localhost ~]# ulimit –n        #查看文件描述符大小

    1024

    [root@localhost ~]# echo '*  -  nofile  65535' >> /etc/security/limits.conf



    配置完成后，重新登录即可查看。

    提示：也可以把ulimit -SHn 65535命令加入到/etc/rc.local，然后每次重启生效

    [root@c64 ~]# cat >>/etc/rc.local<<EOF

    #open files

    ulimit -HSn 65535

    #stack size

    ulimit -s 65535

    EOF

    扩展：文件描述符
    文件描述符在形式上是一个非负整数。实际上，它是一个索引值，指向内核为每一个进程所维护的该进程打开文件的记录表。
    当程序打开一个现有文件或者创建一个新文件时，内核向进程返回一个文件描述符。在程序设计中，一些涉及底层的程序编写往往会围绕着
    文件描述符展开。但是文件描述符这一概念往往只适用于Unix、Linux这样的操作系统。

    习惯上，标准输入（standard input）的文件描述符是 0，标准输出（standard output）是 1，标准错误（standard error）是 
    2。尽管这种习惯并非Unix内核的特性，但是因为一些 shell 和很多应用程序都使用这种习惯，因此，如果内核不遵循这种习惯的话，
    很多应用程序将不能使用。

    11、调整字符集，使其支持中文
    sed -i 's#LANG="en_US.UTF-8"#LANG="zh_CN.GB18030"#' /etc/sysconfig/i18n

    source /etc/sysconfig/i18n

    扩展：什么是字符集？
    简单的说就是一套文字符号及其编码。常用的字符集有：

    GBK 定长双字节不是国际标准，支持系统不少

    UTF-8 非定长 1-4字节广泛支持，MYSQL也使用UTF-8

    12、去除系统及内核版本登录前的屏幕显示
    [root@c64 ~]# >/etc/redhat-release

    [root@c64 ~]# >/etc/issue

    13、内核参数优化
    说明：本优化适合apache，nginx，squid多种等web应用，特殊的业务也可能需要略作调整。

    [root@c64 ~]# vi /etc/sysctl.conf

    #by sun in 20131001

    net.ipv4.tcp_fin_timeout = 2

    net.ipv4.tcp_tw_reuse = 1

    net.ipv4.tcp_tw_recycle = 1

    net.ipv4.tcp_syncookies = 1

    net.ipv4.tcp_keepalive_time =600

    net.ipv4.ip_local_port_range = 4000    65000

    net.ipv4.tcp_max_syn_backlog = 16384

    net.ipv4.tcp_max_tw_buckets = 36000

    net.ipv4.route.gc_timeout = 100

    net.ipv4.tcp_syn_retries = 1

    net.ipv4.tcp_synack_retries = 1

    net.core.somaxconn = 16384

    net.core.netdev_max_backlog = 16384

    net.ipv4.tcp_max_orphans = 16384

    #一下参数是对iptables防火墙的优化，防火墙不开会有提示，可以忽略不理。

    net.ipv4.ip_conntrack_max = 25000000

    net.ipv4.netfilter.ip_conntrack_max = 25000000

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_established = 180

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_time_wait = 120

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_close_wait = 60

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_fin_wait = 120

    [root@localhost ~]# sysctl –p    #使配置文件生效

    提示：由于CentOS6.X系统中的模块名不是ip_conntrack，而是nf_conntrack，所以在/etc/sysctl.conf优化时，
    需要把net.ipv4.netfilter.ip_conntrack_max 这种老的参数，改成net.netfilter.nf_conntrack_max这样才可以。

    即对防火墙的优化，在5.8上是:
    net.ipv4.ip_conntrack_max = 25000000

    net.ipv4.netfilter.ip_conntrack_max = 25000000

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_established = 180

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_time_wait = 120

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_close_wait = 60

    net.ipv4.netfilter.ip_conntrack_tcp_timeout_fin_wait = 120

    在6.4上是:
    net.nf_conntrack_max = 25000000

    net.netfilter.nf_conntrack_max = 25000000

    net.netfilter.nf_conntrack_tcp_timeout_established = 180

    net.netfilter.nf_conntrack_tcp_timeout_time_wait = 120

    net.netfilter.nf_conntrack_tcp_timeout_close_wait = 60

    net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 120

    另外，在此优化过程中可能会有报错：

    1、5.8版本上
    error: "net.ipv4.ip_conntrack_max" is an unknown key

    error: "net.ipv4.netfilter.ip_conntrack_max" is an unknown key

    error: "net.ipv4.netfilter.ip_conntrack_tcp_timeout_established" is an unknown key

    error: "net.ipv4.netfilter.ip_conntrack_tcp_timeout_time_wait" is an unknown key

    error: "net.ipv4.netfilter.ip_conntrack_tcp_timeout_close_wait" is an unknown key

    error: "net.ipv4.netfilter.ip_conntrack_tcp_timeout_fin_wait" is an unknown key

    这个错误可能是你的防火墙没有开启或者自动处理可载入的模块ip_conntrack没有自动载入，解决办法有二，一是开启防火墙，
    二是自动处理开载入的模块ip_conntrack

    modprobe ip_conntrack

    echo "modprobe ip_conntrack" >> /etc/rc.local

    2、6.4版本上
    error: "net.nf_conntrack_max" is an unknown key

    error: "net.netfilter.nf_conntrack_max" is an unknown key

    error: "net.netfilter.nf_conntrack_tcp_timeout_established" is an unknown key

    error: "net.netfilter.nf_conntrack_tcp_timeout_time_wait" is an unknown key

    error: "net.netfilter.nf_conntrack_tcp_timeout_close_wait" is an unknown key

    error: "net.netfilter.nf_conntrack_tcp_timeout_fin_wait" is an unknown key

    这个错误可能是你的防火墙没有开启或者自动处理可载入的模块ip_conntrack没有自动载入，解决办法有二，一是开启防火墙，
    二是自动处理开载入的模块ip_conntrack

    modprobe nf_conntrack

    echo "modprobe nf_conntrack" >> /etc/rc.local

    3、6.4版本上
    error: "net.bridge.bridge-nf-call-ip6tables" is an unknown key

    error: "net.bridge.bridge-nf-call-iptables" is an unknown key

    error: "net.bridge.bridge-nf-call-arptables" is an unknown key

    这个错误是由于自动处理可载入的模块bridge没有自动载入，解决办法是自动处理开载入的模块ip_conntrack

    modprobe bridge

    echo "modprobe bridge" >> /etc/rc.local

    到此，我们Linux系统安装后的基础优化已经操作的差不多了，总结下来一共有13个优化点需要我们来熟知。




## io复用
```
socket阻塞与非阻塞，同步与异步
作者：huangguisu
1. 概念理解
     在进行网络编程时，我们常常见到同步(Sync)/异步(Async)，阻塞(Block)/非阻塞(Unblock)四种调用方式：
同步：
      所谓同步，就是在发出一个功能调用时，在没有得到结果之前，该调用就不返回。也就是必须一件一件事做,等前一件做完了才能做下一件事。
例如普通B/S模式（同步）：提交请求->等待服务器处理->处理完毕返回 这个期间客户端浏览器不能干任何事
异步：
      异步的概念和同步相对。当一个异步过程调用发出后，调用者不能立刻得到结果。实际处理这个调用的部件在完成后，通过状态、
      通知和回调来通知调用者。
     例如 ajax请求（异步）: 请求通过事件触发->服务器处理（这是浏览器仍然可以作其他事情）->处理完毕
阻塞
     阻塞调用是指调用结果返回之前，当前线程会被挂起（线程进入非可执行状态，在这个状态下，cpu不会给线程分配时间片，即线程暂停运行）。
     函数只有在得到结果之后才会返回。
     有人也许会把阻塞调用和同步调用等同起来，实际上他是不同的。对于同步调用来说，很多时候当前线程还是激活的，只是从逻辑上当前函数没有
     返回而已。 例如，我们在socket中调用recv函数，如果缓冲区中没有数据，这个函数就会一直等待，直到有数据才返回。而此时，当前线程还会
     继续处理各种各样的消息。
非阻塞
      非阻塞和阻塞的概念相对应，指在不能立刻得到结果之前，该函数不会阻塞当前线程，而会立刻返回。
对象的阻塞模式和阻塞函数调用
对象是否处于阻塞模式和函数是不是阻塞调用有很强的相关性，但是并不是一一对应的。阻塞对象上可以有非阻塞的调用方式，我们可以通过一定的API
去轮询状 态，在适当的时候调用阻塞函数，就可以避免阻塞。而对于非阻塞对象，调用特殊的函数也可以进入阻塞调用。函数select就是这样的
一个例子。

1. 同步，就是我调用一个功能，该功能没有结束前，我死等结果。
2. 异步，就是我调用一个功能，不需要知道该功能结果，该功能有结果后通知我（回调通知）
3. 阻塞，      就是调用我（函数），我（函数）没有接收完数据或者没有得到结果之前，我不会返回。
4. 非阻塞，  就是调用我（函数），我（函数）立即返回，通过select通知调用者
同步IO和异步IO的区别就在于：数据拷贝的时候进程是否阻塞！
阻塞IO和非阻塞IO的区别就在于：应用程序的调用是否立即返回！

对于举个简单c/s 模式：
同步：提交请求->等待服务器处理->处理完毕返回这个期间客户端浏览器不能干任何事
异步：请求通过事件触发->服务器处理（这是浏览器仍然可以作其他事情）->处理完毕
同步和异步都只针对于本机SOCKET而言的。
同步和异步,阻塞和非阻塞,有些混用,其实它们完全不是一回事,而且它们修饰的对象也不相同。
阻塞和非阻塞是指当进程访问的数据如果尚未就绪,进程是否需要等待,简单说这相当于函数内部的实现区别,也就是未就绪时是直接返回还是等待就绪;
而同步和异步是指访问数据的机制,同步一般指主动请求并等待I/O操作完毕的方式,当数据就绪后在读写的时候必须阻塞(区别就绪与读写二个阶段,
同步的读写必须阻塞),异步则指主动请求数据后便可以继续处理其它任务,随后等待I/O,操作完毕的通知,这可以使进程在数据读写时也不阻塞。
(等待"通知")
1. Linux下的五种I/O模型
1)阻塞I/O（blocking I/O）
2)非阻塞I/O （nonblocking I/O）
3) I/O复用(select 和poll) （I/O multiplexing）
4)信号驱动I/O （signal driven I/O (SIGIO)）
5)异步I/O （asynchronous I/O (the POSIX aio_functions)）

前四种都是同步，只有最后一种才是异步IO。

阻塞I/O模型：
        简介：进程会一直阻塞，直到数据拷贝完成
     应用程序调用一个IO函数，导致应用程序阻塞，等待数据准备好。 如果数据没有准备好，一直等待….数据准备好了，从内核拷贝到用户空间,
     IO函数返回成功指示。

阻塞I/O模型图：在调用recv()/recvfrom（）函数时，发生在内核中等待数据和复制数据的过程。



    当调用recv()函数时，系统首先查是否有准备好的数据。如果数据没有准备好，那么系统就处于等待状态。当数据准备好后，
    将数据从系统缓冲区复制到用户空间，然后该函数返回。在套接应用程序中，当调用recv()函数时，未必用户空间就已经存在数据，那么此时
    recv()函数就会处于等待状态。


     当使用socket()函数和WSASocket()函数创建套接字时，默认的套接字都是阻塞的。这意味着当调用Windows Sockets API不能立即完成时，
     线程处于等待状态，直到操作完成。

    并不是所有Windows Sockets API以阻塞套接字为参数调用都会发生阻塞。例如，以阻塞模式的套接字为参数调用bind()、listen()函数时，
    函数会立即返回。将可能阻塞套接字的Windows Sockets API调用分为以下四种:

    1．输入操作： recv()、recvfrom()、WSARecv()和WSARecvfrom()函数。以阻塞套接字为参数调用该函数接收数据。如果此时套接字缓冲区
    内没有数据可读，则调用线程在数据到来前一直睡眠。

    2．输出操作： send()、sendto()、WSASend()和WSASendto()函数。以阻塞套接字为参数调用该函数发送数据。如果套接字缓冲区没有
    可用空间，线程会一直睡眠，直到有空间。

    3．接受连接：accept()和WSAAcept()函数。以阻塞套接字为参数调用该函数，等待接受对方的连接请求。如果此时没有连接请求，线程就会进
    入睡眠状态。

   4．外出连接：connect()和WSAConnect()函数。对于TCP连接，客户端以阻塞套接字为参数，调用该函数向服务器发起连接。该函数在收到服务器
   的应答前，不会返回。这意味着TCP连接总会等待至少到服务器的一次往返时间。

　　使用阻塞模式的套接字，开发网络程序比较简单，容易实现。当希望能够立即发送和接收数据，且处理的套接字数量比较少的情况下，
使用阻塞模式来开发网络程序比较合适。

    阻塞模式套接字的不足表现为，在大量建立好的套接字线程之间进行通信时比较困难。当使用“生产者-消费者”模型开发网络程序时，为每个
    套接字都分别分配一个读线程、一个处理数据线程和一个用于同步的事件，那么这样无疑加大系统的开销。其最大的缺点是当希望同时处理大量
    套接字时，将无从下手，其扩展性很差

非阻塞IO模型 
       简介：非阻塞IO通过进程反复调用IO函数（多次系统调用，并马上返回）；在数据拷贝的过程中，进程是阻塞的；

       我们把一个SOCKET接口设置为非阻塞就是告诉内核，当所请求的I/O操作无法完成时，不要将进程睡眠，而是返回一个错误。这样我们的
       I/O操作函数将不断的测试数据是否已经准备好，如果没有准备好，继续测试，直到数据准备好为止。在这个不断测试的过程中，会大量的
       占用CPU的时间。
    把SOCKET设置为非阻塞模式，即通知系统内核：在调用Windows Sockets API时，不要让线程睡眠，而应该让函数立即返回。在返回时，
    该函数返回一个错误代码。图所示，一个非阻塞模式套接字多次调用recv()函数的过程。前三次调用recv()函数时，内核数据还没有准备好。
    因此，该函数立即返回WSAEWOULDBLOCK错误代码。第四次调用recv()函数时，数据已经准备好，被复制到应用程序的缓冲区中，recv()函数
    返回成功指示，应用程序开始处理数据。




     当使用socket()函数和WSASocket()函数创建套接字时，默认都是阻塞的。在创建套接字之后，通过调用ioctlsocket()函数，将该套接字
     设置为非阻塞模式。Linux下的函数是:fcntl().
    套接字设置为非阻塞模式后，在调用Windows Sockets API函数时，调用函数会立即返回。大多数情况下，这些函数调用都会调用“失败”，
    并返回WSAEWOULDBLOCK错误代码。说明请求的操作在调用期间内没有时间完成。通常，应用程序需要重复调用该函数，直到获得成功返回代码。

    需要说明的是并非所有的Windows Sockets API在非阻塞模式下调用，都会返回WSAEWOULDBLOCK错误。例如，以非阻塞模式的套接字为参数
    调用
    bind()函数时，就不会返回该错误代码。当然，在调用WSAStartup()函数时更不会返回该错误代码，因为该函数是应用程序第一调用的函数，
    当然不会返回这样的错误代码。

    要将套接字设置为非阻塞模式，除了使用ioctlsocket()函数之外，还可以使用WSAAsyncselect()和WSAEventselect()函数。当调用该函数
    时，套接字会自动地设置为非阻塞方式。

　　由于使用非阻塞套接字在调用函数时，会经常返回WSAEWOULDBLOCK错误。所以在任何时候，都应仔细检查返回代码并作好对“失败”的准备。
应用程序连续不断地调用这个函数，直到它返回成功指示为止。上面的程序清单中，在While循环体内不断地调用recv()函数，以读入1024个字节
的数据。这种做法很浪费系统资源。

    要完成这样的操作，有人使用MSG_PEEK标志调用recv()函数查看缓冲区中是否有数据可读。同样，这种方法也不好。因为该做法对系统造成的
    开销是很大的，并且应用程序至少要调用recv()函数两次，才能实际地读入数据。较好的做法是，使用套接字的“I/O模型”来判断非阻塞套接字
    是否可读可写。

    非阻塞模式套接字与阻塞模式套接字相比，不容易使用。使用非阻塞模式套接字，需要编写更多的代码，以便在每个Windows Sockets API函
    数调用中，对收到的WSAEWOULDBLOCK错误进行处理。因此，非阻塞套接字便显得有些难于使用。

    但是，非阻塞套接字在控制建立的多个连接，在数据的收发量不均，时间不定时，明显具有优势。这种套接字在使用上存在一定难度，但只要排除
    了这些困难，它在功能上还是非常强大的。通常情况下，可考虑使用套接字的“I/O模型”，它有助于应用程序通过异步方式，同时对一个或多个
    套接字的通信加以管理。


IO复用模型：
             简介：主要是select和epoll；对一个IO端口，两次调用，两次返回，比阻塞IO并没有什么优越性；关键是能实现同时对多个IO端口
             进行监听；
      I/O复用模型会用到select、poll、epoll函数，这几个函数也会使进程阻塞，但是和阻塞I/O所不同的的，这两个函数可以同时阻塞多个I/O
      操作。而且可以同时对多个读操作，多个写操作的I/O函数进行检测，直到有数据可读或可写时，才真正调用I/O操作函数。



信号驱动IO
    简介：两次调用，两次返回；

    首先我们允许套接口进行信号驱动I/O,并安装一个信号处理函数，进程继续运行并不阻塞。当数据准备好时，进程会收到一个SIGIO信号，可以
    在信号处理函数中调用I/O操作函数处理数据。



异步IO模型
         简介：数据拷贝的时候进程无需阻塞。
     当一个异步过程调用发出后，调用者不能立刻得到结果。实际处理这个调用的部件在完成后，通过状态、通知和回调来通知调用者的输入输出
     操作


同步IO引起进程阻塞，直至IO操作完成。
异步IO不会引起进程阻塞。
IO复用是先通过select调用阻塞。

5个I/O模型的比较：


1. select、poll、epoll简介
epoll跟select都能提供多路I/O复用的解决方案。在现在的Linux内核里有都能够支持，其中epoll是Linux所特有，而select则应该是POSIX
所规定，一般操作系统均有实现
select：

select本质上是通过设置或者检查存放fd标志位的数据结构来进行下一步处理。这样所带来的缺点是：

1、 单个进程可监视的fd数量被限制，即能监听端口的大小有限。

      一般来说这个数目和系统内存关系很大，具体数目可以cat /proc/sys/fs/file-max察看。32位机默认是1024个。64位机默认是2048.
2、 对socket进行扫描时是线性扫描，即采用轮询的方法，效率较低：
       当套接字比较多的时候，每次select()都要通过遍历FD_SETSIZE个Socket来完成调度,不管哪个Socket是活跃的,都遍历一遍。
       这会浪费很多CPU时间。如果能给套接字注册某个回调函数，当他们活跃时，自动完成相关操作，那就避免了轮询，epoll与kqueue做的。

3、需要维护一个用来存放大量fd的数据结构，这样会使得用户空间和内核空间在传递该结构时复制开销大

poll：

poll本质上和select没有区别，它将用户传入的数组拷贝到内核空间，然后查询每个fd对应的设备状态，如果设备就绪则在设备等待队列中加入
一项并继续遍历，如果遍历完所有fd后没有发现就绪设备，则挂起当前进程，直到设备就绪或者主动超时，被唤醒后它又要再次遍历fd。
这个过程经历了多次无谓的遍历。

它没有最大连接数的限制，原因是它是基于链表来存储的，但是同样有一个缺点：

1、大量的fd的数组被整体复制于用户态和内核地址空间之间，而不管这样的复制是不是有意义。 
2、poll还有一个特点是“水平触发”，如果报告了fd后，没有被处理，那么下次poll时会再次报告该fd。

epoll:
epoll支持水平触发和边缘触发，最大的特点在于边缘触发，它只告诉进程哪些fd刚刚变为就需态，并且只会通知一次。还有一个特点是，
epoll使用“事件”的就绪通知方式，通过epoll_ctl注册fd，一旦该fd就绪，内核就会采用类似callback的回调机制来激活该fd，
epoll_wait便可以收到通知

epoll的优点：

1、没有最大并发连接的限制，能打开的FD的上限远大于1024（1G的内存上能监听约10万个端口）；
2、效率提升，不是轮询的方式，不会随着FD数目的增加效率下降。只有活跃可用的FD才会调用callback函数；
      即Epoll最大的优点就在于它只管你“活跃”的连接，而跟连接总数无关，因此在实际的网络环境中，Epoll的效率就会远远高于select和poll。
3、 内存拷贝，利用mmap()文件映射内存加速与内核空间的消息传递；即epoll使用mmap减少复制开销。

select、poll、epoll 区别总结：
1、支持一个进程所能打开的最大连接数

select

单个进程所能打开的最大连接数有FD_SETSIZE宏定义，其大小是32个整数的大小（在32位的机器上，大小就是32*32，同理64位机器上
FD_SETSIZE为32*64），当然我们可以对进行修改，然后重新编译内核，但是性能可能会受到影响，这需要进一步的测试。

poll

poll本质上和select没有区别，但是它没有最大连接数的限制，原因是它是基于链表来存储的

epoll

虽然连接数有上限，但是很大，1G内存的机器上可以打开10万左右的连接，2G内存的机器可以打开20万左右的连接

2、FD剧增后带来的IO效率问题

select

因为每次调用时都会对连接进行线性遍历，所以随着FD的增加会造成遍历速度慢的“线性下降性能问题”。

poll

同上

epoll

因为epoll内核中实现是根据每个fd上的callback函数来实现的，只有活跃的socket才会主动调用callback，所以在活跃socket较少的情况下，
使用epoll没有前面两者的线性下降的性能问题，但是所有socket都很活跃的情况下，可能会有性能问题。

3、 消息传递方式

select

内核需要将消息传递到用户空间，都需要内核拷贝动作

poll

同上

epoll

epoll通过内核和用户空间共享一块内存来实现的。

总结：

综上，在选择select，poll，epoll时要根据具体的使用场合以及这三种方式的自身特点。

1、表面上看epoll的性能最好，但是在连接数少并且连接都十分活跃的情况下，select和poll的性能可能比epoll好，毕竟epoll的通知机制
需要很多函数回调。

2、select低效是因为每次它都需要轮询。但低效也是相对的，视情况而定，也可通过良好的设计改善

来源： http://blog.csdn.net/jay900323/article/details/18141217
```



## network
```
Network调优

1、 NIC 网络介质卡
（1）、socket  套接字，连接进程的连通性
     具有两种模式：
        1、 基于文件的sock
        ls –l /tmp/mysql.sock 客户端和服务器端在同一个机器上，这种连接是非常高的。
        2、 基于网络的sock（五个元素）
        （1）、源IP 源端口 协议 目标IP 目标端口
        （2）、服务器端的端口和IP是固定的
        （3）、mysql使用的是tcp协议
        （4）、socket buffer 就是一块大内存
        （5）、core 是针对所有协议，IPV4是针对tcp协议的
        （6）、默认值以tcp为准，最大值以核心的为准
        （7）、tcp_mem 可以拿出多大的内存来存储sk_buffer，单位是页：4KB，32位系统最大支持：900M
        （8）、如果增大并发量，可以将tcp_mem的值加大，如果没有什么连接，调大则会浪费内存
        （9）、网络最优值=带宽*延时*1024*1024（基调网可以帮你测出来每个地区连接的延时）
        （10）、增大文件描述符，不建议主机上做防火墙
2、TCP状态对性能的影响
    （1）、当第三次握手成功后，进入established状态
    （2）、半开攻击，syn排队
    （3）、主动断开那端会进入Time_wait状态，被动那端会进入Close_wait
    （4）、established=最大连接数+somaxconn（排队人数）
    （5）、慢速攻击，本来一次可以发送完的数据，改变成多次发送并且时间间隔很长（最好的方法就是将apache换成nginx.php hash攻击）
3、监控网卡工具：安装yum install iptraf
                 命令 iptraf
                      mtr 远程IP
网络监控----cacti
        cactiez工作原理： 数据的采集，存储，分析，画图。
安装cactiez后请注意系统时间和当前时间是否一致（最好使用网络时间）

首先监控主机上安装net-snmp-utils
服务器端安装net-snmp

snmp：简单网络监控协议  port：161
cactiez数据路径： cd /var/www/html/rra
cactiez脚本路径： cd /var/www/html/scripts
log: /var/www/html/log
实验整理：
修改被监控主机的snmp的配置文件： 
vim /etc/snmp/snmpd.conf
rocommunity        public 192.168.18.0/24 #被监控的网段（也可以是单独的IP）
syslocation        China.beijing   #网页里显示的信息
syscontact         Root      haha@vfast.com   #联系方式
主配文件留这三行就可以 其他的可以注释掉或删了
         在被监控主机上启动snmp服务:
service snmpd start
打开浏览器访问cactiez服务器的ip 就可以进行监控的设置了
snmpwalk -v 2c -c public 192.168.18.96 .1.3.6.1.4.1.2021.4.4.0
4、 配置文件
其实linux系统的TCP网络设置并不适用于大文件在广域网中传递，通常只是为了节省内存资源，可以通过调节linux的网络协议栈的缓冲区大小，
增加网络的高速网络连接的服务器系统，以处理更多的数据包。
（1）、linux系统默认tcp缓冲非常小，这个数值是根据系统内存计算出来的
        cat /proc/sys/net/ipv4/tcp_mem
（2）、默认和最大的系统套接字缓冲区（收取）
        cat /proc/sys/net/core/rmem_default
        cat /proc/sys/net/core/rmem_max
（3）、默认和最大的系统套接字缓冲区（发送） 
        cat /proc/sys/net/core/wmem_default
        cat /proc/sys/net/core/wmem_max
（4）、socket buffer 的最大初始化值
        cat /proc/sys/net/core/optmem_max

     调优1
         讲上文提到的收取和发送缓冲到12MB，系统套接字缓冲区的调整将会对所有协议有影响，也就是说以后tcp发送或者接收数据时的缓冲
         都用这个数值
         注：rmem_max和wmem_max的默认大小是128KB，在大多数情况下兵不需要修改，在web或者dns服务器中使用默认值也不错，当你感到
         有明显的延迟时便可以根据以下的参数修改，修改后会增大内存的开销
        （1）、增大系统套接字缓冲区
                echo ‘net.core.wmem_max = 12582912’ >> /etc/sysctl.conf     
echo ‘net.core.rmem_max = 12582912’ >> /etc/sysctl.conf
        （2）、增大tcp接收和发送缓冲区
                echo ‘net.ipv4.tcp_rmem = 10240 87380 12582912’ >> /etc/sysctl.conf
                echo ‘net.ipv4.tcp_wmem = 10240 87380 12582912’ >> /etc/sysctl.conf
        （3）、开启window scaling功能
                echo ‘net.ipv4.tcp_window_scaling = 1’ >> /etc/sysctl.conf
        （4）、时间戳在（请参考RFC 1323）tcp的包含增加12个字节
                echo ‘net.ipv4.tcp_timestamps = 1’ >> /etc/sysctl.conf
        （5）、启动有选择的应答
                echo ‘net.ipv4.tcp_sock = 1’ >> /etc/sysctl.conf
（6）、默认情况下一个tcp连接关闭后，把这个连接曾经有的参数比如慢启动门限snd_sthresh，拥塞窗口snd_cwnd，还有srtt等信息都保存到
dst_entry中，
只要dst_rntey没有失效，下次新建立相同连接的时候就可以使用保存的参数来初始化这个连接，通常是关闭的
    echo ‘net.ipv4.tcp_no_metrics_save = 1’ >> /etc/sysctl.conf
（7）、每个网络接口接收数据包的速率比内核处理这些包的速率时，允许送到队列的数据包的最大数目
    echo ‘net.core.netdev_max_backlog = 5000’ >> /etc/sysctl.conf
（8）、重新加载配置文件    sysctl –p
使用tcpdump看看修改后带来的变化   tcpdump -ni eth0

    调优2
    如下的网络配置参数调整，主要是针对请求压力大的linux（2.6 kernel）服务器而言，如果服务器压力不大，维持默认值即可
    （1）、 /proc/sys/net/core/wmem_max
           最大socket写buffer，可参考的优化值：873200
    （2）、 /proc/sys/net/core/rmem_max
           最大socket读buffer，可参考的优化值：873200
    （3）、 /proc/sys/net/ipv4/tcp_wmem
           Tcp写buffer，可参考的优化值：8192 436600 873200
    （4）、 /proc/sys/net/ipv4/tcp_rmem
           Tcp读buffer，可参考的优化值：32768 436600 873200
    （5）、 /proc/sys/net/ipv4/tcp_mem
           同样有3个值，意思是：
           net.ipv4.tcp_mem[0]：低于此值，tcp没有内存压力
           net.ipv4.tcp_mem[1]：在此值下，进入内存压力阶段
           net.ipv4.tcp_mem[2]：高于此值，tcp拒绝分配socket
           上述内存单位是页，页的大小是：4KB
           可参考的优化值：786432 1048576 1572864
    （6）、 /proc/sys/net/core/netdev_max_backlog
           进入包的最大设备队列，默认是300，对重负载服务器而言，该值太低，可调整到1000
    （7）、 /proc/sys/net/core/somaxconn
Listen()的默认参数，挂起请求的最大数量，默认是128，对繁忙的服务器，增加该值有助于网络性能，可调整到256
    （8）、 /proc/sys/net/core/optmem_max
           socket buffer 的最大初始值，默认是10K
    （9）、 /proc/sys/net/ipv4/tcp_max_syn_backlog
           进入syn包的最大请求队列，默认是1024，对重负载服务器，增加该值显然有好处，可调整到2048
    （10）、/proc/sys/net/ipv4/tcp_retrises2
           tcp失败重传次数，默认是15，以为着重传15次才彻底放弃，可减少到5，以尽早释放内核资源
    （11）、/proc/sys/net/ipv4/tcp_keepalive_time
           /proc/sys/net/ipv4/tcp_keepalive_intvl
           /proc/sys/net/ipv4/tcp_keepalive_probes
           这3个参数与tcp keepalive有关，默认值是：
           tcp_keepalive_time = 7200 seconds (2 hours)
           tcp_keepalive_probes = 9
           tcp_keepalive_intvl = 75 seconds
           意思是如果某个tcp连接在idle 2个小时后，内核才会发起probe
           如果probe 9次（每次75秒）不成功，内核才彻底放弃，认为该连接已失效
           对服务器而言，显然上述值太大，可调整到：
           tcp_keepalive_time = 1800 seconds 
           tcp_keepalive_probes = 3
           tcp_keepalive_intvl = 30 seconds
    （12）、/proc/sys/net/ipv4/ip_local_range
          指定端口范围的一个配置，默认是32768  61000已够大
```



## io_mem
```
磁盘：
修改文件描述符
临时：ulimit -SHn 65535
永久：vim /etc/security/limits.conf
*               soft    nofile          65535
*               hard    nofile          65535

io调度算法   noop           ssd固态硬盘，节省cpu
             anticipatory   预期算法，适合文件服务器
             deadline       要求响应速度的场景，适合数据库
             cfg            默认算法，完全公平

cat /sys/block/sda/queue/scheduler
noop anticipatory deadline [cfq]
临时修改 echo deadline > /sys/block/sda/queue/scheduler
永久： vim /boot/grub/menu.lst
kernel /boot/vmlinuz-2.6.18-8.el5 ro root=LABEL=/ elevator=deadline rhgb quiet


内存：
释放内存
sync
echo 3 > /proc/sys/vm/drop_caches

网络：
vim /etc/sysctl.conf
net.ipv4.tcp_keepalive_intvl = 75
当检测没有确认时，重新发送检测的频度，默认是75秒。

net.ipv4.tcp_keepalive_probes = 9
在认定链接失效之前，发送多少个TCP的keepalive的检测包，默认值为9.这个值乘以tcp_keepalive_intvl之后决定了一个链接发送了
keepalive之后可以有多少时间没有回应。

net.ipv4.tcp_keepalive_time = 7200
当启用keepalive的时候，TCP发送keepalive消息的频度，默认为2小时。

net.ipv4.tcp_syn_retries = 5
在内核放弃建立连接前发送SYN包的数量。

net.ipv4.tcp_synack_retries = 5
为了打开对端的链接，内核需要发送一个SYN并附带一个回应前面一个SYN的ACK。也就是所谓三次握手中的第二次握手。这个设置决定了
内核放弃链接前发送SYN+ACK包的数量。

net.ipv4.tcp_syncookies = 1 
表示开启SYN cookies。当出现SYN等待队列溢出时，启用cookies来处理，可防范少量SYN攻击，默认为0，表示关闭；
net.ipv4.tcp_tw_reuse = 1 
表示开启重用。允许将TIME-WAIT sockets重新用于新的TCP连接，默认为0，表示关闭；
net.ipv4.tcp_tw_recycle = 1 
表示开启TCP连接中TIME-WAIT sockets的快速回收，默认为0，表示关闭。
net.ipv4.tcp_fin_timeout = 30 
修改系統默认的 TIMEOUT 时间


sysctl -p生效
```
