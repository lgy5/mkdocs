## apache反向代理
```
<VirtualHost *:80>
    ServerAdmin yunwei@3mang.com
    ServerName log.3mang.com
    ProxyRequests Off
    ProxyPreserveHost On
    <Proxy *>
        AuthType Basic
        allowoverride AuthConfig
        order allow,deny
        allow from all
        AuthName "admin"
        AuthUserFile /etc/httpd/.htpassword
        require valid-user
    </Proxy>
    ProxyPass /solr http://127.0.0.1:8983/solr
    ProxyPass /solr/admin/cores http://127.0.0.1:8983/solr/admin/cores
    ProxyPassReverse /solr http://127.0.0.1:8983/solr
</VirtualHost>
```



## 代理跨域问题
```

http://www.jianshu.com/p/699f158b218b

apache的配置
mod_proxy 支持转发代理和反向代理，所以配置反向代理时首先需要关闭转发代理，关闭方式见下面
配置示例备注
# Put this after the other LoadModule directives
LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so

# Put this in the main section of your configuration (or desired virtual host, if using 
# Apache virtual hosts)
# 关闭转发代理
ProxyRequests Off
# 指定使用原始Http header的Host属性，在后端服务需要知道原始Host属性
# 时会很有用，默认是关闭的
ProxyPreserveHost On
Header add Access-Control-Allow-Origin *
Header add Access-Control-Allow-Methods "GET, POST, OPTIONS"
Header add Access-Control-Allow-Headers "Content-Type"
# 对被代理资源的指令说明
<Proxy *>
    # Order说明deny 和 allow的执行顺序
    # 一般这个指令可以解释为默认应用xx规则除了yy规则之外
    # xx和yy规则在Order下方指定
    Order deny,allow
    Allow from all
</Proxy>

# 激活针对特定地址的反向代理
ProxyPass /confluence http://app-server.internal.example.com:8090/confluence
# 这个指令会调整HTTP redirect response Header中的 Location, Content-Location 和 URI
 属性中的URL到代理服务器地址
# 作为反向代理服务时强烈建议开启这个选项，避免透传请求到后端服务
ProxyPassReverse /confluence http://app-server.internal.example.com:8090/confluence
# 对新的url权限进行说明
<Location /confluence>
    Order allow,deny
    Allow from all
</Location>
tomcat的配置

tomcat中的配置左右主要是告诉tomcat redirect或者forward的时候使用代理地址，而不是上一节点
所请求的实际服务器地址，具体配置如下

<Connector port="9080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="9443"
    proxyName="sample.com" proxyPort="80"/>
上面配置中的proxyName和proxyPort就是告诉tomcat代理服务器的地址和端口。在servlet中可以通过
下面的代码获得这两个参数的值

request.getServerName();
request.getSreverPort();
```



## option指令
```
Options指令是Apache配置文件中一个比较常见也比较重要的指令，Options指令可以在Apache服务器
核心配置(server config)、
虚拟主机配置(virtual host)、特定目录配置(directory)以及.htaccess文件中使用。Options指令
的主要作用是控制特定目录将
启用哪些服务器特性。

Options指令常见的配置示例代码如下：

<Directory />
#指定根目录"/"启用Indexes、FollowSymLinks两种特性。
    Options Indexes FollowSymLinks
    AllowOverride all
    Order allow,deny
    Allow from all
</Directory>
Options指令的完整语法为：Options [+|-]option [[+|-]option] ...。简而言之，Options指令
后可以附加指定多种服务器特性，
特性选项之间以空格分隔。下面我们来看看Options指令后可以附加的特性选项的具体作用及含义
(Apache配置中的内容均不区分大小写)：

All
表示除MultiViews之外的所有特性。这也是Options指令的默认设置。
None
表示不启用任何的服务器特性。
FollowSymLinks
服务器允许在此目录中使用符号连接。如果该配置选项位于<Location>配置段中，将会被忽略。
Indexes
如果输入的网址对应服务器上的一个文件目录，而此目录中又没有DirectoryIndex指令(例如：
DirectoryIndex index.html index.php)，
那么服务器会返回由mod_autoindex模块生成的一个格式化后的目录列表，并列出该目录下的
所有文件(如下图)。
Options Indexes指令作用效果

MultiViews
允许使用mod_negotiation模块提供内容协商的"多重视图"。简而言之，如果客户端请求的路径
可能对应多种类型的文件，那么服务器将根据
客户端请求的具体情况自动选择一个最匹配客户端要求的文件。例如，在服务器站点的file文件
夹下中存在名为hello.jpg和hello.html的
两个文件，此时用户输入Http://localhost/file/hello，如果在file文件夹下并没有hello子
目录，那么服务器将会尝试在file文件夹下
查找形如hello.*的文件，然后根据用户请求的具体情况返回最匹配要求的hello.jpg或者hello.html。
SymLinksIfOwnerMatch
服务器仅在符号连接与目标文件或目录的所有者具有相同的用户ID时才使用它。简而言之，只有当
符号连接和符号连接指向的目标文件或目录的所有者是同一用户时，才会使用符号连接。如果该配置
选项位于<Location>配置段中，将会被忽略。
ExecCGI
允许使用mod_cgi模块执行CGI脚本。
Includes
允许使用mod_include模块提供的服务器端包含功能。
IncludesNOEXEC
允许服务器端包含，但禁用"#exec cmd"和"#exec cgi"。但仍可以从ScriptAlias目录使用
"#include virtual"虚拟CGI脚本。
```



