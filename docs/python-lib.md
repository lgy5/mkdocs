## os
```
os 模块
    这个模块包含普遍的操作系统功能。如果你希望你的程序能够与平台无关的话，这个模块是尤为重要的。

    os.sep  获取操作系统特定的路径分割符。比如在Linux、Unix下它是'/'，在Windows下它是'\\'，而在Mac OS下它是':'。
    os.name 字符串指示你正在使用的平台。比如对于Windows，它是'nt'，而对于Linux/Unix用户，它是'posix'。
    os.getcwd() 函数得到当前工作目录，即当前Python脚本工作的目录路径。
    os.getenv(key) 函数用来读取环境变量。
    os.putenv(key, value) 函数用来设置环境变量。
    os.listdir(path) 返回指定目录下的所有文件和目录名。
    os.remove(filePath) 函数用来删除一个文件。
    os.system(shellStr) 函数用来运行shell命令，windows平台则是运行批处理命令。
    os.linesep  字符串给出当前平台使用的行终止符。例如，Windows使用'\r\n'，Linux使用'\n'而Mac使用'\r'。
    os.path.split(pathname)  函数返回一个路径的目录名和文件名。
    os.path.isfile(path) 函数检验给出的路径是否一个文件。
    os.path.isdir(path)  函数分别检验给出的路径是否目录。
    os.path.existe(path) 函数用来检验给出的路径是否真地存在。

文件操作
  一、在pythony 3.0 已经废弃了 file 类。

  二、pythony 3.0 内置 open() 函数的构造函数是:
    open(file, mode="r", buffering=None, encoding=None, errors=None, newline=None, closefd=True)
    1.mode(模式):
      r: 读，只能读文件，如果文件不存在，会发生异常
      w: 写，只能写文件，如果文件不存在，创建该文件；如果文件已存在，先清空，再打开文件
      a: 打开供追加
      b: 二进制模式；一般是组合写法,如: rb 以二进制读方式打开；wb 以二进制写方式打开
      t: 文本模式
      +: 打开一个磁盘文件供更新,一般是组合使用,如:
         rb+: 以二进制读方式打开，可以读、写文件，如果文件不存在，会发生异常
         wb+: 以二进制写方式打开，可以读、写文件，如果文件不存在，创建该文件；如果文件已存在，先清空，再打开文件
      u: 通用换行模式
      默认的模式是 rt，即打开供读取的文本模式。
    2.buffering 关键字参数的期望值是以下三个整数中的一个以决定缓冲策略：
      0: 关闭缓冲
      1: 行缓冲
      > 1: 所填的 int 数=缓冲区大小
      默认: 完全缓冲
    3.encoding 默认的编码方式独立于平台。
    4.关闭文件描述符 closefd 可以是 True 或 False 。
      如果是 False,此文件描述符会在文件关闭后保留。若文件名无法奏效的话，那么必须设为 True 。

  三、清空文件内容
    f.truncate()
    注意：当以 "r+","rb+","w","wb","wb+"等模式时可以执行该功能，即具有可写模式时才可以。

  四、文件的指针定位与查询
    (1)文件指针：
         文件被打开后，其对象保存在 f 中， 它会记住文件的当前位置,以便于执行读、写操作，
         这个位置称为文件的指针( 一个从文件头部开始计算的字节数 long 类型 )。
    (2)文件打开时的位置:
         以"r","r+","rb+" 读方式, "w","w+","wb+"写方式 打开的文件，
         一开始，文件指针均指向文件的头部。
    (3)获取文件指针的值:
         L = f.tell()
    (4)移动文件的指针
         f.seek(偏移量, 选项) # 偏移量 是 long 或者 int 类型，计算偏移量时注意换行符是2,汉字可能是2或3
         选项 =0 时， 表示将文件指针指向从文件头部到 "偏移量"字节处。
         选项 =1 时， 表示将文件指针指向从文件的当前位置，向后移动 "偏移量"字节。
         选项 =2 时， 表示将文件指针指向从文件的尾部，，向前移动 "偏移量"字节。

  五、从文件读取指内容
    1.文本文件(以"rt"方式打开的文件)的读取
      s = f.readline()
      返回值： s 是字符串，从文件中读取的一行，含行结束符。
      说明: (1)如果 len(s) = 0 表示已到文件尾(换行符也是有长度的,长度为2)
            (2)如果是文件的最后一行，有可能没有行结束符
    2.二进制文件(以"rb"、"rb+"、"wb+" 方式打开的文件)的读取
      s = f.read(n)
      说明: (1)如果 len( s ) =0 表示已到文件尾
            (2)文件读取后，文件的指针向后移动 len(s) 字节。
            (3)如果磁道已坏，会发生异常。
    with open('/tmp/passwd', 'r') as f:        使用with可以省略a.close()
            for eachline in f:
                    print eachline
    a.read([size])    返回字符串，以字节为单位
    a.readline([size])  返回字符串，读一行，如果定义了size，有可能返回的只是一行的一部分
    a.readlines([size])   返回列表，包含每一行，如果提供size参数，size是表示读取内容的总长，也就是说可能只读到文件的一部分。
    a.fileno()      返回该文件描述符
    a.tell()       返回文件操作标记的当前位置，以文件的开头为原点
    a.next()       返回下一行，并将文件操作标记位移到下一行。把一个file用于for … in file这样的语句时，就是调用next()
    函数来实现遍历的。
    a.seek(offset[,whence])   将文件打操作标记移到offset的位置。这个offset一般是相对于文件的开头来计算的，一般为正数。
    但如果提供了whence参数就不一定了，whence可以为0表示从头开始计算，1表示以当前位置为原点计算。2表示以文件末尾为原点进行计算。
    需要注意，如果文件以a或a+的模式打开，每次进行写操作时，文件操作标记会自动返回到文件末尾
    a.write(str)         把str写到文件中，write()并不会换行
    a.writelines(seq)    把seq的内容全部写到文件中(多行一次性写入)。这个函数也只是忠实地写入，不会在每行后面加上任何东西。
    a.flush()        把缓冲区的内容写入硬盘
    a.isatty()        文件是否是一个终端设备文件（unix系统中的）
    a.truncate([size])   把文件裁成规定的大小，默认的是裁到当前文件操作标记的位置。如果size比文件的大小还要大，
    依据系统的不同可能是不改变文件，也可能是用0把文件补到相应的大小，也可能是以一些随机的内容加上去。


  六、向文件写入一个字符串
      f.write( s )
      参数: s 要写入的字符串
      说明: (1)文件写入后，文件的指针向后移动 len(s) 字节。
            (2)如果磁道已坏，或磁盘已满会发生异常。

  七、常用文件操作参考
      [1.os]
        1.重命名：os.rename(old, new)
        2.删除：os.remove(file)
        3.列出目录下的文件：os.listdir(path)
        4.获取当前工作目录：os.getcwd()
        5.改变工作目录：os.chdir(newdir)
        6.创建多级目录：os.makedirs(r"c:\python\test")
        7.创建单个目录：os.mkdir("test")
        8.删除多个目录：os.removedirs(r"c:\python") #删除所给路径最后一个目录下所有空目录。
        9.删除单个目录：os.rmdir("test")
        10.获取文件属性：os.stat(file)
        11.修改文件权限与时间戳：os.chmod(file)
        12.执行操作系统命令：os.system("dir")
        13.启动新进程：os.exec(), os.execvp()
        14.在后台执行程序：osspawnv()
        15.终止当前进程：os.exit(), os._exit()
        16.分离文件名：os.path.split(r"c:\python\hello.py") --> ("c:\\python", "hello.py")
        17.分离扩展名：os.path.splitext(r"c:\python\hello.py") --> ("c:\\python\\hello", ".py")
        18.获取路径名：os.path.dirname(r"c:\python\hello.py") --> "c:\\python"
        19.获取文件名：os.path.basename(r"r:\python\hello.py") --> "hello.py"
        20.判断文件是否存在：os.path.exists(r"c:\python\hello.py") --> True
        21.判断是否是绝对路径：os.path.isabs(r".\python\") --> False
        22.判断是否是目录：os.path.isdir(r"c:\python") --> True
        23.判断是否是文件：os.path.isfile(r"c:\python\hello.py") --> True
        24.判断是否是链接文件：os.path.islink(r"c:\python\hello.py") --> False
        25.获取文件大小：os.path.getsize(filename)
        26.*******：os.ismount("c:\\") --> True
        27.搜索目录下的所有文件：os.path.walk()
        28.文件的访问时间 :  os.path.getatime(myfile) # 这里的时间以秒为单位，并且从1970年1月1日开始算起
        29.文件的修改时间:  os.path.getmtime(myfile)

      [2.shutil]
        1.复制单个文件：shutil.copy(oldfile, newfle)
        2.复制整个目录树：shutil.copytree(r".\setup", r".\backup")
        3.删除整个目录树：shutil.rmtree(r".\backup")

      [3.tempfile]
        1.创建一个唯一的临时文件：tempfile.mktemp() --> filename
        2.打开临时文件：tempfile.TemporaryFile()

      [4.StringIO] #cStringIO是StringIO模块的快速实现模块
        1.创建内存文件并写入初始数据：f = StringIO.StringIO("Hello world!")
        2.读入内存文件数据： print f.read() #或print f.getvalue() --> Hello world!
        3.想内存文件写入数据：f.write("Good day!")
        4.关闭内存文件：f.close()

      [5.glob]
        1.匹配文件：glob.glob(r"c:\python\*.py")



########### 示例1 运行系统命令行 #################################
    import os
    os_command = 'echo haha...'
    # 运行命令行,返回运行结果(成功时返回0,失败返回1或以上的出错数字)
    result = os.system(os_command)
    if result == 0:
        print('run Successful')
    else:
        print('run FAILED')
    # 注:os.system()函数不推荐使用,它容易引发严重的错误。(可能是因为不具备可移植性)

    #os.system(os_command) # 这命令会弹出一个黑乎乎的cmd运行窗口,而且无法获得输出
    p = os.popen(os_command) # 捕获运行的屏幕输出，以文件类型接收，不再另外弹出窗口
    print(p.read()) # p 是个文件类型，可按文件的操作


########### 杀掉进程(windows) ###########
    def kill(pid):
        """ kill process by pid for windows """
        kill_command = "taskkill /F /T /pid %s" % pid
        os.system(kill_command)


########### 进程监视(windows) ###########

    # 定期监视某进程是否存在，不存在则执行
    import os,time

    def __Is_Process_Running(imagename):
        '''
           功能：检查进程是否存在
           返回：返回有多少个这进程名的程序在运行，返回0则程序不在运行
        '''
        p = os.popen('tasklist /FI "IMAGENAME eq %s"' % imagename) # 利用 windows 批处理的 tasklist 命令
        return p.read().count(imagename) # p 是个文件类型，可按文件的操作

    def test():
        '''
           功能：定期地监视测进程是否还在运行，不再运行时执行指定代码
        '''
        while True:
            time.sleep(10)
            pid = __Is_Process_Running('barfoo.exe')
            if pid <= 0:
                # code .....
                break

    if __name__ == "__main__":
        test()


########### 程序退出时执行 ###########
    import os

    # 运行另外一个进程
    proxy_server = os.popen('cmd.exe /c start "" barfoo_proxy.exe')
    # 等待这个进程结束(其实是读取程序的输出，但程序如果一直不停止的话，就一直阻塞)，再往下执行
    proxy_server.read()

    # 前面的程序结束后，才继续执行下面的代码
    test_file = open('test.txt', 'wb')
    test_file.write('hello')
    test_file.close()


########### 示例2 创建目录 #################################
    import os
    pathDir = r'D:\Work' # 不同系统的目录写法有所不同
    if not os.path.exists(pathDir):
        os.mkdir(pathDir) # 创建目录, os.makedirs(pathDir) 创建多个不存在的目录
    target = pathDir + os.sep + 'test.txt'
    print(target)
    # 注意os.sep变量的用法, os.sep 是目录分隔符,这样写方便移植。即在Linux、Unix下它是'/'，在Windows下它是'\\'，
    而在Mac OS下它是':'。



########### 示例3 文件操作(遍历目录和文件名) ########################
    import os
    import os.path
    rootdir = r"D:\Holemar\1.notes\28.Python\test"
    # os.walk 返回一个三元组，其中parent表示所在目录, dirnames是所有目录名字的列表, filenames是所有文件名字的列表
    for parent,dirnames,filenames in os.walk(rootdir):
        # 所在目录
        print("parent is:" + parent)
        # 遍历此目录下的所有目录(不包含子目录)
        for dirname in dirnames:
           print(" dirname is:" + dirname)
        # 遍历此目录下的所有文件
        for filename in filenames:
           print(" filename with full path:" + os.path.join(parent, filename))

    # 列表显示出某目录下的所有文件及目录(不包括子目录的内容)
    ls = os.listdir(rootdir)


########### 示例4 文件操作(分割路径和文件名) #################################
    import os.path
    #常用函数有三种：分隔路径，找出文件名，找出盘符(window系统)，找出文件的扩展名。
    spath = "d:/test/test.7z"

    # 下面三个分割都返回二元组
    # 分隔目录和文件名
    p,f = os.path.split(spath)  # 注意二元组的接收
    print("dir is:" + p)    # 打印: d:/test
    print(" file is:" + f)  # 打印: test.7z

    # 分隔盘符和文件名
    drv,left = os.path.splitdrive(spath)
    print(" driver is:" + drv)   # 打印: d:
    print(" left is:" + left)    # 打印: /test/test.7z

    # 分隔文件和扩展名
    f,ext = os.path.splitext(spath)
    print(" f is: " + f)    # 打印: d:/test/test
    print(" ext is:" + ext) # 打印: 7z


########### 示例4 文件操作(读写txt文件) #################################
    filePath = 'poem.txt'
    f = open(filePath, 'w') # 以写的模式打开文件,Python 2.x 需将 open() / io.open() 改成 file()
    for a in range( 0, 10 ):
        s = "%5d %5d\n" % (a, a*a)
        f.write( s ) # 把文本写入文件
    f.close() # 关闭io流

    f2 = open(filePath) # 没有提供模式，则默认是读取,即 'r'
    while True:
        line = f2.readline()
        if len(line) == 0: # 读取结束
            break
        print(line, end='') # 避免print自动换行, 此行Python2.x应该写：“print line,”
    f2.close() # close the file

    # 删除文件
    import os
    os.remove(filePath)


########### 示例5 文件操作(获取文件修改时间) #################################
    import os,os.path,time
    timestamp = os.path.getmtime(__file__) # 获取本文件
    time_tuple = time.localtime(timestamp)
    print time.strftime('%Y-%m-%d %H:%M:%S', time_tuple) # 2008-11-12 21:59:27
    # 下面简化成一行代码
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(__file__))) # 2008-11-12 21:59:27
```



