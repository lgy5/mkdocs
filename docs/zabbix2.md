## grafana
```
grafana的版本和grafana-zabbix的版本必须匹配，否则会出现异常,如果后面grafana和grafana-zabbix更新，需要将2个版本匹配即可

yum install  https://grafanarel.s3.amazonaws.com/builds/grafana-2.5.0-1.x86_64.rpm
安装包内容
二进制文件     /usr/sbin/grafana-server
启动脚本         /etc/init.d/grafana-server
环境变量         /etc/sysconfig/grafana-server
配置文件         /etc/grafana/grafana.ini
systemd服务  grafana-server.service
日志                 /var/log/grafana/grafana.log
sqlite3数据库  /var/lib/grafana/grafana.db

启动服务
shell#sudo service grafana-server start
服务详情
启动用户 grafana
服务名称 grafana-server
默认端口 3000

服务自启动
shell#sudo /sbin/chkconfig --add grafana-server
####CentOS7####
shell#sudo systemctl daemon-reload
shell#sudo systemctl start grafana-server
shell#sudo systemctl status grafana-server
shell#sudo systemctl enable grafana-server.service


安装grafana-zabbix插件
wget  https://github.com/alexanderzobnin/grafana-zabbix/archive/v2.5.1.tar.gz
tar -zxf grafana-zabbix-2.5.1.tar.gz 
cd grafana-zabbix-2.5.1/
cp -r zabbix/ /usr/share/grafana/public/app/plugins/datasource/
cd  /usr/share/grafana/public/app/plugins/datasource/zabbix/
修改 plugin.json
{
  "pluginType": "datasource",
  "name": "Zabbix",

  "type": "zabbix",
  "serviceName": "ZabbixAPIDatasource",

  "module": "app/plugins/datasource/zabbix/datasource",

  "partials": {
    "config": "app/plugins/datasource/zabbix/partials/config.html"
  },

  "username": "guangyu.liang",   zabbix web账号 需要管理员权限
  "password": "1qaz2wsx",

  "metrics": true,
  "annotations": true
}

配置 
http://ip:3000/login
账号        admin
密码        admin

http://www.2cto.com/net/201601/487722.html  （打不开看附件）
```



## 主动模式 mail
```
zabbix主动
PidFile=/tmp/zabbix_agentd.pid
LogFile=/tmp/zabbix_agentd.log
#Server=192.168.20.27
ServerActive=192.168.20.27:10051
#Hostname=rongxin01
HostnameItem=system.hostname
EnableRemoteCommands=1
LogRemoteCommands=1
RefreshActiveChecks=60
BufferSize=10000
StartAgents=5
MaxLinesPerSecond=200
Timeout=30
Include=/usr/local/zabbix/etc/zabbix_agentd.conf.d/
LoadModulePath=/usr/local/zabbix/share/zabbix/modules
mail报警
停止sendmail或postfix
/etc/init.d/sendmail stop
chkconfig sendmail off
tar –zxf mailx-12.5.tar.gz
make &&  make install UCBINSTALL=/usr/bin/install
cp /usr/local/bin/mailx /bin/mail
vi /etc/nail.rc
set from=test001@sina.com
set smtp=smtp://smtp.sina.cn:25
set smtp-auth-user= test001@sina.com
set smtp-auth-password= test001
测试 echo "this is test" | mail -v -s "subject" lgy_root@163.com
vim /etc/zabbix/zabbix_server.conf
AlertScriptsPath=/usr/local/zabbix/share/zabbix/alertscripts
vim /usr/local/zabbix/alertscripts/sendmail.sh
#!/bin/bash
echo "$3" | /bin/mail   -s "$2"  $1

2、sendEmail
#!/bin/bash 
export smtpemailfrom=monitor@3mang.com
export zabbixemailto=$1    (发送多人的话，每个人用空格隔开)
export zabbixsubject=$2 
export zabbixbody=$3 
export smtpserver=smtp.ym.163.com
export smtplogin=monitor@3mang.com
export smtppass=123qwe

/usr/local/bin/sendEmail  -o tls=no  -f $smtpemailfrom -t $zabbixemailto -u $zabbixsubject 
-m $zabbixbody -s $smtpserver:25 -xu $smtplogin -xp $smtppass
```



