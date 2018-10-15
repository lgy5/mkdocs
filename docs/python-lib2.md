## 颜色
```
"""
from colors import blue,cyan,green,magenta,red,white,yellow
 
def color_test():
    print blue('blue',bold=True)
    print cyan('cyan',bold=True)
    print green('green',bold=True)
    print magenta('magenta',bold=True)
    print red('red',bold=True)
    print white('white',bold=True)
    print yellow('yellow',bold=True)
 
"""
 
 
def _wrap_with(code):
 
    def inner(text, bold=False):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner
 
red = _wrap_with('31')
green = _wrap_with('32')
yellow = _wrap_with('33')
blue = _wrap_with('34')
magenta = _wrap_with('35')
cyan = _wrap_with('36')
white = _wrap_with('37')
```



## urlencode
```
urlencode 调用方法

urlencode的参数必须是Dictionary

d= {'par1':'a','par2':'b',}
print urllib.urlencode(m)
#par2=b&par1=a
urlencode 编码

函数urlencode不会改变传入参数的原始编码，也就是说需要在调用之前将post或get参数的编码调整好。Python编码转换可以参考 
http://www.pythonclub.org/python-basic/codec 。

问题：现在模拟请求Google和baidu，由于baidu使用的是gb2312编码,google使用的是utf8编码，两个站点提交到URL中的中文
参数的urlencode值是不一样，下面以”帝国”为例:

python文件的

# coding: UTF-8

执行urllib.urlencode(“帝国”)得到的结果是：%E5%B8%9D%E5%9B%BD, 此结果说明默认使用 urlencode得到的结果是utf8编码的“帝国”。

现在想得到gb2312编码的“帝国”怎么办呢？

st = u'帝国'
st = st.encode('gb2312')
m = {'par':st,}
s = urllib.urlencode(m)
print s
#结果为par=%B5%DB%B9%FA
django中urlencode类似，方法如下：

from django.utils.http import urlquote
a = urlquote('帝国')
print a
得到汉字的GBK编码

其实可以用urllib的quote函数对URL中的中文进行转换，将中文转换成GBK的编码，得到的编码是符合URI标准的URL。

>>> import urllib
>>> a = "帝国"
>>> a
'\xb5\xdb\xb9\xfa'
>>> urllib.quote(a)
'%B5%DB%B9%FA'
>>>
```



## syslog
```
配置Cisco ASA 5550 Firewall2. syslog 服务器脚本配置Cisco ASA 5550 Firewall
logging enable

logging timestamp

logging trap warnings

logging host inside 172.16.0.5

logging facility local0

172.16.0.5 改为你的syslog服务器地址

syslog 服务器脚本
*注意：Python版本必须3.0以上

chmod 700 syslogd

./syslogd

# -*- encoding: utf-8 -*-
# Cisco ASA Firewall - Syslog Server by neo
# Author: neo<openunix@163.com>

import logging
import socketserver
import threading

LOG_FILE = '/var/log/asa5550.log'

logging.basicConfig(level=logging.INFO,
                    format='%(message)s',
                    datefmt='',
                    filename=LOG_FILE,
                    filemode='a')

class SyslogUDPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = bytes.decode(self.request[0].strip())
        socket = self.request[1]
        print( "%s : " % self.client_address[0], str(data))
        logging.info(str(data))
#        socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    try:
        HOST, PORT = "0.0.0.0", 515
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("Crtl+C Pressed. Shutting down.")
```


