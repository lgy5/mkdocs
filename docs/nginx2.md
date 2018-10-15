

## nginx启动脚本
```
#!/bin/bash
NGINX=/usr/local/nginx/sbin/nginx
PID=/usr/local/nginx/logs/nginx.pid
##fun
START () {
pstree -p |grep nginx > /dev/null 2>&1
   if [ -f $PID ] && [ $? -eq 0 ]
      then
                        echo "Warnning: nginx already running"
   else
            
               if [ -f $PID ];then
                rm -rf $PID
                fi
     $NGINX
##stdin OK
             if [ $? -eq 0 ];then
              echo -e "nginx start\t\t\t\t [\033[32m OK \033[0m]"
             else
               echo -e "nginx start\t\t\t\t [\033[31m Fail \033[0m]"
             fi
   fi
}
STOP () {
pstree -p |grep nginx > /dev/null 2>&1
if [ -f $PID ] && [ $? -eq 0 ]
      then
                       killall -s QUIT nginx
#check
                  if [ $? -eq 0 ];then
                    echo -e "nginx stop\t\t\t\t [\033[32m OK \033[0m]"
                  fi
   else
             rm -rf /usr/local/nginx/logs/nginx.pid > /dev/null 2>&1
             echo -e "nginx stop\t\t\t\t [\033[31m Fail \033[0m]"
   fi
}
RESTART () {
STOP;sleep 1;START
}
RELOAD () {
if [ -f $PID ] && [ $? -eq 0 ]
      then
          killall -s HUP $NGINX
#reload check
              if [ $? -eq 0 ];then
                     echo -e "nginx reload\t\t\t\t [\033[32m OK \033[0m]"
              fi
else
         echo "Warnning: nginx stop,please start nginx"
fi
}
STATUS () {
elinks http://localhost -dump > /dev/null 2>&1
          if [ $? -eq 0 ];then
             echo "nginx running..."
          else
             echo "nging stop"
          fi
}
#main
case $1 in
start) START;;
stop) STOP;;
restart) RESTART;;
reload) RELOAD;;
status) STATUS;;
*) echo "USAGE: AVGE is start|stop|restart|reload|status";;
esac
```