## zabbix key
```
zabbix服务器端通过与zabbix agent通信来获取客户端服务器的数据，agent分为两个版本，在配置主机我们可以看到一个是agent，
另一个是agent（active）。

agent：zabbix server向zabbix agent讨要数据。
agent（active）：zabbix agent提交数据给zabbix server。

模板中勾选所以key后，选择mass update  ，可以批量更换key的类型


监控项keys列表
以下表格是zabbix agent所支持的所有key列表，添加一向监控的时候，首先想到的应该是zabbix agent是否已经有相关的key存在，
而不是自己去写脚本来获取key。

agent.hostname
返回被监控端名称(字符串)

agent.ping
检测被监控端是否存活(1:运行中 其他:未运行)-使用函数 nodata()检测客户端是否正在运行

agent.version
zabbix agent版本字符串

kernel.maxfiles
系统支持最大的open files整数

kernel.maxproc
系统支持最大的进程数量整数

log[file,<regexp>,<encoding>,<maxlines>,<mode>,<output>]
监控日志文件
file - 文件详细路径
regexp - 正则
encoding - 编码
maxlines - zabbix agent向server或者proxy发送最大的行数。
  这个参数覆盖配置文件zabbxi_agentd.conf中的’MaxLinesPerSecond’ 
mode - 可选值:all (默认), skip (跳过处理老数据).mode参数从2.0版本开始支持
output - 可选项，输出格式模板.
示例: log[/var/log/syslog] log[/var/log/syslog,error] log[/home/zabbix/logs/logfile,,,100]

logrt[file_pattern,<regexp>,<encoding>,<maxlines>,<mode>,<output>]
Monitoring of log file with log rotation support.
file_pattern - 文件绝对路径

net.dns[<ip>,zone,<type>,<timeout>,<count>]
检测DNS服务是否开启0 – DNS挂了  1 - DNS运行中
ip - DNS服务器的ip地址(留空表示使用本地DNS, ignored onWindows)
zone - 需要测试的域名
type - 记录类型 (默认为 SOA),type可选值:  ANY, A, NS, CNAME, MB, MG, MR, PTR, MD, MF, MX, SOA, NULL, WKS 
(除了windows), HINFO, MINFO, TXT, SRV SRV
timeout (ignored on Windows) – 超时时间(默认1秒)
count (ignored on Windows) – 重试次数 (默认值2)
示例key: net.dns[8.8.8.8,zabbix.com,MX,2,1] 

net.dns.record[<ip>,zone,<type>,<timeout>,<count>]
执行一个DNS查询获取DNS查询数据.
ip - DNS服务器的ip地址(留空表示使用本地DNS, ignored on Windows)
zone - 需要测试的域名
type - 记录类型 (默认SOA,可选值同net.dns)
timeout (ignored on Windows) – 超时时间(默认1秒)
count (ignored on Windows) – 重试次数 (默认值2)
示例key: net.dns.record[8.8.8.8,ttlsa.com,MX,2,1]

net.if.collisions[if]
Out-of-window collision.Number of collisions. Integer.if - 网卡

net.if.discovery
列出网卡.通常用于低级别的discovery.JSON对象

net.if.in[if,<mode>]
网卡入口流量整数.
if - 网卡名称
mode - 可用值: bytes - 字节数 (默认)
packets - 包数量
errors - 错误数量
dropped - 丢包数量
示例keys: net.if.in[eth0,errors] net.if.in[eth0]

net.if.out[if,<mode>]
网卡出口流量（参数参见net.if.in）

net.if.total[if,<mode>]
网卡进/出流量的总和（参数参见net.if.in）


net.tcp.listen[port]
检测端口是否开启0 – （not listen） 1 –  in LISTEN stateport
示例: net.tcp.listen[80]

net.tcp.port[<ip>,port]
是否可以连接到指定的TCP端口0 – cannot connect 1 – can connect
   ip - IP地址(默认是 127.0.0.1)
   port - 端口
范例: net.tcp.port[,80] 检测web服务器端口是否运行中

net.tcp.service[service,<ip>,<port>]
检测服务是否开启，并且端口可用0 – 服务挂了 1 – 服务运行中
    service - 如下:ssh, ntp, ldap, smtp, ftp, http, pop, nntp,imap, tcp, https, telnet
    ip - IP地址 (默认127.0.0.1)
    port - 端口 (默认情况为标准端口号)
示例key: net.tcp.service[ftp,,45]

net.tcp.service.perf[service,<ip>,<port>]
检测服务器性能0 – 服务挂了; seconds – 链接到服务器端口消耗的时间
service - 如下:ssh, ntp, ldap, smtp, ftp, http, pop, nntp,imap, tcp, https, telnet
ip - IP地址 (默认127.0.0.1)
port - 端口 (默认情况为标准端口号)
示例key: net.tcp.service.perf[ssh]

         net.udp.listen[port]

proc.mem[<name>,<user>,<mode>,<cmdline>]
用户进程消耗的内存内存使用量 (字节单位).
name - 进程名 (默认值 “all processes”)
user - 用户名 (默认值“all users”)
mode - 可选值: avg, max, min, sum (默认)
cmdline - 命令行过滤(正则表达时)
示例keys: proc.mem[,root] – root的进程消耗了多少内存
    proc.mem[zabbix_server,zabbix] – zabbix用户运行的zabbix_server使用了多少内存
    proc.mem[,oracle,max,oracleZABBIX]


proc.num[<name>,<user>,<state>,<cmdline>]
某用户某些状态的进程的数量进程数量
name - 进程名称 (默认“all processes”)
user - 用户名 (默认 “all users”)
state - 可用值: all (默认), run,sleep, zomb
cmdline - 命令行过滤(正则表达时)
示例keys: proc.num[,mysql] – MySQL用户运行的进程数量
proc.num[apache2,www-data] – www-data运行了多少个apache2进程
proc.num[,oracle,sleep,oracleZABBIX]
备注：Windows系统只支持name和user两个参数


sensor[device,sensor,<mode>]
读取硬件传感器
device - 设备名称 
sensor - 传感器名称 
mode - 可选值:avg, max, min
示例key: sensor[w83781d-i2c-0-2d,temp1] Prior to Zabbix 1.8.4, the sensor[temp1] format was used. 
On Linux 2.6+, 读取/sys/class/hwmon. On OpenBSD, 读取hw.sensors MIB.示例keys: sensor[cpu0,temp0] – 
CPU0的温度 sensor[cpu[0-2]$,temp,avg] – cpu平均温度Zabbix 1.8.4开始支持OpenBSD

system.boottime
系统启动的时间戳整数.unix时间戳

system.cpu.intr
设备中断整数

system.cpu.load[<cpu>,<mode>]
CPU负载浮点数
cpu - 可用值: all (默认), percpu (所有在线cpu的负载)
mode - 可用值:avg1 (1分钟 默认值), avg5(5分钟平均), avg15 (15分钟平均值)
范例key: system.cpu.load[,avg5]

system.cpu.num[<type>]
CPU数量处理器个数type - 可用值: online (默认值), max范例: system.cpu.num

system.cpu.switches
上下文交换交换次数老命名方式: system[switches]

system.cpu.util[<cpu>,<type>,<mode>]
CPU利用率百分比
cpu - cpu数量 (默认是所有cpu)
type - 可用值: idle, nice, user (默认), system (windows系统默认值）, iowait, interrupt, softirq,steal
mode - 可用值: avg1 (一分钟平均，默认值), avg5(5分钟平均, avg15 (15分钟平均值)
范例key: system.cpu.util[0,user,avg5]

system.hostname[<type>]
返回主机名字符串
type (仅用于windows系统) – 可用值: netbios(默认) or host

system.hw.chassis[<info>]
返回机架信息字符串
info - full (默认), model, serial, type 或vendor
例如: system.hw.chassis
Hewlett-Packard HP Pro 3010 Small Form Factor PC CZXXXXXXXX Desktop]
备注：要root权限，因为这些信息是从内存中读取的。

system.hw.cpu[<cpu>,<info>]
返回CPU信息字符/数字
cpu - cpu数量或者all (默认)
info - full (默认), curfreq, maxfreq, model 或者vendor
例如: system.hw.cpu[0,vendor] AuthenticAMD 从/proc/cpuinfo、/sys/devices/system/cpu/[cpunum]/
cpufreq/cpuinfo_max_freq获取信息. 如果指定了CPU数量和 curfreq或者maxfreq, 将会返回数值(Hz).

system.hw.devices[<type>]
列出PCI或者USB文本值
type - pci (默认) or usb
范例: system.hw.devices[pci] 00:00.0 Host bridge: Advanced Micro Devices [AMD] RS780 Host Bridge 
[..] 返回lspci或者lsusb (不带参数)

system.hw.macaddr[<interface>,<format>]
列出MAC地址字符串
interface - all (默认) 或者正则表达式
format - full (默认) 、short
范例: system.hw.macaddr["eth0$",full] [eth0] 00:11:22:33:44:55 列出指定接口mac地址 如果format指定为short，
MAC地址相同的将会被忽略掉

system.localtime[<type>]
系统时间.数字或者字符串

system.run[command,<mode>]
在制定的主机上运行命令文本
command - 命令
mode - wait (默认值, 执行超时时间), nowait (不等待)最大可用返回512KB数据，包含空白数据。 命令输出数据必须是文本
例如: system.run[ls -l /] – 列出/的文件和目录.
Note: 启用这个方法, agent配置文件必须配置 EnableRemoteCommands=1选项

system.stat[resource,<type>]
虚拟内存状态数字ent


system.sw.arch
返回软件信息字符串
范例: system.sw.arch i686


system.sw.os[<info>]
返回系统信息字符串
info - full (default), short ,name
范例: system.sw.os[short] Ubuntu 2.6.35-28.50-generic 2.6.35.11
信息来自如下文件：
/proc/version [short]
/proc/version_signature [name]
/etc/issue.net


system.sw.packages[<package>,<manager>,<format>]
已安装软件列表文本值
package - all (默认)或者正则表达式
manager - all (默认) or a package manager
format - full (默认) ，short
范例: system.sw.packages[mini,dpkg,short]


system.swap.in[<device>,<type>]
交换分区IN（磁盘交换到内存）数字
device - 交换分区设备 (默认all)
type - 可选值: count (swapins数量), sectors(sectors swapped in), pages (pages swapped in).
示例key: system.swap.in[,pages]
数据采集自: Linux 2.4: /proc/swaps, /proc/partitions, /proc/stat
            Linux 2.6: /proc/swaps, /proc/diskstats, /proc/vmstat


system.swap.out[<device>,<type>]
Swap out (f内存到磁盘) .数字
device - swap设备 (默认all)
type - count (number of swapouts), sectors(sectors swapped out), pages (pages swapped out). 示
例key: system.swap.out[,pages]
数据采集自: Linux 2.4: /proc/swaps, /proc/partitions, /proc/stat
            Linux 2.6: /proc/swaps, /proc/diskstats, /proc/vmstat


system.swap.size[<device>,<type>]
交换分区大小字节或者百分比
device - 交换分区 (默认值 all)
type - free (free swap space, default), pfree (free swap space, in percent), pused (used swap space,
 in percent), total (total swap space), used (used swap space)
示例 system.swap.size[,pfree] – 空闲swap百分比


system.uname
返回主机相信信息.字符串


system.uptime
系统运行时长(秒)多少秒使用s/uptime来获取


system.users.num
登陆用户数量多少用户agent使用who命令获取


vfs.dev.read[<device>,<type>,<mode>]
磁盘读取状态整数，浮点数（如果type为如下）
device - 磁盘设备 (默认值 “all”) 
type - 可选值:sectors, operations, bytes, sps, ops, bps(必须指定, 不同操作系统下不同).  sps, ops, bps
 stand for: sectors, operations, bytes per second, respectively
mode - 可选值: avg1, avg5, avg15. 
备注: 只有type为sps, ops, bps的时候，第三个参数才被支持。
不同操作系统的TYPE参数： FreeBSD – bps Linux – sps OpenBSD – operations Solaris – bytes
示例key: vfs.dev.read[,operations]


vfs.dev.write[<device>,<type>,<mode>]
磁盘写入状态整数，
device - 磁盘设备 (默认 all) 
type - sectors, operations, bytes, sps, ops, bps
mode - one of avg1 (default),avg5 , avg15.
example: vfs.dev.write[,operations] Old naming: io


vfs.file.cksum[file]
计算文件校验 UNIX cksum.
file - 文件完整路径


vfs.file.contents[file,<encoding>]
获取文本内容若为空，只返回 LF/CR characters.
file - 文件完整路径
例如: vfs.file.contents[/etc/passwd] 文件不可以超过64KB. 


vfs.file.exists[file]
检测文件是否存在1 – 存在 0 – 不存在
    file - 文件完整路径


vfs.file.md5sum[file]
文件MD5校验码文件MD5哈希值
file - 完整路径

vfs.file.regexp[file,regexp,<encoding>,<start line>,<end line>,<output>]
文件中搜索字符串包含字符串的行，或者为空
file - 文件完整路径
regexp - GNU正则表达式
encoding - 编码
start line - 从哪一行开始，默认第一行
end line - 从哪一行结束，默认最后一行
如: vfs.file.regexp[/etc/passwd,zabbix]
    vfs.file.regexp[/path/to/some/file,”([0-9]+)$”,,3,5,\1]
    vfs.file.regexp[/etc/passwd,^zabbix:.:([0-9]+),,,,\1]


vfs.file.regmatch[file,regexp,<encoding>,<start line>,<end line>]
文件中搜索字符串0 – 未找到 1 – 找到
file - 文件完整路径
regexp - GNU 正则表达式
encoding - 编码
start line - 哪行开始，默认第一行
end line - 哪行结束，默认最后一行
例如: vfs.file.regmatch[/var/log/app.log,error]


vfs.file.size[file]
文件大小字节fzabbix必须有可读此文件的权限


vfs.file.time[file,<mode>]
文件时间信息Unix 时间戳.
mode -  modify (默认, 修改时间), access – 最后访问时间, change – 最后改变时间
例如: vfs.file.time[/etc/passwd,modify] 备注：文件大小有限制

vfs.fs.discovery
列出挂载的文件系统 用于lld.JSON对象


vfs.fs.inode[fs,<mode>]
inodes数量数字
fs - 文件系统
mode - total (默认), free, used, pfree (空闲百分比), pused (使用百分比)
例如: vfs.fs.inode[/,pfree]


vfs.fs.size[fs,<mode>]
磁盘空间，返回本地文件系统的使用量字节
fs - 文件系统
mode -  total (默认), free, used, pfree (空闲百分比), pused (使用百分比).
例如: vfs.fs.size[/tmp,free]


vm.memory.size[<mode>]
内存大小字节或百分比
mode - total (默认), active, anon, buffers, cached, exec, file, free, inactive, pinned, shared,
 wired, used, pused, available
监控项vm.memory.size[] 允许三种类型的参数：
第一类：包含total - 总内存
第二类： 系统指定内存类型:active, anon, buffers, cached, exec, file, free, inactive,pinned, shared,
 wired. 第三类：用户级别，一共使用了多少内存，还有多少内存可用: used, pused, available,pavailable.


web.page.get[host,<path>,<port>]
获取网页内容网页源代码
host - 主机名/域名
path - 文件地址，默认/
port - 端口，默认80返回空字符串表示失败. 例如: web.page.get[


web.page.perf[host,<path>,<port>]
获取完全加载网页消耗的时长秒，返回0表示失败
host - 主机名/域名
path - html地址，默认是/
port - 端口,默认80


web.page.regexp[host,<path>,<port>,<regexp>,<length>,<output>]
在网页中搜索字符串  失败则返回空字符 (不匹配).
host - 主机名
path - html文件路径 (默认值 /)
port - 端口 (默认80)
regexp - GNU正则表达式
length - 返回的最大的字符串数量
output - 输出格式模板可选项.
```



