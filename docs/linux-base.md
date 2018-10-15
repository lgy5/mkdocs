## 升级glibc-2.14
```
http://ftp.gnu.org/gnu/glibc/glibc-2.14.tar.gz

tar -xzf glibc-2.14.tar.gz
mkdir build // 在glibc-2.14目录下建立build文件夹
cd build // 进入build目录
../configure --prefix=/opt/glibc-2.14 // 配置glibc并设置当前glibc-2.14安装目录
make && make install // 编译安装glibc-2.14库
cp /etc/ld.so.conf /usr/local/glibc-2.14/etc/ （ld.so.conf not found报错时）

当前环境生效
export LD_LIBRARY_PATH=/usr/local/glibc-2.14/lib/:$LD_LIBRARY_PATH

修改系统（尽量不修改）
rm -rf /lib64/libc.so.6 // 先删除先前的libc.so.6软链
ln -s /opt/glibc-2.14/lib/libc-2.14.so /lib64/libc.so.6

```



## phantomjs网页截图
```
yum -y install bitmap-fonts bitmap-fonts-cjk mkfontscale fontconfig cjkuni-fonts*  中文字体

http://phantomjs.org/
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2

rander.js：
var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

if (system.args.length < 3 || system.args.length > 5) {
    console.log('Usage: rasterize.js URL filename');
    phantom.exit(1);
} else {
    address = system.args[1];
    output = system.args[2];
    page.viewportSize = { width: 1280, height: 1580 };     设定默认大小
    page.open(address, function (status) {
      // 通过在页面上执行脚本获取页面的渲染高度
      var bb = page.evaluate(function () { 
        return document.getElementsByTagName('html')[0].getBoundingClientRect(); 
      });
      // 按照实际页面的高度，设定渲染的宽高
      page.clipRect = {
        top:    bb.top,
        left:   bb.left,
        width:  bb.width,
        height: bb.height
      };
      // 预留一定的渲染时间
      window.setTimeout(function () {
        page.render(output);
        page.close();
        console.log('render ok');
        phantom.exit();
      }, 1000);
    });
}

截图命令 ： 
/usr/local/src/phantomjs-2.1.1-linux-x86_64/bin/phantomjs rander.js 
http://192.168.1.5:9380/DaChuibus/manage/statistics/allstatistics/quanjutongji.do 1.png
```



## doxygen生成代码文档
```
yum install doxygen  graphviz
进入项目目录
cd cuishouv1/
doxygen -g  生成一个模板配置文件
doxygen -s -g  生成一个模板配置文件无注释

修改Doxyfile
PROJECT_NAME           = "cuishou"   项目名称
PROJECT_NUMBER         = "1.0.0"     版本信息
OUTPUT_DIRECTORY       = doc/       输出文件到的目录
INPUT                  = src/java                  代码所在目录，使用空格分割
FILE_PATTERNS          = *.java            指定INPUT的目录中特定文件
RECURSIVE              = YES                  是否递归INPUT中目录
INCLUDE_FILE_PATTERNS  = *.java   指定分析的文件的类型
GENERATE_LATEX         = NO                不产生LaTeX 的文件
HAVE_DOT               = YES                     使用 dot 工具生成更强大的图形


生成文档
doxygen Doxyfile  
```


## dell omsa安装
```
dell服务器使用
http://en.community.dell.com/techcenter/systems-management/w/wiki/1760.openma
nage-server-administrator-omsa#Download_OMSA

http://www.dell.com/support/home/us/en/19/Drivers/DriversDetails?driverId=K37MM
下载后解压
mv OM-SrvAdmin-Dell-Web-LX-8.5.0-2372.RHEL6.x86_64_A00.tar.gz omsa/
tar -zxf OM-SrvAdmin-Dell-Web-LX-8.5.0-2372.RHEL6.x86_64_A00.tar.gz

vim linux/supportscripts/srvadmin-install.sh  centos系统修改，rhel系统不需要
grep -c "Santiago" /etc/redhat-release
修改为 grep -c "CentOS" /etc/redhat-release  

安装依赖：
yum install -y libcmpi CppImpl0 openwsman-server sblim-sfcb sblim-sfcc libwsman1 net-snmp-utils
 openwsman-client libcmpiCppImpl0

./setup.sh 安装 
访问 https://ip:1311  账号为服务器root登陆账号

iptables -I INPUT -p tcp -s 192.168.1.0/24 --dport 1311 -j ACCEPT
```


## boot分区损坏
```
挂载 /boot/
从别的机器复制boot分区

/boot/grub/grub.conf  修改里面的 root分区的  uuid, 别的地方复制的会和本机不一致
查看uuid命令   blkid
并修改 /etc/fstab 文件的uuid，格式化后uuid就会修改

/boot/grub/menu.lst  为软连接，注意修改，确定其他还有没有软连接
menu.lst -> ./grub.conf 

yum install kernel  （可选）


grub-install /dev/sda  （boot 所在分区的磁盘，不是分区）
```