## psutil系统信息
```
安装  yum install python-devel python-pip -y && pip install psutil

#!/usr/bin/env python
#coding:utf-8
import psutil
 
def meminfo():
    #单位为字节
    mem = psutil.virtual_memory()
    print mem
    print mem.total,mem.used,mem.free #单项数据
 
def cpuinfo():
    #需要显示所有逻辑CPU信息,指定方法变量percpu=True即可
    print psutil.cpu_times(percpu=True)
    cpu = psutil.cpu_times()
    print cpu
    print cpu.user #单项数据
 
    print psutil.cpu_count() #获取CPU的逻辑个数
    print psutil.cpu_count(logical=False)    #获取CPU的物理个数
 
def swapinfo():
    print psutil.swap_memory() #swap,单项数据类似
 
def diskinfo():
    print psutil.disk_partitions() #磁盘完整信息
    print psutil.disk_usage("/")   #分区（参数）的使用情况
    print psutil.disk_io_counters() #取硬盘总的IO个数 读写信息
    print psutil.disk_io_counters(perdisk=True)  #"perdisk=True"参数获取单个分区IO个数、
 
def netinfo():
    print psutil.net_io_counters() #网络总的IO信息
    print psutil.net_io_counters(pernic=True) #每个网络接口的IO信息
 
def otherinfo():
    from datetime import datetime
    print psutil.users() #当前登录系统的用户信息
    boot_time = psutil.boot_time() #获取开机时间，以Linux时间戳格式返回
    print datetime.fromtimestamp(boot_time).strftime ("%Y-%m-%d %H：%M：%S") #转换时间
 
def proceinfo():
    psutil.pids() #所有进程PID
    p = psutil.Process(1050)  #实例化一个Process对象，参数为一进程PID
    print p.name(),p.exe(),p.cwd(),p.status(),p.create_time(),p.uids(),p.gids(),p.cpu_times()
    #p.exe ()  #进程bin路径  p.cpu_times ()      #进程CPU时间信息，包括user、system两个CPU时间
    print p.cpu_affinity() , p.memory_percent() , p.memory_info() , p.io_counters() , p.num_threads()
    #     get进程CPU亲和度   进程内存利用率       内存rss、vms信息    IO信息           程开启的线程数
 
def popenuse():
    from subprocess import PIPE
    p = psutil.Popen(["/usr/bin/python", "-c", "print('hello')"], stdout=PIPE)
    print p.name() , p.username(),p.communicate()
    #print p.cpu_times()
```



## IPy地址处理
```
#!/usr/bin/env python
#coding:utf-8
from IPy import IP
 
#区分出IPv4与IPv6
print IP('10.0.0.0/8').version() , IP('::1').version()
 
def wanduan():
    ip = IP('192.168.0.0/24')
    print ip.len() #网段的IP个数
    for x in ip:
        print x  #所有IP清单
 
def zhuanhuan():
    print IP("192.168.1.20").reverseNames() #反向解析地址格式
    print IP('8.8.8.8').iptype() #ip类型，公网'PUBLIC' 私网'PRIVATE'
    print IP("8.8.8.8").int()       #转换成整型格
    print IP('8.8.8.8').strHex()    #转换成十六进制格式
    print IP('8.8.8.8').strBin()    #转换成二进制格式
    print (IP(0x8080808))      #十六进制转成IP格式
    #根据IP与掩码生产网段格式
    print IP('192.168.1.0').make_net('255.255.254.0')
    print IP('192.168.1.0/255.255.255.0', make_net=True)
    print IP('192.168.1.0-192.168.1.255', make_net=True)
    #strNormal
    for i in range(4):
        print "strNormal(%s):%s" % (i,IP('192.168.1.0/24').strNormal(i))
 
def jishuan(ip_s):
    ips = IP(ip_s)
    if len(ips) > 1: #多个地址
        print("网络地址: %s" % ips.net())
        print("网络掩码: %s" % ips.netmask())
        print("广播地址: %s" % ips.broadcast())
        print('地址反向解析: %s' % ips.reverseNames()[0])
        print('网络子网数: %s' % len(ips))
    else:
        #为单个IP地址   
        print ('IP反向解析: %s' % ips.reverseNames ()[0]) 
        print ('十六进制地址: %s' % ips.strHex ())
        print ('二进制地址: %s' % ips.strBin ())
        print ('iptype: %s' % ips.iptype ())    #输出地址类型，如PRIVATE、PUBLIC、LOOPBACK等
```



## difflib文件比较
```
#!/usr/bin/env python
#coding:utf-8
import difflib
 
#字符串比较
text1 = """text1:
This module provides classes and functions for comparing sequences.
including HTML and context and unified diffs
difflib document V7.4
and string
"""
text1_lines = text1.splitlines() #按行切割
text2 = """text2:
This module provides classes and functions for comparing sequences.
including HTML and context and unifiled diffs.
difflb document V7.5"""
text2_lines = text2.splitlines()
 
def diffstr():
    d = difflib.Differ()  #创建Differ对象
    diff = d.compare(text1_lines,text2_lines)
    print "\n".join(list(diff))
 
    d = difflib.HtmlDiff()  #生成html,用 python difflib_l1.py > result.html,网页查看结果
    print d.make_file(text1_lines,text2_lines)
 
#文件比较
import sys
try:
    textfile1 = sys.argv[1]
    textfile2 = sys.argv[2]
except Exception,e:
    print "Error:" + str(e)
    print "Usage: ./simple filename1 filename2"
    sys.exit()
 
def readline(filename): #等于文件读取函数
    try:
        fileHandle = open(filename,'rb')
        text = fileHandle.read().splitlines() #读取文件内容，按行切割
        fileHandle.close()
        return text
    except IOError as error:
        print("Read file  Error:"+str(error))
        sys.exit()
 
text1_lines = readline(textfile1)
text2_lines = readline(textfile2)
 
d = difflib.HtmlDiff()
print d.make_file(text1_lines,text2_lines)
```