## random
```
#随机数
import random
 
# 生成0至1之间的随机浮点数，结果大于等于0.0，小于1.0
print( random.random() )
# 生成1至10之间的随机浮点数
print( random.uniform(1, 10) )
 
# 产生随机整数
print( random.randint(1, 5) ) # 生成1至5之间的随机整数，结果大于等于1，小于等于5，前一个参数必须小于等于第二个参数
for i in xrange(5):
    print(i, random.randint(10, 90) ) # 产生 10~90 的随机整数(结果包含 10 和 90)
 
# 随机选取0到100间的偶数(第二个参数是选取间隔,如果从1开始,就是选取基数)
print( random.randrange(0, 101, 2) )
 
# 在指定范围内随机选一个值
print( random.choice(range(50)) ) # 这的选值范围是0~49
print( random.choice(['a', 2, 'c']) ) # 从列表中随机挑选一个数，也可以是元组、字符串
print( random.choice('abcdefg') ) # 可从字符串中随机选一个字符
# 在指定范围内随机选多个值(返回一个 list, 第二个参数是要选取的数量)
print( random.sample('abcdefghij',3) )
print( random.sample(['a', 2, 'c', 5, 0, 'ii'],2) )
 
# 洗牌,让列表里面的值乱序
items = [1, 2, 3, 4, 5, 6]
random.shuffle(items) # 这句改变列表里面的值,返回:None
print( items ) # 输出乱序后的列表
```



## request
```
requests官方文档中文版: http://cn.python-requests.org/en/latest/

import requests
requests.get(ts_url, headers={'User-Agent': "chrome/63/xxx"}, timeout=10, proxies={"http": "http://10.10.1.10:3128"})

r = requests.get('http://www.zhidaow.com')  # 发送请求
print r.status_code  # 状态码,打印: 200
print r.headers['content-type']  # 返回头部信息,打印:'text/html; charset=utf8'
print r.headers # 返回头部信息,打印:{'content-encoding': 'gzip', 'transfer-encoding': 'chunked', 'content-type': 
'text/html; charset=utf-8';  ... }
print r.encoding  # 获取网页编码信息,打印:'utf-8'
print r.text  #内容部分（PS，由于编码问题，建议这里使用 r.content ）,打印:u'<!DOCTYPE html>\n<html 
xmlns="http://www.w3.org/1999/xhtml"...'
print r.content #文档中说r.content是以字节的方式去显示，所以在IDLE中以b开头。但我在cygwin中用起来并没有，
下载网页正好。所以就替代了urllib2的urllib2.urlopen(url).read()功能。
print r.json() # 如果返回内容是 json 格式,会自动转成 json 并返回

设置超时时间
    #我们可以通过timeout属性设置超时时间，一旦超过这个时间还没获得响应内容，就会提示错误。
    requests.get('http://github.com', timeout=0.001)


json 参数的请求
    payload = {'wd': '张亚楠', 'rn': '100'}
    r = requests.get("http://www.baidu.com/s", params=payload)
    print r.url # 打印请求地址,会将自动转码的内容打印出来
    # post 请求
    r = requests.post("http://www.baidu.com/s", params=payload)



代理访问
    采集时为避免被封IP，经常会使用代理。requests也有相应的proxies属性。

    import requests
    proxies = {
      "http": "http://10.10.1.10:3128",
      "https": "http://10.10.1.10:1080",
    }
    requests.get("http://www.zhidaow.com", proxies=proxies)
    #如果代理需要账户和密码，则需这样：
    proxies = {
        "http": "http://user:pass@10.10.1.10:3128/",
    }



官方文档
requests的具体安装过程请看：http://docs.python-requests.org/en/latest/user/install.html#install
requests的官方指南文档：http://docs.python-requests.org/en/latest/user/quickstart.html
requests的高级指南文档：http://docs.python-requests.org/en/latest/user/advanced.html#advanced
```