## http head头
```
Requests部分
Header    解释    示例
Accept    指定客户端能够接收的内容类型    Accept: text/plain, text/html
Accept-Charset    浏览器可以接受的字符编码集。    Accept-Charset: iso-8859-5
Accept-Encoding    指定浏览器可以支持的web服务器返回内容压缩编码类型。    Accept-Encoding: compress, gzip
Accept-Language    浏览器可接受的语言    Accept-Language: en,zh
Accept-Ranges    可以请求网页实体的一个或者多个子范围字段    Accept-Ranges: bytes
Authorization    HTTP授权的授权证书    Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
Cache-Control    指定请求和响应遵循的缓存机制    Cache-Control: no-cache
Connection    表示是否需要持久连接。（HTTP 1.1默认进行持久连接）    Connection: close
Cookie    HTTP请求发送时，会把保存在该请求域名下的所有cookie值一起发送给web服务器。    Cookie: $Version=1; Skin=new;
Content-Length    请求的内容长度    Content-Length: 348
Content-Type    请求的与实体对应的MIME信息    Content-Type: application/x-www-form-urlencoded
Date    请求发送的日期和时间    Date: Tue, 15 Nov 2010 08:12:31 GMT
Expect    请求的特定的服务器行为    Expect: 100-continue
From    发出请求的用户的Email    From: user@email.com
Host    指定请求的服务器的域名和端口号    Host: www.zcmhi.com
If-Match    只有请求内容与实体相匹配才有效    If-Match: “737060cd8c284d8af7ad3082f209582d”
If-Modified-Since    如果请求的部分在指定时间之后被修改则请求成功，未被修改则返回304代码   
If-None-Match    如果内容未改变返回304代码，参数为服务器先前发送的Etag，与服务器回应的Etag比较判断是否改变 
If-Range    如果实体未改变，服务器发送客户端丢失的部分，否则发送整个实体。参数也为Etag  
If-Unmodified-Since    只在实体在指定时间之后未被修改才请求成功    If-Unmodified-Since: Sat, 29 Oct 2010 19:43:31 GMT
Max-Forwards    限制信息通过代理和网关传送的时间    Max-Forwards: 10
Pragma    用来包含实现特定的指令    Pragma: no-cache
Proxy-Authorization    连接到代理的授权证书    Proxy-Authorization: Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ==
Range    只请求实体的一部分，指定范围    Range: bytes=500-999
Referer    先前网页的地址，当前请求网页紧随其后,即来路    Referer: http://www.zcmhi.com/archives/71.html
TE    客户端愿意接受的传输编码，并通知服务器接受接受尾加头信息    TE: trailers,deflate;q=0.5
Upgrade    向服务器指定某种传输协议以便服务器进行转换（如果支持）    Upgrade: HTTP/2.0, SHTTP/1.3, IRC/6.9, RTA/x11
User-Agent    User-Agent的内容包含发出请求的用户信息    User-Agent: Mozilla/5.0 (Linux; X11)
Via    通知中间网关或代理服务器地址，通信协议    Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1)
Warning    关于消息实体的警告信息    Warn: 199 Miscellaneous warning
Responses 部分 
Header    解释    示例
Accept-Ranges    表明服务器是否支持指定范围请求及哪种类型的分段请求    Accept-Ranges: bytes
Age    从原始服务器到代理缓存形成的估算时间（以秒计，非负）    Age: 12
Allow    对某网络资源的有效的请求行为，不允许则返回405    Allow: GET, HEAD
Cache-Control    告诉所有的缓存机制是否可以缓存及哪种类型    Cache-Control: no-cache
Content-Encoding    web服务器支持的返回内容压缩编码类型。    Content-Encoding: gzip
Content-Language    响应体的语言    Content-Language: en,zh
Content-Length    响应体的长度    Content-Length: 348
Content-Location    请求资源可替代的备用的另一地址    Content-Location: /index.htm
Content-MD5    返回资源的MD5校验值    Content-MD5: Q2hlY2sgSW50ZWdyaXR5IQ==
Content-Range    在整个返回体中本部分的字节位置    Content-Range: bytes 21010-47021/47022
Content-Type    返回内容的MIME类型    Content-Type: text/html; charset=utf-8
Date    原始服务器消息发出的时间    Date: Tue, 15 Nov 2010 08:12:31 GMT
ETag    请求变量的实体标签的当前值    ETag: “737060cd8c284d8af7ad3082f209582d”
Expires    响应过期的日期和时间    Expires: Thu, 01 Dec 2010 16:00:00 GMT
Last-Modified    请求资源的最后修改时间    Last-Modified: Tue, 15 Nov 2010 12:45:26 GMT
Location    用来重定向接收方到非请求URL的位置来完成请求或标识新的资源    Location: http://www.zcmhi.com/archives/94.html
Pragma    包括实现特定的指令，它可应用到响应链上的任何接收方    Pragma: no-cache
Proxy-Authenticate    它指出认证方案和可应用到代理的该URL上的参数    Proxy-Authenticate: Basic
refresh    应用于重定向或一个新的资源被创造，在5秒之后重定向（由网景提出，被大部分浏览器支持）    
Refresh: 5; url=
http://www.zcmhi.com/archives/94.html
Retry-After    如果实体暂时不可取，通知客户端在指定时间之后再次尝试    Retry-After: 120
Server    web服务器软件名称    Server: Apache/1.3.27 (Unix) (Red-Hat/Linux)
Set-Cookie    设置Http Cookie    Set-Cookie: UserID=JohnDoe; Max-Age=3600; Version=1
Trailer    指出头域在分块传输编码的尾部存在    Trailer: Max-Forwards
Transfer-Encoding    文件传输编码    Transfer-Encoding:chunked
Vary    告诉下游代理是使用缓存响应还是从原始服务器请求    Vary: *
Via    告知代理客户端响应是通过哪里发送的    Via: 1.0 fred, 1.1 nowhere.com (Apache/1.1)
Warning    警告实体可能存在的问题    Warning: 199 Miscellaneous warning
WWW-Authenticate    表明客户端请求实体应该使用的授权方案    WWW-Authenticate: Basic
```