## Nginx优化
```
Nginx(读音engine x)服务器由于性能优秀稳定、配置简单以及跨平台，被越来越多的公司和个人所采用，现已成为市场份额继Apache之后的
第二大Web服务器。各大小网站论坛博客也介绍说明了Nginx从安装到优化的各种配置。不过看了很多这些相关Nginx的文档之后，发现一个
比较大的问题，就是这些文档基本也就从两个方面着手，一是修改Nginx的配置文件，二是调整操作系统的相关内核参数；而且文档说明也不
够明了，缺乏比较系统级别的优化。本文将从Nginx源码编译安装开始，到修改配置文件，调整系统内核参数以及架构四个方面着手分别介绍如何优化。
一.     安装
(1)  精简模块
Nginx由于不断添加新的功能，附带的模块也越来越多。很多操作系统厂商为了用户方便安装管理，都增加了rpm、deb或者其他自有格式
软件包，可以本地甚至在线安装。不过我不太建议使用这种安装方式。这虽然简化了安装，在线安装甚至可以自动解决软件依赖关系，但是
安装后软件的文件布局过于分散，不便管理维护；同时也正是由于存在软件包之间的依赖关系，导致当有安全漏洞、或者其它问题，想要
通过更新升级Nginx新版本时却发现yum、deb源还未发布新版本(一般都落后于官网发布的软件版本)。最重要的是采用非源码编译安装的
方式，默认会添加入许多模块，比如邮件相关、uwsgi、memcache等等，很多网站运行时这些模块根本未用到，虽然平时占用的资源很小，
但是仍然可能是压弯骆驼的一根稻草。各种非必需模块默认安装运行的同时，也给Web系统带来了安全隐患。尽量保持软件的轻装上阵，
是每个运维应当尽力做到的，所以我建议一般常用的服务器软件使用源码编译安装管理。。我一般使用的编译参数如下，PHP相关模块
fastcgi被保留用作后文优化说明，：


./configure \
"--prefix=/App/nginx" \
"--with-http_stub_status_module" \
"--without-http_auth_basic_module" \
"--without-http_autoindex_module" \
"--without-http_browser_module" \
"--without-http_empty_gif_module" \
"--without-http_geo_module" \
"--without-http_limit_conn_module" \
"--without-http_limit_req_module" \
"--without-http_map_module" \
"--without-http_memcached_module" \
"--without-http_proxy_module" \
"--without-http_referer_module" \
"--without-http_scgi_module" \
"--without-http_split_clients_module" \
"--without-http_ssi_module" \
"--without-http_upstream_ip_hash_module" \
"--without-http_upstream_keepalive_module" \
"--without-http_upstream_least_conn_module" \
"--without-http_userid_module" \
"--without-http_uwsgi_module" \
"--without-mail_imap_module" \
"--without-mail_pop3_module" \
"--without-mail_smtp_module" \
"--without-poll_module" \
"--without-select_module" \
"--with-cc-opt='-O2'"
编译参数根据网站是否真正用到的原则增添或者减少，比如我们公司如果需要用到ssi模块,从而能够实现访问shtml页面，可以将第17行删除，
那么Nginx将默认安装。大家可以通过运行 "./configure --help" 查看编译帮助，决定是否需要安装哪些模块。
(2)  GCC编译参数优化 [可选项】
GCC总共提供了5级编译优化级别：
-O0: 无优化。
-O和-O1: 使用能减少目标代码尺寸以及执行时间并且不会使编译时间明显增加的优化。在编译大型程序的时候会显著增加编译时内存的使用。
-O2: 包含-O1的优化并增加了不需要在目标文件大小和执行速度上进行折衷的优化。编译器不执行循环展开以及函数内联。此选项将增加编译
时间和目标文件的执行性能。
-Os: 可以看成 -O2.5，专门优化目标文件大小，执行所有的不增加目标文件大小的-O2优化选项，并且执行专门减小目标文件大小的优化选项。
适用于磁盘空间紧张时使用。但有可能有未知的问题发生，况且目前硬盘容量很大，常用程序无必要使用。
-O3: 打开所有 -O2 的优化选项外增加 -finline-functions、-funswitch-loops、-fgcse-after-reload 优化选项。相对于 -O2 性能
并未有较多提高，编译时间也最长，生成的目标文件也更大更占内存，有时性能不增反而降低，甚至产生不可预知的问题(包括错误)，所以并不
被大多数软件安装推荐，除非有绝对把握方可使用此优化级别。
修改GCC编译参数，提高编译优化级别，此方法适用于所有通过GCC编译安装的程序，不止Nginx。稳妥起见用 -O2，这也是大多数软件编译推荐
的优化级别。查看Nginx源码文件 auto/cc/gcc，搜索NGX_GCC_OPT，默认GCC编译参数为-O，可以直接修改内容为NGX_GCC_OPT="-O2"或者
在 ./configure配置时添加--with-cc-opt='-O2'选项。
二.      配置
应用服务器的性能优化主要在合理使用CPU、内存、磁盘IO和网络IO四个方面，现在我们从Nginx配置文件 nginx.conf 入手进行优化：
(1)  工作进程数的选择
指令：worker_processes 
定义了Nginx对外提供web服务时的工作进程数。最优值取决于许多因素，包括（但不限于）CPU核心的数量、存储数据的硬盘数量及负载模式。
不能确定的时候，将其设置为可用的CPU内核数将是一个好的开始（设置为“auto”将尝试自动检测它）。
Shell执行命令  ps ax | grep "nginx: worker process" | grep -v "grep" 可以看到运行中的Nginx工作进程数，
一般建议设置成服务器逻辑核心数，Shell执行命令 cat /proc/cpuinfo | grep processor | wc -l 可以检测出服务
器逻辑核心总数，偷懒可以直接写auto，Nginx自适应。
        (2)  是否绑定CPU
指令：worker_cpu_affinity

绑定工作进程到对应CPU核心，Nginx默认未开启CPU绑定。目前的服务器一般为多核CPU，当并发很大时，服务器各个CPU的使用
率可能出现严重不均衡的局面，这时候可以考虑使用CPU绑定，以达到CPU使用率相对均匀的状态，充分发挥多核CPU的优势。
top、htop等程序可以查看所有CPU核心的使用率状况。绑定样例：

1
2
worker_processes    4;
worker_cpu_affinity 0001 0010 0100 1000;
(3)  打开文件数限制
指令：worker_rlimit_nofile
设定了每个Nginx工作进程打开的最大文件数，受限于系统的用户进程打开文件数限制，未设置则使用系统默认值。理论上应该
设置为当前Shell启动进程的最大打开文件数除以Nginx的工作进程数。由于Nginx的工作进程打开文件数并不一完全均匀，
所以可以将其设置成Shell启动进程的最大打开文件数。Shell执行命令 ulimit -n 可以查看当前登录Shell会话最大打开
文件数数限制。Linux系统用户进程默认同时打开文件最大数为1024，这个值太小，访问量稍大就报“too many open files"。
Shell执行命令先修改用户打开文件数限制：


echo "* - nofile 65536" >> /etc/security/limits.conf
然后添加入/etc/profile如下两行内容，修改所有Shell和通过Shell启动的进程打开文件数限制：

1
echo "ulimit -n 65536" >> /etc/profile
Shell执行命令使当前Shell临时会话立即生效：

1
ulimit -n 65536
(4) 惊群问题
指令：accept_mutex

如果 accept_mutex 指令值为 on 启用，那么将轮流唤醒一个工作进程接收处理新的连接，其余工作进程继续保持睡眠；
如果值为 off 关闭，那么将唤醒所有工作进程，由系统通过use指令指定的网络IO模型调度决定由哪个工作进程处理，
未接收到连接请求的工作进程继续保持睡眠，这就是所谓的“惊群问题”。Web服务器Apache的进程数很多，成百上千也是
时有的事，“惊群问题”也尤为明显。Nginx为了稳定，参数值保守的设置为 on 开启状态。可以将其设置成Off 提高性能
和吞吐量，但这样也会带来上下文切换增多或者负载升高等等其它资源更多消耗的后果。
(5)  网络IO模型
指令：use
定义了Nginx设置用于复用客户端线程的轮询方法(也可称多路复用网络IO模型)。这自然是选择效率更高的优先，Linux 2.6+内
核推荐使用epoll，FreeBSD推荐使用kqueue，安装时Nginx会自动选择。
(6)  连接数
指令：worker_connections
定义了Nginx一个工作进程的最大同时连接数，不仅限于客户端连接，包括了和后端被代理服务器等其他的连接。官网文档还指出
了该参数值不能超过 worker_rlimit_nofile 值，所以建议设置成和 worker_rlimit_nofile 值相等。
(7)  打开文件缓存
指令：open_file_cache

开启关闭打开文件缓存，默认值 off 关闭，强烈建议开启，可以避免重新打开同一文件带来的系统开销，节省响应时间。如需开启必须
后接参数 max=数字，设置缓存元素的最大数量。当缓存溢出时，使用LRU(最近最少使用)算法删除缓存中的元素；可选参数 inactive=
时间 设置超时，在这段时间内缓存元素如果没有被访问，将从缓存中删除。示例：open_file_cache max=65536  inactive=60s。
指令：open_file_cache_valid
设置检查open_file_cache缓存的元素的时间间隔。
指令：open_file_cache_min_uses
设置在由open_file_cache指令的inactive参数配置的超时时间内， 文件应该被访问的最小次数。如果访问次数大于等于此值，文件描
述符会保留在缓存中，否则从缓存中删除。
(8)  日志相关
指令：access_log 和 error_log
当并发很大时，Nginx的访问日志和错误日志的保存肯定会造成对磁盘的大量读写，也将影响Nginx的性能。并发量越大，IO越高。这时候
可以考虑关闭访问日志和错误日志，或者将日志保存到tmpfs文件系统里，或者减少保存的访问日志条目和错误日志的级别，从而避免磁盘
IO的影响。关闭日志使用 access_log off。如必须保存日志，可以按每日或者每时或者其它时间段对日志做切割，这也可以减小IO，
虽然可能效果不是特别大，不过因为日志文件尺寸变小了很多，也方便查阅或归档分析日志。一般线上环境建议错误日志设置为 error 
或者 crit。自定义访问日志的条目和错误日志的级别，详细信息可以参阅官网或者网上其它文档，按需修改。
(9)  隐藏Nginx版本号
指令：server_tokens
开启或关闭“Server”响应头中输出的Nginx版本号。推介设置为 off，关闭显示响应头的版本号，对性能的提高有小小的裨益，主要还是
为了安全起见，不被骇客找到版本号对应的漏洞，从而被攻击。
(10) 压缩相关
指令：gzip
Nginx默认开启了gzip压缩功能。有可能很多人认为，开启gzip压缩会增加CPU的处理时间和负载。但是经过我们网站的测试发现，关闭了
gzip压缩功能的Nginx虽然减少了CPU计算，节省了服务器的响应时间，但网站页面总体响应时间反而加长了，原因在于js和css、xml、j

son、html等等这些静态文件的数据传输时间的增长大大超过了服务器节省出来的响应时间，得不偿失。gzip on 开启压缩后，大约可以减

少75%的文件尺寸，不但节省了比较多的带宽流量，也提高了页面的整体响应时间。所有建议还是开启。当然也不是所有的静态文件都需要压
缩，比如静态图片和PDF、视频，文件本身就应当做压缩处理后保存到服务器。这些文件再次使用gzip压缩，压缩的比例并不高，甚至适得其
反，压缩后文件尺寸增大了。CPU压缩处理这些静态文件增加占用的服务器响应时间绝大部分时候会超过了被压缩减小的文件尺寸减少的数据
传输时间，不划算。是否需要对Web网站开启压缩，以及对哪些文件过滤压缩，大家可以通过使用HttpWatch、Firebug等等网络分析工具对比测试。
指令：gzip_comp_level
指定压缩等级，其值从1到9，数字越大，压缩率越高，越消耗CPU，负载也越高。9等级无疑压缩率最高，压缩后的文件尺寸也最小，但也是
最耗CPU资源，负载最高，速度最慢的，这对于用户访问有时是无法忍受的。一般推荐使用1-4等级，比较折衷的方案。我们公司网站使用等级2。
指令：gzip_min_length
指定压缩的文件最小尺寸，单位 bytes 字节，低于该值的不压缩，超过该值的将被压缩。我们网站设置为1k，太小的文件没必要压缩，压缩
过小尺寸文件带来增加的CPU消耗时间和压缩减少的文件尺寸降低的数据下载时间互相抵消，并有可能增加总体的响应时间。
指令：gzip_types
指定允许压缩的文件类型，Nginx配置目录 conf 下的 mime.types 文件存放了Nginx支持的文件类型，text/html类型文件，文件后缀为
html htm shtml默认压缩。推荐配置：gzip_types text/plain text/css application/json application/x-javascript text/xml
 application/xml application/xml+rss text/javascript。
(11) 浏览器缓存
指令：expires
设置HTTP应答中的“Expires”和“Cache-Control”头标。"Expires"一般结合"Last-Modified"使用。当设置了合理的expires配置时，
浏览器第一次访问Web页面元素，会下载页面中的的静态文件到本机临时缓存目录下。第二次及之后再次访问相同URL时将发送带头标识
"If-Modified-Since"和本地缓存文件时间属性值的请求给服务器，服务器比对服务器本地文件时间属性值，如果未修改，服务器直接
返回http 304状态码，浏览器直接调用本地已缓存的文件；如果时间属性值修改了，重新发送新文件。这样就避免了从服务器再次传送
文件内容，减小了服务器压力，节省了带宽，同时也提高了用户访问速度，一举三得。指令后接数字加时间单位，即为缓存过期时间；-1 
表示永远过期，不缓存。强烈建议添加expires配置，过期时间的选择具体分析。我们公司的部分Nginx配置如下：


location ~ .+\.(gif|jpg|jpeg|png|bmp|swf)$
{
    expires 30d;
}

location ~ .+\.(js|css|xml|javascript|txt|csv)$
{
    expires 30d;
}
或者统一将静态文件放在固定目录下再对目录做location和expires，示例：

location /static/
{
    expires 30d;
}
(12) 持久连接
指令：keepalive_timeout
启用Http的持久连接Keepalive属性，复用之前已建立的TCP连接接收请求、发送回应，减少重新建立TCP连接的资源时间开销。
在此的建议是当网站页面内容以静态为主时，开启持久连接；若主要是动态网页，且不能被转化为静态页面，则关闭持久连接。
后接数字和时间单位符号。正数为开启持久连接，0关闭。
(13) 减少HTTP请求次数
网站页面中存在大量的图片、脚本、样式表、Flash等静态元素，减少访问请求次数最大的优点就是减少用户首次访问页面的加载
时间。可以采用合并相同类型文件为一个文件的办法减少请求次数。这其实属于Web前端优化范畴，应当由Web前段工程师做好相
关静态文件的规划管理，而不是由运维来做。不过Nginx也可以通过安装阿里巴巴提供的Concat或者Google的PageSpeed模块实
现这个合并文件的功能。我们公司并未使用合并功能，具体安装配置信息请查询网上相关文档，这里不再累述。Concat源代码网
址：https://github.com/alibaba/nginx-http-concat/，PageSpeed源代码网址：https://github.com/pagespeed/ngx_pagespeed。
(14) PHP相关
Nginx不能直接解析PHP代码文件，需要调用FastCGI接口转给PHP解释器执行，然后将结果返回给Nginx。PHP优化本文暂不介绍。
Nginx可以开启FastCGI的缓存功能，从而提高性能。
指令：fastcgi_temp_path
定义FastCGI缓存文件保存临时路径。
指令：fastcgi_cache_path
定义FastCGI缓存文件保存路径和缓存的其它参数。缓存数据以二进制数据文件形式存储，缓存文件名和key都是通过对访问URL使用
MD5计算获得的结果。缓存文件先保存至fastcgi_temp_path指定的临时目录下，然后通过重命名操作移至fastcgi_cache_path指
定的缓存目录。levels指定了目录结构,子目录数以16为基数；keys_zone指定了共享内存区名和大小，用于保存缓存key和数据信息；
inactive指定了缓存数据保存的时间，当这段时间内未被访问，将被移出；max_size指定了缓存使用的最大磁盘空间，超过容量时将
最近最少使用数据删除。建议fastcgi_temp_path和fastcgi_cache_path设为同一分区，同分区移动操作效率更高。示例：


fastcgi_temp_path /tmp/fastcgi_temp;
fastcgi_cache_path /tmp/fastcgi_cache levels=1:2 keys_zone=cache_fastcgi:16m inactive=30m max_size=1g;
示例中使用/tmp/fastcgi_temp作为FastCGI缓存的临时目录；/tmp/fastcgi_cache作为FastCGI缓存保存的最终目录；一级子目录为
16的一次方16个，二级子目录为16的2次方256个；共享内存区名为cache_fastcgi，占用内存128MB；缓存过期时间为30分钟；缓存数据
保存于磁盘的最大空间大小为1GB。
指令：fastcgi_cache_key
定义FastCGI缓存关键字。启用FastCGI缓存必须加上这个配置，不然访问所有PHP的请求都为访问第一个PHP文件URL的结果。
 指令：fastcgi_cache_valid
为指定的Http状态码指定缓存时间。
指令：fastcgi_cache_min_uses
指定经过多少次请求相同的URL将被缓存。
指令：fastcgi_cache_use_stale
指定当连接FastCGI服务器发生错误时，哪些情况使用过期数据回应。
指令：fastcgi_cache
缓存使用哪个共享内存区。
我常用nginx.conf模板，大家根据情况做适当修改：


user  nginx nginx;
worker_processes  auto;

error_log  logs/error.log error;

pid        logs/nginx.pid;
worker_rlimit_nofile    65536;

events
{
    use epoll;
    accept_mutex off;
    worker_connections  65536;
}


http
{
    include       mime.types;
    default_type  text/html;

    charset UTF-8;
    server_names_hash_bucket_size 128;
    client_header_buffer_size 4k;
    large_client_header_buffers 4 32k;
    client_max_body_size            8m;

    open_file_cache max=65536  inactive=60s;
    open_file_cache_valid      80s;
    open_file_cache_min_uses   1;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  logs/access.log  main;

    sendfile    on;
    server_tokens off;

    fastcgi_temp_path  /tmp/fastcgi_temp;
    fastcgi_cache_path /tmp/fastcgi_cache levels=1:2 keys_zone=cache_fastcgi:128m inactive=30m max_size=1g;
    fastcgi_cache_key $request_method://$host$request_uri;
    fastcgi_cache_valid 200 302 1h;
    fastcgi_cache_valid 301     1d;
    fastcgi_cache_valid any     1m;
    fastcgi_cache_min_uses 1;
    fastcgi_cache_use_stale error timeout http_500 http_503 invalid_header;

    keepalive_timeout  60;

    gzip  on;
    gzip_min_length 1k;
    gzip_buffers  4 64k;
    gzip_http_version 1.1;
    gzip_comp_level 2;
    gzip_types text/plain text/css application/json application/x-javascript text/xml application/xml application/
    xml+rss text/javascript;

    server
    {
        listen       80;
        server_name  localhost;
        index        index.html;
        root         /App/web;

        location ~ .+\.(php|php5)$
        {
            fastcgi_pass   unix:/tmp/php.sock;
            fastcgi_index  index.php;
            include        fastcgi.conf;
            fastcgi_cache  cache_fastcgi;
        }

        location ~ .+\.(gif|jpg|jpeg|png|bmp|swf|txt|csv|doc|docx|xls|xlsx|ppt|pptx|flv)$
        {
            expires 30d;
        }

        location ~ .+\.(js|css|html|xml)$
        {
            expires 30d;
        }

        location /nginx-status
        {
            stub_status on;
            allow 192.168.1.0/24;
            allow 127.0.0.1;
            deny all;
        }
    }
}
三.        内核
Linux内核参数部分默认值不适合高并发，一般临时方法可以通过调整/Proc文件系统，或者直接修改/etc/sysctl.conf配置文件永久保存。
调整/Proc文件系统，系统重启后还原至默认值，所以不推荐。Linux内核调优，主要涉及到网络和文件系统、内存等的优化，下面是我常用
的内核调优配置：


grep -q "net.ipv4.tcp_max_tw_buckets" /etc/sysctl.conf || cat >> /etc/sysctl.conf << EOF
########################################
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.core.somaxconn = 262144
net.core.netdev_max_backlog = 262144
net.ipv4.tcp_max_orphans = 262144
net.ipv4.tcp_max_syn_backlog = 262144
net.ipv4.tcp_max_tw_buckets = 10000
net.ipv4.ip_local_port_range = 1024 65500
net.ipv4.tcp_tw_recycle = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_synack_retries = 1
net.ipv4.tcp_syn_retries = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3
net.ipv4.tcp_mem = 786432 1048576 1572864
fs.aio-max-nr = 1048576
fs.file-max = 6815744
kernel.sem = 250 32000 100 128
vm.swappiness = 10
EOF
sysctl -p
详细说明大家可以查看我的Linux内核优化文章：http://dongsong.blog.51cto.com/916653/1631085。
四.        架构
Nginx的最大优势在于处理静态文件和代理转发功能，支持7层负载均衡和故障隔离。 动静分离是每个网站发展到一定规模之后必然的结果。
静态请求则应当最好将其拆分，并启用独立的域名，既便于管理的需要，也便于今后能够快速支持CDN。如果一台Nginx性能无法满足，
则可以考虑在Nginx前端添加LVS负载均衡，或者F5等硬件负载均衡（费用昂贵，适合土豪公司单位），由多台Nginx共同分担网站请求。
还可以考虑结合Varnish或者Squid缓存静态文件实现类似CDN功能。新版Nginx目前已经支持直接读写Memcache，可以编译安装时候选择
添加此类模块，从而节省了转交给PHP或者JPS等动态程序服务器处理时间，提高效率的同时，减小了动态服务器的负载。

来源： http://www.ttlsa.com/nginx/web-server-nginx-optimization/
```