## paramiko
```
yum install python-devel -y && pip install paramiko

运行报错
AttributeError: 'module' object has no attribute 'HAVE_DECL_MPZ_POWM_SEC'
找到 /usr/lib64/python2.6/site-packages/Crypto/Util/number.py
注释
#if _fastmath is not None and not _fastmath.HAVE_DECL_MPZ_POWM_SEC:
)
#!/usr/bin/env python
#coding:utf-8
import paramiko
import sys

hostname = sys.argv[1]
username = 'root'
passwd = sys.argv[2]
paramiko.util.log_to_file('syslogin.log') # 发送 paramiko 日志到 syslogin.log 文件

#SSH
ssh=paramiko.SSHClient() # 创建一个 ssh 客户端 client 对象
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #自动添加主机名及主机密钥到本地HostKeys对象，
并将其保存，不依赖load_sys-tem_host_keys()的配置，即使~/.ssh/known_hosts不存在也不产生影响；
ssh.load_system_host_keys() # 获取客户端 host_keys ，默认 ~/.ssh/known_hosts ，非默认路径需指定

#密码方式连接
ssh.connect(hostname=hostname,username=username,password=passwd) # 创建 ssh 连接

#密钥key方式连接
privatekey = os.path.expanduser('~/.ssh/id_rsa')  #定义私钥存放路径 返回用户家目录，/root.id_rse
key = paramiko.RSAKey.from_private_key_file(privatekey)  #创建私钥对象
ssh.connect(hostname=hostname,username=username,pkey = key)

stdin,stdout,stderr=ssh.exec_command('free -m') # 调用远程执行命令方法 exec_command()
print stdout.read() # 打印命令执行结果，得到 Python 列表形式，可以使用 stdout.readlines()
ssh.close() # 关闭 ssh 连接

try:
    #SFTP
    t = paramiko.Transport((hostname,22))
    t.connect(username=username, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(t)

    localpath='/root/mylog.txt'
    remotepath='/tmp/mylog.txt'
    sftp.put(localpath,remotepath) #上传

    sftp.get(remotepath, localpath) #下载

    #SFTP其他方法
    sftp.mkdir("/home/userdir",0755)
    sftp.rmdir("/home/userdir")
    sftp.rename("/home/test.sh","/home/testfile.sh")
    sftp.stat("/home/testfile.sh")
    sftp.listdir("/home")
    t.close()
except Exception , e:
    print str(e)
```



## hashlib
```
# coding:utf-8
import hashlib
 
a = "a test string"
print hashlib.md5(a).hexdigest()
print hashlib.sha1(a).hexdigest()
print hashlib.sha224(a).hexdigest()
print hashlib.sha256(a).hexdigest()
print hashlib.sha384(a).hexdigest()
print hashlib.sha512(a).hexdigest()
```



## zipfile
```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from zipfile import *
import zipfile
 
#解压zip文件
def unzip():
    source_zip="c:\\update\\SW_Servers_20120815.zip"
    target_dir="c:\\update\\"
    myzip=ZipFile(source_zip)
    myfilelist=myzip.namelist()
    for name in myfilelist:
        f_handle=open(target_dir+name,"wb")
        f_handle.write(myzip.read(name))      
        f_handle.close()
    myzip.close()
 
#添加文件到已有的zip包中
def addzip():
    f = zipfile.ZipFile('archive.zip','w',zipfile.ZIP_DEFLATED)
    f.write('file_to_add.py')
    f.close()
 
#把整个文件夹内的文件打包
def adddirfile():
    f = zipfile.ZipFile('archive.zip','w',zipfile.ZIP_DEFLATED)
    startdir = "c:\\mydirectory"
    for dirpath, dirnames, filenames in os.walk(startdir):
        for filename in filenames:
            f.write(os.path.join(dirpath,filename))
    f.close()
 
```


## pycurl
```
#!/usr/bin/env python
#coding:utf-8
import os,sys
import time
import pycurl
import StringIO
URL="http://www.baidu.com" #探测目标url
c = pycurl.Curl()
c.setopt(pycurl.URL,URL) #定义请求URL

# 获取内容
L1 = pycurl.Curl()
L1buf = StringIO.StringIO()
L1.setopt(pycurl.WRITEFUNCTION, L1buf.write)
L1.perform()
L1txt = L1buf.getvalue()

和多线程结合使用需要设置,可能还有其他问题
L1.setopt(pycurl.NOSIGNAL, 1)

c.setopt(pycurl.CUSTOMREQUEST,"DELETE")  设置封装方法，有put，post，get，delete等多种方法，不支持HEAD
c.setopt(pycurl.NOBODY, True)  		     不要内容，相当于HEAD请求 
c.setopt(pycurl.HTTPHEADER, ["range: bytes=0-2048"])  range请求  curl -H "range: bytes=0-10"

c.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)  内容长度

c.setopt(pycurl.CONNECTTIMEOUT,5) #定义请求连接的等待时间
c.setopt(pycurl.MAXREDIRS, 5) #设置最大重定向次数
c.setopt(pycurl.USERAGENT, "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)") #模拟浏览器
c.perform() #服务器端返回的信息
c.getinfo(pycurl.HTTP_CODE) #查看HTTP的状态 类似urllib中status属性
c.setopt(pycurl.TIMEOUT,5) #超时时间
c.setopt(pycurl.FORBID_REUSE,1) #交互后断开连接，不重用
c.setopt(pycurl.MAXREDIRS,1) #HTTP重定向最大为1
c.setopt(pycurl.DNS_CACHE_TIMEOUT,30) #保存dns信息为30秒
#创建一个文件对象, 以”wb”方式打开, 用来存储返回的http头部及页面内容in
indexfile = open(os.path.dirname(os.path.realpath(__file__))+"/content.txt", "wb")
c.setopt(pycurl.WRITEHEADER, indexfile)    #将返回的HTTP HEADER定向到indexfile文件对象
c.setopt(pycurl.WRITEDATA, indexfile)    #将返回的HTML内容定向到indexfile文件对象
try:
    c.perform()    #提交请求
except Exception, e:
    print "connecion error:"+str (e)
    indexfile.close()
    c.close()
    sys.exit()
NAMELOOKUP_TIME =  c.getinfo(c.NAMELOOKUP_TIME)    #获取DNS解析时间
CONNECT_TIME =  c.getinfo(c.CONNECT_TIME)    #获取建立连接时间
PRETRANSFER_TIME =  c.getinfo(c.PRETRANSFER_TIME)    #获取从建立连接到准备传输所消耗的时间
STARTTRANSFER_TIME = c.getinfo(c.STARTTRANSFER_TIME)    #获取从建立连接到传输开始消耗的时间
TOTAL_TIME = c.getinfo(c.TOTAL_TIME)    #获取传输的总时间
HTTP_CODE =  c.getinfo(c.HTTP_CODE)    #获取HTTP状态码
SIZE_DOWNLOAD =  c.getinfo(c.SIZE_DOWNLOAD)    #获取下载数据包大小
HEADER_SIZE = c.getinfo(c.HEADER_SIZE)    #获取HTTP头部大小
SPEED_DOWNLOAD=c.getinfo(c.SPEED_DOWNLOAD)    #获取平均下载速度#打印输出相关数据
#打印输出相关数据
print "HTTP状态码:%s" % (HTTP_CODE)
print "DNS解析时间:%.2f ms"% (NAMELOOKUP_TIME*1000)
print "建立连接时间:%.2f ms" % (CONNECT_TIME*1000)
print "准备传输时间:%.2f ms" % (PRETRANSFER_TIME*1000)
print "传输开始时间:%.2f ms" % (STARTTRANSFER_TIME*1000)
print "传输结束总时间:%.2f ms" % (TOTAL_TIME*1000)
print "下载数据包大小:%d bytes/s" % (SIZE_DOWNLOAD)
print "HTTP头部大小:%d byte" % (HEADER_SIZE)
print "平均下载速度:%d bytes/s" % (SPEED_DOWNLOAD)
#关闭文件及Curl对象
indexfile.close()
c.close()
```