## 命令历史记录
    1、vim /etc/bashrc
    export HISTORY_FILE=/var/log/`whoami`_`date '+%y-%m-%d'`.log
    readonly PROMPT_COMMAND='{ date "+%y-%m-%d %T ### $(who am i |awk "{print $1" "$2" "$5}") ### 
    $(history 1 | { read x cmd; echo "$cmd"; })"; } >> $HISTORY_FILE'
    或者
    export HISTORY_FILE=/var/log/`whoami`_`date '+%y-%m-%d'`.log
    readonly PROMPT_COMMAND='{ msg=$(history 1 | { read x y; echo $y; }); echo $(who am i):[`pwd`]"$msg"; } >> 
    $HISTORY_FILE'


    2、vim /etc/profile
    export HISTTIMEFORMAT="%F %T `whoami` "

    1和2一起用格式会重复



## 监测系统
```
awk -F: '$3==0 {print $1}' /etc/passwd（查看是否存在特权用户）
awk -F: 'length($2)==0 {print $1}' /etc/shadow（查看是否存在空口令帐户）
lsof -p pid（察看该进程所打开端口和文件）
top ps等一起用，有时只用一个会不准
cat /etc/crontab
ls /etc/cron.*
cat /etc/rc.d/rc.local

yum install rkhunter -y
rkhunter -c   检测系统

1. MD5校验测试, 检测任何文件是否改动.
2. 检测rootkits使用的二进制和系统工具文件.
3. 检测特洛伊木马程序的特征码.
4. 检测大多常用程序的文件异常属性.
5. 执行一些系统相关的测试 - 因为rootkit hunter可支持多个系统平台.
6. 扫描任何混杂模式下的接口和后门程序常用的端口.
7. 检测如/etc/rc.d/目录下的所有配置文件, 日志文件, 任何异常的隐藏文件等等. 例如, 在检测/dev/.udev和/etc/.pwd.lock文件时候, 
我的系统被警告.
8. 对一些使用常用端口的应用程序进行版本测试. 如: Apache Web Server, Procmail等.

    完成上面检测后, 你的屏幕会显示扫描结果: 可能被感染的文件, 不正确的MD5校验文件和已被感染的应用程序.


    rkhunter是通过一个含有rootkit名字的数据库来检测系统的rootkits漏洞, 所以经常更新该数据库非常重要, 你可以通过下面命令来
    更新该数据库:

# rkhunter --update

当然最好是通过cron job定期执行上面的命令, 你需要用root用户添加下面命令到crontab文件:

59 23 1 * * echo “Rkhunter update check in progress”;/usr/local/bin/rkhunter --update
```



