## web压侧
```
# coding=utf-8
import urllib
import urllib2
import cookielib
import threading
import time
from Queue import Queue
from time import sleep

THREAD_NUM = 100        # 并发线程总数
ONE_WORKER_NUM = 10000      # 每个线程的循环次数
LOOP_SLEEP = 0.5        # 每次请求时间间隔(秒)
# 出错数
ERROR_NUM = 0


requrl = "http://cs.dachuizichan.com/login.do"
test_data = {
    'loginid':'17326800227',
    'password':'111111',
    'rand':'1111'
}
test_data_urlencode = urllib.urlencode(test_data)
header = {
    "Host" : "cs.dachuizichan.com",
    "Referer" : "http://cs.dachuizichan.com/manage/frame.do",
     "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)
      Chrome/54.0.2840.71 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded"
}
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))


req = urllib2.Request(requrl, test_data_urlencode,header)
result = opener.open(req)
# for key in header:
#     req.add_header(key, header[key])

def doWork(index):
    t = threading.currentThread()
    try:
        result2 = opener.open("http://cs.dachuizichan.com/manage/myDebtor/list.do")
        print result2.read()
    except urllib2.URLError,e:
        print "["+t.name+" "+str(index)+"] "
        print e
        global ERROR_NUM
        ERROR_NUM += 1

def working():
    t = threading.currentThread()
    print "["+t.name+"] Sub Thread Begin"

    i = 0
    while i < ONE_WORKER_NUM:
        i += 1
        doWork(i)
        sleep(LOOP_SLEEP)

    print "["+ t.name+"] Sub Thread End"


def main():
    #doWork(0)
    #return

    t1 = time.time()

    Threads = []

    # 创建线程
    for i in range(THREAD_NUM):
        t = threading.Thread(target=working, name="T"+str(i))
        t.setDaemon(True)
        Threads.append(t)

    for t in Threads:
        t.start()

    for t in Threads:
        t.join()

    print "main thread end"

    t2 = time.time()
    print "========================================"
    #print "URL:", PERF_TEST_URL
    print "任务数量:", THREAD_NUM, "*", ONE_WORKER_NUM, "=", THREAD_NUM*ONE_WORKER_NUM
    print "总耗时(秒):", t2-t1
    print "每次请求耗时(秒):", (t2-t1) / (THREAD_NUM*ONE_WORKER_NUM)
    print "每秒承载请求数:", 1 / ((t2-t1) / (THREAD_NUM*ONE_WORKER_NUM))
    print "错误数量:", ERROR_NUM


if __name__ == "__main__":
    main()
```


## 一行python
```
打印心形
print'\n'.join([''.join([('PYTHON!'[(x-y)%7]if((x*0.05)**2+(y*0.1)**2-1)**3-(x*0.05)**2*(y*0.1)**3<=0 else' ')
for x in range(-30,30)])for y in range(15,-15,-1)])

99乘法表
print '\n'.join([' '.join(['%s*%s=%-2s' % (y,x,x*y) for y in range(1,x+1)]) for x in range(1,10)])

斐波那契数列
print [x[0] for x in [  (a[i][0], a.append((a[i][1], a[i][0]+a[i][1]))) for a in ([[1,1]], ) for i in xrange(100) ]]

8皇后
_=[__import__('sys').stdout.write("\n".join('.' * i + 'Q' + '.' * (8-i-1) for i in vec) + "\n===\n") for vec 
in __import__('itertools').permutations(xrange(8)) if 8 == len(set(vec[i]+i for i in xrange(8))) == 
len(set(vec[i]-i for i in xrange(8)))]

打印自己
_='_=%r;print _%%_';print _%_
print(lambda x:x+str((x,)))('print(lambda x:x+str((x,)))',)
```