## urllib
```
python发送post和get请求
get请求：
使用get方式时，请求数据直接放在url中。
方法一、
import urllib
import urllib2
url = "http://192.168.81.16/cgi-bin/python_test/test.py?ServiceCode=aaaa"
req = urllib2.Request(url)
print req
res_data = urllib2.urlopen(req)
res = res_data.read()
print res
方法二、
import httplib
url = "http://192.168.81.16/cgi-bin/python_test/test.py?ServiceCode=aaaa"
conn = httplib.HTTPConnection("192.168.81.16")
conn.request(method="GET",url=url) 
response = conn.getresponse()
res= response.read()
print res

post请求：
使用post方式时，数据放在data或者body中，不能放在url中，放在url中将被忽略。
方法一、
import urllib
import urllib2
test_data = {'ServiceCode':'aaaa','b':'bbbbb'}
test_data_urlencode = urllib.urlencode(test_data)
requrl = "http://192.168.81.16/cgi-bin/python_test/test.py"
req = urllib2.Request(url = requrl,data =test_data_urlencode)
print req
res_data = urllib2.urlopen(req)
res = res_data.read()
print res
方法二、
import urllib
import httplib 
test_data = {'ServiceCode':'aaaa','b':'bbbbb'}
test_data_urlencode = urllib.urlencode(test_data)
requrl = "http://192.168.81.16/cgi-bin/python_test/test.py"
headerdata = {"Host":"192.168.81.16"}
conn = httplib.HTTPConnection("192.168.81.16")
conn.request(method="POST",url=requrl,body=test_data_urlencode,headers = headerdata) 
response = conn.getresponse()
res= response.read()
print res
对python中json的使用不清楚，所以临时使用了urllib.urlencode(test_data)方法;
模块urllib,urllib2,httplib的区别
httplib实现了http和https的客户端协议，但是在python中，模块urllib和urllib2对httplib进行了更上层的封装。
介绍下例子中用到的函数：
1、HTTPConnection函数
httplib.HTTPConnection(host[,port[,stict[,timeout]]])
这个是构造函数，表示一次与服务器之间的交互，即请求/响应
host 标识服务器主机(服务器IP或域名)
port 默认值是80
strict 模式是False，表示无法解析服务器返回的状态行时，是否抛出BadStatusLine异常
例如:
conn = httplib.HTTPConnection("192.168.81.16"，80) 与服务器建立链接。
2、HTTPConnection.request(method,url[,body[,header]])函数
这个是向服务器发送请求
method 请求的方式，一般是post或者get，
例如：
method="POST"或method="Get"
url 请求的资源，请求的资源(页面或者CGI,我们这里是CGI)
例如：
url="http://192.168.81.16/cgi-bin/python_test/test.py" 请求CGI
或者
url="http://192.168.81.16/python_test/test.html" 请求页面
body 需要提交到服务器的数据，可以用json，也可以用上面的格式，json需要调用json模块
headers 请求的http头headerdata = {"Host":"192.168.81.16"}
例如:
test_data = {'ServiceCode':'aaaa','b':'bbbbb'}
test_data_urlencode = urllib.urlencode(test_data)
requrl = "http://192.168.81.16/cgi-bin/python_test/test.py"
headerdata = {"Host":"192.168.81.16"}
conn = httplib.HTTPConnection("192.168.81.16"，80)
conn.request(method="POST",url=requrl,body=test_data_urlencode,headers = headerdata) 
conn在使用完毕后，应该关闭，conn.close()
3、HTTPConnection.getresponse()函数
这个是获取http响应，返回的对象是HTTPResponse的实例。
4、HTTPResponse介绍：
HTTPResponse的属性如下：
read([amt]) 获取响应消息体，amt表示从响应流中读取指定字节的数据，没有指定时，将全部数据读出；
getheader(name[,default]) 获得响应的header，name是表示头域名，在没有头域名的时候，default用来指定返回值
getheaders() 以列表的形式获得header
例如：
date=response.getheader('date');
print date
resheader=''
resheader=response.getheaders();
print resheader
列形式的响应头部信息:
[('content-length', '295'), ('accept-ranges', 'bytes'), ('server', 'Apache'),
 ('last-modified', 'Sat, 31 Mar 2012 10:07:02 GMT'), ('connection', 'close'), 
 ('etag', '"e8744-127-4bc871e4fdd80"'), ('date', 'Mon, 03 Sep 2012 10:01:47 GMT'),
  ('content-type', 'text/html')] 
date=response.getheader('date');
print date
取出响应头部的date的值。
```

## smtplib邮件
```
指定邮件编码
from email.mime.text import MIMEText
from email.header import Header
msg = MIMEText(content,'html', 'utf-8')  # 内容编码
msg.add_header("Content-Type",'text/plain; charset="utf-8"')
msg['Subject'] = "%s" % Header(subject, 'utf-8')  # 标题编码


#!/usr/bin/env python
#coding:utf-8
import smtplib
from email.mime.text import MIMEText
import sys

mail_host = 'smtp.qq.com'
mail_user = '2219722370'
mail_pass = 'tyztnlzandbbeahj'
mail_postfix = 'qq.com'

def send_mail(to_list,subject,content):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = ",".join(to_list)

    try:
        s = smtplib.SMTP()  #创建SMTP对象
        s.connect(mail_host,"25") #通过connect方法连接smtp主机
        s.starttls()    #启用TLS（安全传输）模式，所有SMTP指令都将加密传输，例如使用gmail的smtp服务时需要启动此项才能正常发送邮件
        s.login(mail_user,mail_pass)
        s.sendmail(me,to_list,msg.as_string())
        s.quit()    #断开smtp连接
        print "邮件发送成功!"
        return True
    except Exception as e:
        print "失败:" + str(e)
        return False

if __name__ == "__main__":
    #send_mail(sys.argv[1], sys.argv[2], sys.argv[3])
    to_list = ["liangguangyu@dachuizichan.com", "2219722370@qq.com"]
    send_mail(to_list,"title","msg")

#附件
#!/usr/bin/env python
#coding:utf-8
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys

mail_host = 'smtp.qq.com'
mail_user = '2219722370'
mail_pass = 'tyztnlzandbbeahj'
mail_postfix = 'qq.com'

def send_mail(to_list,subject,content):
    me = mail_user + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEMultipart('related')
    msgtext = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to_list
    attach = MIMEText(open("/etc/passwd","rb").read(),"base64","utf-8")  #附件
    attach["Content-Disposition"] = 
    "attachment; filename=\"业务服务质量周报(12周).xlsx\"".decode("utf-8").encode("gb18030") #附件名
    msg.attach(msgtext)    #MIMEMultipart对象附加MIMEText的内容，邮件内容
    msg.attach(attach)

    try:
        s = smtplib.SMTP()  #创建SMTP对象
        s.connect(mail_host,"25") #通过connect方法连接smtp主机
        s.starttls()    #启用TLS（安全传输）模式，所有SMTP指令都将加密传输，例如使用gmail的smtp服务时需要启动此项才能正常发送邮件
        s.login(mail_user,mail_pass)
        s.sendmail(me,to_list,msg.as_string())
        s.quit()    #断开smtp连接
        print "邮件发送成功!"
        return True
    except Exception as e:
        print "失败:" + str(e)
        return False

if __name__ == "__main__":
    #send_mail(sys.argv[1], sys.argv[2], sys.argv[3])
    send_mail("lgy_root@163.com","subject","msg")
```



## smtplib附件
```
#!/usr/bin/env python
#coding=utf-8
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
def SendMail():
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'sql result'
    msgRoot['From'] = "notice@dachuizichan.com"
    to_list = ["liangguangyu@dachuizichan.com"]
    msgRoot['To'] = ",".join(to_list)
    msgzip1 = MIMEApplication(open("/script/sql/EXCEL.tar.gz", 'rb').read())
    msgzip1.add_header('Content-Disposition', 'attachment',filename='EXCEL.tar.gz')
    msgRoot.attach(msgzip1)
    msgzip2 = MIMEApplication(open("/script/sql/csv.tar.gz", 'rb').read())
    msgzip2.add_header('Content-Disposition', 'attachment',filename='csv.tar.gz')
    msgRoot.attach(msgzip2)
    sendText = 'sql 运行结果'
    msgText = MIMEText(sendText, 'txt', 'utf-8')
    msgRoot.attach(msgText)
    smtp = smtplib.SMTP_SSL()
    smtp.connect('183.232.93.197', "465")
    smtp.login("notice@dachuizichan.com", "Dachui0002")
    smtp.sendmail(msgRoot['From'], to_list, msgRoot.as_string())
    smtp.quit()
SendMail()


基本思路就是，使用MIMEMultipart来标示这个邮件是多个部分组成的，然后attach各个部分。如果是附件，则add_header加入附件的声明。
在python中，MIME的这些对象的继承关系如下。
MIMEBase
    |-- MIMENonMultipart
        |-- MIMEApplication
        |-- MIMEAudio
        |-- MIMEImage
        |-- MIMEMessage
        |-- MIMEText
    |-- MIMEMultipart
一般来说，不会用到MIMEBase，而是直接使用它的继承类。MIMEMultipart有attach方法，而MIMENonMultipart没有，只能被attach。
MIME有很多种类型，这个略麻烦，如果附件是图片格式，我要用MIMEImage，如果是音频，要用MIMEAudio，如果是word、excel，
都不知道该用哪种MIME类型了，得上google去查。
最懒的方法就是，不管什么类型的附件，都用MIMEApplication，MIMEApplication默认子类型是application/octet-stream。
application/octet-stream表明“这是个二进制的文件，希望你们那边知道怎么处理”，然后客户端，比如qq邮箱，收到这个声明后，
会根据文件扩展名来猜测。
下面上代码。

假设当前目录下有foo.xlsx/foo.jpg/foo.pdf/foo.mp3这4个文件。
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
_user = "sigeken@qq.com"
_pwd  = "***"
_to   = "402363522@qq.com"

#如名字所示Multipart就是分多个部分
msg = MIMEMultipart()
msg["Subject"] = "don't panic"
msg["From"]    = _user
msg["To"]      = _to

#---这是文字部分---
part = MIMEText("乔装打扮，不择手段")
msg.attach(part)

#---这是附件部分---
#xlsx类型附件
part = MIMEApplication(open('foo.xlsx','rb').read())
part.add_header('Content-Disposition', 'attachment', filename="foo.xlsx")
msg.attach(part)

#jpg类型附件
part = MIMEApplication(open('foo.jpg','rb').read())
part.add_header('Content-Disposition', 'attachment', filename="foo.jpg")
msg.attach(part)

#pdf类型附件
part = MIMEApplication(open('foo.pdf','rb').read())
part.add_header('Content-Disposition', 'attachment', filename="foo.pdf")
msg.attach(part)

#mp3类型附件
part = MIMEApplication(open('foo.mp3','rb').read())
part.add_header('Content-Disposition', 'attachment', filename="foo.mp3")
msg.attach(part)

s = smtplib.SMTP("smtp.qq.com", timeout=30)#连接smtp邮件服务器,端口默认是25
s.login(_user, _pwd)#登陆服务器
s.sendmail(_user, _to, msg.as_string())#发送邮件
s.close()
```