## core dump
    在Linux下产生并调试core文件 先看看我用的是个什么机器：

    $ uname -a
    Linux dev 2.4.21-9.30AXsmp #1 SMP Wed May 26 23:37:09 EDT 2004 i686 i686 i386 GNU/Linux

    再看看默认的一些参数，注意core file size是个0，程序出错时不会产生core文件了。


    $ ulimit -a
    core file size (blocks, -c) 0
    data seg size (kbytes, -d) unlimited
    file size (blocks, -f) unlimited
    max locked memory (kbytes, -l) 4
    max memory size (kbytes, -m) unlimited
    open files (-n) 2048
    pipe size (512 bytes, -p) 8
    stack size (kbytes, -s) 10240
    cpu time (seconds, -t) unlimited
    max user processes (-u) 7168
    virtual memory (kbytes, -v) unlimited

    写个简单的程序，看看core文件是不是会被产生。

    $ more foo.c

    #include

    static void sub(void);

    int main(void)
    {
    sub();
    return 0;
    }

    static void sub(void)
    {
    int *p = NULL;

    /* derefernce a null pointer, expect core dump. */
    printf("%d", *p);
    }

    $ gcc -Wall -g foo.c
    $ ./a.out
    Segmentation fault

    $ ls -l core.*
    ls: core.*: No such file or directory

    没有找到core文件，我们改改ulimit的设置，让它产生。1024是随便取的

    $ ulimit -c 655355

    $ ulimit -a
    core file size (blocks, -c) 1024
    data seg size (kbytes, -d) unlimited
    file size (blocks, -f) unlimited
    max locked memory (kbytes, -l) 4
    max memory size (kbytes, -m) unlimited
    open files (-n) 2048
    pipe size (512 bytes, -p) 8
    stack size (kbytes, -s) 10240
    cpu time (seconds, -t) unlimited
    max user processes (-u) 7168
    virtual memory (kbytes, -v) unlimited

    $ ./a.out
    Segmentation fault (core dumped)
    $ ls -l core.*
    -rw------- 1 uniware uniware 53248 Jun 30 17:10 core.9128

    注意看上述的输出信息，多了个(core dumped)。确实产生了一个core文件，9128是该进程的PID。我们用GDB来看看这个core。

    $ gdb --core=core.9128
    GNU gdb Asianux (6.0post-0.20040223.17.1AX)
    Copyright 2004 Free Software Foundation, Inc.
    GDB is free software, covered by the GNU General Public License, and you are
    welcome to change it and/or distribute copies of it under certain conditions.
    Type "show copying" to see the conditions.
    There is absolutely no warranty for GDB. Type "show warranty" for details.
    This GDB was configured as "i386-asianux-linux-gnu".
    Core was generated by `./a.out'.
    Program terminated with signal 11, Segmentation fault.
    #0 0x08048373 in ?? ()
    (gdb) bt
    #0 0x08048373 in ?? ()
    #1 0xbfffd8f8 in ?? ()
    #2 0x0804839e in ?? ()
    #3 0xb74cc6b3 in ?? ()
    #4 0x00000000 in ?? ()

    此时用bt看不到backtrace，也就是调用堆栈，原来GDB还不知道符号信息在哪里。我们告诉它一下：

    (gdb) file ./a.out
    Reading symbols from ./a.out...done.
    Using host libthread_db library "/lib/tls/libthread_db.so.1".
    (gdb) bt
    #0 0x08048373 in sub () at foo.c:17
    #1 0x08048359 in main () at foo.c:8

    此时backtrace出来了。

    (gdb) l
    8 sub();
    9 return 0;
    10 }
    11
    12 static void sub(void)
    13 {
    14 int *p = NULL;
    15
    16 /* derefernce a null pointer, expect core dump. */
    17 printf("%d", *p);
    (gdb)

    在程序不寻常退出时，内核会在当前工作目录下生成一个core文件（是一个内存映像，同时加上调试信息）。使用gdb来查看core文件，
    可以指示出导致程序出错的代码所在文件和行数。

    1.core文件的生成开关和大小限制
    ---------------------------------
    1）使用ulimit -c命令可查看core文件的生成开关。若结果为0，则表示关闭了此功能，不会生成core文件。
    2）使用ulimit -c filesize命令，可以限制core文件的大小（filesize的单位为kbyte）。若ulimit -c unlimited，则表示
    core文件的大小不受限制。如果生成的信息超过此大小，将会被裁剪，最终生成一个不完整的core文件。在调试此core文件的时候，gdb会提示错误。

    2.core文件的名称和生成路径
    ----------------------------
    core文件生成路径:
    输入可执行文件运行命令的同一路径下。
    若系统生成的core文件不带其他任何扩展名称，则全部命名为core。新的core文件生成将覆盖原来的core文件。

    1）/proc/sys/kernel/core_uses_pid可以控制core文件的文件名中是否添加pid作为扩展。文件内容为1，表示添加pid作为扩展名，
    生成的core文件格式为core.xxxx；为0则表示生成的core文件同一命名为core。
    可通过以下命令修改此文件：
    echo "1" > /proc/sys/kernel/core_uses_pid

    2）proc/sys/kernel/core_pattern可以控制core文件保存位置和文件名格式。
    可通过以下命令修改此文件：
    echo "/corefile/core-%e-%p-%t" > core_pattern，可以将core文件统一生成到/corefile目录下，产生的文件名为core-命令名-pid-时间戳
    以下是参数列表:
    %p - insert pid into filename 添加pid
    %u - insert current uid into filename 添加当前uid
    %g - insert current gid into filename 添加当前gid
    %s - insert signal that caused the coredump into the filename 添加导致产生core的信号
    %t - insert UNIX time that the coredump occurred into filename 添加core文件生成时的unix时间
    %h - insert hostname where the coredump happened into filename 添加主机名
    %e - insert coredumping executable name into filename 添加命令名

    3.core文件的查看
    -----------------
    core文件需要使用gdb来查看。
    gdb ./a.out
    core-file core.xxxx
    使用bt命令即可看到程序出错的地方。
    以下两种命令方式具有相同的效果，但是在有些环境下不生效，所以推荐使用上面的命令。
    1）gdb -core=core.xxxx
    file ./a.out
    bt
    2）gdb -c core.xxxx
    file ./a.out
    bt

    4.开发板上使用core文件调试
    -----------------------------
    如果开发板的操作系统也是linux，core调试方法依然适用。如果开发板上不支持gdb，可将开发板的环境（依赖库）、可执行文件和core
    文件拷贝到PC的linux下。
    在 PC上调试开发板上产生的core文件，需要使用交叉编译器自带的gdb，并且需要在gdb中指定solib-absolute-prefix和 
    solib-search-path两个变量以保证gdb能够找到可执行程序的依赖库路径。有一种建立配置文件的方法，不需要每次启动gdb都配置以上变量，
    即：在待运行gdb的路径下建立.gdbinit。
    配置文件内容：
    set solib-absolute-prefix YOUR_CROSS_COMPILE_PATH
    set solib-search-path YOUR_CROSS_COMPILE_PATH
    set solib-search-path YOUR_DEVELOPER_TOOLS_LIB_PATH
    handle SIG32 nostop noprint pass


## idrac管理
```
wget -q -O - http://linux.dell.com/repo/hardware/latest/bootstrap.cgi | bash
yum -y install srvadmin-idrac7

racadm closessn -a 关闭所有session
racadm racreset    重启idrac

1、RHEL 系统环境iDRAC 命令工具包：