## 斐波那契数列
```
# coding:utf-8
def fib(n):
    """公式法"""
    from math import sqrt, pow
    return int(1/sqrt(5)*(pow((1+sqrt(5))/2,n) - pow((1-sqrt(5))/2,n)))
def fib2(n):
    """累加，使用之前计算的数"""
    if n == 0:
        return 0
    elif n == 1:
        return 1
    firstnum = 0
    secondnum = 1
    fibnum = 0
    cnt = 1
    while cnt < n:
        fibnum = firstnum + secondnum
        firstnum ,secondnum = secondnum, fibnum
        cnt += 1
    return fibnum
def fib3(n):
    """列表计算追加，简洁"""
    begin = [1, 1]
    for count in xrange(1, n-2):
        begin.append(begin[-1]+begin[-2])
    return begin
def fib4(n):
    """递归计算"""
    if n <= 1:
        return n
    else:
        return fib4(n - 1) + fib4(n - 2)
# fib1 fib2 fib4
for i in range(1, 10):
    print fib4(i)
# fib3
print fib3(10)

```



## 迭代器生成器
```
在了解Python的数据结构时，容器(container)、可迭代对象(iterable)、迭代器(iterator)、生成器(generator)、
列表/集合/字典推导式(list,set,dict comprehension)众多概念参杂在一起，难免让初学者一头雾水，我将用一篇文章试
图将这些概念以及它们之间的关系捋清楚。

relations

容器(container)
容器是一种把多个元素组织在一起的数据结构，容器中的元素可以逐个地迭代获取，可以用in, not in关键字判断元素是否包含在容器中。
通常这类数据结构把所有的元素存储在内存中（也有一些特列并不是所有的元素都放在内存）在Python中，常见的容器对象有：

list, deque, ....
set, frozensets, ....
dict, defaultdict, OrderedDict, Counter, ....
tuple, namedtuple, …
str
容器比较容易理解，因为你就可以把它看作是一个盒子、一栋房子、一个柜子，里面可以塞任何东西。从技术角度来说，当它可以用来询问
某个元素是否包含在其中时，那么这个对象就可以认为是一个容器，比如 list，set，tuples都是容器对象：

>>> assert 1 in [1, 2, 3]      # lists
>>> assert 4 not in [1, 2, 3]
>>> assert 1 in {1, 2, 3}      # sets
>>> assert 4 not in {1, 2, 3}
>>> assert 1 in (1, 2, 3)      # tuples
>>> assert 4 not in (1, 2, 3)
询问某元素是否在dict中用dict的中key：

d = {1: 'foo', 2: 'bar', 3: 'qux'}
assert 1 in d
assert 'foo' not in d  # 'foo' 不是dict中的元素
尽管绝大多数容器都提供了某种方式来获取其中的每一个元素，但这并不是容器本身提供的能力，而是可迭代对象赋予了容器这种能力，
当然并不是所有的容器都是可迭代的，比如：Bloom filter，虽然Bloom filter可以用来检测某个元素是否包含在容器中，但是并不能从
容器中获取其中的每一个值，因为Bloom filter压根就没把元素存储在容器中，而是通过一个散列函数映射成一个值保存在数组中。
可迭代对象(iterable)
刚才说过，很多容器都是可迭代对象，此外还有更多的对象同样也是可迭代对象，比如处于打开状态的files，sockets等等。但凡是可以
返回一个迭代器的对象都可称之为可迭代对象，听起来可能有点困惑，没关系，先看一个例子：

x = [1, 2, 3]
y = iter(x)
z = iter(x)
next(y)          1
next(y)          2
next(z)          1
type(x)
<class 'list'>>>> type(y)
<class 'list_iterator'>
这里x是一个可迭代对象，可迭代对象和容器一样是一种通俗的叫法，并不是指某种具体的数据类型，list是可迭代对象，dict是可迭代对象，
set也是可迭代对象。y和z是两个独立的迭代器，迭代器内部持有一个状态，该状态用于记录当前迭代所在的位置，以方便下次迭代的时候获
取正确的元素。迭代器有一种具体的迭代器类型，比如list_iterator，set_iterator。可迭代对象实现了__iter__和__next__方法
（python2中是next方法，python3是__next__方法），这两个方法对应内置函数iter()和next()。__iter__方法返回可迭代对象本身，
这使得他既是一个可迭代对象同时也是一个迭代器。

当运行代码：

x = [1, 2, 3]
for elem in x:
    ...
实际执行情况是：

iterable-vs-iterator.png

反编译该段代码，你可以看到解释器显示地调用GET_ITER指令，相当于调用iter(x)，FOR_ITER指令就是调用next()方法，不断地获
取迭代器中的下一个元素，但是你没法直接从指令中看出来，因为他被解释器优化过了。

import dis
>>> x = [1, 2, 3]
>>> dis.dis('for _ in x: pass')
  1           0 SETUP_LOOP              14 (to 17)
              3 LOAD_NAME                0 (x)
              6 GET_ITER
        >>    7 FOR_ITER                 6 (to 16)
             10 STORE_NAME               1 (_)
             13 JUMP_ABSOLUTE            7
        >>   16 POP_BLOCK
        >>   17 LOAD_CONST               0 (None)
             20 RETURN_VALUE
迭代器(iterator)

那么什么迭代器呢？它是一个带状态的对象，他能在你调用next()方法的时候返回容器中的下一个值，任何实现了__next__()
（python2中实现next()）方法的对象都是迭代器，至于它是如何实现的这并不重要。

所以，迭代器就是实现了工厂模式的对象，它在你每次你询问要下一个值的时候给你返回。有很多关于迭代器的例子，比如
itertools函数返回的都是迭代器对象。

生成无限序列：

from itertools import  count
counter  = count(start=13)
print next(counter)   # 13
print next(counter)   # 14
from itertools import cycle
colors = cycle(['red', 'white', 'blue'])
next(colors)  # 'red'
next(colors)  # 'white'
next(colors)  # 'blue'
next(colors)  # 'red'
from itertools import islice
limited = islice(colors,0,4)
print list(limited)
#  ['white', 'blue', 'red', 'white']

为了更直观地感受迭代器内部的执行过程，我们自定义一个迭代器，以斐波那契数列为例：


class Fib:
    def __init__(self):
        self.prev = 0
        self.curr = 1
    def __iter__(self):
        return self
    def next(self):
        value = self.curr
        self.curr += self.prev
        self.prev = value
        return value
f = Fib()
print list(islice(f,0,10))
Fib既是一个可迭代对象（因为它实现了__iter__方法），又是一个迭代器（因为实现了next方法）。实例变量prev和curr用户维护迭
代器内部的状态。每次调用next()方法的时候做两件事：

为下一次调用next()方法修改状态
为当前这次调用生成返回结果
迭代器就像一个懒加载的工厂，等到有人需要的时候才给它生成值返回，没调用的时候就处于休眠状态等待下一次调用。

生成器(generator)
生成器算得上是Python语言中最吸引人的特性之一，生成器其实是一种特殊的迭代器，不过这种迭代器更加优雅。它不需要再像上面的
类一样写__iter__()和__next__()方法了，只需要一个yiled关键字。 生成器一定是迭代器（反之不成立），因此任何生成器也是以一
种懒加载的模式生成值。用生成器来实现斐波那契数列的例子是：

def fib(n):
    prev, curr = 0, 1
    while prev < n:
        yield curr
        prev, curr = curr, curr + prev
>>> print [x for x in fib(10)]
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
fib就是一个普通的python函数，它特需的地方在于函数体中没有return关键字，函数的返回值是一个生成器对象。当执行f=fib()返回
的是一个生成器对象，此时函数体中的代码并不会执行，只有显示或隐示地调用next的时候才会真正执行里面的代码。

生成器在Python中是一个非常强大的编程结构，可以用更少地中间变量写流式代码，此外，相比其它容器对象它更能节省内存和CPU，当然
它可以用更少的代码来实现相似的功能。现在就可以动手重构你的代码了，但凡看到类似：

def something():
    result = []    for ... in ...:
        result.append(x)    return result
都可以用生成器函数来替换：

def iter_something():for ... in ...:        yield x
生成器表达式(generator expression)
生成器表达式是列表推倒式的生成器版本，看起来像列表推导式，但是它返回的是一个生成器对象而不是列表对象。


a = (x*x for x in xrange(10))
print type(a)
# <type 'generator'>
print sum(a)
# 285
```