## pexpect交互
```
Expect是一个用来处理交互的命令。借助Expect，我们可以将交互过程写在一个脚本上，使之自动化完成。形象的说，ssh登录，
ftp登录等都符合交互的定义。

Expect中最关键的四个命令是send,expect,spawn,interact。

send：用于向进程发送字符串
expect：从进程接收字符串
spawn：启动新的进程
interact：允许用户交互

================================================================
2.7版本以上的Python：
pip install pyexpect

装好pyexpect之后：
In [1]: import pexpect

In [2]: output,exitstatus = pexpect.run('ls -l',withexitstatus=1)

In [3]: print output,exitstatus

解释：
以上的output和exitstatus这两个变量名字是自己定义的
'ls -l'的执行结果赋值给前面的变量output
withexitstatus=1是开启返回状态，然后把这个返回状态赋值给前面的变量exitstatus

================================================================
接下来更深入的学习一下spawn，它能帮我们解决更加复杂的交互问题
先概念性的记住以下方法：
1、产生子进程执行相关命令pexpect.spawn()返回一个子进程实例：
child = pexpect.spawn(‘command’)

2、该实例产生的日志信息可以通过child.logfile进行配置：(可选项)
f = file（’/tmp/plog.out’, ‘w’）
child.logfile = f

3、使用expect进行交互
index = child.expect([“命令执行成功输出的内容”，”命令执行失败输出的内容”pexpect.EOF，pexpect.TIMEOUT]) 
pexpect.EOF 子进程结束
pexpect.TIMEOUT 超时，默认30s
然后通过if判断index的值，当index为0代表出现了“命令执行成功输出的内容”，当命令为1时代表”命令执行失败输出的内容”

4、通过sendline给子进程发送信息,自动带一个回车：
child.sendline(‘command’)
#甚至可以通过sendcontrol（‘c’）来发送ctrl+c

5、使用try，except来进行异常处理
try:
    index = p.expect(['good', 'bad'])
    if index == 0:
        do_something()
    elif index == 1:
        do_something_else()
except EOF:
    do_some_other_thing()
    except TIMEOUT:
    do_something_completely_different()

6、可以使用before来打印命令执行结果:
p = pexpect.spawn('/bin/ls')
p.expect(pexpect.EOF)
print p.before

以上6点我觉得可以让你游刃有余的解决日常90%进程交互的问题。
这里share一个经验就是写程序之前，先把这6个问题思考好，定义好，再去写程序的主题就ok了！

================================================================
例1：
现在有一台ftp服务器，地址为192.168.100.194，我要连上去，并且下载一个名为passwd的文件，然后退出。这个操作可以手动操作，
但如果工作量大了，我们就可以写个脚本来操作：

#!/usr/bin/env python

import pexpect
import sys

child = pexpect.spawn ('ftp 192.168.100.194')
child.expect ('Name .*: ')
child.sendline (sys.argv[1])    #这里是传的的一个参数，即下文的hello
child.expect ('Password:')
child.sendline (sys.argv[2])    #这里是第二个参数，即下文的123
child.expect ('ftp> ')
child.sendline ('get passwd')   #下载passwd这个文件
child.expect('ftp> ')
child.sendline ('bye')          #退出

执行结果：
[root@localhost test]# python a.py hello 123
[root@localhost test]# ls
a.py  passwd

例1修改版:
import pexpect

username = 'ptest'
key = '123456'
f = file('/tmp/plog.out', 'w')

if __name__ == "__main__":
    child = pexpect.spawn('ftp localhost') #产生新的子进程对象
    child.logfile = f                      #指定日志文件为上面的变量f
try:
    index = child.expect(['Name'])         #期待命令执行成功并输出Name
    if index == 0:                           #如果是列表里的第0个，即Name，则往下走
        child.sendline(username)           #通过sendline给子进程发送信息，自带回车
        index = child.expect(['Password']) #期待命令执行成功并输出Password
        if index == 0:
            child.sendline(key)            #如果命中上面的Pwassword，则发送key
            index = child.expect(['Login successful.*ftp>'])
            if index == 0:
                child.sendline('ls')
                index = child.expect(['test.mp3'])
                if index == 0:
                    child.sendline('bin')  #改为二进制，防止下面get的时候乱码
                    child.sendline('get test.mp3')   #下载test.mp3文件
                    index = child.expect(['Transfer complete.*ftp>'])
                    if index == 0:
                        print 'download complete!'
                        child.sendline('bye')  #退出
except:
print child.before
print 'see /tmp/plog.out can find more info!'

执行一下这段代码，然后去查看一下/tmp/plog.out文件的内容
这段代码虽然非常丑陋，但还是能起到练习的作用，稍加变化就能满足您生产需求！

================================================================
例2：线上实例，可拿去用。生成公钥并拷贝到指定主机，支持多台。
#!/usr/bin/env python
#coding=utf8

import pexpect

#指定本地公钥所在的家目录
home = '/root'
#指定远程主机的用户、IP和密码，多台用逗号隔开
info = {'root@192.168.0.156':'123456'
       }

f = file('/tmp/plog.out', 'w')

def genkey():
    child = pexpect.spawn("ssh-keygen -t rsa")
    child.logfile = f
    try:
        index = child.expect(['save the key'])
        if index == 0:
            child.sendline()
            index = child.expect(['Enter passphrase', 'Overwrite'])
            if index == 0:
                child.sendline()
                index = child.expect(['Enter same passphrase'])
                if index == 0:
                    child.sendline()
            else:
                child.sendline('n')
    except:
        print child.before

def copykey():
    try:
        for k,v in info.items():
            child = pexpect.spawn("ssh-copy-id -i %s/.ssh/id_rsa.pub %s"%(home,k))
            child.logfile = f
            index = child.expect(['continue connecting','password'])
            if index == 0:
                child.sendline('yes')
            else:
                child.sendline(v)
                child.expect(pexpect.EOF)
    except:
        print child.before

if __name__ == "__main__":
    genkey()
    copykey()

================================================================
例3：这里是ssh登录的过程，有超时，ssh_newkey,让你输入password三种情况：

#!/usr/bin/env python
#encoding=utf8

import pexpect
import getpass, os

#user: ssh 主机的用户名
#host：ssh 主机的域名
#password：ssh 主机的密码
#command：即将在远端 ssh 主机上运行的命令
def ssh_command (user, host, password, command):
    """
    This runs a command on the remote host. This could also be done with the
    pxssh class, but this demonstrates what that class does at a simpler level.
    This returns a pexpect.spawn object. This handles the case when you try to
    connect to a new host and ssh asks you if you want to accept the public key
    fingerprint and continue connecting.
    """
    ssh_newkey = 'Are you sure you want to continue connecting'
    # 为 ssh 命令生成一个 spawn 类的子程序对象.
    child = pexpect.spawn('ssh -l %s %s %s'%(user, host, command))
    i = child.expect([pexpect.TIMEOUT, ssh_newkey, 'password: '])
    # 如果登录超时，打印出错信息，并退出.
    if i == 0: # Timeout
        print 'ERROR!'
        print 'SSH could not login. Here is what SSH said:'
        print child.before, child.after
        return None
    # 如果 ssh 没有 public key，接受它.
    if i == 1: # SSH does not have the public key. Just accept it.
        child.sendline ('yes')
        child.expect ('password: ')
        i = child.expect([pexpect.TIMEOUT, 'password: '])
        if i == 0: # Timeout
            print 'ERROR!'
            print 'SSH could not login. Here is what SSH said:'
            print child.before, child.after
            return None
    # 输入密码.
    child.sendline(password)
    return child

def main ():
    # 获得用户指定 ssh 主机域名.
    host = raw_input('Hostname: ')
    # 获得用户指定 ssh 主机用户名.
    user = raw_input('User: ')
    # 获得用户指定 ssh 主机密码.
    password = getpass.getpass()
    # 获得用户指定 ssh 主机上即将运行的命令.
    command = raw_input('Enter the command: ')
    child = ssh_command (user, host, password, command)
    # 匹配 pexpect.EOF
    child.expect(pexpect.EOF)
    # 输出命令结果.
    print child.before

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        print str(e)
        os._exit(1)


1.密钥
用shell下的except，这个不好用，ssh可以
#!/usr/bin/env python
# encoding: UTF-8
"""
ssh-copy-id -i /root/.ssh/id_rsa.pub root@localhost
"""
import pexpect
keyfile='/root/.ssh/id_rsa.pub'
target_user='root'
target_host='localhost'
command = 'ssh-copy-id -i ' + keyfile + ' ' + target_user + '@' + target_host
password = '123456'
child = pexpect.spawn(command)
try:
    index = child.expect(['yes/no', 'password'])
    if index == 0:
        child.sendline('yes')
        index = child.expect(['password'])
        if index == 0:
            child.sendline(password)
    else:
        child.sendline(password)
except pexpect.EOF:
    print 'now to try U sshkey'
2、
#!/usr/bin/env python
#coding:utf-8
import pexpect,sys
child = pexpect.spawn("ssh root@127.0.0.1")
# pexpect.spawn(command, args=[], timeout=30, maxread=2000, searchwindowsize=None, logfile=None, cwd=None, 
env=None, ignore_sighup=True)
# 其中command参数可以是任意已知的系统命令 参数timeout为等待结果的超时时间；参数maxread为pex-pect从终端控制台一次读取的最大字节数，
searchwindowsize参数为匹配缓冲区字符串的位置，默认是从开始位置匹配。
#需要注意的是，pexpect不会解析shell命令当中的元字符，包括重定向“>”、管道“|”或通配符“*”，当然，我们可以通过一个技巧来解决这个问题，
将存在这三个特殊元字符的命令作为/bin/bash的参数进行调用，
#例如：child = pexpect.spawn('/bin/bash -c "ls -l | grep LOG > logs.txt"')
#      child.expect(pexpect.EOF)
#我们可以通过将命令的参数以Python列表的形式进行替换，从而使我们的语法变成更加清晰，下面的代码等价于上面的。
#       shell_cmd = 'ls -l | grep LOG > logs.txt'
#       child = pexpect.spawn('/bin/bash', ['-c', shell_cmd])
#       child.expect(pexpect.EOF)
fout = file("mylog.txt",'w')
#child.logfile = fout  #输出到文件
child.logfile = sys.stdout  #标准输出，当前终端
passwd = "1"
comm = "free -m"
try:
    index = child.expect(["yes/no","password:"]) #匹配，返回索引值
    if index == 0:
        child.sendline("yes")
        child.expect("password:")
        child.sendline(passwd)
        child.expect('#')
        child.sendline(comm)
        child.expect('#')
        child.sendline("exit")
    elif index == 1:
        child.sendline(passwd)
        child.expect('#')
        child.sendline(comm)
        child.expect('#')
        child.sendline("exit")
    else:
        print "Error"
except Exception,e:
    print str(e)
```