## scapy网络轨迹
```
yum -y install tcpdump graphviz ImageMagick
pip install scapy
#!/usr/bin/env python
#coding:utf-8
import os,sys,time,subprocess
import warnings,logging
warnings.filterwarnings("ignore",category=DeprecationWarning)  #屏蔽scapy无用告警信息
logging.getLogger("scapy.runtime").setLevel (logging.ERROR) #屏蔽模块IPv6多余告警

from scapy.all import traceroute
domains = raw_input('Please input one or more IP/domain: ') #接受输入的域名或IP
target =  domains.split(' ')
dport = [80]    #扫描的端口列表
if len (target) >= 1 and target[0]!='':
     res, unans = traceroute(target, dport=dport, retry=-2) #启动路由跟踪
     res.graph (target="> test.svg")    #生成svg矢量图形
     time.sleep(1)
     subprocess.Popen("/usr/bin/convert test.svg test.png", shell=True) #svg转png格式
else:
     print "IP/domain number of errors, exit"
代码运行结果见图3-15，“-”表示路由节点无回应或超时；“11”表示扫描的指定服务无回应；“SA”表示扫描的指定服务有回应，
一般是最后一个主机IP。生成的路由轨迹图见图3-16（仅局部），“-”将使用unk*单元代替，重点路由节点将通过ASN获取所处的
运营商或IDC位置，如IP“202.102.69.210”为“CHINANET-JS-AS-AP ASNumber for CHINANET jiangsu province backbone,
CN”意思为该IP所处中国电信江苏省骨干网。
```



## nmap端口扫描
```
yum install nmap -y  && pip install python-nmap
#!/usr/bin/env python
#coding:utf-8
import sys
import nmap

scan_row = []
try:
    hosts = sys.argv[1]
    port = sys.argv[2]
except IndexError:
    print "Uasge ./scanport.py ip port"
    sys.exit(1)

try:
    nm = nmap.PortScanner()
except namp.PortScannerError:
    print "Nmap not found",sys.enc_info()[0]
    sys.exit(2)
except:
    print("Unexpected error:",sys.exc_info()[0])
    sys.exit(3)

try:
    nm.scan(hosts=hosts,arguments="-v -sS -p"+port)
except Exception,e:
    print "Scan error:" +str(e)

for host in nm.all_hosts():
    print "----------------------------------------------------------------------"
    print('Host : %s (%s)' % (host, nm[host].hostname()))    #输出主机及主机名
    print('State : %s' % nm[host].state())    #输出主机状态,如up、down
    for proto in nm[host].all_protocols():    #遍历扫描协议
        print('----------')
        print('Protocol : %s' % proto)    #输入协议名
        lport = nm[host][proto].keys()    #获取协议的所有扫描端口
        lport.sort()    #端口列表排序
        for port in lport:    #遍历端口及输出端口与状态
            print('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))
其中主机输入支持所有表达方式，如www.qq.com、192.168.1.*、192.168.1.1-20、192.168.1.0/24等，
端口输入格式也非常灵活，如80,443,22、80,22-443。
```