## zabbix api
```
For Zabbix proxy database only schema.sql should be imported (no images.sql nor data.sql)
zabbix_proxy 安装只需要导入schema.sql

zabbix-key
https://www.zabbix.com/documentation/2.4/manual/config/items/itemtypes/zabbix_agent

api
https://www.zabbix.com/documentation/2.4/manual/api

zabbix数据库
https://www.zabbix.com/documentation/2.4/manual/appendix/install/db_scripts

post不同data实现不同功能
# coding:utf-8
import json
import urllib2
def zab_api(data):
    url = 'http://monitor.3mang.com/zabbix/api_jsonrpc.php'
    header = {"Content-Type": "application/json"}
    request = urllib2.Request(url, data, header)
    # for key in header:
    #     request.add_header(key, header[key])
    result = urllib2.urlopen(request)
    response = json.loads(result.read())
    result.close()
    return response
auth_data = json.dumps({
    "jsonrpc": "2.0",
    "method": "user.login",
    "params": {
        "user": "guangyu.liang",
        "password": "1qaz2wsx"
    }, "id": 2
})
auth = zab_api(auth_data)["result"]
hostget = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.get",
    "params": {
        "output": ["hostid", "host"],
        "selectInterfaces": ["interfaceid", "ip"]
    }, "id": 2, "auth": auth
})
hostgroup = json.dumps({
    "jsonrpc": "2.0",
    "method": "hostgroup.get",
    "params": {
        "output": "extend",
        "filter": {"name": ["Linux servers","windows"]}
    }, "id": 2, "auth": auth
})
# print json.dumps(zab_api(hostgroup)["result"], indent=4)
for i in zab_api(hostgroup)["result"]:
    print '"', i["name"], '"', "groupid is: ", i["groupid"]
template = json.dumps({
    "jsonrpc": "2.0",
    "method": "template.get",
    "params": {
        "output": "extend",
        "filter": {"host": ["Template OS Linux","Template OS Windows"]}
    }, "id": 3, "auth": auth
})
# print json.dumps(zab_api(template)["result"], indent=4)
for i in zab_api(template)["result"]:
    print '"', i["host"], '"', "templateid is:", i["templateid"]
hostcreate = json.dumps({
    "jsonrpc": "2.0",
    "method": "host.create",
    "params": {
        "host": "api test",
        "interfaces": [
            {
                "type": 1,  # 1 - agent; 2 - SNMP; 3 - IPMI; 4 - JMX.
                "main": 1,
                "useip": 1,
                "ip": "192.168.3.1",
                "dns": "",
                "port": "10050"
            }
        ],
        "groups": [{"groupid": "2"}],
        "templates": [{"templateid": "10001"}],
        "inventory_mode": 1,  # -1 - disabled; 0 - (default) manual; 1 - automatic.
        # "inventory": {
        #     "macaddress_a": "01234",
        #     "macaddress_b": "56768"
        # }
    }, "id": 4, "auth": auth
})
# print zab_api(hostcreate)


1.user.login方法获取zabbix server的认证结果官方地址：https://www.zabbix.com/documentation/2.2/manual/api/
reference/user/login
python脚本：

[root@yang python]# cat auth.py
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://1.1.1.1/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}
# auth user and password
data = json.dumps(
{
"jsonrpc": "2.0",
"method": "user.login",
"params": {
"user": "Admin",
"password": "zabbix"
},
"id": 0
})
# create request object
request = urllib2.Request(url,data)
for key in header:
    request.add_header(key,header[key])
# auth and get authid
try:
    result = urllib2.urlopen(request)
except URLError as e:
    print "Auth Failed, Please Check Your Name AndPassword:",e.code
else:
    response = json.loads(result.read())
    result.close()
print"Auth Successful. The Auth ID Is:",response['result']
python脚本运行结果：
[root@yang python]# python auth.py
Auth Successful. The Auth ID Is: a0b82aae0842c2041386a61945af1180

curl命令：
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":
"2.0","method":"user.login","params":{"user":"admin","password":"zabbix"},"auth":
null,"id":0}' http://1.1.1.1/zabbix/api_jsonrpc.php

curl命令运行结果：
{"jsonrpc":"2.0","result":"b895ce91ba84fe247e444817c6773cc3","id":0}


2.hostgroup.get方法获取所有主机组ID把认证密钥放到脚本中，每次获取数据时都需要认证。此处是获取zabbix server上的
所有主机组名称与ID号。
官方地址：https://www.zabbix.com/documentation/2.2/manual/api/reference/hostgroup/get
python脚本：

[root@yang python]# catget_hostgroup_list.py
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://1.1.1.1/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}
# request json
data = json.dumps(
{
"jsonrpc":"2.0",
"method":"hostgroup.get",
"params":{
"output":["groupid","name"],
   },
"auth":"3c0e88885a8cf8af9502b5c850b992bd", # theauth id is what auth script returns, remeber it is string
"id":1,
})
# create request object
request = urllib2.Request(url,data)
for key in header:
    request.add_header(key,header[key])
# get host list
try:
    result = urllib2.urlopen(request)
except URLError as e:
    if hasattr(e, 'reason'):
        print 'We failed to reach a server.'
        print 'Reason: ', e.reason
elif hasattr(e, 'code'):
    print 'The server could not fulfill the request.'
    print 'Error code: ', e.code
else:
    response = json.loads(result.read())
    result.close()
print "Number Of Hosts: ", len(response['result'])
#print response
for group in response['result']:
    print "Group ID:",group['groupid'],"\tGroupName:",group['name']
python脚本执行结果：

[root@yang python]# pythonget_hostgroup_list.py
Number Of Hosts:  12
Group ID: 11    Group Name: DB Schedule
Group ID: 14    Group Name: DG-WY-KD-Server
Group ID: 5     Group Name: Discovered hosts
Group ID: 7     Group Name: Hypervisors
Group ID: 2     Group Name: Linux servers
Group ID: 8     Group Name: monitored_linux
Group ID: 9     Group Name: qsmind
Group ID: 12    Group Name: qssec
Group ID: 13    Group Name: switch
Group ID: 1     Group Name: Templates
Group ID: 6     Group Name: Virtual machines
Group ID: 4     Group Name: Zabbix servers


curl命令：
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc": "2.0","method":"hostgroup.get","params":
{"output":["groupid","name"]},"auth":"11d2b45415d5de6770ce196879dbfcf1","id": 0}' http://1.1.1.1/zabbix/
api_jsonrpc.php

curl执行结果：
{"jsonrpc":"2.0","result":[{"groupid":"11","name":"DBSchedule"},{"groupid":"14","name":"DG-WY-KD-Server"},
{"groupid":"5","name":"Discoveredhosts"},{"groupid":"7","name":"Hypervisors"},{"groupid":"2","name":"Linuxservers"},
{"groupid":"8","name":"monitored_linux"},{"groupid":"9","name":"qsmind"},{"groupid":"12","name":"qssec"},
{"groupid":"13","name":"switch"},{"groupid":"1","name":"Templates"},{"groupid":"6","name":"Virtualmachines"},
{"groupid":"4","name":"Zabbixservers"}],"id":0}

3.itemsid.get方法获取单个主机下所有的监控项ID根据标题3中获取到的所有主机id与名称，找到你想要获取的主机id，获取它下面的所有items。
官方地址：https://www.zabbix.com/documentation/2.2/manual/api/reference/item
python脚本：

#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://1.1.1.1/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}
# request json
data = json.dumps(
{
"jsonrpc":"2.0",
"method":"host.get",
"params":{
"output":["hostid","name"],
"groupids":"14",
   },
"auth":"3c0e88885a8cf8af9502b5c850b992bd", # theauth id is what auth script returns, remeber it is string
"id":1,
})
# create request object
request = urllib2.Request(url,data)
for key in header:
request.add_header(key,header[key])
# get host list
try:
result = urllib2.urlopen(request)
except URLError as e:
   if hasattr(e, 'reason'):
print 'We failed to reach a server.'
print 'Reason: ', e.reason
elif hasattr(e, 'code'):
print 'The server could not fulfill the request.'
print 'Error code: ', e.code
else:
response = json.loads(result.read())
result.close()
print "Number Of Hosts: ", len(response['result'])
for host in response['result']:
print "Host ID:",host['hostid'],"HostName:",host['name']

[root@yang python]# cat get_items.py
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://1.1.1.1/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}
# request json
data = json.dumps(
{
"jsonrpc":"2.0",
"method":"item.get",
   "params":{
"output":["itemids","key_"],
"hostids":"10146",
   },
"auth":"3c0e88885a8cf8af9502b5c850b992bd", # theauth id is what auth script returns, remeber it is string
"id":1,
})
# create request object
request = urllib2.Request(url,data)
for key in header:
request.add_header(key,header[key])
# get host list
try:
result = urllib2.urlopen(request)
except URLError as e:
   if hasattr(e, 'reason'):
print 'We failed to reach a server.'
print 'Reason: ', e.reason
elif hasattr(e, 'code'):
print 'The server could not fulfill the request.'
print 'Error code: ', e.code
else:
response = json.loads(result.read())
result.close()
print "Number Of Hosts: ", len(response['result'])
for host in response['result']:
print host
#print "Host ID:",host['hostid'],"HostName:",host['name']

python脚本运行结果：
[root@yang python]# python get_items.py
Number Of Hosts:  54
{u'itemid': u'24986', u'key_':u'agent.hostname'}
{u'itemid': u'24987', u'key_':u'agent.ping'}
{u'itemid': u'24988', u'key_':u'agent.version'}
{u'itemid': u'24989', u'key_':u'kernel.maxfiles'}
{u'itemid': u'24990', u'key_':u'kernel.maxproc'}
{u'itemid': u'25157', u'key_':u'net.if.in[eth0]'}
{u'itemid': u'25158', u'key_':u'net.if.in[eth1]'}
… …

curl命令：
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"item.get","params":
{"output":"itemids","hostids":"10146","search":{"key_":"net.if.out[eth2]"}},"auth":
"11d2b45415d5de6770ce196879dbfcf1","id": 0}' http://1.1.1.1/zabbix/api_jsonrpc.php
#此处加上了单个key的名称


curl命令执行结果：
{"jsonrpc":"2.0","result":[{"itemid":"25154"}],"id":0}



5.history.get方法获取单个监控项的历史数据根据第4项的获取到的所有items id的值，找到想要监控的那项，获取它的历史数据。
官方地址：https://www.zabbix.com/documentation/2.2/manual/api/reference/history/get
python脚本：
[root@yang python]# catget_items_history.py
#!/usr/bin/env python2.7
#coding=utf-8
import json
import urllib2
# based url and required header
url = "http://1.1.1.1/zabbix/api_jsonrpc.php"
header = {"Content-Type":"application/json"}
# request json
data = json.dumps(
{
"jsonrpc":"2.0",
"method":"history.get",
"params":{
"output":"extend",
"history":3,
"itemids":"25159",
"limit":10
   },
"auth":"3c0e88885a8cf8af9502b5c850b992bd", # theauth id is what auth script returns, remeber it is string
"id":1,
})
# create request object
request = urllib2.Request(url,data)
for key in header:
    request.add_header(key,header[key])
# get host list
try:
    result = urllib2.urlopen(request)
except URLError as e:
   if hasattr(e, 'reason'):
       print 'We failed to reach a server.'
       print 'Reason: ', e.reason
   elif hasattr(e, 'code'):
       print 'The server could not fulfill the request.'
       print 'Error code: ', e.code
else:
    response = json.loads(result.read())
    result.close()
    print "Number Of Hosts: ", len(response['result'])
for host in response['result']:
    print host
#print "Host ID:",host['hostid'],"HostName:",host['name']


python脚本执行结果：
[root@yang python]# pythonget_items_history.py
Number Of Hosts:  10
{u'itemid': u'25159', u'ns': u'420722133',u'value': u'3008', u'clock': u'1410744079'}
{u'itemid': u'25159', u'ns': u'480606614',u'value': u'5720', u'clock': u'1410744139'}
{u'itemid': u'25159', u'ns': u'40905600',u'value': u'6144', u'clock': u'1410744200'}
{u'itemid': u'25159', u'ns': u'175337062',u'value': u'2960', u'clock': u'1410744259'}
{u'itemid': u'25159', u'ns': u'202705084',u'value': u'3032', u'clock': u'1410744319'}
{u'itemid': u'25159', u'ns': u'263158421',u'value': u'2864', u'clock': u'1410744379'}
{u'itemid': u'25159', u'ns': u'702285081',u'value': u'7600', u'clock': u'1410744439'}
{u'itemid': u'25159', u'ns': u'231191890',u'value': u'3864', u'clock': u'1410744499'}
{u'itemid': u'25159', u'ns': u'468566742',u'value': u'3112', u'clock': u'1410744559'}
{u'itemid': u'25159', u'ns': u'421679098',u'value': u'2952', u'clock': u'1410744619'}


curl命令：
curl -i -X POST -H 'Content-Type:application/json' -d '{"jsonrpc":"2.0","method":"history.get","params":
{"history":3,"itemids":"25154","output":"extend","limit":10},"auth":"11d2b45415d5de6770ce196879dbfcf1","id": 0}' 
http://1.1.1.1/zabbix/api_jsonrpc.php

curl命令运行结果：
{"jsonrpc":"2.0","result":[{"itemid":"25154","clock":"1410744134","value":"4840","ns":"375754276"},
{"itemid":"25154","clock":"1410744314","value":"5408","ns":"839852515"},{"itemid":"25154",
"clock":"1410744374","value":"7040","ns":"964558609"},{"itemid":"25154","clock":"1410744554","value":"4072",
"ns":"943177771"},{"itemid":"25154","clock":"1410744614","value":"8696","ns":"995289716"},{"itemid":"25154",
"clock":"1410744674","value":"6144","ns":"992462863"},{"itemid":"25154","clock":"1410744734","value":"6472",
"ns":"152634327"},{"itemid":"25154","clock":"1410744794","value":"4312","ns":"479599424"},{"itemid":"25154",
"clock":"1410744854","value":"4456","ns":"263314898"},{"itemid":"25154","clock":"1410744914","value":"8656",
"ns":"840460009"}],"id":0}


6.history.get方法获取单个监控项最后的值只需把上个脚本中或curl中的limit参数改为1就可。

此时监控项的数据已拿到了，接下来的把它传给前台展示就行了。

http://www.iyunv.com/thread-25496-1-1.html
```