## apache用户认证
```
alias /phpredis "/var/www/html/phpredis"
<Directory /var/www/html/phpredis>
    Options Indexes MultiViews
    AuthType basic
    AuthName "welcome test"
    AuthUserFile /etc/httpd/.htpasswd
    require valid-user = user test  #如有其它用户以此 列在 test 之后
</Directory>

htpasswd -c /etc/httpd/.htpasswd 用户名
#第一次创建用户要用到-c 参数 第2次添加用户，就不用-c参数
htpasswd -m .htpasswd 用户名 更改密码
htpasswd -D .htpasswd 用户名 删除用户
重启apache

==================================
通过用户组方式访问
alias /test01 "/data/web/test01/"
<Directory /data/web/test01>
　　Options Indexes MultiViews
　　AuthType basic
　　AuthName "welcome test"
　　AuthUserFile /etc/httpd/httppwd
　　AuthGroupFile /etc/httpd/httpgrp #用户组文件路径
　　require group admin #admin 是用户组
</Directory>
 
创建用户组配置文件

vi /etc/httpd/httpgrp  #创建路径与配置文件中指定文件相同

内容如下：admin:test #注意test 是已经创建好的用户，如果该组中有其它用户，一次排列以空格隔开
```



## apache2.4语法变化
```
http://httpd.apache.org/docs/2.4/upgrading.html


In this example, all requests are denied.

2.2 configuration:

Order deny,allow
Deny from all
2.4 configuration:

Require all denied
In this example, all requests are allowed.

2.2 configuration:

Order allow,deny
Allow from all
2.4 configuration:

Require all granted
In the following example, all hosts in the example.org domain are allowed access; all other hosts are denied access.

2.2 configuration:

Order Deny,Allow
Deny from all
Allow from example.org
2.4 configuration:

Require host example.org
In the following example, mixing old and new directives leads to unexpected results.

Mixing old and new directives: NOT WORKING AS EXPECTED

DocumentRoot "/var/www/html"

<Directory "/">
    AllowOverride None
    Order deny,allow
    Deny from all
</Directory>

<Location "/server-status">
    SetHandler server-status
    Require 127.0.0.1
</Location>

access.log - GET /server-status 403 127.0.0.1
error.log - AH01797: client denied by server configuration: /var/www/html/server-status
Why httpd denies access to servers-status even if the configuration seems to allow it? 
Because mod_access_compat directives take precedence over the 
mod_authz_host one in this configuration merge scenario.

This example conversely works as expected:

Mixing old and new directives: WORKING AS EXPECTED

DocumentRoot "/var/www/html"

<Directory "/">
    AllowOverride None
    Require all denied
</Directory>

<Location "/server-status">
    SetHandler server-status
    Order deny,allow
    Deny from all
    Allow From 127.0.0.1
</Location>

access.log - GET /server-status 200 127.0.0.1
So even if mixing configuration is still possible, please try to avoid it
 when upgrading: either keep old 
directives and then migrate to the new ones on a later stage or just migrate 
everything in bulk.
```