## 模拟登陆
```
用fiddler过滤出地址和需要的参数

先用cookielib获取cookie，再用获取到的cookie，进入需要登录的网站。
# -*- coding: utf-8 -*-

# !/usr/bin/python

import urllib2
import urllib
import cookielib
import re
auth_url = 'http://www.nowamagic.net/'
home_url = 'http://www.nowamagic.net/';
# 登陆用户名和密码
data={
   "username":"nowamagic",
   "password":"pass"
}
# urllib进行编码
post_data=urllib.urlencode(data)
# 发送头信息

headers ={

   "Host":"www.nowamagic.net",
"Referer": "http://www.nowamagic.net"
}
# 初始化一个CookieJar来处理Cookie

cookieJar=cookielib.CookieJar()
# 实例化一个全局opener

opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))

# 获取cookie
req=urllib2.Request(auth_url,post_data,headers)
result = opener.open(req)
# 访问主页 自动带着cookie信息
result = opener.open(home_url)
# 显示结果
print result.read()

再附带几个示例程序：
1. 使用已有的cookie访问网站
import cookielib, urllib2

ckjar = cookielib.MozillaCookieJar(os.path.join('C:\Documents and Settings\tom\Application 
Data\Mozilla\Firefox\Profiles\h5m61j1i.default', 'cookies.txt'))
req = urllib2.Request(url, postdata, header)

req.add_header('User-Agent', \
   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(ckjar) )

f = opener.open(req)
htm = f.read()
f.close()

2. 访问网站获得cookie，并把获得的cookie保存在cookie文件中
import cookielib, urllib2

req = urllib2.Request(url, postdata, header)
req.add_header('User-Agent', \
   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')

ckjar = cookielib.MozillaCookieJar(filename)
ckproc = urllib2.HTTPCookieProcessor(ckjar)

opener = urllib2.build_opener(ckproc)

f = opener.open(req)
htm = f.read()
f.close()

ckjar.save(ignore_discard=True, ignore_expires=True)
3. 使用指定的参数生成cookie,并用这个cookie访问网站
import cookielib, urllib2

cookiejar = cookielib.CookieJar()
urlOpener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
values = {'redirect':", 'email':'abc@abc.com',
      'password':'password', 'rememberme':", 'submit':'OK, Let Me In!'}
data = urllib.urlencode(values)

request = urllib2.Request(url, data)
url = urlOpener.open(request)
print url.info()
page = url.read()

request = urllib2.Request(url)
url = urlOpener.open(request)
page = url.read()
print page
```