## jmx监控
```
工作原理：
zabbixserver想知道一台主机上的特定的JMX值时，它向ZabbixJavagateway询问，而ZabbixJavagateway使用“JMXmanagementAPI”
去查询特定的应用程序，而前提是应用程序这端在开启时需要“-Dcom.sun.management.jmxremote”参数来开启JMX查询就行了。
Zabbixserver有一个特殊的进程用来连接Javagateway叫StartJavaPollers；Javagateway通过配置文件中START_POLLERS参数设置
启动多个线程，在zabbix服务器这边如果一个连接所用时间超过Timeout，将会被中断，但是Javagateway将继续从JMXcounter取数据。所以
StartJavaPollers设置的值要小于等于START_POLLERS设置的值。
ZabbixJavagateway就相当于一个代理。
Zabbix监控之JMX协议

zabbix-server端安装
yum -y install zabbix-java-gateway 
也可以通过源码安装，请参考官方文档。

zabbix-java-gateway的配置文件是/etc/zabbix/zabbix_java_gateway.conf，配置文件很简单，如下：
# 监听地址
LISTEN_IP=”0.0.0.0″
# 监听端口
LISTEN_PORT=10052
# PID_FILE文件
PID_FILE=”/var/run/zabbix/zabbix_java.pid”
# 开启的工作线程数
START_POLLERS=5

启动zabbix-java-gateway:
service zabbix-java-gateway start
再修改zabbix-server的配置，编辑/etc/zabbix/zabbix_server.conf ，修改下面几个参数：
# JavaGateway的服务器IP地址
JavaGateway=192.168.89.204
# JavaGateway的服务端口
JavaGatewayPort=10052
# 从javaGateway采集数据的进程数
StartJavaPollers=5
配置文件修改后，重启zabbix-server：
service zabbix-server restart


被监控端 
开启JMX
使用JMX前需要先开启JMX，默认是关闭的，在启动JAVA程序时，加入下面的参数，就可以开启JMX：
enableJMX

Apache Tomcat 
如果是windows版本，编辑TOMCAT_HOME/bin/catalina.bat，在开头加入下面几行：
set CATALINA_OPTS=%CATALINA_OPTS% -Djava.rmi.server.hostname=JMX_HOST
set CATALINA_OPTS=%CATALINA_OPTS% -Djavax.management.builder.initial=
set CATALINA_OPTS=%CATALINA_OPTS% -Dcom.sun.management.jmxremote=true
set CATALINA_OPTS=%CATALINA_OPTS% -Dcom.sun.management.jmxremote.port=JMX_PORT 
set CATALINA_OPTS=%CATALINA_OPTS% -Dcom.sun.management.jmxremote.ssl=false
set CATALINA_OPTS=%CATALINA_OPTS% -Dcom.sun.management.jmxremote.authenticate=false

如果是linux版本，编辑TOMCAT_HOME/bin/catalina.sh，在开头加入下面几行：
CATALINA_OPTS="${CATALINA_OPTS} -Djava.rmi.server.hostname=JMX_HOST”
CATALINA_OPTS="${CATALINA_OPTS} -Djavax.management.builder.initial=“
CATALINA_OPTS="${CATALINA_OPTS} -Dcom.sun.management.jmxremote=true” 
CATALINA_OPTS="${CATALINA_OPTS} -Dcom.sun.management.jmxremote.port=JMX_PORT“
CATALINA_OPTS=“${CATALINA_OPTS} -Dcom.sun.management.jmxremote.ssl=false”
CATALINA_OPTS=”${CATALINA_OPTS} -Dcom.sun.management.jmxremote.authenticate=false“

注意JMX_HOST为tomcat的主机名或IP地址，由于zabbix-server访问，JMX_PORT为JMX端口，通常使用12345，然后重启tomcat，JMX就开启了。

下面的配置以监控tomcat为例
1.    在 tomcat 下载页面 Extras 类别中下载 JMX Remote jar 二进制包。放在 tomcat/lib 下面.
#wget  –S  http://mirror.bit.edu.cn/apache/tomcat/tomcat-6/v6.0.39/bin/extras/catalina-jmx-remote.jar
# mv catalina-jmx-remote.jar  /webapp/tomcat6/lib/
2. 修改 tomcat/bin 目录下 catalina.sh ，添加以下内容：
CATALINA_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false 
-Dcom.sun.management.jmxremote.ssl=fa lse
-Djava.rmi.server.hostname=客户端ip地址"
3.启动tomcat
# cd /usr/local/tomcat/bin/
# ./startup.sh
4.下载cmdline-jmxclient-0.10.3.jar文件测试是否恩能够取得数据
#wget http://repo.typesafe.com/typesafe/repo/cmdline-jmxclient/cmdline-jmxclient/0.10.3/cmdline-jmxclient-0.10.3.jar
5.测试 有数据则表示成功
# java -jar cmdline-jmxclient-0.10.3.jar - localhost:12345 java.lang:type=Memory NonHeapMemoryUsage
01/26/2014 11:55:55 +0800 org.archive.jmx.Client NonHeapMemoryUsage:
committed: 52690944
init: 24313856
max: 136314880
used: 52454776
```