## 执行系统命令
```
commands
import commands
commands.getstatusoutput(cmd)         返回(status, output)
commands.getoutput(cmd)                   只返回输出结果
os
import os 
os.system("echo \"Hello World\"")
or
print os.popen('ls -lt').read()
传shell的参数
import os
var=123或var='123'
os.environ['var']=str(var) #environ的键值必须是字符串
os.system('echo $var')
import os
var='123'
os.popen('wc -c', 'w').write(var)
```



## fabric
```
pip install fabric
fab -f fabfile -l  显示定义好的任务函数名
fab -f fabfile func  执行相应函数

文件打包上传---------------------------------------
#!/usr/bin/env python
#coding:utf-8
from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.console import confirm
env.user='root'
env.hosts=['192.168.1.21','192.168.1.22']
env.password='LKs934jh3'
@task
@runs_once
def tar_task():    #本地打包任务函数，只限执行一次
    with lcd("/data/logs"):
        local("tar -czf access.tar.gz access.log")
@task
def put_task():    #上传文件任务函数
    run("mkdir -p /data/logs")
    with cd("/data/logs"):
        with settings(warn_only=True):    #put（上传）出现异常时继续执行，非终止
            result = put("/data/logs/access.tar.gz", "/data/logs/access.tar.gz")
        if result.failed and not confirm("put file failed, Continue[Y/N]?"):
            abort("Aborting file put task!")    #出现异常时，确认用户是否继续，（Y继续）
@task
def check_task():    #校验文件任务函数
    with settings(warn_only=True):        #本地local命令需要配置capture=True才能捕获返回值
        lmd5=local("md5sum /data/logs/access.tar.gz",capture=True).split(' ')[0]
        rmd5=run("md5sum /data/logs/access.tar.gz").split(' ')[0]
    if lmd5==rmd5:    #对比本地及远程文件md5信息
        print "OK"
    else:
        print "ERROR"
@task
def go():
        tar_task()
        put_task()
        check_task()
LNMP安装--------------------------------------------------
#!/usr/bin/env python
#coding:utf-8
from fabric.colors import *
from fabric.api import *
env.user='root'
env.roledefs = {    #定义业务角色分组
    'webservers': ['192.168.1.21', '192.168.1.22'],
    'dbservers': ['192.168.1.23']
}
env.passwords = {
    'root@192.168.1.21:22': 'SJk348ygd',
    'root@192.168.1.22:22': 'KSh458j4f',
    'root@192.168.1.23:22': 'KSdu43598'
}
@roles('webservers')    #webtask任务函数引用'webservers'角色修饰符
def webtask():    #部署nginx php php-fpm等环境
    print yellow("Install nginx php php-fpm...")
    with settings(warn_only=True):
        run("yum -y install nginx")
        run("yum -y install php-fpm php-mysql php-mbstring php-xml php-mcrypt php-gd")
        run("chkconfig --levels 235 php-fpm on")
        run("chkconfig --levels 235 nginx on")
@roles('dbservers')    # dbtask任务函数引用'dbservers'角色修饰符
def dbtask():    #部署mysql环境
    print yellow("Install Mysql...")
    with settings(warn_only=True):
        run("yum -y install mysql mysql-server")
        run("chkconfig --levels 235 mysqld on")
@roles ('webservers', 'dbservers') # publictask任务函数同时引用两个角色修饰符
def publictask():    #部署公共类环境，如epel、ntp等
    print yellow("Install epel ntp...")
    with settings(warn_only=True):
        run("rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm")
        run("yum -y install ntp")
def deploy(): #以实现不同角色执行不同的任务函数
    execute(publictask)
    execute(webtask)
    execute(dbtask)


代码发布--------------------------------------------------
#!/usr/bin/env python
#coding:utf-8
from fabric.api import *
from fabric.colors import *
from fabric.context_managers import *
from fabric.contrib.console import confirm
import time
env.user='root'
env.hosts=['192.168.1.21','192.168.1.22']
env.password='LKs934jh3'
env.project_dev_source = '/data/dev/Lwebadmin/'    #开发机项目主目录
env.project_tar_source = '/data/dev/releases/'    #开发机项目压缩包存储目录
env.project_pack_name = 'release'    #项目压缩包名前缀，文件名为release.tar.gz
env.deploy_project_root = '/data/www/Lwebadmin/'    #项目生产环境主目录
env.deploy_release_dir = 'releases'    #项目发布目录，位于主目录下面
env.deploy_current_dir = 'current'    #对外服务的当前版本软链接
env.deploy_version=time.strftime("%Y%m%d")+"v2"    #版本号
@runs_once
def input_versionid():    #获得用户输入的版本号，以便做版本回滚操作
    return prompt("please input project rollback version ID:",default="")
@task
@runs_once
def tar_source():    #打包本地项目主目录，并将压缩包存储到本地压缩包目录
    print yellow("Creating source package...")
    with lcd(env.project_dev_source):
        local("tar -czf %s.tar.gz ." % (env.project_tar_source + env.project_pack_name))
    print green("Creating source package success!")
@task
def put_package():    #上传任务函数
    print yellow("Start put package...")
    with settings(warn_only=True):
        with cd(env.deploy_project_root+env.deploy_release_dir):
            run("mkdir %s" % (env.deploy_version))    #创建版本目录
    env.deploy_full_path=env.deploy_project_root + env.deploy_release_dir + "/"+env.deploy_version
    with settings(warn_only=True):    #上传项目压缩包至此目录
        result = put(env.project_tar_source + env.project_pack_name +".tar.gz", env.deploy_full_path)
    if result.failed and no("put file failed, Continue[Y/N]?"):
        abort("Aborting file put task!")
    with cd(env.deploy_full_path):   #成功解压后删除压缩包
        run("tar -zxvf %s.tar.gz" % (env.project_pack_name))
        run("rm -rf %s.tar.gz" % (env.project_pack_name))
    print green("Put & untar package success!")
@task
def make_symlink():    #为当前版本目录做软链接
    print yellow("update current symlink")
    env.deploy_full_path=env.deploy_project_root + env.deploy_release_dir + "/"+env.deploy_version
    with settings(warn_only=True):    #删除软链接，重新创建并指定软链源目录，新版本生效
        run("rm -rf %s" % (env.deploy_project_root + env.deploy_current_dir))
        run("ln -s %s %s" % (env.deploy_full_path, env.deploy_project_root + env.deploy_current_dir))   
        #删除软链接，重新创建并指定软链源目录，新版本生效
    print green("rollback success!")
@task
def go():    #自动化程序版本发布入口函数
    tar_source()
    put_package()
    make_symlink()
```