## json
```
# coding:utf-8
from json import dumps, loads
a = {"a": 1, "b": 2, "c": 3}
b = str({"a": 1, "b": 2, "c": 3})
print dumps(a,indent=4)   格式化输出
{
    "a": 1, 
    "c": 3, 
    "b": 2
}
print dumps(b, indent=4)
"{'a': 1, 'c': 3, 'b': 2}"
print dumps(eval(b), indent=4)
{
    "a": 1, 
    "c": 3, 
    "b": 2
}


编码问题
json.dumps在默认情况下，对于非ascii字符生成的是相对应的字符编码，而非原始字符
# coding:utf-8
from json import dumps, loads
test = loads('{"haha": "哈哈"}')
print dumps(test)
# {"haha": "\u54c8\u54c8"}
print dumps(test, ensure_ascii=False)
# {"haha": "哈哈"}

```



## ftplib
```
ftp登陆连接
from ftplib import FTP #加载ftp模块
ftp=FTP() #设置变量
ftp.set_pasv(False)    关闭被动模式
ftp.set_debuglevel(2) #打开调试级别2，显示详细信息
ftp.connect("IP","port") #连接的ftp sever和端口
ftp.login("user","password")#连接的用户名，密码
print ftp.getwelcome() #打印出欢迎信息
ftp.cwd("xxx/xxx") #更改远程目录
bufsize=1024 #设置的缓冲区大小
filename="filename.txt" #需要下载的文件
file_handle=open(filename,"wb").write #以写模式在本地打开文件
ftp.retrbinaly("RETR filename.txt",file_handle,bufsize) #接收服务器上文件并写入本地文件
ftp.set_debuglevel(0) #关闭调试模式
ftp.quit #退出ftp
ftp相关命令操作
ftp.cwd(pathname) #设置FTP当前操作的路径
ftp.dir() #显示目录下文件信息
ftp.nlst() #获取目录下的文件
ftp.mkd(pathname) #新建远程目录
ftp.pwd() #返回当前所在位置
ftp.rmd(dirname) #删除远程目录
ftp.delete(filename) #删除远程文件
ftp.rename(fromname, toname)#将fromname修改名称为toname。
ftp.storbinaly("STOR filename.txt",file_handel,bufsize) #上传目标文件
ftp.retrbinary("RETR filename.txt",file_handel,bufsize)#下载FTP文件

例子：
from ftplib import FTP  
      
ftp = FTP()  
timeout = 30  
port = 21  
ftp.connect('192.168.1.188',port,timeout) # 连接FTP服务器  
ftp.login('UserName','888888') # 登录  
print ftp.getwelcome()  # 获得欢迎信息   
ftp.cwd('file/test')    # 设置FTP路径  
list = ftp.nlst()       # 获得目录列表  
for name in list:  
    print(name)             # 打印文件名字  
path = 'd:/data/' + name    # 文件保存路径  
f = open(path,'wb')         # 打开要保存文件  
filename = 'RETR ' + name   # 保存FTP文件  
ftp.retrbinary(filename,f.write) # 保存FTP上的文件  
ftp.delete(name)            # 删除FTP文件  
ftp.storbinary('STOR '+filename, open(path, 'rb')) # 上传FTP文件  
ftp.quit()                  # 退出FTP服务器  

#!/usr/bin/python
# -*- coding: utf-8 -*-
import ftplib
import os
import socket
HOST = 'ftp.mozilla.org'
DIRN = 'pub/mozilla.org/webtools'
FILE = 'bugzilla-3.6.7.tar.gz'
def main():
    try:
        f = ftplib.FTP(HOST)
    except (socket.error, socket.gaierror):
        print 'ERROR:cannot reach " %s"' % HOST
        return
    print '***Connected to host "%s"' % HOST
    try:
        f.login()
    except ftplib.error_perm:
        print 'ERROR: cannot login anonymously'
        f.quit()
        return
    print '*** Logged in as "anonymously"'
    try:
        f.cwd(DIRN)
    except ftplib.error_perm:
        print 'ERRORL cannot CD to "%s"' % DIRN
        f.quit()
        return
    print '*** Changed to "%s" folder' % DIRN
    try:
        #传一个回调函数给retrbinary() 它在每接收一个二进制数据时都会被调用
        f.retrbinary('RETR %s' % FILE, open(FILE, 'wb').write)
    except ftplib.error_perm:
        print 'ERROR: cannot read file "%s"' % FILE
        os.unlink(FILE)
    else:
        print '*** Downloaded "%s" to CWD' % FILE
    f.quit()
    return
if __name__ == '__main__':
    main()
```