## keepalived
```
Keepalived介绍
keepalived是一个类似于layer3, 4, 5 交换机制的软件，也就是我们平时说的第3层、第4层和第5层交换。Keepalived的作用是
检测web服务器的状态，如果有一台web服务器死机，或工作出现故障，Keepalived将检测到，并将有故障的web服务器从系统中剔除，
当web服务器工作正常后Keepalived自动将web服务器加入到服务器群中，这些工作全部自动完成，不需要人工干涉，需要人工做的只是
修复故障的web服务器
官网地址：http://www.keepalived.org
keepalved官方体系结构图：

环境准备
操作系统：CentOS6.6 64位 2台
Nginx-Master   10.0.0.60
Nginx-Backup   10.0.0.61
VIP                      10.0.0.62
注：未做特别说明，两台服务器(两个节点)都一样操作
安装Nginx
使用《OneinStack》Nginx选择y，其余n
安装Keepalived
在Nginx-Master、Nginx-Backup：
cd ~/oneinstack/src
wget http://www.keepalived.org/software/keepalived-1.2.22.tar.gz
tar xzf keepalived-1.2.22.tar.gz
cd keepalived-1.2.22
./configure --prefix=/usr/local/keepalived
make && make install
配置Keepalived
在Nginx-Master、Nginx-Backup：
ln -s /usr/local/keepalived/etc/keepalived /etc/keepalived
ln -s /usr/local/keepalived/etc/rc.d/init.d/keepalived /etc/rc.d/init.d/keepalived
ln -s /usr/local/keepalived/etc/sysconfig/keepalived /etc/sysconfig/keepalived
ln -s /usr/local/keepalived/sbin/keepalived /usr/bin/keepalived
chkconfig keepalived on
在Nginx-Master修改配置文件，vi /etc/keepalived/keepalived.conf
! Configuration File for keepalived

global_defs {
   notification_email {
       admin@linuxeye.com     #设置报警邮件地址，可以设置多个，每行一个。 需开启本机的sendmail服务
   }
   notification_email_from no-reply@linuxeye.com  #设置邮件的发送地址
   smtp_server 127.0.0.1            #设置smtp server地址
   smtp_connect_timeout 30    #设置连接smtp server的超时时间
   router_id LVS_DEVEL              #表示运行keepalived服务器的一个标识。发邮件时显示在邮件主题的信息
}

vrrp_script chk_nginx {
    script "/usr/local/keepalived/sbin/check_nginx.sh"   #该脚本检测ngnix的运行状态，并在nginx进程不存在时尝试
    重新启动ngnix，如果启动失败则停止keepalived，准备让其它机器接管。
    interval 2              #每2s检测一次，设置的时间要大于check_nginx.sh 的运行时间，否则会一直运行而无法生效
    weight 2               #检测失败（脚本返回非0）则优先级2
}

vrrp_instance VI_1 {
    state MASTER              #指定keepalived的角色，MASTER表示此主机是主服务器，BACKUP表示此主机是备用服务器
    interface eth0              #指定HA监测网络的接口
    virtual_router_id 55    #虚拟路由标识，这个标识是一个数字，同一个vrrp实例使用唯一的标识。即同一vrrp_instance下
    ，MASTER和BACKUP必须是一致的

    priority 100                  #定义优先级，数字越大，优先级越高，在同一个vrrp_instance下，MASTER的优先级必须大
    于BACKUP的优先级
    advert_int 1            #设定MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒
    authentication {        #设置验证类型和密码
        auth_type PASS      #设置验证类型，主要有PASS和AH两种
        auth_pass linuxeye  #设置验证密码，在同一个vrrp_instance下，MASTER与BACKUP必须使用相同的密码才能正常通信
    }
    virtual_ipaddress {     #设置虚拟IP地址，可以设置多个虚拟IP地址，每行一个
        10.0.0.62
    }
    track_script {
        chk_nginx           #引用VRRP脚本，即在 vrrp_script 部分指定的名字。定期运行它们来改变优先级，并最终引发主备切换。
    }
}
在Nginx-Backup修改配置文件，vi /etc/keepalived/keepalived.conf
! Configuration File for keepalived

global_defs {
   notification_email {
       admin@linuxeye.com     #设置报警邮件地址，可以设置多个，每行一个。 需开启本机的sendmail服务
   }
   notification_email_from no-reply@linuxeye.com  #设置邮件的发送地址
   smtp_server 127.0.0.1      #设置smtp server地址
   smtp_connect_timeout 30    #设置连接smtp server的超时时间
   router_id LVS_DEVEL        #表示运行keepalived服务器的一个标识。发邮件时显示在邮件主题的信息
}

vrrp_script chk_nginx {
    script "/usr/local/keepalived/sbin/check_nginx.sh"   #该脚本检测ngnix的运行状态，并在nginx进程不存在时尝试重新
    启动ngnix，如果启动失败则停止keepalived，准备让其它机器接管。
    interval 2              #每2s检测一次
    weight 2                #检测失败（脚本返回非0）则优先级2
}

vrrp_instance VI_1 {
    state BACKUP            #指定keepalived的角色，MASTER表示此主机是主服务器，BACKUP表示此主机是备用服务器
    interface eth0          #指定HA监测网络的接口
    virtual_router_id 55    #虚拟路由标识，这个标识是一个数字，同一个vrrp实例使用唯一的标识。即同一vrrp_instance下，
    MASTER和BACKUP必须是一致的
    priority 50             #定义优先级，数字越大，优先级越高，在同一个vrrp_instance下，MASTER的优先级必须大于BACKUP的优先级
    advert_int 1            #设定MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒
    nopreempt               #设置nopreempt防止抢占资源，只生效BACKUP节点
    authentication {        #设置验证类型和密码
        auth_type PASS      #设置验证类型，主要有PASS和AH两种
        auth_pass linuxeye  #设置验证密码，在同一个vrrp_instance下，MASTER与BACKUP必须使用相同的密码才能正常通信
    }
    virtual_ipaddress {     #设置虚拟IP地址，可以设置多个虚拟IP地址，每行一个
        10.0.0.62
    }
    track_script {
        chk_nginx           #引用VRRP脚本，即在 vrrp_script 部分指定的名字。定期运行它们来改变优先级，并最终引发主备切换。
    }
}
检测脚本，vi /usr/local/keepalived/sbin/check_nginx.sh
#!/bin/bash
if [ "$(ps -ef | grep "nginx: master process"| grep -v grep )" == "" ];then
    #echo 1
    /etc/init.d/nginx start
    sleep 5

    if [ "$(ps -ef | grep "nginx: master process"| grep -v grep )" == "" ];then
        /etc/init.d/keepalived stop
        #echo 2
    fi
fi
脚本加上可执行权限
chmod +x /usr/local/keepalived/sbin/check_nginx.sh
验证
service keepalived start  #启动Nginx-Master
service keepalived start  #启动Nginx-Backup
ip addr  #2台服务器分别执行，绑定虚拟IP在Nginx-Master
service keepalived stop  #停止Nginx-Backup
ip addr  #2台服务器分别执行，绑定虚拟IP在Nginx-Backup
service keepalived start  #再启动Nginx-Backup
ip addr  #2台服务器分别执行，绑定虚拟IP在Nginx-Master
上述切换默认测试会导致的master和backup之间来回切换
通常如果master服务死掉后backup会变成master，但是当master服务又好了的时候master此时会抢占VIP，这样就会发生两次切换对业务
繁忙的网站来说是不好的。我们可以在配置文件加入nopreempt非抢占，但是这个参数只能用于state为BACKUP，故我们在用HA的时候最好
MASTER和backup的state都设置成BACKUP让其通过priority来竞争。
拓展
假设我要重装这2台服务器，但是过程不容许丢一个包，通常情况下先替换backup，把master停止，让vip漂移只backup，替换master，
但是在vip漂移过程可能会有丢2个包，如果避免丢包？
方法：我们可以在master替换之前，利用iptables将数据包转发到backup，再停止master keepalived
iptables -F
iptables -t nat -I PREROUTING -i eth0 -j DNAT --to-destination 10.0.0.61
iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
```