## discover rule
```
首先是写脚本，输出当前机器监听的tcp端口

portscan.py

zabbix用户启动的，默认不能执行netstat -p   chmod +s /bin/netstat或者不用或者sudo

#!/usr/bin/env python
import os
import json
 
data = {}
tcp_list = []
port_list = []
command = '''netstat -ntl | awk '{print $4}' | grep 0.0.0.0 | awk -F":" '{print $2}' '''
line = os.popen(command).readlines()
 
for port in line:
    port_dict = {}
    port = port.replace('\n','')
    if int(port) > 20000:
        continue
    port_dict['{#TCP_PORT}'] = port.replace('\n','')
    tcp_list.append(port_dict)
 
data['data'] = tcp_list
jsonStr = json.dumps(data, sort_keys=True, indent=4)
print jsonStr
这个脚本运行的结果如下：

{
    "data": [
        {
            "{#TCP_PORT}": "843"
        }, 
        {
            "{#TCP_PORT}": "3035"
        }, 
        {
            "{#TCP_PORT}": "10050"
        }
    ]
}
修改win下zabbix_agent的配置文件zabbix_agentd.conf

UnsafeUserParameters=1
UserParameter=tcpportlisten,python /etc/zabbix/portscan.py
修改完成后重启zabbix_agent服务。
这个时候在zabbix_server端就可以用zabbix_get来测试是否正常。
zabbix_get -s ip -k tcpportlisten
返回的结果和在agent上运行脚本返回的结果一致就表示正常。

在页面添加discover

在模版或者主机的页面上点击Discovery(探索)，然后在右上角点击Create discovery rule(创建探索规则)
zabbix利用discovery批量添加端口监控 - 第1张  | ㄨ销声匿迹、Linux
然后在这个新建的tcp port discover里面建立一个Item
zabbix利用discovery批量添加端口监控 - 第2张  | ㄨ销声匿迹、Linux

最后创建报警的trigger
zabbix利用discovery批量添加端口监控 - 第3张  | ㄨ销声匿迹、Linux

注意这个地方的表达式

{Template OS Linux:net.tcp.listen[{#TCP_PORT}].count(#3,0,eq)}>1
如果你是在单个机器上添加的，这里Template OS Linux就应该是某个机器的具体名称，如果是模版，这里就是模版的名称

.count(#3,0,eq)}>1
表示最后三次的值等于0，触发次数大于一次则报警
```