## 文件与目录
```
file
通常建议用内置函数 open() 打开文件，file 用于类型判断。

>>> with open("test.txt", "w") as f:
...     print isinstance(f, file)   // 类型判断
...     f.writelines(map(str, range(10)))

True
File Object 实现了上下文协议，可确保文件被及时关闭。实际上，文件对象被回收时总是会调用 close 方法，所以可以写下面这样的代码。

>>> open("test.txt", "r").read()
'0123456789'
如果要把数据写到磁盘上，除调用 flush() 外，还得用 sync()，以确保数据从系统缓冲区同步到磁盘。close() 总是会调用这两个方法。

打开模式：

r: 只读。
w: 只写。已存在文件将被清除 (truncate)。
a: 添加。总是添加到文件尾部。
b: 二进制模式。
r+: 更新文件，可读写，不会截短文件。
w+: 更新文件，可读写，清除原有内容。
a+: 更新文件，可读写，总是在尾部添加。
文件对象还实现了迭代器协议，可直接循环获取其内容。

>>> with open("main.py", "r") as f:
...     for line in f: print line
...
读方法总能判断不同平台的换行标记，但写方法不会添加任何换行字符，包括 writelines。

>>> with open("test.txt", "w") as f:
...     f.write("a")
...     f.writelines("bc")

>>> cat test.txt
abc
如必须按不同平台写入换行标记，可使用 os.linesep。

>>> os.linesep
'\n'
字符串本身就是序列类型，可以直接用 writelines(str)。readline() 会返回包括换行符在内的整个行数据。通常建议用迭代器或
 xreadlines() 代替 readlines()，后者默认一次性读取整个文件。

binary
用 struct 将其他类型构建成二进制字节数组，然后写入文件即可。

>>> import struct

>>> data = struct.pack("2i2s", 0x1234, 0xFF56, "ab")
>>> open("test.dat", "w").write(data)

>>> !xxd -g 1 test.dat
0000000: 34 12 00 00 56 ff 00 00 61 62 4...V...ab

>>> struct.unpack("2i2s", open("test.dat").read())
(4660, 65366, 'ab')

>>> with open("test.dat") as f:   // 结构化读取
...     def xread(fmt):
...         n = struct.calcsize(fmt)  // 计算长度
...         s = f.read(n)
...         return struct.unpack(fmt, s)
...     print xread("i")
...     print xread("i")
...     print xread("2s")

(4660,)
(65366,)
('ab',)
对于相同类型的数据，可考虑用 array，以获得更好的性能。

>>> import array

>>> datas = array.array("i")
>>> datas.append(0x1234)
>>> datas.append(0xFF56)
>>> datas.tofile(open("test.dat", "w"))

>>> !xxd -g 1 test.dat
0000000: 34 12 00 00 56 ff 00 00 4...V...

>>> d2 = array.array("i")
>>> d2.fromfile(open("test.dat"), 2)
>>> d2
array('i', [4660, 65366])
类似的还有 bytearray，可作 Buffer 用，详情参见 struct 章节。

encoding
标准库 codecs 提供了一个包装版的 open()，可自动完成编码转换工作。

>>> import sys
>>> reload(sys)
>>> sys.setdefaultencoding("utf-8")

>>> with codecs.open("test.txt", "w", "gbk") as f:
...     f.write("中国")

>>> !xxd -g 1 test.txt
0000000: d6 d0 b9 fa ....

>>> "中国".encode("gbk")
'\xd6\xd0\xb9\xfa'

>>> s = codecs.open("test.txt", encoding = "gbk").read()
>>> s
u'\u4e2d\u56fd'
>>> print s
中国
descriptor
除使用文件对象外，某些时候还可能需要直接操控文件描述符。

>>> import os

>>> fd = os.open("test.txt", os.O_CREAT | os.O_RDWR, 0644) // 注意是八进制。

>>> ls -l test.txt
-rw-r--r-- 1 yuhen staff 6 3 25 10:45 test.txt

>>> os.write(fd, "abc")
3

>>> f = os.fdopen(fd, "r+")  // 通过描述符创建文件对象。
>>> f.seek(0, os.SEEK_SET)  // 注意调整位置。
>>> f.read()
'abc'
>>> f.write("123")
>>> f.flush()    // os 库提供的函数是系统调用，因此需要把数据从用户缓存
      // 刷新到系统缓存。

>>> os.lseek(fd, 0, os.SEEK_SET)
0

>>> os.read(fd, 100)
'abc123'

>>> os.close(fd)    // 通常建议用和打开对应的方式关闭。
文件对象 fileno() 方法返回其对应的文件描述符。

tempfile
Python 对临时文件的支持算是我所见过语言中最丰富的。通常建议使用 NamedTemporaryFile，其他可以忽略。

TemporaryFile: 创建临时文件对象，关闭时自动删除。
NamedTemporaryFile: 创建临时文件对象，可获取文件名，参数决定是否自动删除。
SpooledTemporaryFile: 和 TemporaryFile 类似，只有在数据超过阈值时，才写入硬盘。
>>> import tempfile, os.path

>>> tmp = tempfile.NamedTemporaryFile()
>>> tmp.name
'/var/folders/r2/4vkjhz6s6lz02hk6nh2qb99c0000gn/T/tmpYYB6p3'

>>> os.path.exists(tmp.name)
True

>>> tmp.close()
>>> os.path.exists(tmp.name)
False
默认使用系统临时目录和前缀，当然也可以指定不同的配置。

>>> with tempfile.NamedTemporaryFile(prefix = "xxx_", suffix = ".tmp", dir = ".") as f:
...     print f.name
...
/Users/yuhen/test/xxx_SL3apY.tmp
与临时文件有关的函数还有：

tempfile.gettempdir: 返回系统临时文件存放路径。
tempfile.gettempprefix: 返回默认的临时文件名前缀。
tempfile.mkdtemp: 创建临时目录。
tempfile.mkstemp: 创建临时文件，返回描述符和文件名，需手工删除。
os.tempnam: 仅返回有效的临时文件名，并不创建文件。
os.tmpfile(): 创建临时文件对象，关闭后自动删除。
>>> tempfile.gettempdir()
'/var/folders/r2/4vkjhz6s6lz02hk6nh2qb99c0000gn/T'

>>> tempfile.gettempprefix()
'tmp'
>>> d = tempfile.mkdtemp(); d
'/var/folders/r2/4vkjhz6s6lz02hk6nh2qb99c0000gn/T/tmpE_bRWd'

>>> os.path.exists(d)
True

>>> os.removedirs(d)
>>> fd, name = tempfile.mkstemp()

>>> os.write(fd, "123\n")
4

>>> os.close(fd)

>>> os.path.exists(name)
True

>>> os.remove(name)
os.path
常用函数列表：





拼接的目录看上乱糟糟让人烦心。

>>> os.path.normpath("./../a/b/../c")
'../a/c'
展开用户根路径，或者包含系统环境变量的路径。

>>> os.path.expanduser("~/.vimrc")
'/Users/yuhen/.vimrc'

>>> os.path.expandvars("$HOME/.vimrc")
'/Users/yuhen/.vimrc'
除非只要扩展名，否则还是先用 basename 将路径去掉。

>>> os.path.splitext(os.path.basename("/usr/local/lib/libevent.a"))
('libevent', '.a')
os
常用函数列表：





迭代 walk，返回 "(路径，子目录列表，文件列表)"，可配合 fnmatch 做通配符过滤。

>>> for path, dirs, files in os.walk("."):
...     for f in files:
...         if fnmatch.fnmatch(f, "*.py"):
...             print os.path.join(path, f)

./main.py
./bak/amqplib_test.py
./bak/eventlet_test.py
./bak/extract_text.py
./bak/fabric_test.py
如果仅操作当前目录，可以用 glob 代替 listdir，前者支持通配符。

>>> glob.glob("./bak/[rs]*.py")    # 迭代器版本: iglob
['./bak/redis_test.py', './bak/socket_test.py']
如目录中还有文件存在，removedirs 会抛出异常。建议用 shutil.rmtree() 代替，注意参数区别。

>>> os.makedirs("./a/b/c")
>>> open("./a/b/c/test.txt", "w").write("abc")

>>> os.removedirs("./a/b/c")
OSError: [Errno 66] Directory not empty: './a/b/c'

>>> import shutil
>>> shutil.rmtree("./a")
某些时候，需要先测试文件是否拥有某些权限。

>>> os.access("a.txt", os.W_OK)
True
都是哪些人需要修改文件时间？

>>> stat -x a.txt
    File: "a.txt"
    Size: 0 FileType: Regular File
    Mode: (0644/-rw-r--r--) Uid: ( 501/ yuhen) Gid: ( 20/ staff)
Device: 1,2 Inode: 5111644 Links: 1
Access: Mon Mar 25 17:43:01 2013
Modify: Mon Mar 25 17:43:01 2013
Change: Mon Mar 25 17:43:01 2013
>>> atime = time.mktime(datetime.datetime(2010, 10, 1).utctimetuple())
>>> mtime = time.mktime(datetime.datetime(2010, 11, 2).utctimetuple())
>>> os.utime("a.txt", (atime, mtime))

>>> os.stat("a.txt").st_atime == atime
True
获取文件权限信息时，别忘了转换成八进制。

>>> oct(os.stat("a.txt").st_mode)
'0100644'
shutil
常用函数列表：



copytree 可以指定多个忽略通配符，且必须确保目标路径不存在。

>>> shutil.copytree("./bak", "./b/bak", ignore = shutil.ignore_patterns("*.pyc",
"*.bak"))
```