## 嵌套函数
```
闭包closures
函数套函数
import time
def hl(func):
    def wrap():
        begin = int(time.time())
        print begin
        func()
        end = int(time.time())
        print end
        print "cost:",end - begin
    return end - begin
return wrap
def t():
    time.sleep(1)
     hl(t)()
 
装饰器
函数执行前扩展一些函数、执行后扩展一些函数
import time
def hl(func):
    def wrap():
        begin = int(time.time())
        print begin
        func()
        end = int(time.time())
        print end
        print "cost:",end - begin
        return end - begin
    return wrap
@hl
def t():
    time.sleep(1)
    t()
 
##############################
def mb(func):
    def wrap():
        return '<b>' + func() + '</b>'
    return wrap
def mi(func):
    def wrap():
        return '<i>' + func() + '</i>'
    return wrap
@mb
@mi
def hello():
return('hello')
print(hello())
```



## pip.conf
```
#$HOME/.pip/pip.conf

[global]
index-url = http://pypi.douban.com/simple
[install]
trusted-host = pypi.douban.com
或者
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com

windows设置HOME变量，放到%HOME%/pip/pip.ini

单次使用 pip install Jinja2 -i http://pypi.douban.com/simple
```

## 小技巧
```
    交换变量

        x = 6
        y = 5

        x, y = y, x

        print x # 打印:5
        print y # 打印:6



    if 语句在行内
        作用相当于 C/Java 的三目运算符

        a = "Hello" if True else "World"
        b = "Hello" if False else "World"

        print a # 打印:Hello
        print b # 打印:World


    连接
        # 列表、元组 拼接
        nfc = ["Packers", "49ers"]
        afc = ["Ravens", "Patriots"]
        print nfc + afc  # 打印:['Packers', '49ers', 'Ravens', 'Patriots']

        # 字符串 拼接
        print str(1) + " world" # 打印:1 world

        # 数值的这种写法，我还不清楚是什么, 会当成字符串处理，却又不是真正的字符串
        print `1` + " world" # 打印:1 world


        # python2.x 的 print 可以这样打印多个不同类型的内容
        print 1, "world" # 打印:1 world
        print nfc, 1 # 打印:['Packers', '49ers'] 1

        # python3.x 的 print 可以这样打印多个不同类型的内容(效果同上面 2.x 的)
        print(1, "world", end=' ') # 打印:1 world
        print(nfc, 1, end=' ') # 打印:['Packers', '49ers'] 1


    序列(包括:列表、元组、字符串)

    带索引的 序列 迭代(很实用的获取索引的写法)

        teams = ["Packers", "49ers", "Ravens", "Patriots"]
        for index, team in enumerate(teams):
            print index, team  # 打印如:0 Packers

    序列 的乘法
        items = [0]*3
        print(items)

    序列 拼接为字符串
        teams = ["Packers", "49ers", "Ravens", "Patriots"]
        print(", ".join(teams))

    序列 的子集
        teams = ["Packers", "49ers", "Ravens", "Patriots"]
        print(teams[-2])     # 最后两项(负数表示倒数几项)
        print(teams[:])      # 复制一份
        print(teams[::-1])   # 反序
        print(teams[::2])    # 奇数项
        print(teams[1::2])   # 偶数项


    数值比较
        这是我见过诸多语言中很少有的如此棒的简便法

        x = 2
        if 3 > x > 1:
           print x # 打印:2

        if 1 < x > 0:
           print x # 打印:2


    同时迭代两个列表

        nfc = ["Packers", "49ers"]
        afc = ["Ravens", "Patriots"]
        for teama, teamb in zip(nfc, afc):
             print teama + " vs. " + teamb
        # 打印1: Packers vs. Ravens
        # 打印2: 49ers vs. Patriots


    60个字符解决FizzBuzz
        前段时间Jeff Atwood 推广了一个简单的编程练习叫FizzBuzz，问题引用如下：
        写一个程序，打印数字1到100，3的倍数打印“Fizz”来替换这个数，5的倍数打印“Buzz”，对于既是3的倍数又是5的倍数的数字打印“FizzBuzz”。

        这里就是一个简短的，有意思的方法解决这个问题：
        for x in range(101):print"fizz"[x%3*4::]+"buzz"[x%5*4::]or x


    False == True
        比起实用技术来说这是一个很有趣的事，在python中, True 和 False 是全局变量(值允许改变)，因此：

        False = True
        if False:
           print "Hello"
        else:
           print "World"
        # 打印: Hello
```


## 流量转换
```
import math

def convertBytes(bytes, lst=None):
    if lst is None:
        lst=['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = int(math.floor( # 舍弃小数点，取小
             math.log(bytes, 1024) # 求对数(对数：若 a**b = N 则 b 叫做以 a 为底 N 的对数)
            ))

    if i >= len(lst):
        i = len(lst) - 1
    return ('%.2f' + " " + lst[i]) % (bytes/math.pow(1024, i))
```