## io
```
disk_scan.py
#!/usr/bin/env python
from json import dumps
from commands import getoutput
result = {}
disklist = []
disks = getoutput(''' egrep "\\bsd[a-z]\\b|\\bxvd[a-z]\\b|\\bvd[a-z]\\b" /proc/diskstats | awk '{print $3}' ''')
for disk in disks.split("\n"):
    if len(disk)!=0:
        disklist.append({'{#DISK_NAME}':disk})
result["data"] = disklist
print dumps(result,indent=4,sort_keys=True)


vi /usr/local/zabbix/etc/zabbix_agentd.conf

UserParameter=disk.discovery,/usr/bin/python /etc/zabbix/disk_scan.py
UserParameter=custom.vfs.dev.read.ops[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$4}' //磁盘读的次数
UserParameter=custom.vfs.dev.read.ms[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$7}'   //磁盘读的毫秒数
UserParameter=custom.vfs.dev.write.ops[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$8}'    //磁盘写的次数
UserParameter=custom.vfs.dev.write.ms[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$11}'   //磁盘写的毫秒数
UserParameter=custom.vfs.dev.io.active[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$12}'  
UserParameter=custom.vfs.dev.io.ms[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$13}'   
//花费在IO操作上的毫秒数
UserParameter=custom.vfs.dev.read.sectors[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$6}'   
   //读扇区的次数（一个扇区的等于512B）
UserParameter=custom.vfs.dev.write.sectors[*],cat /proc/diskstats | grep $1 | head -1 | awk '{print $$10}'  
   //写扇区的次数（一个扇区的等于512B）
UserParameter=custom.vfs.dev.iowait[*],iostat -x 1 2 | grep $1 | tail -n 1 | awk '{print $$10}'
```