## filecmp
```
filecmp模块用于比较文件及文件夹的内容，它是一个轻量级的工具，使用非常简单。python标准库还提供了difflib模块用于
比较文件的内容。关于difflib模块，且听下回分解。
    filecmp定义了两个函数，用于方便地比较文件与文件夹：
filecmp.cmp(f1, f2[, shallow])：
    比较两个文件的内容是否匹配。参数f1, f2指定要比较的文件的路径。可选参数shallow指定比较文件时是否需要考虑文件
    本身的属性（通过os.stat函数可以获得文件属性）。如果文件内容匹配，函数返回True，否则返回False。
filecmp.cmpfiles(dir1, dir2, common[, shallow])：
    比较两个文件夹内指定文件是否相等。参数dir1, dir2指定要比较的文件夹，参数common指定要比较的文件名列表。函数
    返回包含3个list元素的元组，分别表示匹配、不匹配以及错误的文件列表。错误的文件指的是不存在的文件，或文件被琐
    定不可读，或没权限读文件，或者由于其他原因访问不了该文件。
    filecmp模块中定义了一个dircmp类，用于比较文件夹，通过该类比较两个文件夹，可以获取一些详细的比较结果（如只在
    A文件夹存在的文件列表），并支持子文件夹的递归比较。
dircmp提供了三个方法用于报告比较的结果：
report()：只比较指定文件夹中的内容（文件与文件夹）
report_partial_closure()：比较文件夹及第一级子文件夹的内容
report_full_closure()：递归比较所有的文件夹的内容
例子：在文件夹"1"中含有文件"1.txt", 在文件夹"2"中含有文件"1.txt"和"2.txt",其两个文件夹下面的文件"1.txt"内容一样，
>>>import filecmp
>>>x = filecmp.dircmp("1", "2")
>>>x.report()
>>>
diff 1 2
Only in 2 : ['2.txt']
Identical files : ['1.txt']

如果两个文件夹下面的文件"1.txt"内容不相同那么结果如下：
>>>import filecmp
>>>x = filecmp.dircmp("1", "2")
>>>x.report()
>>>
diff 1 2
Only in 2 : ['2.txt']
Differing files : ['1.txt']


dircmp还提供了下面这些属性用于获取比较的详细结果：
left_list：左边文件夹中的文件与文件夹列表；
right_list：右边文件夹中的文件与文件夹列表；
common：两边文件夹中都存在的文件或文件夹；
left_only：只在左边文件夹中存在的文件或文件夹；
right_only：只在右边文件夹中存在的文件或文件夹；
common_dirs：两边文件夹都存在的子文件夹；
common_files：两边文件夹都存在的子文件；
common_funny：两边文件夹都存在的子文件夹；
same_files：匹配的文件；
diff_files：不匹配的文件；
funny_files：两边文件夹中都存在，但无法比较的文件；
subdirs：我没看明白这个属性的意思，python手册中的解释如下：A dictionary mapping names in common_dirs to dircmp objects
```