Dell EMC OpenManage Linux Remote Access Utilities :
http://www.dell.com/support/home/cn/zh/cndhs1/drivers/driversdetails?driverId=49T1M
下载后，需解决net-snmp-utils包的依赖关系在执行此目录下的rpm包安装/root/linux/rac/RHEL7/x86_64，然后软链接
物理机环境的安装和虚拟机环境安装区别：
物理机环境：安装在物理机环境后，可直接 # racadm command查看和修改iDRAC配置
虚拟机环境：安装在虚拟机环境后，需 -r IP #racadm -r 192.168.1.1 -u User -p 'Password' command 查看和修改iDRAC配置
2、iDRAC 命令手册：

http://topics-cdn.dell.com/pdf/idrac7-8-lifecycle-controller-v2.50.50.50_reference-guide_en-us.pdf
3、iDRAC 常用命令

创建、删除、赋权用户的操作
# racadm config -g cfgUserAdmin -o cfgUserAdminUserName -i 10 User01           创建索引10的用户User01
# racadm config -g cfgUserAdmin -o cfgUserAdminPassword -i 10 'Password'      给创建的用户设置密码
# racadm set iDRAC.Users.10.Password 'NewPassword'                                         更改用户密码
# racadm config -g cfgUserAdmin -i 10 -o cfgUserAdminEnable 1                           启用用户<1表示启用，0表示禁用>
# racadm config -g cfgUserAdmin -o cfgUserAdminUserName -i 10                        删除用户
# racadm config -g cfgUserAdmin -o cfgUserAdminPrivilege -i 10 4                         赋予User01用户超级管理员权限
物理机重启、关机等操作
# racadm serveraction powerup                                               开启服务器
# racadm serveraction powerdown                                          关闭服务器
# racadm serveraction powercycle                                           关机后再开启服务器
# racadm serveraction powerstatus                                         查看服务器状态
iDRAC 重启操作
# racadm racreset soft                                                             软重启iDRAC
# racadm racreset hard                                                            硬重启iDRAC
# racadm racreset soft -f                                                          强制软重启iDRAC
# racadm racreset hard -f                                                         强制硬重启iDRAC
# racadm set iDRAC.IPv4.Address x.x.x.x                              修改IP地址
# racadm set iDRAC.IPv4.Netmask x.x.x.x                             修改子网掩码
# racadm set iDRAC.IPv4.Gateway x.x.x.x                             修改默认网关<无需重启idrac，配置即生效>
```



## idrac ssh
```
ssh idrac的IP 进入ssh模式
/admin1-> racadm  config...  可以使用racadm命令

修改网关
racadm config -g cfgLanNetworking -o cfgNicGateway 192.168.63.155



% Get all iDRAC settings in a file

racadm get -f config.txt

If you like you can change the contents of config.txt and apply it back to iDRAC
racadm set -f config.txt

% Set password for root user
racadm set iDRAC.Users.2.Password PASSWORD"

% List all ssh keys for root user
racadm sshpkauth -i 2 -v -k all

% Add ssh key to root user
racadm sshpkauth -i 2 -k 1 "CONTENTS OF PUBLIC KEY"

% Delete ssh key for root user
racadm sshpkauth -i 2 -d -k 1

% Get iDRAC IP config

racadm getniccfg
racadm get iDRAC.NIC

% set iDRAC IP

Using config command:
racadm config -g cfgLanNetworking -o cfgNicEnable 1
racadm config -g cfgLanNetworking -o cfgNicIpAddress x.x.x.x
racadm config -g cfgLanNetworking -o cfgNicNetmask 255.255.255.0
racadm config -g cfgLanNetworking -o cfgNicGateway x.x.x.x
racadm config -g cfgLanNetworking -o cfgNicUseDHCP 0
racadm config -g cfgLanNetworking -o cfgDNSServersFromDHCP 0
racadm config -g cfgLanNetworking -o cfgDNSServer1 y.y.y.y
racadm config -g cfgLanNetworking -o cfgDNSServer2 y.y.y.y
• Using set command:
racadm set iDRAC.Nic.Enable 1
racadm set iDRAC.IPv4.Address x.x.x.x
racadm set iDRAC.IPv4.Netmask 255.255.255.0
racadm set iDRAC.IPv4.Gateway x.x.x.x
racadm set iDRAC.IPv4.DHCPEnable 0
racadm set iDRAC.IPv4.DNSFromDHCP 0
racadm set iDRAC.IPv4.DNS1 y.y.y.y
racadm set iDRAC.IPv4.DNS2 y.y.y.y

% Set iDRAC DNS Name
racadm set iDRAC.NIC.DNSRacName iDRACNAME

% Set iDRAC domain name
racadm set iDRAC.NIC.DNSDomainName DOMAIN.NAME

% Set iDRAC DNS Server

racadm config -g cfgLanNetworking -o cfgDNSServer1 x.x.x.x
racadm config -g cfgLanNetworking -o cfgDNSServer2 y.y.y.y

% Set Front LCD to hostname
racadm set System.LCD.Configuration 16

% Reset iDRAC to factory defaults
racadm racresetcfg

% Reset/Reboot iDRAC

racadm racreset OPTIONS

Options : soft, hard, cold
or
racadm serveraction powercycle

% Get Serial number (service tag)
racadm getsvctag

% Get current system information
racadm getsysinfo

% Configure one-time-boot to PXE

racadm set BIOS.OneTimeBoot.OneTimeBootMode OneTimeBootSeq
racadm set BIOS.OneTimeBoot.OneTimeBootSeqDev NIC.Integrated.1-1-1