## datetime
```
  打印时间

import time
print(time.strftime('%Y-%m-%d %H:%M:%S')) # time.strftime(format[, tuple]) 将指定的struct_time(默认为当前时间),
根据指定的格式化字符串输出,打印如: 2011-04-13 18:30:10
print(time.strftime('%Y-%m-%d %A %X', time.localtime(time.time()))) # 显示当前日期； 
打印如: 2011-04-13 Wednesday 18:30:10
print(time.strftime("%Y-%m-%d %A %X", time.localtime())) # 显示当前日期； 打印如: 2011-04-13 Wednesday 18:30:10
print(time.time()) # 以浮点数形式返回自Linux新世纪以来经过的秒数； 打印如: 1302687844.7；  
使用 time.localtime(time.time()) 可返转回 time 类型
print(time.ctime(1150269086.6630149)) #time.ctime([seconds]) 把秒数转换成日期格式的字符串，如果不带参数，
则显示当前的时间。打印如: Wed Apr 13 21:13:11 2011
    print(time.gmtime(1150269086.6630149)) # time.gmtime([seconds]) 将一个时间戳转换成一个UTC时区(0时区)
    的struct_time，如果seconds参数未输入，则以当前时间为转换标准
    print(time.gmtime()) # 打印如： time.struct_time(tm_year=2014, tm_mon=8, tm_mday=27, tm_hour=7, 
    tm_min=28, tm_sec=19, tm_wday=2, tm_yday=239, tm_isdst=0)
    print(time.localtime(1150269086.6630149)) # time.localtime([seconds]) 将一个时间戳转换成一个当前时区的
    struct_time，如果seconds参数未输入，则以当前时间为转换标准
    print(time.mktime(time.localtime())) # time.mktime(tuple) 将一个以struct_time转换为时间戳(float类型),
    打印如：1409124869.0

格式转换
    from datetime import datetime
    datetime.strptime('2017 Sep 21 14:16:52', '%Y %b %d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

    # 获取当前时间的具体值(年、月、日、时、分、秒)
    print(time.localtime()) # 打印如: time.struct_time(tm_year=2014, tm_mon=8, tm_mday=27, tm_hour=15, 
    tm_min=10, tm_sec=16, tm_wday=2, tm_yday=239, tm_isdst=0)
    print(time.localtime()[:]) # 打印如: (2014, 8, 27, 15, 10, 16, 2, 239, 0)
    # 取上一月月份
    print(time.localtime()[1]-1) # 打印如: 7
    # 取两个月后的月份
    print(time.localtime()[1]+2) # 打印如: 10
    # 取去年年份
    print(time.localtime()[0]-1) # 打印如: 2013

# 获取时间戳
    import time, datetime
    print(time.time()) # 打印如： 1409127119.16
    print time.mktime(time.strptime('2012-10-21 18:51:50', '%Y-%m-%d %H:%M:%S')) 指定时间的
    print(long(time.time())) # 打印如： 1409127119
    print(time.mktime( datetime.datetime.now().timetuple() )) # 打印如： 1409127119.0
    print(long(time.mktime(time.strptime('2014-03-25 19:25:33', '%Y-%m-%d %H:%M:%S')))) # 打印如：1395746733



# 时间暂停两秒
    import time
    time.sleep(2)


# 获取今天、昨天、前几或者后几小时(datetime实现)
    import datetime
    # 得到今天的日期
    print(datetime.date.today()) # 打印如: 2011-04-13
    # 得到前一天的日期
    print(datetime.date.today() + datetime.timedelta(days=-1)) # 打印如: 2011-04-12
    print(datetime.date.today() - datetime.timedelta(days=1))  # 打印如: 2011-04-12
    # 得到10天后的时间
    print(datetime.date.today() + datetime.timedelta(days=10)) # 打印如: 2011-04-23
    # 得到10小时后的时间，上面的 days 换成 hours
    print(datetime.datetime.now() + datetime.timedelta(hours=10)) # 打印如: 2011-04-14 04:30:10.189000
    # 获取明天凌晨 1 点的时间
    d1 = datetime.datetime(*time.localtime()[:3]) + datetime.timedelta(days=1) + datetime.timedelta(hours=1) 
    # 打印如: 2011-04-13 01:00:00
    print(time.mktime( d1.timetuple() )) # 获取时间戳打印如： 1409127119.0



# 获取今天、昨天、前几或者后几小时(time实现)
    import time
    # 取一天后的当前具体时间
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()+24*60*60)))
    # 取20天后的当前具体时间
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()+20*24*60*60)))
    # 取20天后当前具体时间的前2小时
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()+20*24*60*60-2*60*60)))


#两日期相减(也可以大于、小于来比较):
    import datetime
    # 指定具体时间的参数： datetime.datetime(year, month, day[, hour[, minute[, second[, microsecond[,tzinfo]]]]])
    d1 = datetime.datetime(2005, 2, 16)
    d2 = datetime.datetime(2004, 12, 31)
    print((d1 - d2).days) # 打印： 47


#运行时间：
    import time,datetime
    starttime = datetime.datetime.now()
    time.sleep(1) # 暂停1秒
    endtime = datetime.datetime.now()
    print((endtime - starttime).seconds) # 秒, 打印： 1
    print((endtime - starttime).microseconds) # 微秒(百万分之一秒)； 打印： 14000

# 精确计算函数的运行时间
    import time
    start = time.clock()
    func(*args, **kwargs) # 运行函数
    end =time.clock()
    print( 'used:' + str(end) ) # 耗时单位:秒

# 精确计算函数的运行时间2(实测发现 time.clock() 计算不严谨,前面用没用过很难确定)
    import time
    start = time.time()
    func(*args, **kwargs) # 运行函数
    end =time.time()
    print( 'used:' + str(end - start) ) # 耗时单位:秒

# time.clock() 用法
    clock() -> floating point number
    该函数有两个功能，
    在第一次调用的时候，返回的是程序运行的实际时间；
    以第二次之后的调用，返回的是自第一次调用后,到这次调用的时间间隔

    import time
    time.sleep(1)
    print "clock1:%s" % time.clock() # 打印如: clock1:2.17698990094e-06
    time.sleep(1)
    print "clock2:%s" % time.clock() # 打印如: clock2:1.00699529055
    time.sleep(1)
    print "clock3:%s" % time.clock() # 打印如: clock3:2.00698720459



# 字符串 转成 时间 time
    import time
    s2='2012-02-16';
    a=time.strptime(s2,'%Y-%m-%d')
    print a # time.struct_time(tm_year=2012, tm_mon=2, tm_mday=16, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3,
     tm_yday=47, tm_isdst=-1)
    print type(a) # <type 'time.struct_time'>
    print repr(a) # time.struct_time(tm_year=2012, tm_mon=2, tm_mday=16, tm_hour=0, tm_min=0, tm_sec=0, tm_wday=3,
     tm_yday=47, tm_isdst=-1)

# 字符串 转成 时间 datetime
    import datetime
    date_str = "2008-11-10 17:53:59"
    dt_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    print dt_obj # 2008-11-10 17:53:59
    print dt_obj.strftime('%Y-%m-%d %H:%M:%S') # 2008-11-10 17:53:59
    print type(dt_obj) # <type 'datetime.datetime'>
    print repr(dt_obj) # datetime.datetime(2008, 11, 10, 17, 53, 59)

# timestamp to time tuple in UTC
    import time
    timestamp = 1226527167.595983
    time_tuple = time.gmtime(timestamp)
    print repr(time_tuple) # time.struct_time(tm_year=2008, tm_mon=11, tm_mday=12, tm_hour=21, tm_min=59, tm_sec=27,
     tm_wday=2, tm_yday=317, tm_isdst=0)
    print time.strftime('%Y-%m-%d %H:%M:%S', time_tuple) # 2008-11-12 21:59:27

# timestamp to time tuple in local time (返转 time.time() 生成的时间戳)
    import time
    timestamp = 1226527167.595983
    time_tuple = time.localtime(timestamp)
    print repr(time_tuple) # time.struct_time(tm_year=2008, tm_mon=11, tm_mday=13, tm_hour=5, tm_min=59, tm_sec=27, 
    tm_wday=3, tm_yday=318, tm_isdst=0)
    print time.strftime('%Y-%m-%d %H:%M:%S', time_tuple) # 2008-11-13 05:59:27

# datetime 转成 time
    import time, datetime
    # datetime 的 timetuple 函数可直接转成 time.struct_time
    print(datetime.datetime.now().timetuple())
    # 上行打印如：time.struct_time(tm_year=2014, tm_mon=8, tm_mday=27, tm_hour=16, tm_min=7, tm_sec=37, tm_wday=2,
     tm_yday=239, tm_isdst=-1)
    print(time.localtime())
    # 上行打印如：time.struct_time(tm_year=2014, tm_mon=8, tm_mday=27, tm_hour=16, tm_min=7, tm_sec=37, tm_wday=2,
     tm_yday=239, tm_isdst=0)


日期格式化符号:
%%: %号本身
%A: 本地星期(全称),如:Tuesday   %a: 本地星期(简称),如:Tue
%B: 本地月份(全称),如:February  %b: 本地月份(简称),如:Feb
                                %c: 本地相应的日期表示和时间表示,如:02/15/11 16:50:57
                                %d: 月内中的一天(0-31),如:15
%H: 24进制小时数(0-23)
%I: 12进制小时数(01-12)
                                %j: 年内的一天(001-366),如:046
%M: 分钟(00-59),如:50           %m: 月份(01-12),如:02
                                %p: 上下午(本地A.M.或P.M.的等价符),如:PM
%S: 秒钟(00-59),如:57           %f: 微秒数值(仅 datetime 类型有, time 类型用会报错)
%X: 本地的时间,如:16:50:57      %x: 本地的日期,如:02/15/11
%Y: 四位的年(000-9999)          %y: 两位数的年份表示(00-99)

%U: 年里的星期数(00-53)从星期天开始,如:07
%W: 年里的星期数(00-53)从星期一开始,如:07
%w: 星期(0-6),星期天为星期的开始,如:2 (星期天为0)
%Z: 当前时区的名称,如:中国标准时间
%z: 当前时区的名称,如:中国标准时间
```