## tcp状态
/etc/zabbix/zabbix\_agentd.d/tcp\_net.conf



UserParameter=TIME\_WAIT,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep TIME\_WAIT \|awk '{print $2}'

UserParameter=CLOSE\_WAIT,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep CLOSE\_WAIT \|awk '{print $2}'

UserParameter=FIN\_WAIT1,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep FIN\_WAIT1 \|awk '{print $2}'

UserParameter=ESTABLISHED,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep ESTABLISHED \|awk '{print $2}'

UserParameter=SYN\_RECV,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep SYN\_RECV \|awk '{print $2}'

UserParameter=LAST\_ACK,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep LAST\_ACK \|awk '{print $2}'

UserParameter=LISTEN,netstat -an \| awk '/^tcp/ {++S\[$NF\]} END {for\(a in S\) print a, S\[a\]}' \| grep LISTEN \|awk '{print $2}'

## zabbix_proxy
```
﻿
yum install zabbix-proxy zabbix-proxy-mysql mysql-server -y
mysql
create database zabbix_proxy;
grant all on zabbix_proxy.* to 'zabbix'@'127.0.0.1' identified by 'zbpass';
delete from mysql.user where user="";
flush privileges;
导入表
mysql zabbix_proxy < /usr/share/doc/zabbix-proxy-mysql-2.4.8/create/schema.sql
cat  /etc/zabbix/zabbix_proxy.conf  修改
Server=172.16.10.126             #指向Zabbix Server
Hostname=本机ip
DBHost=localhost                 #指定数据库
DBName=zabbix_proxy              #数据库名
DBUser=zbuser                    #数据库用户
DBPassword=zbpass                #数据库密码






agent的server改为proxy的ip
注意所有key必须为主动模式
agent报not found可以重启proxy和agent试试
```