## csv
```
# coding=gbk
import csv

rows = [['AA', 39.48, '6/11/2007', '9:36am', -0.18, 181800],
         ('AIG', 71.38, '6/11/2007', '9:36am', -0.15, 195500),
         ('AXP', 62.58, '6/11/2007', '', -0.46, 935000,"你好"),
       ]
with open('121.csv','wb') as f:
    f_csv = csv.writer(f)
    f_csv.writerows(rows)
```

## xlsxwriter表格
```
追加数据
import xlrd
import xlwt
from xlutils.copy import copy

oldWb = xlrd.open_workbook(old_file, formatting_info=True)   只有xls文件支持formatting_info，保留原始格式
newWb = copy(oldWb)   #拷贝原始文件

sheet = newWb.get_sheet(0)  #原始文件中存在sheetname=0的文件
sheet.write(row, col, data, style)   #row行，col列，data追加的数据，style数据样式

newWb.save(new_file)

注：一定要保存为.xls文件类型。

写新的excel文件
#!/usr/bin/env python   
#coding:utf-8
import xlsxwriter
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

workbook = xlsxwriter.Workbook('demo1.xlsx')    #创建一个Excel文件
worksheet = workbook.add_worksheet()    #创建一个工作表对象Sheet1
worksheet2 = workbook.add_worksheet('Foglio2')    # Foglio2
title = [u'业务名称', u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日', u'平均流量']
buname = [u'业务官网', u'新闻中心', u'购物频道', u'体育频道', u'亲子频道']  #定义频道名称#定义5频道一周7天流量数据列表
data = [
    [150, 152, 158, 149, 155, 145, 148],
    [89, 88, 95, 93, 98, 100, 99],
    [201, 200, 198, 175, 170, 198, 195],
    [75, 77, 78, 78, 74, 70, 79],
    [88, 85, 87, 90, 93, 88, 84],]
format=workbook.add_format()    #定义format格式对象
format.set_border(1)    #定义format对象单元格边框加粗(1像素)的格式
format_title=workbook.add_format()    #定义format_title格式对象
format_title.set_border(1)   #定义format_title对象单元格边框加粗(1像素)的格式
format_title.set_bg_color('#cccccc')   #定义format_title对象单元格背景颜色为       #'#cccccc'的格式
format_title.set_align('center')    #定义format_title对象单元格居中对齐的格式
format_title.set_bold()    #定义format_title对象单元格内容加粗的格式
format_ave=workbook.add_format()    #定义format_ave格式对象
format_ave.set_border(1)    #定义format_ave对象单元格边框加粗(1像素)的格式
format_ave.set_num_format('0.00')   #定义format_ave对象单元格数字类别显示格式

#下面分别以行或列写入方式将标题、业务名称、流量数据写入起初单元格, 同时引用不同格式对象
worksheet.write_row('A1', title, format_title)
worksheet.write_column('A2', buname, format)
worksheet.write_row('B2',  data[0], format)
worksheet.write_row('B3',  data[1], format)
worksheet.write_row('B4',  data[2], format)
worksheet.write_row('B5',  data[3], format)
worksheet.write_row('B6',  data[4], format)
#图表
chart = workbook.add_chart({'type':'column'})    #创建一个column (柱形)图表
#area：面积样式；bar：条形样式；column：柱形样式 line：线条样式   pie：饼图；
#scatter：散点样式 stock：股票样式  radar：雷达样式
#定义图表数据系列函数
def chart_series(cur_row):
    worksheet.write_formula('I'+cur_row,'=AVERAGE(B'+cur_row+':H'+cur_row+')', format_ave)    
    #计算(AVERAGE函数)频道周平均流量
    chart.add_series({
        'categories': '=Sheet1!$B$1:$H$1',     #将“星期一至星期日”作为图表数据标签(X轴) 
        'values':     '=Sheet1!$B$'+cur_row+':$H$'+cur_row,     #频道一周所有数据作为数据区域
        'line':       {'color': 'black'},     #线条颜色定义为black(黑色)
        'name': '=Sheet1!$A$'+cur_row,     #引用业务名称为图例项
    })
for row in range(2,7):    #数据域以第2～6行进行图表数据系列函数调用
    chart_series(str(row))
#chart.set_table()    #设置X轴表格格式, 本示例不启用
#chart.set_style(30)    #设置图表样式, 本示例不启用
chart.set_size({'width': 577,  'height': 287})    #设置图表大小
chart.set_title({'name': u'业务流量周报图表'})    #设置图表(上方)大标题
chart.set_y_axis({'name': 'Mb/s'})    #设置y轴(左侧)小标题
worksheet.insert_chart('A8',  chart)    #在A8单元格插入图表

workbook.close()
```