## php
```
apache+php
php.ini 的 short_open_tag = Off改为
short_open_tag = On
否则php的页面不生效

index.php
<?phpphpinfo();?>
```



## apache虚拟主机
```
修改/etc/httpd/conf/httpd.conf

基于ip静态
<VirtualHost 192.168.1.11:80>
　　ServerName www.test1.com
　　DocumentRoot /www/test1/
　　<Directory "/www/test1">
　　　　Options Indexes FollowSymLinks
　　　　 AllowOverride None
　　　　 Order allow,deny
　　 　　Allow From All
　 </Directory>
</VirtualHost>
 
<VirtualHost 192.168.1.12:80>
　　ServerName www.test1.com
　　DocumentRoot /www/test2/
　　<Directory "/www/test2">
　　　　Options Indexes FollowSymLinks
　　　　 AllowOverride None
　　　　 Order allow,deny
　　 　　Allow From All
　 </Directory>
</VirtualHost>

基于域名静态
NameVirtualHost *:80
<VirtualHost *:80>
　　ServerName www.test1.com
　　DocumentRoot /www/test1/
　　<Directory "/www/test1">
　　　　Options Indexes FollowSymLinks
　　　　AllowOverride None
　　　　Order allow,deny
　　　　Allow from all
　　</Directory>
</VirtualHost>

<VirtualHost *:80> 
　　ServerName www.test2.com
　　DocumentRoot /www/test2/
　　<Directory "/www/test2">
　　　　Options Indexes FollowSymLinks
　　　　AllowOverride None
　　　　Order allow,deny
　　　　Allow from all
　　</Directory>
</VirtualHost>


基于ip动态
192.168.1.11            www.163.com
192.168.1.22            www.263.com
%1  %2  %3 %4       %1     %2  %3
VirtualDocumentRootIP   /tmp/www/%4
/tmp/www/11
/tmp/www/22

基于域名动态
www.163.com            192.168.1.11
www.263.com            192.168.1.12
VirtualDocumentRoot   /tmp/www/%2
/tmp/www/163
/tmp/www/263

www.163.com            192.168.1.11
www.263.com            192.168.1.12
mail.163.com
VirtualDocumentRoot   /tmp/a/%1/%2
/tmp/a/www/163
/tmp/a/www/263
/tmp/a/mail

```

## apache安全
```
关闭trace和track方法

/etc/httpd/conf/httpd.conf 添加
TraceEnable Off
RewriteEngine on
RewriteCond %{REQUEST_METHOD} ^(TRACE|TRACK)
RewriteRule .* - [F]
```