## logging
```
logging 模块
    # 1. 直接使用 logging, 会受到前面对 logging 的设置的影响,默认情况下窗口显示
    import logging
    # logging提供多种级别的日志信息，如: NOTSET(值为0), DEBUG(10), INFO(20), WARNING(默认值30), ERROR(40), 
    CRITICAL(50)等。每个级别都对应一个数值。
    logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(module)s.%(funcName)s %(lineno)s: %(levelname)s : %(message)s',
                datefmt='%Y-%m-%d %X', filename='log.log')
    logging.info('logging message')


    # 2. 按自己需要设置 log 后再使用
    def initlog():
        import logging
        logger = logging.getLogger() # 生成一个日志对象，可以带一个名字，可以缺省
        hdlr = logging.FileHandler('crawl.log') # 生成一个Handler。logging支持许多Handler，象FileHandler, 
        SocketHandler, SMTPHandler等，我由于要写文件就使用了FileHandler。
        # 生成一个格式器，用于规范日志的输出格式。
        # 如果没有这行代码，那么缺省的格式就是："%(message)s"。也就是写日志时，信息是什么日志中就是什么，没有日期，
        没有信息级别等信息。
        # logging支持许多种替换值，详细请看Formatter的文档说明。这里有三项：时间，信息级别，日志信息。
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        hdlr.setFormatter(formatter) # 将格式器设置到处理器上

        #logger.addHandler(hdlr) # 将处理器加到日志对象上
        # 上面使用 addHandler 会有两份日志输出,一份输出到文件(新加的 handler),一份输出到屏幕(默认的 handler)。
        logger.handlers = [hdlr] # 这样写则只有一份日志输出,消耗更少、效率更高。

        # 设置日志信息输出的级别。如果不执行此句，缺省为30(WARNING)。
        # 可以执行：logging.getLevelName(logger.getEffectiveLevel())来查看缺省的日志级别。日志对象对于不同的级别
        信息提供不同的函数进行输出,如:info(), error(), debug()等。
        # 当写入日志时，小于指定级别的信息将被忽略。因此为了输出想要的日志级别一定要设置好此参数。这里我设为NOTSET（值为0），
        也就是想输出所有信息。
        logger.setLevel(logging.NOTSET)
        return logger

    # 使用日志对象：
    logger = initlog()
    logger.info('message info')
    logger.error('message error')


logging介绍
    Python的 logging 模块提供了通用的日志系统，可以方便第三方模块或者是应用使用。
    这个模块提供不同的日志级别，并可以采用不同的方式记录日志，比如文件，HTTP GET/POST，SMTP，Socket等，甚至可以自己实现
    具体的日志记录方式。

    logging模块与log4j的机制是一样的，只是具体的实现细节不同。模块提供logger，handler，filter，formatter。
    logger：提供日志接口，供应用代码使用。
    logger最常用的操作有两类：配置和发送日志消息。
    可以通过logging.getLogger(name)获取logger对象，如果不指定name则返回root对象，多次使用相同的name调用getLogger方法
    返回同一个logger对象。

    handler：将日志记录（log record）发送到合适的目的地（destination），比如文件，socket等。
    一个logger对象可以通过addHandler方法添加0到多个handler，每个handler又可以定义不同日志级别，以实现日志分级过滤显示。
    filter：提供一种优雅的方式决定一个日志记录是否发送到handler。
    formatter：指定日志记录输出的具体格式。formatter的构造方法需要两个参数：消息的格式字符串和日期字符串，这两个参数都是可选的。
    与log4j类似，logger，handler和日志消息的调用可以有具体的日志级别（Level），只有在日志消息的级别大于logger和handler的级别。

    示例(log_test.py 文件)：

        import logging
        import logging.handlers

        LOG_FILE = 'tst.log'

        # 注意,按大小拆分、按时间拆分,是两个不同的 handler 类
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) 
        # 实例化handler,文件到达一定大小时拆分
        handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when='midnight', backupCount = 10) 
        # 凌晨时拆分log文件，以免文件太大
        # 上面的 backupCount参数 用于指定保留的log备份文件的个数,如写 10 表示最多保留 10 个 log备份文件
        fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

        formatter = logging.Formatter(fmt)   # 实例化formatter
        handler.setFormatter(formatter)      # 为handler添加formatter

        logger = logging.getLogger('tst')    # 获取名为tst的logger
        logger.addHandler(handler)           # 为logger添加handler
        logger.setLevel(logging.DEBUG)

        logger.info('first info message')    # 输出到 log 文件
        logger.debug('first debug message')


    输出结果：
        2012-03-04 23:21:59,682 - log_test.py:16 - tst - first info message
        2012-03-04 23:21:59,682 - log_test.py:17 - tst - first debug message


关于 formatter 的配置，采用的是%(<dict key>)s的形式，就是字典的关键字替换。提供的关键字包括：
      Format                    Description
    %(name)s                Logger 的名字。 Name of the logger (logging channel).
    %(levelno)s           数字形式的日志级别。 Numeric logging level for the message
     (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    %(levelname)s       文本形式的日志级别。 Text logging level for the message
('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    %(pathname)s            调用日志输出函数的模块的完整路径名，可能没有。 Full pathname of the source file 
    where the logging call was issued (if available).
    %(filename)s            调用日志输出函数的模块的文件名。 Filename portion of pathname.
    %(module)s                调用日志输出函数的模块名。 Module (name portion of filename).
    %(funcName)s            调用日志输出函数的函数名。 Name of function containing the logging call.
    %(lineno)d                调用日志输出函数的语句所在的代码行。 Source line number where the logging
     call was issued (if available).
    %(created)f                当前时间，用UNIX标准的表示时间的浮点数表示。 Time when the LogRecord was
     created (as returned by time.time()).
    %(relativeCreated)d        输出日志信息时的，自Logger创建以来的毫秒数。 Time in milliseconds when the
     LogRecord was created, relative to the time the logging module was loaded.
    %(asctime)s                字符串形式的当前时间。默认格式是“2003-07-08 16:49:45,896”。逗号后面的是毫秒。
     Human-readable time when the LogRecord was created.
                            By default this is of the form “2003-07-08 16:49:45,896” (the numbers after
                             the comma are millisecond portion of the time).
    %(msecs)d                Millisecond portion of the time when the LogRecord was created.
    %(thread)d                线程ID。可能没有。 Thread ID (if available).
    %(threadName)s            线程名。可能没有。 Thread name (if available).
    %(process)d                进程ID。可能没有。 Process ID (if available).
    %(message)s                用户输出的消息。 The logged message, computed as msg % args.
    这个是摘自官网，提供了很多信息。


logging的配置
    logging的配置可以采用python代码或是配置文件。
    python代码的方式就是在应用的主模块中，构建handler，handler，formatter等对象。
    而配置文件的方式是将这些对象的依赖关系分离出来放在文件中。比如前面的例子就类似于python代码的配置方式。

    示例(采用配置文件的方式)：

        import logging
        import logging.config

        logging.config.fileConfig("logging.conf")    # 采用配置文件

        # create logger
        logger = logging.getLogger("simpleExample")  # 获取名为 simpleExample 的 logger, 对应配置文件的
         [logger_simpleExample]

        # "application" code
        logger.debug("debug message")
        logger.info("info message")
        logger.warn("warn message")
        logger.error("error message")
        logger.critical("critical message")


    配置文件 logging.conf 的内容:
        [loggers]
        keys=root,simpleExample

        [handlers]
        keys=consoleHandler

        [formatters]
        keys=simpleFormatter

        [logger_root]
        level=DEBUG
        handlers=consoleHandler

        [logger_simpleExample]
        level=DEBUG
        handlers=consoleHandler
        qualname=simpleExample
        propagate=0

        [handler_consoleHandler]
        class=StreamHandler
        level=DEBUG
        formatter=simpleFormatter
        args=(sys.stdout,)

        [formatter_simpleFormatter]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        datefmt=

    loggin.conf采用了模式匹配的方式进行配置，正则表达式是r'^[(.*)]$'，从而匹配出所有的组件。
    对于同一个组件具有多个实例的情况使用逗号','进行分隔。
    对于一个实例的配置采用componentName_instanceName配置块。
    使用这种方式还是蛮简单的。

    在指定handler的配置时，class是具体的handler类的类名，可以是相对logging模块或是全路径类名，比如需要RotatingFileHandler，
    则class的值可以为: RotatingFileHandler 或者logging.handlers.RotatingFileHandler 。
    args就是要传给这个类的构造方法的参数，就是一个元组，按照构造方法声明的参数的顺序。

     这里还要明确一点，logger对象是有继承关系的，比如名为a.b和a.c的logger都是名为a的子logger，并且所有的logger对象都继承于root。
     如果子对象没有添加handler等一些配置，会从父对象那继承。这样就可以通过这种继承关系来复用配置。


多模块使用 logging
    logging模块保证在同一个python解释器内，多次调用logging.getLogger('log_name')都会返回同一个logger实例，即使是在
    多个模块的情况下。
    所以典型的多模块场景下使用logging的方式是在main模块中配置logging，这个配置会作用于多个的子模块，然后在其他模块中直
    接通过getLogger获取Logger对象即可。

    示例:
    配置文件 logging.conf 的内容:
        [loggers]
        keys=root,main

        [handlers]
        keys=consoleHandler,fileHandler

        [formatters]
        keys=fmt

        [logger_root]
        level=DEBUG
        handlers=consoleHandler

        [logger_main]
        level=DEBUG
        qualname=main
        handlers=fileHandler

        [handler_consoleHandler]
        class=StreamHandler
        level=DEBUG
        formatter=fmt
        args=(sys.stdout,)

        [handler_fileHandler]
        class=logging.handlers.RotatingFileHandler
        level=DEBUG
        formatter=fmt
        args=('tst.log','a',20000,5,)

        [formatter_fmt]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        datefmt=

    主模块 main.py 的内容：
        import logging
        import logging.config

        logging.config.fileConfig('logging.conf')
        root_logger = logging.getLogger('root')
        root_logger.debug('test root logger...')

        logger = logging.getLogger('main')
        logger.info('test main logger')
        logger.info('start import module \'mod\'...')
        import mod

        logger.debug('let\'s test mod.testLogger()')
        mod.testLogger()

        root_logger.info('finish test...')

    子模块 mod.py 的内容：
        import logging
        import submod

        logger = logging.getLogger('main.mod')
        logger.info('logger of mod say something...')

        def testLogger():
            logger.debug('this is mod.testLogger...')
            submod.tst()

    子子模块 submod.py 的内容：
        import logging

        logger = logging.getLogger('main.mod.submod')
        logger.info('logger of submod say something...')

        def tst():
            logger.info('this is submod.tst()...')

    运行python main.py，控制台输出所有log信息
    但 tst.log 中没有root logger输出的信息，因为logging.conf中配置了只有main logger及其子logger使用RotatingFileHandler，
    而root logger是输出到标准输出。



出错时发邮件
    import os
    import logging
    import logging.handlers

    def init_log(logfile, backupCount, debug=True):
        '''初始化日志'''
        log_path = os.path.dirname(logfile)
        if not os.path.isdir(log_path):
            os.makedirs(log_path)

        logger = logging.getLogger()
        formatter = logging.Formatter("[%(asctime)s]: %(module)s %(levelname)s %(message)s ")

        # 文件 log 输出
        #handler_record = logging.FileHandler(logfile)
        handler_record = logging.handlers.TimedRotatingFileHandler(logfile, when='midnight', backupCount=backupCount)
        handler_record.setFormatter(formatter)
        logger.addHandler(handler_record)
        if debug:
            logger.setLevel(logging.DEBUG)
            handler_record.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARNING)
            handler_record.setLevel(logging.WARNING)

        # 邮件 log 输出
        handler_email = logging.handlers.SMTPHandler(
                        "mail.guoling.com", # 邮件服务器
                        "backend_program@guoling.com", # 发出邮件的地址
                        "fengwanli@guoling.com", # 接收邮件的地址。 发给多个人则用列表(如：['292598441@qq.com',
                        'fengwanli@guoling.com']),用字符串则只发给第一个
                        "test email logging", # 邮件主题
                        ("backend_program@guoling.com", "guoling") # 凭证(CREDENTIALS)
                        )
        handler_email.setFormatter(formatter)
        handler_email.setLevel(logging.ERROR)
        email_logger = logging.getLogger('email') # 定义发邮件的 logger
        email_logger.addHandler(handler_email)
        email_logger.setLevel(logging.ERROR)

        # http 的 log 输出
        http_handler = logging.handlers.HTTPHandler('127.0.0.1:3333','/log/', method='GET')
        http_handler.setFormatter(formatter)
        http_handler.setLevel(logging.ERROR)


    # 调用 logger
    init_log('./log/run.log', 30, False) # 初始化
    #os.remove('./log/run.log')

    logging.error(u"logging.error 测试。。。") # 普通的 log,写到文件上

    email_logger = logging.getLogger('email') # 需要发邮件的 log
    msg = "email_logger.error gbk 测试 2..."
    msg = msg.decode(sys.stdin.encoding).encode('gbk') # 处理中文,让 foxmail 显示正常
    email_logger.error(msg) # 会发出邮件,并且也写到文件上


第三方模块 mlogging
====================================
https://pypi.python.org/pypi/mlogging/

使用好处:
    发起多线程写log，性能优化

缺点:
    windows 下貌似不能用


安装:
    # linux 下 easy_install
    sudo easy_install mlogging
```