% Configure persistent Boot Device

racadm config -g cfgServerInfo -o cfgServerBootOnce 0
racadm config -g cfgServerInfo -i cfgServerFirstBootDevice HDD

% Check boot order list
racadm get BIOS.BiosBootSettings.bootseq

% Disable HyperThreading
racadm set BIOS.ProcSettings.LogicalProc Disabled

% Disable OS to iDRAC pass-thru for iDRAC service module (automatically create a pseudo NIC in OS)
racadm set iDRAC.OS-BMC.AdminState Disabled

% Change SNMP public community string
racadm set iDRAC.SNMP.AgentCommunity NEW STRING

% Disable ASR
racadm config -g cfgRacTuning -o cfgRacTuneAsrEnable 0

% Configure Serial redirection

racadm config -g cfgSerial -o cfgSerialConsoleEnable 1
racadm config -g cfgSerial -o cfgSerialBaudRate 115200
racadm config -g cfgSerial -o cfgSerialCom2RedirEnable 1
racadm config -g cfgSerial -o cfgSerialTelnetEnable 0
racadm config -g cfgSerial -o cfgSerialSshEnable 1

to access console via ssh console com2

% Disable Serial On Lan
racadm config -g cfgImpiSol -o cfgIpmiSolEnable 0

% Change Power Profile
racadm set BIOS.SysProfileSettings PerfPerWattOptimizedOs

% Set AC Power Recovery

racadm set BIOS.SysSecurity.AcPwdRcvry Last
racadm set BIOS.SysSecurity.AcPwdRcvryDelay Immediate

% Get RAID physical Disk information

racadm raid get pdisks
racadm raid get pdisks -o (all information)
racadm raid get pdisks -o -p state,size (specific information)

% Get RAID Virtual Disk Information
Racadm raid get vdisks
```

## dns解析慢
```
添加超时
cat /etc/resolv.conf
nameserver 223.5.5.5
options timeout:1 attempts:1
```

## centos网卡休眠
```
修改启动引导参数
vim /etc/grub.conf
quiet    后面添加    pcie_aspm=off
重启后
[root@localhost ~]# dmesg | grep PCIe
[    0.000000] PCIe ASPM is disabled

关闭tuned
systemctl stop tuned
systemctl disable tuned

配置 xorg.conf，且不能出错，否则系统可能会起不来，所以配置时要格外小心。
vi /etc/X11/xorg.conf
       添加以下内容
Section "ServerFlags"
       Option "BlankTime" "0"
       Option "StandbyTime" "0"
       Option "SuspendTime" "0"
       Option "OffTime" "0"
EndSection
Section "Monitor"
       Option "DPMS" "false"
EndSection
重启CentOS系统即可！

```





## kernel panic自动重启
```
编辑 /etc/sysctl.conf 文件，并定义遇到 kernel panic 20秒后自动重启 Linux：
# vi /etc/sysctl.conf
kernel.panic = 20
```



## 安装src.rpm
```
yum install rpm-build
rpm -ivh     --xxx--.src.rpm
cd /usr/src/redhat/SPECS
rpmbuild -bb xxx.spec
cd /usr/src/redhat/RPMS/i386/
rpm -ivh xxxx.rpm
```


## ab测试
```
yum install gcc apr-devel apr-util-devel pcre-devel
wget https://mirrors.aliyun.com/apache/httpd/httpd-2.2.32.tar.gz

解压源码http，修改support/ab.c 1395行左右
             } else {
1395                 //apr_err("apr_socket_recv", status);
1396                 bad++;
1397                 close_connection(c);
1398                 return;
1399             }
1400         }

./configure --prefix=/usr/local/apache
make 

make完成后ab在边缘目录下：
./support/ab （或者 make install）

/usr/local/apache/bin/ab -n 10000 -c 1000 http://www.baidu.com/



Server Software:        web服务器软件及版本
Server Hostname:        请求的地址
Server Port:            请求的端口

Document Path:          请求的页面路径
Document Length:        页面大小

Concurrency Level:      并发数
Time taken for tests:   测试总共花费的时间
Complete requests:      完成的请求数
Failed requests:        失败的请求数
Write errors:           写入错误
Total transferred:      总共传输字节数，包含http的头信息等
HTML transferred:       html字节数，实际的页面传递字节数
Requests per second:    每秒处理的请求数，服务器的吞吐量（重要）
Time per request:       平均数，用户平均请求等待时间
Time per request:       服务器平均处理时间
Transfer rate:          平均传输速率（每秒收到的速率）

测试时出现的Failed requests原因分析：
Failed requests: 2303
(Connect: 0, Length: 2303, Exceptions: 0)
只要出现Failed requests就会多一行数据来统计失败的原因，分别有Connect、Length、Exceptions。
Connect 无法送出要求、目标主机连接失败、要求的过程中被中断。
Length 响应的内容长度不一致 ( 以 Content-Length 头值为判断依据 )。
Exception 发生无法预期的错误。
```


## 网卡bond
```
cat ifcfg-eth0 
DEVICE="eth0"
BOOTPROTO=none
ONBOOT="yes"
TYPE=Ethernet
MASTER=bond1
SLAVE=yes