## apache优化
```
vim /etc/httpd/conf/httpd.conf
MPM 有两种工作方式：1、worker 线程 
         2、prefork 进程时（一个连接产生一个进程）

解压     tar fzxv httperf-0.9.0
    cd httperf-0.9.0
    ./configure && make && make install
    vim /tmp/wsesslog
    #session 1 definition 定义一个session，即一个来的访问操作
    /index.html
        /cs.jpg
    /b.html
        /x.jgp

通过脚本可以判定出热点网页：
awk -F \" '{print $2}' /var/log/httpd/access_log | awk '{print $2}' | grep 'html$' | 
sort | uniq -c | sort -nr | head -n 10 
awk ' $7 ~ "html$" {print $7} ' /var/log/httpd/access_log | sort | uniq -c | 
sort -nr | head -n 10

规则    
httperf --hog（优化参数） --server=192.168.18.199(被测试的主机) --rate(测试的频率) 1 --wsesslog=4,1(thinktime),
/tmp/wesslog  
Reply time[ms]:response  transfer 

压缩
<Ifmodule mod_deflate.c>
DeflateCompressionLevel 6
AddOutputFilterByType DEFLATE text/html
</Ifmodule>



并发量  
1、连接进程数的多少
2、netstat -ant | grep -i "estab" | wc -l 处于estab状态的数量
3、凡是与80端口有关的都算是并发
4、syn estalished

Reply status
2 代表正常
3 代表重定向
4 页面无法请求
5 服务器资源不足

apache的worker模式（如果想用线程方式，建议去用nginx）
vim /etc/sysconfig/httpd
HTTPD=/usr/sbin/httpd.worker
/etc/inint.d/httpd restart

ps -eo nlwp,pid,user,comm | grep apache

nlwp 产看当前进程中有多少个线程
apache自身
1、日志（可以连接到/dev/null）
2、文件描述符（限制进程使用的数是1024）
3、mkdir -pv /tmp/mm
   mount -o size=500M -t tmpfs none /tmp/mm  
   500M 内存到这个目下，以后在对数据处理时，就相当于往内存中写，而这些数据不会因清空缓存
   而数据丢失，而是相当于做了一个
   预热（保证数据都在内存中,把内存当作硬盘来用）

apache与I/O
1、挂载的时候加上 notime
2、BI/O（电梯层：整合、排序 ）层用deadline 时时性比较好
3、分raid

apache与Memory
单个apache对内存的使用情况
awk ' $3 ~ "kB" { sum[$1] += $2 } END {for (key in sum) print key,sum[key]"KB"}' smaps
1、与调用的模快有关 LoadModule
2、与进程数多少有关

apache网络 
httpd协议的最重要参数 
1、http的连线超时时间  Timeout 默认10S
2、KeepAlive on  占用的是内存
   KeepAlive Tmieout 15 
   解决Time_wait数量多的时候
   echo 1 > /proc/sys/net/ipv4/tcp_tw_recycle
   echo 1 > /proc/sys/net/ipv4/tcp_tw_reuse
   注：短时间内不会有请求页面的时候，不需要开启。通常情况下静态页面开启
网络数据进行压缩，用CPU来换取带宽
注：建议大家用apache作动态页面
wiki.nginx.org nginx优化

php优化调整（都与开发进行沟通）

vim /etc/php.ini
max_execution_time = 600;     最大运行时间，最多占用600S
max_input_time = 600;          最大超时时间
memory_limit = 128M           内存限制
-output_buffering = 4096      数据发送之前需要多少缓存

opcode 操作码
软件 xpc apc
首先保证安装PHP: yum install php -y
安装:rpm -ivh php-eaccelerator-0.9.5.2-2.el5.i386.rpm 
vim /etc/php.d/eaccelerator.ini
eaccelerator.shm_sime = "0"   系统默认的内存 ipcs -l  
eaccelerator.shm_ttl = "3600" 缓存时间
eaccelerator.allowed_admin_path = "/var/www/html/control.php 指定管理页面
eaccelerator.cache_dir = "/var/cache/php-eaccelerator" 缓存的磁盘路径
cp /usr/share/doc/php-eaccelerator-0.9.5.2/control.php /var/www/html 拷贝模板
测试:ab -n 100 -c 10 http://192.168.18.199/time.php
关闭缓存再进行测试，比较两次测试里面的时间


vim /etc/security/limits.conf
* soft nofile 102400
* soft nofile 102400
su -
ulimit -SHn
vim /usr/include/bits/typesizes.h
#define __FD_SETSIZE            102400

cd httperf-0.9.0
./configure && make && make install

测试
1、考虑你的并发量：
httperf --hog --server=192.168.18.199 --rate 500 --wsesslog=5000000,1,/tmp/wesslog
2、vim /etc/httpd/conf/httpd.conf
   <IfModule prefork.c>
    StartServers       80
    MinSpareServers    50
    MaxSpareServers   200
    ServerLimit       500
    MaxClients        500
    MaxRequestsPerChild  4000
   </IfModule>
3、apache测试脚本 在被测试的机器上运行
vim /tmp/net
netstat -ant|awk '$1 ~ "^tcp" {sum[$NF] += 1} END {for (key in sum) print key,sum[key]}'

    chmod +x /tmp/net
    watch -n 1 /tmp/net
4、    netstat -ant | grep 18.113(用来测试的机器) | grep -i 'syn_recv' | wc -l
    netstat -ant | grep 18.113(用来测试的机器) | grep -i 'established' | wc -l
    top  load average
    free -m
注：将测试主机和被测试主机的文件描述符都改成 102400
并发：avg        14
     进程数     8900
     进程数＋established   8900
     进程数＋established＋syn_baklog  大约3万多
```