## ztree插件
```
https://github.com/spide4k/zatree


1：下载文件

git clone https://github.com/spide4k/zatree.git zatree

2：为了减少编辑文件带来的误操作，以后zatree只提供和zabbix整合好的包

php需要支持php-xml、php-gd、php-mysql

先备份当前zabbix web目录并挪走，然后解压zatree-zabbix-2.4.5.tar.gz，然后修改以下两个文件

3：zabbix数据库 拷贝源目录的conf/zabbix.conf.php到新目录覆盖

如果原来有添加字体也顺手拷贝过来

4：支持web interface,修改配置文件 zatree/zabbix_config.php

'user'=>'xxx', //web登陆的用户名    zabbix账号

'password'=>'xxx', //web登陆的密码

'http_user'=>'xxx', //httpsweb登陆的用户名

'http_password'=>'xxx', //httpsweb登陆的密码

删除运维帮 广告
编辑 zabbix/zatree/graph.php文件 删除 411-416 行
 <div align="center" style='font-size:12px;'>
             <font size="5px" color="red">运维帮,一个技术分享订阅号,扫描我,给我们力量</font><br>
                 <font size="2px" color="red">编辑 zatree/graph.php 文件删除我</font><br>
            <img src="static/yunweibang-weixin.jpg" /><br>
           <a href="https://github.com/spide4k/zatree" target="_blank">Zatree</a> version 2.4 for Zabbix 2.4.x, 
           技术支持QQ群: 271659981, 微信订阅号:yunweibang
        </div>
```



## 自动注册
```
上一篇内容《zabbix自动发现配置》，大概内容是zabbix server去扫描一个网段，把在线的主机添加到Host列表中。
我们本篇内容与上篇相反，这次是Active agent主动联系zabbix server，最后由zabbix server将这些agent加到host里。
对于需要部署特别多服务器的人来说，这功能相当给力。所有服务器批量装好zabbix agent，server配置好trigger，
所有的服务器都配置好了，非常快速。
2. 配置
2.1配置文件修改
指定server ip

1
2
# cat /usr/local/zabbix-2.2.2/etc/zabbix_agentd.conf | grep -E ^ServerActive
 ServerActive=66.175.222.232
修改Hostname

1
2
# cat /usr/local/zabbix-2.2.1/etc/zabbix_agentd.conf | grep -E ^Hostname                           
Hostname=auto-reg-for-ttlsa-01
关于主机名：如果zabbix_agentd.conf配置有定义Hostname，那么zabbix会使用这个Hostname命名，否则agent的主机名（hostname得来的）
修改metadataitem

1
2
cat /usr/local/zabbix-2.2.1/etc/zabbix_agentd.conf | grep HostMetadataItem=
 HostMetadataItem=system.uname

2.2 配置action
步骤：configuration>>action>>Event source（选择Auto registration）>>Create Action，我们按如下步骤来定义个action
2.2.1 action选项卡
hostmetadata

定义Action名称，以及发送消息的主题和内容，使用默认的就行了
2.2.2 Conditions选项卡
hostmetadata

Host metadata包含Linux字符的主机将会触发 2.2.3的操作，什么是metadata，文章的下半段会专门讲解。
2.2.3 operations选项卡
hostmetadata

满足条件的active host发起请求，server会完成三个动作：
把agent加到host列表
把agent加入linux servers组
agent主机link模板Template OS linux
3. 查看结果
查看/tmp/zabbix_server.log我们能看到如下内容：

1
 16585:20150203:161110.910 enabling Zabbix agent checks on host "auto-reg-for-ttlsa-01": host became available
看到如上内容，表明host增加成功，此时此刻的host列表如下：
hostmetadata

4. HostMetadataItem与HostMetadata
作用：用于标示主机，通过该符号能够把主机区别开来。比如我们经常用它来区分linux与windows系统，这样才能分别给他们设置组与template等等
4.1 HostMetadataItem用法

1
HostMetadataItem=system.uname
它的值来之key
4.2 HostMetadata用法

1
HostMetadata: Linux hehehehehehehehe xxxxx
他的值是直接定义的
通过使用各式各样的metadata我们可以用于区分各个主机，来达到我们各种需求。
```



## 自定义key
    自定义
    UserParameter=mysql.ping,mysqladmin -uroot ping|grep -c alive
    如果返回1表示MySQL运行中，如果返回0表示MySQL挂了
    UserParameter=key[*],command

    Key    唯一. [*]表示里面可以传递多个参数
    Command    需要执行的脚本，key的[]里面的参数一一对应$1到$9，一共9个参数。$0表示脚本命令.
    注意事项
    1. 如果需要使用命令行里面出现$2这种变量，那么你要使用两个$$2，例如awk ’{ print $$2 }’，之前就遇到过这个问题，
    不停的测试自己脚本输出正常，但是zabbix却拿不到数据，原来是出在这里。为了防止和参数冲突，所以zabbix做了这个规定。
    2. zabbix禁止使用一些不安全的参数，如下：
    \ ' ” ` * ? [ ] { } ~ $ ! & ; ( ) < > | # @
    3. 从zabbix 2.0开始，zabbix返回文本数据可以是空格。

    UserParameter=mysql.ping[*],mysqladmin -u$1 -p$2 ping | grep -c alive
    如下参数用于监控MYSQL，并且可以传递用户名和密码。
    mysql.ping[zabbix,our_password]
    统计一个文件中有多少行被匹配?
    UserParameter=wc[*],grep -c "$2" $1
    如下方法将会返回文件中出现指定字符的行数
    wc[/etc/passwd,root]
    wc[/etc/services,zabbix]

    --------------------------------------------------------------------------------
    监控mcu的cpu和内存
    UserParameter=proce.cpu[*],top -b -n 1 | grep $1 | awk '{print $$9}'
    UserParameter=proce.mem[*],sudo cat /proc/`ps aux | grep $1 |  grep -v grep | awk '{print $$2}'`/smaps 
    | grep -i pss | awk '{sum += $$2}END{print sum*1024}'