## nginx_upstream_check_module
    提供负载均衡器内节点的健康检查的。这个就是淘宝技术团队开发的 nginx 模块 nginx_upstream_check_module，
    通过它可以用来检测后端 realserver 的健康状态。如果后端 realserver 不可用，则所以的请求就不会转发到该节点上。
    在淘宝自己的 tengine 上是自带了该模块的，大家可以访问淘宝tengine的官网来获取该版本的nginx，官方地址： 
    http://tengine.taobao.org/ 。

    下载 nginx_upstream_check_module模块

    [root@localhost ~]# cd /usr/local/src
    wget https://codeload.github.com/yaoweibin/nginx_upstream_check_module/zip/master
    unzip master
    [root@localhost /usr/local/src]# ll -d nginx_upstream_check_module-master
    drwxr-xr-x. 6 root root 4096 Dec  1 02:28 nginx_upstream_check_module-master
    2、为nginx打补丁

    [root@localhost /usr/local/src]# cd nginx-1.6.0 # 进入nginx的源码目录
    [root@localhost nginx-1.6.0]# patch -p1 < ../nginx_upstream_check_module-master/check_1.5.12+.patch
    [root@localhost nginx-1.6.0]# ./configure --user=nginx --group=nginx --prefix=/usr/local/nginx-1.6.0 
    --with-http_ssl_module --with-openssl=/usr/local/src/openssl-0.9.8q --with-pcre=/usr/local/src/pcre-8.32 
    --add-module=/usr/local/src/nginx_concat_module/ --add-module=../nginx_upstream_check_module-master/
    make (注意：此处只make，编译参数需要和之前的一样)
    [root@localhost nginx-1.6.0]# mv /usr/local/nginx/sbin/nginx /usr/local/nginx/sbin/nginx-1.6.0.bak
    [root@localhost nginx-1.6.0]# cp ./objs/nginx /usr/local/nginx/sbin/
    [root@localhost nginx-1.6.0]# /usr/local/nginx/sbin/nginx -t  # 检查下是否有问题
    [root@localhost nginx-1.6.0]# kill -USR2 `cat /usr/local/nginx/logs/nginx.pid`
    3、在nginx.conf配置文件里面的upstream加入健康检查，如下：

    upstream name {
           server 192.168.0.21:80;
           server 192.168.0.22:80;
           check interval=3000 rise=2 fall=5 timeout=1000 type=http;

    }
    上面 配置的意思是，对name这个负载均衡条目中的所有节点，每个3秒检测一次，请求2次正常则标记 realserver状态为up，
    如果检测 5 次都失败，则标记 realserver的状态为down，超时时间为1秒。

    这里列出 nginx_upstream_check_module 模块所支持的指令意思：


    Syntax: check interval=milliseconds [fall=count] [rise=count] [timeout=milliseconds] [default_down=true|false]
     [type=tcp|http|ssl_hello|mysql|ajp] [port=check_port]Default: 如果没有配置参数，默认值是：interval=30000 fall=5 
     rise=2 timeout=1000 default_down=true type=tcpContext: upstream
    该指令可以打开后端服务器的健康检查功能。

    指令后面的参数意义是：

      - interval：向后端发送的健康检查包的间隔。
      - fall(fall_count): 如果连续失败次数达到fall_count，服务器就被认为是down。
      - rise(rise_count): 如果连续成功次数达到rise_count，服务器就被认为是up。
      - timeout: 后端健康请求的超时时间。
      - default_down: 设定初始时服务器的状态，如果是true，就说明默认是down的，如果是false，就是up的。默认值是true，也就是一
      开始服务器认为是不可用，要等健康检查包达到一定成功次数以后才会被认为是健康的。
      - type：健康检查包的类型，现在支持以下多种类型
        - tcp：简单的tcp连接，如果连接成功，就说明后端正常。
        - ssl_hello：发送一个初始的SSL hello包并接受服务器的SSL hello包。
        - http：发送HTTP请求，通过后端的回复包的状态来判断后端是否存活。
        - mysql: 向mysql服务器连接，通过接收服务器的greeting包来判断后端是否存活。
        - ajp：向后端发送AJP协议的Cping包，通过接收Cpong包来判断后端是否存活。
      - port: 指定后端服务器的检查端口。你可以指定不同于真实服务的后端服务器的端口，比如后端提供的是443端口的应用，你可以去检查
      80端口的状态来判断后端健康状况。默认是0，表示跟后端server提供真实服务的端口一样。该选项出现于Tengine-1.4.0。
    Syntax: check_keepalive_requests request_numDefault: 1Context: upstream
    该指令可以配置一个连接发送的请求数，其默认值为1，表示Tengine完成1次请求后即关闭连接。

    Syntax: check_http_send http_packetDefault: "GET / HTTP/1.0\r\n\r\n"Context: upstream
    该指令可以配置http健康检查包发送的请求内容。为了减少传输数据量，推荐采用"HEAD"方法。

    当采用长连接进行健康检查时，需在该指令中添加keep-alive请求头，如："HEAD / HTTP/1.1\r\nConnection: keep-alive\r\n\r\n"。 
    同时，在采用"GET"方法的情况下，请求uri的size不宜过大，确保可以在1个interval内传输完成，否则会被健康检查模块视为后端服务器或
    网络异常。

    Syntax: check_http_expect_alive [ http_2xx | http_3xx | http_4xx | http_5xx ]Default: http_2xx | http_3xxContext: 
    upstream
    该指令指定HTTP回复的成功状态，默认认为2XX和3XX的状态是健康的。

    Syntax: check_shm_size sizeDefault: 1MContext: http
    所有的后端服务器健康检查状态都存于共享内存中，该指令可以设置共享内存的大小。默认是1M，如果你有1千台以上的服务器并在配置的时候
    出现了错误，就可能需要扩大该内存的大小。

    Syntax: check_status [html|csv|json]Default: check_status htmlContext: location
    显示服务器的健康状态页面。该指令需要在http块中配置。

    在Tengine-1.4.0以后，你可以配置显示页面的格式。支持的格式有: html、csv、 json。默认类型是html。

    你也可以通过请求的参数来指定格式，假设‘/status’是你状态页面的URL， format参数改变页面的格式，比如：

    /status?format=html
    /status?format=csv
    /status?format=json
    同时你也可以通过status参数来获取相同服务器状态的列表，比如：

    /status?format=html&status=down
    /status?format=csv&status=up
    下面是一个状态也配置的范例：

    http {
          server {
           location /nstatus {
             check_status;
             access_log off;
             #allow IP;         #deny all;       }
          }
    }
    配置完毕后，重启nginx。此时通过访问定义好的路径，就可以看到当前 realserver 实时的健康状态啦。效果如下图： 
    realserver 都正常的状态：

    wKiom1SZZXKQcPJTAAFnMqUEfBo238.jpg

    一台 realserver 故障的状态：

    wKioL1SZZivDAzdWAAGTyIK9cS8558.jpgOK，以上nginx_upstream_check_module模块的相关信息，更多的信息大家可以去该模块的淘宝
    tengine页面和github上该项目页面去查看，下面是访问地址：

    http://tengine.taobao.org/document_cn/http_upstream_check_cn.html

    https://github.com/yaoweibin/nginx_upstream_check_module

    在生产环境的实施应用中，需要注意的有 2 点：

    1、主要定义好type。由于默认的type是tcp类型，因此假设你服务启动，不管是否初始化完毕，它的端口都会起来，所以此时前段负载均衡器
    为认为该服务已经可用，其实是不可用状态。

    2、注意check_http_send值的设定。由于它的默认值是"GET / HTTP/1.0\r\n\r\n"。假设你的应用是通过http://ip/name访问的，那么
    这里你的 check_http_send值就需要更改为 "GET /name HTTP/1.0\r\n\r\n"才可以。针对采用长连接进行检查的， 这里增加keep-alive
    请求 头，即"HEAD /name HTTP/1.1\r\nConnection: keep-alive\r\n\r\n"。如果你后端的tomcat是基于域名的多虚拟机，此时你需要通
    过 check_http_send定义host，不然每次访问都是失败，范例：check_http_send "GET /mobileapi HTTP/1.0\r\n HOST www.redhat.sx
    \r\n\r\n";

    三、 ngx_http_healthcheck_module模块

    除了上面两个模块，nginx官方在早期的时候还提供了一个ngx_http_healthcheck_module  模块用来进行 nginx后端节点的健康检查。
    nginx_upstream_check_module模块就是参照 该模块的设计理念进行开发的，因此在使用和效果上都大同小异。但是需要注意的是， 
    ngx_http_healthcheck_module  模块仅仅支持nginx的1.0.0版本，1.1.0版本以后都不支持了！因此，对于目前常见的生产环境上都不
    会去用了，这里仅仅留个纪念，给大家介绍下这个模块！

    具体的使用方法，这里可以贴出几篇靠谱的博文地址以及官方地址：

    http://wiki.nginx.org/HttpHealthcheckModule

    https://github.com/cep21/healthcheck_nginx_upstreams/blob/master/README

    OK！

    以上就是本文的内容，希望能够对51博友有所帮助！


    来源： http://www.tuicool.com/articles/vuiQry



## 虚拟主机
```
基于域名的虚拟主机
server {
    listen 80;
    server_name www.example.com;
    ...
}
server {
    listen 80;
    server_name www.test.com;
    ...
}

基于ip的虚拟主机
server {
    listen 10.0.0.88:80;
    root 88.com;
    index index.html;
}
server {
    listen 10.0.0.87:80;
    root 87.com;
    index index.html;
}
```



## 正向代理
```
server {
 listen 8093;
 location / {
 resolver 218.85.157.99 218.85.152.99; #dns
 resolver_timeout 30s;
 proxy_pass http://$host$request_uri;
 }
 access_log  /var/log/proxy-aceess.log;      
}

因为Nginx不支持CONNECT，所以无法正向代理Https网站(如：网上银行，Gmail)   但是squid支持CONNECT
curl http://www.baidu.com/  -x 172.29.0.70:8093
curl https://www.baidu.com  -x 10.191.174.31:3128  squid

rsync代理设置
export RSYNC_PROXY="192.168.0.123:8080"
http/ftp代理设置
export http_proxy="192.168.0.123:8080"
export FTP_PROXY="192.168.0.123:8080"
export HTTP_PROXY="192.168.0.123:8080"
export ftp_proxy="192.168.0.123:8080"
对于wget可以单独建立.wgetrc
http-proxy = "192.168.0.123:8080"
ftp-proxy = "192.168.0.123:8080"
对于常用代理的，可以写入/etc/profile或者~/.bash_profile
临时取消代理可以unset

=======================
yum使用
export http_proxy="
http://172.29.0.70:8093
" 后直接yum install
unset http_proxy (取消)
========================

pip使用
pip --proxy http://172.29.0.70:8093 install -r pip_requirements.txt -i  http://pypi.douban.com/simple


rsync使用squid
yum install squid
vim /etc/squid/squid.conf
acl localnet src 10.191.173.0/24
acl SSL_ports port 443 563 873
acl Safe_ports port 873

/etc/init.d/squid start

客户端配置公网dns
export RSYNC_PROXY="192.168.0.123:3128"
```



## 404跳转
nginx+php 使用的时候经常需要伪静态，一般大家都手动设置。那有没有办法让 nginx 自动补全路径呢？  
这两天折腾很久，才实现了这样一个功能：  
请求 /a/b/c  
若文件不存在，查找 /a/b/index.php，/c 作为 PATH\_INFO；  
若文件不存在，查找 /a/index.php，/b/c 作为 PATH\_INFO；  
若文件不存在，查找 /index.php，/a/b/c 作为 PATH\_INFO；  
若文件不存在，返回 404.

虽然这种损耗性能的行为不适合部署，但在本机调试的时候还是能够带来方便的 🙂

server 端应有如下代码，其他部分使用自己的配置：

index index.php index.html index.htm;

```
location / {
    set $path $request_uri;
    set $path_info "";

    try_files $uri $uri/ @404;
}

location @404 {
    if ($path ~ ^(.*)(/.+)$) {
        set $path $1/index.php;
        set $path_info $2;
        rewrite .* $path last;
    }
    return 404;
}

location ~ .+.php($|/) {
    fastcgi_split_path_info ^(.+.php)(/.+)$;
    if ($path_info !~ .*) {
        set $path_info $fastcgi_path_info;
    }
    try_files $fastcgi_script_name @404php;

    fastcgi_param PATH_INFO $path_info;

    fastcgi_index index.php;
    include fastcgi.conf;

    fastcgi_pass unix:/usr/local/var/run/php-fpm.sock;
    fastcgi_connect_timeout 60;
    fastcgi_send_timeout 300;
    fastcgi_read_timeout 300;
}

location @404php {
    if ($path = /index.php) {
        return 404;
    }

    if ($path ~ ^(.*)(/.+)/index.php$) {
        set $path_info $2;
        set $path $1/index.php;
        rewrite .* $path last;
    }
    return 404;
}
```



## yum代理缓存
```
# nginx.conf log_format 添加  "$upstream_cache_status" 命中状态

proxy_cache_path /data/cache levels=1:2 keys_zone=rpm-cache:50m max_size=20g inactive=365d use_temp_path=off; 
proxy_cache_path /data/repo levels=1:2 keys_zone=repo-cache:50m max_size=1g inactive=1d use_temp_path=off; 
proxy_redirect off;
proxy_connect_timeout 30;
proxy_cache_valid  200 304 302 24h;
proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504; #后端超时使用缓存的数据
add_header X-Cache-Status $upstream_cache_status;
server_tokens off;

server {
    listen 80;

    root html;
    index index.html index.htm index.php;
    location / {
            return 404;
    }

    location ~ (\.iso|\.filez|\.dirtree|\.png|\.gif)$ {
            return 403;
    }

    location /itv/ {
        alias /data/itv/;
    }

    location /base/ {
        set $key rpm-cache;
        if ( $uri ~* repodata ){
            set $key repo-cache;
        }
        proxy_pass http://mirrors.aliyun.com/centos/;
        proxy_cache $key;
    }

    location /epel/ {
                set $key rpm-cache;
                if ( $uri ~* repodata ){
                        set $key repo-cache;
                }
                proxy_pass http://mirrors.aliyun.com/epel/;
                proxy_cache $key;
        }
}


repo文件
[iTV]
name=iTV
baseurl=http://192.168.41.21/itv/$releasever/$basearch/
enabled=1
gpgcheck=0

[iTV-base]
name=iTV-base
baseurl=http://192.168.41.21/base/$releasever/os/$basearch/
enabled=1
gpgcheck=0


[iTV-updates]
name=iTV-updates
baseurl=http://192.168.41.21/base/$releasever/updates/$basearch/
enabled=1
gpgcheck=0

[iTV-extras]
name=iTV-extras
baseurl=http://192.168.41.21/base/$releasever/extras/$basearch/
enabled=1
gpgcheck=0

[iTV-epel]
name=iTV-epel
baseurl=http://192.168.41.21/epel/$releasever/$basearch/
enabled=1
gpgcheck=0
```



## ssl和h2
```
# rpm -ivh https://nginx.org/packages/rhel/7/x86_64/RPMS/nginx-1.14.0-1.el7_4.ngx.x86_64.rpm
# wget https://raw.githubusercontent.com/Neilpang/acme.sh/master/acme.sh
# sh acme.sh --issue -d *.zxdr.tk -d zxdr.tk --dns --yes-I-know-dns-manual-mode-enough-go-ahead-please # add dns record
# sh acme.sh --issue -d *.zxdr.tk -d zxdr.tk --dns --yes-I-know-dns-manual-mode-enough-go-ahead-please --renew
user  nobody;
worker_processes  auto;
events {
    use epoll;
    accept_mutex off;
    worker_connections  65536;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout  65;
    gzip  on;
    server_tokens  off;
    
    map $http_upgrade $connection_upgrade {
	default upgrade;
	'' close;
    }
    #server { listen 80 default; location / { root html; } }
    server {
	listen 0.0.0.0:443 ssl http2 default;
	ssl on;
	ssl_certificate /root/.acme.sh/*.zxdr.tk/fullchain.cer;
	ssl_certificate_key /root/.acme.sh/*.zxdr.tk/*.zxdr.tk.key;
	ssl_session_timeout 1d;
    	ssl_session_cache shared:SSL:50m;
    	ssl_session_tickets off;
	ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
	ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
    	ssl_prefer_server_ciphers on;
	add_header Strict-Transport-Security max-age=15768000;
	ssl_stapling on;
    	ssl_stapling_verify on;
	resolver 8.8.8.8;

	location / {
                alias /tmp/down/;
                autoindex on;
		charset utf-8;
		autoindex_localtime on;
    		autoindex_exact_size off;
		add_before_body /.nginx/header.html;
                add_after_body /.nginx/footer.html;
        }

	location /co/ {
		proxy_pass http://127.0.0.1:9090;
        	proxy_http_version 1.1;
        	proxy_buffering off;
        	proxy_set_header X-Real-IP  $remote_addr;
        	proxy_set_header Host $host;
        	proxy_set_header X-Forwarded-For $remote_addr;
	        proxy_set_header Upgrade $http_upgrade;
        	proxy_set_header Connection $connection_upgrade;
        	proxy_set_header Origin http://$host;
        	#gzip off;
	}

	location /test/ {
		proxy_redirect off;
		proxy_pass http://127.0.0.1:7923;
		proxy_http_version 1.1;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "upgrade";
		proxy_set_header Host $http_host;
		proxy_intercept_errors on;
  	}
	location /stat {
                stub_status on;
        }
        error_page  400 500 502 503 504  /50x.html;
        location = /50x.html {
            	root   /usr/share/nginx/html;
        }
    }
}
```



## 跨域
```
add_header Access-Control-Allow-Origin *;
location / {
    if ($request_method = 'OPTIONS') { 
        add_header Access-Control-Allow-Origin *; 
        add_header Access-Control-Allow-Methods GET,POST,PUT,DELETE,OPTIONS;
        return 204; 
    }
    index index.php;
    try_files $uri @rewriteapp;
}
```



## openresty
https://openresty.org/package/centos/openresty.repo

```
[openresty]
name=Official OpenResty Open Source Repository for CentOS
baseurl=https://openresty.org/package/centos/$releasever/$basearch
skip_if_unavailable=False
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://openresty.org/package/pubkey.gpg
enabled=1
enabled_metadata=1
```



## proxy获取真实ip
```
upstream www.264.cn {
    ip_hash;
    server serving-server1.com:80;
    server serving-server2.com:80;
}
server {
    listen www.264.cn:80;
    server_name www.264.cn;

    location / {
        proxy_pass http://www.264.cn;
    }

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

}
在nginx的配置文件中加入下面三个指令，这样后端php就可以使用$_SERVER['HTTP_X_REAL_IP']获取到访客的ip。


proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

如果你想使用$_SERVER['REMOTE_ADDR']，不想修改代码，那么可以通过修改REMOTE_ADDR的值来实现。

经过多层代理后 $http_x_forwared_for 会含有多个ip，其中第一个ip是客户端的ip，REMOTE_ADDR只能是客户端的ip，
所以可以用正则提取 $http_x_forwarded_for的第一个ip给REMOTE_ADDR:


  set $realip $remote_addr;
  if ($http_x_forwarded_for ~ "^(\d+\.\d+\.\d+\.\d+)") {
    set $realip $1;
  }
  fastcgi_param REMOTE_ADDR $realip;
  
```

## php-fpm
```
yum install php-fpm
systemctl start php-fpm

        root /var/www;
        location / {
              index index.php;
        }
        location ~ \.php$ {
              fastcgi_pass 127.0.0.1:9000;
              fastcgi_index index.php;
              fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
              include fastcgi_params;
        }
```