## 数学运算
```
random
伪随机数生成模块。如果不提供 seed，默认使用系统时间。使用相同 seed，可获得相同的随机数序列，常用于测试。

>>> from random import *

>>> a = Random(); a.seed(1)

>>> [a.randint(1, 100) for i in range(20)]
[14, 85, 77, 26, 50, 45, 66, 79, 10, 3, 84, 44, 77, 1, 45, 73, 23, 95, 91, 4]

>>> b = Random(); b.seed(1)

>>> [b.randint(1, 100) for i in range(20)]
[14, 85, 77, 26, 50, 45, 66, 79, 10, 3, 84, 44, 77, 1, 45, 73, 23, 95, 91, 4]
使用示例

生成最大 N 个二进制位的长整数。

>>> getrandbits(5)
29L

>>> bin(getrandbits(5))
'0b11101'
生成 start <= N < stop 范围内的随机整数。

>>> randrange(1, 10)
2

>>> randrange(1, 10, 3)   # 支持步进
4

>>> randrange(1, 10, 3)
1

>>> randrange(1, 10, 3)
7
生成 a <= N <= b 范围内的整数。

>>> randint(1, 10)
5
从序列中随机返回元素。

>>> import string

>>> string.digits
'0123456789'

>>> choice(string.digits)
'6'

>>> choice(string.digits)
'1'

>>> choice(string.digits)
'3'
打乱序列，随机洗牌。

>>> a = range(10)

>>> shuffle(a)

>>> a
[6, 4, 8, 7, 5, 3, 0, 9, 2, 1]
从序列中随机挑选 n 个不同元素组合成列表。

>>> string.letters
'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

>>> sample(string.letters, 10)
['I', 'F', 'W', 'O', 'r', 'o', 'A', 'K', 'i', 'h']

>>> "".join(sample(string.letters, 10))  # 生成指定长度的随机字符串很容易
'kMmSgPVWIi'

>>> "".join(sample(string.letters, 10))
'feCTyRZrHv'
生成 0.0 <= N < 1 的随机浮点数。

>>> random()
0.39559451765020448

>>> random()
0.62378508101496177
生成 min <= N <= max 范围内的随机浮点数。

>>> uniform(1, 10)
7.6889886379206587

>>> uniform(10, 1)
5.1617099528426609
该模块还支持三角、β分布、指数分布、伽马分布、高斯分布等非常专业的随机算法。
```