cat ifcfg-eth1
DEVICE="eth1"
BOOTPROTO=none
ONBOOT="yes"
TYPE=Ethernet
MASTER=bond1
SLAVE=yes

cat ifcfg-bond1 
DEVICE=bond1
NAME=bond1
BOOTPROTO=none
ONBOOT=yes
IPADDR=10.21.20.210
NETMASK=255.255.255.0
GATEWAY=10.21.20.1
TYPE=Bond
BONDING_MASTER=yes
BONDING_OPTS="mode=1 miimon=100"

删除bond网卡：
1、# ls /sys/class/net
bond0  bond1  bonding_masters  br0  eth0  eth1  lo
注意：直接删除bond0目录会提示权限问题
2、# cat bonding_masters
bond0  bond1
注意：直接编辑此文件也会提示权限问题
方法如下：
# echo -bond0 > bonding_masters
备注：echo后的 - 号表示删除设备， + 号表示添加设备
```



## snoopy命令记录
```
https://github.com/a2o/snoopy

yum install gcc socat

wget http://source.a2o.si/download/snoopy/snoopy-2.4.6.tar.gz

tar -zxf snoopy-2.4.6.tar.gz

cd snoopy-2.4.6

./configure

make

make install

make enable

--

vim /usr/local/etc/snoopy.ini(#不是注释)

[snoopy]

message_format = "%{datetime} %{hostname} %{pid} %{eusername} %{tty_username} %{tty} %{cwd} %{filename} # %{cmdline}"

filter_chain = "exclude_spawns_of:cron"

output = file:/var/log/.snoopy.log

--

/usr/local/sbin/snoopy-disable  关闭snoopy

/usr/local/sbin/snoopy-enable   开启snoopy

重新登陆后即可记录操作日志

/var/log/.snoopy.log  进行logstash grok匹配

SNOOPYLOG %{TIMESTAMP_ISO8601:datetime} %{USERNAME:hostname} %{INT:pid} %{USER:eusername} %{USER:tty_username} %{NOTSPACE:tty} %{UNIXPATH:pwd} %{UNIXPATH:cmd_name} # %{GREEDYDATA:cmdline}
```

## 连接跟踪表
```
LVS 或 Cache在请求频繁的情况下，可能会导致系统丢包，不能正常提供服务。并且在/var/log/messages会有如下报警

nf_conntrack: table full, dropping packet.

解决方法： 关闭防火墙

# chkconfig iptables off

# chkconfig ip6tables off

# service iptables stop

# service ip6tables stop

在防火墙关闭状态下，不要通过iptables指令（比如 iptables -nL）来查看当前状态！因为这样会导致防火墙被启动，而且规则为空。虽然不会有任何拦截效果，但所有连接状态都会被记录，浪费资源且影响性能并可能导致防火墙主动丢包！

移除相关模块

# lsmod |grep nf


nf_nat                 22759  0 

nf_conntrack_ipv4       9506  2 nf_nat

nf_conntrack           79645  2 nf_nat,nf_conntrack_ipv4

nf_defrag_ipv4          1483  1 nf_conntrack_ipv4


# rmmod nf_nat

# rmmod nf_conntrack_ipv4

# rmmod nf_conntrack

之后重启系统
```


## centos系统升级
```
Centos6.6升级到Centos7.2： 新版的7.4不支持直接升级
如想使用最新的7.x系统，可以在升级7.2完成后使用update升级

从Centos6.9更新到7.2会出现一些问题
例如ssh yum 无法正常使用所以，再重启之前，先做好准备,升级完成后清理掉

vi start.sh #在root目录创建start.sh文件
#!/bin/bash
ln -s /usr/lib64/libsasl2.so.3.0.0 /usr/lib64/libsasl2.so.2
ln -s /usr/lib64/libpcre.so.1.2.0 /usr/lib64/libpcre.so.0
service sshd restart

#执行以下命令
chmod +x start.sh
chmod +x /etc/rc.d/rc.local
cp /etc/rc.d/rc.local /etc/rc.d/rc.local.bak #创建备份
echo 'bash /root/start.sh' >>/etc/rc.d/rc.local #添加脚本为开机自启动


step 1：

cat /etc/yum.repos.d/upgrade.repo
[upgrade]
name=upgrade
baseurl=http://dev.centos.org/centos/6/upg/x86_64/
enable=1
gpgcheck=0

step 2：

yum erase openscap

yum install http://dev.centos.org/centos/6/upg/x86_64/Packages/openscap-1.0.8-1.0.1.el6.centos.x86_64.rpm

yum install openscap-1.0.8

[root@localhost ~]# yum install preupgrade-assistant-contents redhat-upgrade-tool preupgrade-assistant

step 3:

[root@localhost ~]# preupg

step 4：

[root@localhost ~]# rpm --import http://vault.centos.org/centos/7.2.1511/os/x86_64/RPM-GPG-KEY-CentOS-7

[root@localhost ~]# redhat-upgrade-tool --network 7 --instrepo http://vault.centos.org/centos/7.2.1511/os/x86_64/

(265/266): zlib-1.2.7-13.el7.x86_64.rpm                                                                       |  89 kB     00:00

(266/266): zlib-devel-1.2.7-13.el7.x86_64.rpm                                                             |  49 kB     00:00

testing upgrade transaction rpm transaction 100%

[===========================================] rpm install 100%

[===========================================] setting up system for upgrade Finished. Reboot to start upgrade.

升级完成后卸载el6的rpm包
```


## web管理系统
```
1、webmin
http://www.webmin.com/rpm.html

wget http://prdownloads.sourceforge.net/webadmin/webmin-1.881-1.noarch.rpm
yum -y install perl perl-Net-SSLeay openssl perl-IO-Tty perl-Encode-Detect
rpm -U webmin-1.881-1.noarch.rpm

https://ip:10000/  登陆账号和系统一致


2、redhat的一个项目
https://cockpit-project.org

yum install cockpit-ws cockpit-system cockpit-bridge
# cockpit-docker docker管理，需要安装docker
systemctl restart cockpit
systemctl enable cockpit


vim /etc/cockpit/cockpit.conf  新增文件
[Log]
Fatal = criticals

[WebService]
AllowUnencrypted=true
UrlRoot=/co/

vim /usr/lib/systemd/system/cockpit.socket
ListenStream=127.0.0.1:9090 监听本地

systemctl daemon-reload
systemctl restart cockpit.socket


nginx代理

map $http_upgrade $connection_upgrade {
default upgrade;
'' close;
}

upstream websocket {
server 127.0.0.1:9090;
}

server {
       listen         80;
       server_name    cockpit.domain.tld www.cockpit.domain.tld;
       return         301 https://$server_name$request_uri;
}

server {
    listen 443;
    server_name www.cockpit.domain.tld cockpit.domain.tld;

        ssl on;
        ssl_certificate /path/to/certificate;
        ssl_certificate_key /path/to/key;

    location /co/ {  # 对应cockpit.conf的uri
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        # needed for websocket
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
        # change scheme of "Origin" to http
        proxy_set_header Origin http://$host;

        # Pass ETag header from cockpit to clients.
        # See: https://github.com/cockpit-project/cockpit/issues/5239
        # gzip off;
    }
}
```


## crontab注意点
    今天遇见一个问题，crontab的定时任务不能自动执行，但是手动执行脚本一直能成功。查到最后，发现是脚本里用了系统的环境变量。下面开始解释：
    1.crontab与环境变量
    不要假定cron知道所需要的特殊环境，它其实并不知道。所以你要保证在shelll脚本中提供所有必要的路径和环境变量，除了一些自动
    设置的全局变量。所以注意如下3点：
    1）脚本中涉及文件路径时写全局路径；
    2）脚本执行要用到java或其他环境变量时，通过source命令引入环境变量，如：
    cat start_cbp.sh
    #!/bin/sh
    source /etc/profile
    export RUN_CONF=/home/d139/conf/platform/cbp/cbp_jboss.conf
    /usr/local/jboss-4.0.5/bin/run.sh -c mev &
    3）当手动执行脚本OK，但是crontab死活不执行时。这时必须大胆怀疑是环境变量惹的祸，并可以尝试在crontab中直接引入环境变量解决问题。如：
    0 * * * * . /etc/profile;/bin/sh /var/www/java/audit_no_count/bin/restart_audit.sh
    2.其他应该注意的问题
    1）新创建的cron job，不会马上执行，至少要过2分钟才执行。如果重启cron则马上执行。
    2）每条 JOB 执行完毕之后，系统会自动将输出发送邮件给当前系统用户。日积月累，非常的多，甚至会撑爆整个系统。所以每条 JOB 命令
    后面进行重定向处理是非常必要的： >/dev/null 2>&1 。前提是对 Job 中的命令需要正常输出已经作了一定的处理, 比如追加到某个特定日志文件。
    3）当crontab突然失效时，可以尝试/etc/init.d/crond restart解决问题。或者查看日志看某个job有没有执行/报错tail -f /var/log/cron。
    4）千万别乱运行crontab -r。它从Crontab目录（/var/spool/cron）中删除用户的Crontab文件。删除了该用户的所有crontab都没了。
    5）在crontab中%是有特殊含义的，表示换行的意思。如果要用的话必须进行转义%，如经常用的date ‘+%Y%m%d’在crontab里是不会执行的，
    应该换成date ‘+%Y%m%d’`。

    3.crontab中的输出配置
    crontab中经常配置运行脚本输出为：>/dev/null 2>&1，来避免crontab运行中有内容输出。
    shell命令的结果可以通过‘> ’的形式来定义输出
    /dev/null 代表空设备文件　　
    > 代表重定向到哪里，例如：echo "123" > /home/123.txt　
    1 表示stdout标准输出，系统默认值是1，所以">/dev/null"等同于"1>/dev/null"
    2 表示stderr标准错误
    　 & 表示等同于的意思，2>&1，表示2的输出重定向等同于1　
    那么重定向输出语句的含义：
    1>/dev/null 首先表示标准输出重定向到空设备文件，也就是不输出任何信息到终端，不显示任何信息。
    2>&1 表示标准错误输出重定向等同于标准输出，因为之前标准输出已经重定向到了空设备文件，所以标准错误输出也重定向到空设备文件。

## centos改网卡名
```
centos6

新增文件
cat /etc/modprobe.conf 
alias em2 bond0

mv ifcfg-em2 ifcfg-bond0  还有配置里面的名字，之后重启


centos7

/etc/udev/rules.d/70-persistent-net.rules
```

## 查询service tag
```
linux: dmidecode -s system-serial-number


windows:
打开cmd界面，输入：wmic 
再输入：bios  get  serialnumber即可看到
```