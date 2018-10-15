## map
```
map $uri $match {
        ~^/common/file/dachui/(.*) /dachui/;
    }

$match  为 /dachui/
$uri  nginx内置变量  

假如 $uri 为 /common/file/dachui/20170427160407.jpg
正则匹配后 $1 为 20170427160407.jpg

$match$1 为  dachui/20170427160407.jpg   要放一起用，否则$1不生效

http://www.ttlsa.com/nginx/using-nginx-map-method/
```



## session hash规则
```
if ( $http_cookie ~* "JSESSIONID=(.*?);") #(.*?);(.*)
        {
        set $wap_cookie $1;
        }

upstream pool1 {
hash  $cookie_jsessionid;         后端为tomcat或者php等使用session服务器（无cookie方式）
server server1:80;
server server2:80;
server server3:80;
hash_again 2;      提高系统可用性
}

hash_again=1，那么当server2和 server1都宕机，但是server3可用。用户请求时仍然会无法访问。
如果我们改成hash_again=2，那么nginx会进行两次hash尝试，尝试访问后端其他可以用的机器。
也就是说hash_again的值越大，整个系统的可用性就越高。
```



## nginx rewrite
```
$arg_PARAMETER #这个变量包含GET请求中，如果有变量PARAMETER时的值
例如  gRead.do?imgurl=/dachui/20170427160407.jpg   $args   为     imgurl=/dachui/20170427160407.jpg
                                                   $arg_imgurl  为 /dachui/20170427160407.jpg
$args, 请求中的参数;
$document_root, 针对当前请求的根路径设置值;
$host, 请求信息中的"Host"，如果请求中没有 Host 行，则等于设置的服务器名;
$limit_rate, 对连接速率的限制;
$request_method, 请求的方法，比如"GET"、"POST"等;
$remote_addr, 客户端地址;
$remote_port, 客户端端口号;
$remote_user, 客户端用户名，认证用;
$request_filename, 当前请求的文件路径名
$query_string, 与$args 相同;
$scheme, 所用的协议，比如 http 或者是 https
$server_protocol, 请求的协议版本，"HTTP/1.0"或"HTTP/1.1";
$server_addr, 服务器地址，如果没有用 listen 指明服务器地址，使用这个变量将发起一次系统调用
以取得地址(造成资源浪费);
$server_name, 请求到达的服务器名;
$document_uri 与$uri 一样，URI地址;
$server_port, 请求到达的服务器端口号;

nginx rewrite指令执行顺序：
1.执行server块的rewrite指令(这里的块指的是server关键字后{}包围的区域，其它xx块类似)
2.执行location匹配
3.执行选定的location中的rewrite指令
如果其中某步URI被重写，则重新循环执行1-3，直到找到真实存在的文件

如果循环超过10次，则返回500 Internal Server Error错误

if ($hosts ~* ^www.hah) {
    set $who 'who.html';        set  指令是用于定义一个变量，并且赋值
    rewrite ^/(.*)$ http://$host/$1$2/ permanent;
}
last 相当于 Apache 里的[L]标记，表示完成 rewrite
break 本条规则匹配完成后，终止匹配，不再匹配后面的规则
redirect 返回 302 临时重定向，浏览器地址会显示跳转后的 URL地址
permanent 返回 301 永久重定向，浏览器地址会显示跳转后 URL地址

rewrite  ^/test.php  /new  permanent;       //重写向带参数的地址
rewrite  ^/test.php  /new?  permanent;      //重定向后不带参数
rewrite  ^/test.php   /new?id=$arg_id?  permanent;    //重定向后带指定的参数

location /search {
            if ($args ~* "ei=") {
                rewrite ^/ /search?newwindow=1&q=$arg_q&start=$arg_start?  permanent;
            }
            proxy_pass https://ipv6.google.com/search;
            proxy_hide_header "Set-Cookie";
            proxy_hide_header "Cache-Control";
            proxy_ignore_headers "Expires" "Cache-Control" "Set-Cookie";
            expires 30d;
        }

```



## 动静分离
```
nginx.conf
动静分离rewrite新域名跨越问题
rewrite ^/ http://staticwww.dachuizichan.com$uri permanent;

add_header Access-Control-Allow-Origin *;
if ($request_method = 'OPTIONS') {
                add_header Access-Control-Allow-Origin *;
                add_header Access-Control-Allow-Credentials true;
                add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS';
                add_header 'Access-Control-Allow-Headers' 'Access-Control-Allow-Origin, x-requested-with, content-type';
                return 200;
            }



user  nginx;
worker_processes  1;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';
    #access_log  logs/access.log  main;
    sendfile        on;
    keepalive_timeout  65;
    gzip  on;
    gzip_min_length 1k;
    gzip_buffers    4 16k;
    gzip_http_version 1.0;
    gzip_comp_level 2;   1-10，数字越大压缩的越好，时间也越长
    gzip_types text/plain application/x-javascript text/css application/xml text/javascript application/
    x-httpd-php image/jpeg image/gif image/png;
    gzip_vary off;  跟Squid等缓存服务有关，on的话会在Header里增加"Vary: Accept-Encoding"

    proxy_temp_path /tmp/temp_dir;   #缓存目录
    proxy_cache_path /tmp/cache levels=1:2 keys_zone=cache_one:200m inactive=1d max_size=30g;
    server {
        listen       81;
        server_name  localhost;
        rewrite ^/ http://$host:8081/3m/index.do last;
    }
    server {
        listen       8081;
        server_name  localhost;
        root  /usr/local/tomcat/webapps;
        location ~ (\.jsp|\.do|imageServlet)$ {
            proxy_pass http://127.0.0.1:8080;
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            client_max_body_size 10m;   #允许客户端请求的最大单文件字节数
            client_body_buffer_size 128k; #缓冲区代理缓冲用户端请求的最大字节数
            proxy_connect_timeout 90;   #nginx跟后端服务器连接超时时间(代理连接超时)
            proxy_read_timeout 90;      #连接成功后，后端服务器响应时间(代理接收超时)
            proxy_buffer_size 4k;       #设置代理服务器（nginx）保存用户头信息的缓冲区大小
            proxy_buffers 6 32k;        #proxy_buffers缓冲区，网页平均在32k以下的话，这样设置
            proxy_busy_buffers_size 64k;#高负荷下缓冲大小（proxy_buffers*2）
            proxy_temp_file_write_size 64k; #设定缓存文件夹大小，大于这个值，将从upstream服务器传   
        }
        location ~ .*\.(html|js|css|gif|jpg|png|bmp|swf|ico|txt)?$ {
            proxy_cache cache_one; # 设置缓存共享内存区块，也就是keys_zone名称。
            proxy_cache_valid 200 302 1h;
            expires 1d;
            root /usr/local/nginx/aaa/;  文件目录
        }
        error_page  404              /404.html;
        error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
```



## location和rewrite
```
location  /manage/ {
           proxy_pass http://dachui_servers/DaChui/manage/;  可以写uri
           sub_filter 'dachui_servers:80/DaChui/' 'wwwtest.dachuizichan.com/';     进行替换url
           #sub_filter 'http://dachui_servers:80/DaChui/' 'http://wwwtest.dachuizichan.com/';
           sub_filter 'http://dachui_servers/DaChui/' 'http://wwwtest.dachuizichan.com/';
           sub_filter_once off;
}
   不能在有正则匹配的location中用带URI的proxy_pass，因为这可能导致nginx不知道怎么做替换
location  = / {
  # 精确匹配 / ，主机名后面不能带任何字符串
  [ configuration A ] 
}

location  / {
  # 因为所有的地址都以 / 开头，所以这条规则将匹配到所有请求# 但是正则和最长字符串会优先匹配
  [ configuration B ] 
}

location /documents/ {
  # 匹配任何以 /documents/ 开头的地址，匹配符合以后，还要继续往下搜索# 只有后面的正则表达式没有匹配到时，这一条才会采用这一条
  [ configuration C ] 
}

location ~ /documents/Abc {
  # 匹配任何以 /documents/ 开头的地址，匹配符合以后，还要继续往下搜索# 只有后面的正则表达式没有匹配到时，这一条才会采用这一条
  [ configuration CC ] 
}

location ^~ /images/ {
  # 匹配任何以 /images/ 开头的地址，匹配符合以后，停止往下搜索正则，采用这一条。
  [ configuration D ] 
}

location ~* \.(gif|jpg|jpeg)$ {
  # 匹配所有以 gif,jpg或jpeg 结尾的请求# 然而，所有请求 /images/ 下的图片会被 config D 处理，因为 ^~ 到达不了这一条正则
  [ configuration E ] 
}

location /images/ {
  # 字符匹配到 /images/，继续往下，会发现 ^~ 存在
  [ configuration F ] 
}

location /images/abc {
  # 最长字符匹配到 /images/abc，继续往下，会发现 ^~ 存在# F与G的放置顺序是没有关系的
  [ configuration G ] 
}

location ~ /images/abc/ {
  # 只有去掉 config D 才有效：先最长匹配 config G 开头的地址，继续往下搜索，匹配到这一条正则，采用
    [ configuration H ] 
}

location ~* /js/.*/\.js
已=开头表示精确匹配
如 A 中只匹配根目录结尾的请求，后面不能带任何字符串。
^~ 开头表示uri以某个常规字符串开头，不是正则匹配
~ 开头表示区分大小写的正则匹配;
~* 开头表示不区分大小写的正则匹配
/ 通用匹配, 如果没有其它匹配,任何请求都会匹配到
顺序 no优先级：
(location =) > (location 完整路径) > (location ^~ 路径) > (location ~,~* 正则顺序) > (location 部分起始路径) > (/)

上面的匹配结果
按照上面的location写法，以下的匹配示例成立：

/ -> config A
精确完全匹配，即使/index.html也匹配不了
/downloads/download.html -> config B
匹配B以后，往下没有任何匹配，采用B
/images/1.gif -> configuration D
匹配到F，往下匹配到D，停止往下
/images/abc/def -> config D
最长匹配到G，往下匹配D，停止往下
你可以看到 任何以/images/开头的都会匹配到D并停止，FG写在这里是没有任何意义的，H是永远轮不到的，这里只是为了说明匹配顺序
/documents/document.html -> config C
匹配到C，往下没有任何匹配，采用C
/documents/1.jpg -> configuration E
匹配到C，往下正则匹配到E
/documents/Abc.jpg -> config CC
最长匹配到C，往下正则顺序匹配到CC，不会往下到E
实际使用建议
所以实际使用中，个人觉得至少有三个匹配规则定义，如下：
#直接匹配网站根，通过域名访问网站首页比较频繁，使用这个会加速处理，官网如是说。#这里是直接转发给后端应用服务器了，
也可以是一个静态首页# 第一个必选规则
location = / {
    proxy_pass http://tomcat:8080/index
}
# 第二个必选规则是处理静态文件请求，这是nginx作为http服务器的强项# 有两种配置模式，目录匹配或后缀匹配,任选其一或搭配使用
location ^~ /static/ {
    root /webroot/static/;
}
location ~* \.(gif|jpg|jpeg|png|css|js|ico)$ {
    root /webroot/res/;
}
#第三个规则就是通用规则，用来转发动态请求到后端应用服务器#非静态文件请求就默认是动态请求，自己根据实际把握#毕竟目前的一些
框架的流行，带.php,.jsp后缀的情况很少了
location / {
    proxy_pass http://tomcat:8080/
}
http://tengine.taobao.org/book/chapter_02.html
http://nginx.org/en/docs/http/ngx_http_rewrite_module.html

Rewrite规则
rewrite功能就是，使用nginx提供的全局变量或自己设置的变量，结合正则表达式和标志位实现url重写以及重定向。rewrite只能放在
server{},location{},if{}中，并且只能对域名后边的除去传递的参数外的字符串起作用，
例如 http://seanlook.com/a/we/index.php?id=1&u=str 只对/a/we/index.php重写。语法rewrite regex replacement [flag];

如果相对域名或参数字符串起作用，可以使用全局变量匹配，也可以使用proxy_pass反向代理。

表明看rewrite和location功能有点像，都能实现跳转，主要区别在于rewrite是在同一域名内更改获取资源的路径，而location是对
一类路径做控制访问或反向代理，可以proxy_pass到其他机器。很多情况下rewrite也会写在location里，它们的执行顺序是：

执行server块的rewrite指令
执行location匹配
执行选定的location中的rewrite指令
如果其中某步URI被重写，则重新循环执行1-3，直到找到真实存在的文件；循环超过10次，则返回500 Internal Server Error错误。

flag标志位
last : 相当于Apache的[L]标记，表示完成rewrite
break : 停止执行当前虚拟主机的后续rewrite指令集
redirect : 返回302临时重定向，地址栏会显示跳转后的地址
permanent : 返回301永久重定向，地址栏会显示跳转后的地址
因为301和302不能简单的只返回状态码，还必须有重定向的URL，这就是return指令无法返回301,302的原因了。这里 last 和 break 
区别有点难以理解：

last一般写在server和if中，而break一般使用在location中
last不终止重写后的url匹配，即新的url会再从server走一遍匹配流程，而break终止重写后的匹配
break和last都能组织继续执行后面的rewrite指令
if指令与全局变量
if判断指令
语法为if(condition){...}，对给定的条件condition进行判断。如果为真，大括号内的rewrite指令将被执行，if条件(conditon)可
以是如下任何内容：

当表达式只是一个变量时，如果值为空或任何以0开头的字符串都会当做false
直接比较变量和内容时，使用=或!=
~正则表达式匹配，~*不区分大小写的匹配，!~区分大小写的不匹配
-f和!-f用来判断是否存在文件
-d和!-d用来判断是否存在目录
-e和!-e用来判断是否存在文件或目录
-x和!-x用来判断文件是否可执行

例如：

if ($http_user_agent ~ MSIE) {
    rewrite ^(.*)$ /msie/$1 break;
} //如果UA包含"MSIE"，rewrite请求到/msid/目录下

if ($http_cookie ~* "id=([^;]+)(?:;|$)") {
    set $id $1;
 } //如果cookie匹配正则，设置变量$id等于正则引用部分

if ($request_method = POST) {
    return 405;
} //如果提交方法为POST，则返回状态405（Method not allowed）。return不能返回301,302if ($slow) {
    limit_rate 10k;
} //限速，$slow可以通过 set 指令设置

if (!-f $request_filename){
    break;
    proxy_pass  http://127.0.0.1; 
} //如果请求的文件名不存在，则反向代理到localhost 。这里的break也是停止rewrite检查

if ($args ~ post=140){
    rewrite ^ http://example.com/ permanent;
} //如果query string中包含"post=140"，永久重定向到example.com

location ~* \.(gif|jpg|png|swf|flv)$ {
    valid_referers none blocked www.jefflei.com www.leizhenfang.com;
    if ($invalid_referer) {
        return 404;
    } //防盗链
}
全局变量
下面是可以用作if判断的全局变量

$args ： #这个变量等于请求行中的参数，同$query_string
$content_length ： 请求头中的Content-length字段。
$content_type ： 请求头中的Content-Type字段。
$document_root ： 当前请求在root指令中指定的值。
$host ： 请求主机头字段，否则为服务器名称。
$http_user_agent ： 客户端agent信息
$http_cookie ： 客户端cookie信息
$limit_rate ： 这个变量可以限制连接速率。
$request_method ： 客户端请求的动作，通常为GET或POST。
$remote_addr ： 客户端的IP地址。
$remote_port ： 客户端的端口。
$remote_user ： 已经经过Auth Basic Module验证的用户名。
$request_filename ： 当前请求的文件路径，由root或alias指令与URI请求生成。
$scheme ： HTTP方法（如http，https）。
$server_protocol ： 请求使用的协议，通常是HTTP/1.0或HTTP/1.1。
$server_addr ： 服务器地址，在完成一次系统调用后可以确定这个值。
$server_name ： 服务器名称。
$server_port ： 请求到达服务器的端口号。
$request_uri ： 包含请求参数的原始URI，不包含主机名，如：”/foo/bar.php?arg=baz”。
$uri ： 不带请求参数的当前URI，$uri不包含主机名，如”/foo/bar.html”。
$document_uri ： 与$uri相同。
例：http://localhost:88/test1/test2/test.php
$host：localhost
$server_port：88
$request_uri：http://localhost:88/test1/test2/test.php
$document_uri：/test1/test2/test.php
$document_root：/var/www/html
$request_filename：/var/www/html/test1/test2/test.php

常用正则
. ： 匹配除换行符以外的任意字符
? ： 重复0次或1次
+ ： 重复1次或更多次
* ： 重复0次或更多次
\d ：匹配数字
^ ： 匹配字符串的开始
$ ： 匹配字符串的介绍
{n} ： 重复n次
{n,} ： 重复n次或更多次
[c] ： 匹配单个字符c
[a-z] ： 匹配a-z小写字母的任意一个
小括号()之间匹配的内容，可以在后面通过$1来引用，$2表示的是前面第二个()里的内容。正则里面容易让人困惑的是\转义特殊字符。

rewrite实例
例1：

rewrite ^ http://staticwww.dachuizichan.com$request_uri? permanent;   域名重定向

http {
    # 定义image日志格式log_format imagelog '[$time_local] ' $image_file ' ' $image_type ' ' $body_bytes_sent ' ' 
    $status;
    # 开启重写日志rewrite_log on;

    server {
        root /home/www;

        location / {
                # 重写规则信息error_log logs/rewrite.log notice; 
                # 注意这里要用‘’单引号引起来，避免{}rewrite '^/images/([a-z]{2})/([a-z0-9]{5})/(.*)\.(png|jpg|gif)$' 
                /data?file=$3.$4;
                # 注意不能在上面这条规则后面加上“last”参数，否则下面的set指令不会执行set $image_file $3;
                set $image_type $4;
        }
        

        location /data {
                # 指定针对图片的日志格式，来分析图片类型和大小access_log logs/images.log mian;
                root /data/images;
                # 应用前面定义的变量。判断首先文件在不在，不在再判断目录在不在，如果还不在就跳转到最后一个url里try_files
                 /$arg_file /image404.html;
        }
        location = /image404.html {
                # 图片不存在返回特定的信息return 404 "image not found\n";
        }
}

对形如/images/ef/uh7b3/test.png的请求，重写到/data?file=test.png，于是匹配到location /data，先看/data/images/test.png
文件存不存在，如果存在则正常响应，如果不存在则重写tryfiles到新的image404 location，直接返回404状态码。

例2：

rewrite ^/images/(.*)_(\d+)x(\d+)\.(png|jpg|gif)$ /resizer/$1.$4?width=$2&height=$3? last;
对形如/images/bla_500x400.jpg的文件请求，重写到/resizer/bla.jpg?width=500&height=400地址，并会继续尝试匹配location。

正则匹配的参数，$1表示第一个()内的正则匹配内容，$2为第二个，以此类推。
```



## nginx忽略参数
```
例如：
把http://example.com/test.php?para=xxx 重定向到 http://example.com/new
若按照默认的写法：rewrite ^/test.php(.*) /new permanent;
重定向后的结果是：http://example.com/new?para=xxx
如果改写成：rewrite ^/test.php(.*) /new? permanent;
那结果就是：http://example.com/new
 
所以，关键点就在于“？”这个尾缀。假如又想保留某个特定的参数，那又该如何呢？可以利用Nginx本身就带有的$arg_PARAMETER参数来实现。
 
例如：
把http://example.com/test.php?para=xxx&p=xx 重写向到 http://example.com/new?p=xx
可以写成：rewrite  ^/test.php   /new?p=$arg_p?  permanent;


rewrite  ^/test.php  /new  permanent;       //重写向带参数的地址
rewrite  ^/test.php  /new?  permanent;      //重定向后不带参数
rewrite  ^/test.php   /new?id=$arg_id?  permanent;    //重定向后带指定的参数
permanent是永久重定向参数，根据需要去掉也可以，不过最好是带有。

if ($args) {     不做判断会循环rewrite
                rewrite ^/(.*) /$1? permanent;    忽略后面的参数
            }
```



## 配置cdn后做限制
```
http {    放到http下
# for pre-open closed test
map $http_x_forwarded_for $allowed {
    default deny;
    ~\s*111.222.333.444$ allow;
    ~\s*123.456.789.*$   allow;
}
} 
location / {
    if ($allowed = "deny") { return 403; }
    alias /path/to/document_root
}

===========================================
nginx http_realip_module模块
location = /getRealip.php
        {
                set_real_ip_from  192.168.50.0/24;
                set_real_ip_from  61.22.22.22;
                set_real_ip_from  121.207.33.33;
                set_real_ip_from 127.0.0.1;
                real_ip_header    X-Forwarded-For;
                real_ip_recursive on;
                fastcgi_pass  unix:/var/run/phpfpm.sock;
                fastcgi_index index.php;
                include fastcgi.conf;
        }
set_real_ip_from：真实服务器上一级代理的IP地址或者IP段,可以写多行
real_ip_header：从哪个header头检索出要的IP地址
real_ip_recursive：递归排除IP地址,ip串从右到左开始排除set_real_ip_from里面出现的IP,如果出现了未出现这些ip段的IP，
那么这个IP将被认为是用户的IP。例如我这边的例子，真实服务器获取到的IP地址串如下：
120.22.11.11,61.22.22.22,121.207.33.33,192.168.50.121
在real_ip_recursive on的情况下
61.22.22.22,121.207.33.33,192.168.50.121都出现在set_real_ip_from中,仅仅120.22.11.11没出现,那么他就被认为是用户的ip地址，
并且赋值到remote_addr变量
在real_ip_recursive off或者不设置的情况下
192.168.50.121出现在set_real_ip_from中,排除掉，接下来的ip地址便认为是用户的ip地址
如果仅仅如下配置：
    set_real_ip_from   192.168.50.0/24;
    set_real_ip_from 127.0.0.1;
    real_ip_header    X-Forwarded-For;
    real_ip_recursive on;
访问结果如下：
   121.207.33.33
使用realip获取
优点：程序不需要改动，直接使用remote_addr即可获取IP地址
缺点：ip地址有可能被伪装，而且需要知道所有CDN节点的ip地址或者ip段
或者 set_real_ip_from 0.0.0.0/0; 待验证
```



## 反向代理
```
http {
… …
client_max_body_size 300m;
#允许客户端请求的最大单个文件字节数，它出现在请求头部的 Content-Length 字段。 （可以更改此参数达到限制用户上传文件大小的目的）
client_body_buffer_size 128k;
#这个指令可以指定连接请求使用的缓冲区大小，默认值：8k/16k 。如果客户端请求一个文
件大于 128k，则 Nginx 会尝试在硬盘上创建临时文件。如果硬盘满了，则会报错。
client_body_temp_path /dev/shm/client_body_temp;
#这个指令指定连接请求试图写入缓存文件的目录路径。
proxy_connect_timeout 600;
#跟后端服务器连接的超时时间，发起握手等候响应超时时间
proxy_read_timeout 600;
#默认值：proxy_read_timeout 60。决定读取后端服务器应答的超时时间，它决定 nginx 将
等待多久时间来取得一个请求的应答。超时时间是指完成了两次握手后并且状态为 established 的超
时时间，而不是所有的应答时间。 相对于 proxy_connect_timeout，这个时间可以扑捉到一台将你
的连接放入连接池延迟处理并且没有数据传送的服务器，注意不要将此值设置太低，某些情况下代理
服务器将花很长的时间来获得页面应答 。如果被代理服务器在设置的时间内没有传递数据，nginx
将关闭连接。
proxy_send_timeout 600;
#设置代理服务器转发请求的超时时间，同样指完成两次握手后的时间，如果超过这个时间代
理服务器没有数据转发到后端服务器，nginx 将关闭连接。
proxy_buffer_size 16k;
#默认值：proxy_buffer_size 4k/8k 。设置从后端服务器读取的第一部分应答的缓冲区大小，
通常情况下这部分应答中包含一个小的应答头。
proxy_buffers 4 32k;
#设置用于读取应答（来自后端服务器）的缓冲区数目和大小，告诉 Nginx 保存单个用的几个
Buffer，最大用多大空间
proxy_busy_buffers_size 64k;
#如果系统很忙的时候可以申请更大的 proxy_buffers，官方推荐*2
proxy_temp_file_write_size 64k;
#设置在写入 proxy_temp_path 时缓存临文件数据的大小，在预防一个工作进程在传递文件
时阻塞太长。
proxy_temp_path /dev/shm/proxy_temp;
#类似于 http 核心模块中的 client_body_temp_path 指令，指定一个目录来缓冲比较大的被
代理请求。
upstream server_pool  {
server 192.168.0.88:80 weight=4 max_fails=2 fail_timeout=30s;
server 192.168.0.89:80 weight=2 max_fails=2 fail_timeout=30s;
}
#HTTP 负载均衡模块。upstream 这个字段设置一群服务器，可以将这个字段放在
proxy_pass 和 fastcgi_pass 指令中作为一个单独的实体，它们可以是监听不同端口的服务器，并且
也可以是同时监听 TCP和 Unix socket 的服务器。 服务器可以指定不同的权重，默认为 1。

location / {
proxy_pass http://server_pool/;
#确定需要代理的 URL，端口或 socket。
proxy_redirect off;
#如果需要修改从后端服务器传来的应答头中的"Location"和"Refresh"字段，可以用这个指令
设置。
proxy_set_header X-Real-IP $remote_addr;
#这个指令允许将发送到后端服务器的请求头重新定义或者增加一些字段。 这个值可以是一个
文本，变量或者它们的组合。
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header Host $host;
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503
http_504 http_404;
#确定在何种情况下请求将转发到下一个服务器：
#error - 在连接到一个服务器，发送一个请求，或者读取应答时发生错误。
#timeout - 在连接到服务器，转发请求或者读取应答时发生超时。
#invalid_header - 服务器返回空的或者错误的应答。
#http_500 - 服务器返回 500 代码。
#http_502 - 服务器返回 502 代码。
#http_503 - 服务器返回 503 代码。
#http_504 - 服务器返回 504 代码。
#http_404 - 服务器返回 404 代码。
#off - 禁止转发请求到下一台服务器。
}

Nginx 的 upstream 目前支持 5 种方式的分配
1 　轮询（默认）
每个请求按时间顺序逐一分配到不同的后端服务器，如果后端服务器 down 掉，能自
动剔除。
2 　 weight
指定轮询几率， weight 和访问比率成正比，用于后端服务器性能不均的情况。
例如：
upstream bakend {
server 192.168.0.88 weight=10;
server 192.168.0.89 weight=10;
}
3 　 ip_hash
每个请求按访问 ip 的 hash 结果分配，这样每个访客固定访问一个后端服务器，可以
解决 session 的问题。
例如：
upstream bakend {
ip_hash;
或者  hash $http_x_forwarded_for;  前面还有cdn
server 192.168.0.88:80;
server 192.168.0.89:80;
}
4 　 fair （第三方）
按后端服务器的响应时间来分配请求，响应时间短的优先分配。
例如：
upstream bakend {
server 192.168.0.88:80;
server 192.168.0.89:80;
fair;
}
5 　 url_hash （第三方）
按访问 url 的 hash 结果来分配请求，使每个 url 定向到同一个后端服务器，后端服务
器为缓存时比较有效。
例如：
upstream backend {
server 192.168.0.88:3128;
server 192.168.0.89:3128;
hash $request_uri;
或者  hash $http_x_forwarded_for;  前面还有cdn
#hash_method crc32;
}
每个设备的状态设置为 :
1. down  表示单前的 server 暂时不参与负载
2. weight  默认为 1.weight 越大，负载的权重就越大。
3. max_fails  ：允许请求失败的次数默认为 1. 当超过最大次数时，返回
proxy_next_upstream  模块定义的错误
4. fail_timeout:max_fails 次失败后，暂停的时间。
5. backup ： 其它所有的非 backup 机器 down 或者忙的时候，请求 backup 机器。
所以这台机器压力会最轻。
Nginx 支持同时设置多组的负载均衡，用来给不用的 server 来使用。

```



## proxy_pass
```
           sub_filter 'www_servers:80/DaChui/' 'www.xxx.com/';
           sub_filter 'http://www_servers:80/DaChui/' 'http://www.xxx.com/';
           sub_filter 'http://www_servers/DaChui/' 'http://www.xxx.com/';
           sub_filter_once off;

在nginx中配置proxy_pass代理转发时，如果在proxy_pass后面的url加/，表示绝对根路径；如果没有/，表示相对路径，
把匹配的路径部分也给代理走。

代理非80端口问题 需要添加 proxy_set_header Host $host:$server_port
upstream falcon {
        server 172.31.20.205:8010;
}
location / {
            proxy_pass http://falcon/;
            proxy_set_header Host $host:$server_port;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

假设下面四种情况分别用 http://192.168.1.1/proxy/test.html 进行访问。


第一种：
location /proxy/ {
    proxy_pass http://127.0.0.1/;
}
代理到URL：http://127.0.0.1/test.html


第二种（相对于第一种，最后少一个 / ）
location /proxy/ {
    proxy_pass http://127.0.0.1;
}
代理到URL：http://127.0.0.1/proxy/test.html


第三种：
location /proxy/ {
    proxy_pass http://127.0.0.1/aaa/;
}
代理到URL：http://127.0.0.1/aaa/test.html


第四种（相对于第三种，最后少一个 / ）
location /proxy/ {
    proxy_pass http://127.0.0.1/aaa;
}
代理到URL：http://127.0.0.1/aaatest.html
```



## 用户认证
```
/etc/nginx/conf.d/default.conf
location /logio {
        proxy_pass http://192.168.1.2:28778/;
        auth_basic "secret";
        auth_basic_user_file /etc/nginx/passwd.db;
    }
语法:     auth_basic string | off;
默认值:     auth_basic off;
配置段:     http, server, location, limit_except
默认表示不开启认证，后面如果跟上字符，这些字符会在弹窗中显示。
语法:     auth_basic_user_file file;
默认值:     —
配置段:     http, server, location, limit_except

htpasswd -c /etc/nginx/passwd.db admin   用户密码文件
chmod 400 /etc/nginx/passwd.db
chown nginx.nginx /etc/nginx/passwd.db
 
/etc/init.d/nginx reload
```



## root和alias
```
location /img/ {
    alias /var/www/image/;
}
#若按照上述配置的话，则访问/img/目录里面的文件时，ningx会自动去/var/www/image/目录找文件

location /img/ {
    root /var/www/image;
}
#若按照这种配置的话，则访问/img/目录下的文件时，nginx会去/var/www/image/img/目录下找文件

alias是一个目录别名的定义，root则是最上层目录的定义。

还有一个重要的区别是alias后面必须要用“/”结束，否则会找不到文件的   而root则可有可无
```



## nginx限速
```
在nginx.conf的http{}添加
#ip limit
limit_conn_zone $binary_remote_addr zone=perip:10m;
limit_conn_zone $server_name zone=perserver:10m;
然后在location里写

location / {
  limit_conn perip 2;
  limit_conn perserver 20;
  limit_rate 100k;
}

补充说明下参数：
$binary_remote_addr是限制同一客户端ip地址；
$server_name是限制同一server最大并发数；
limit_conn为限制并发连接数；
limit_rate为限制下载速度；

nginx 1.1.8 之后的版本的语法改为limit_conn_zone $binary_remote_addr zone=NAME:10m;

NAME 就是 zone 的名字详情请看这里 http://nginx.org/en/docs/http/ngx_http_limit_conn_module.html



限制连接数:

要限制连接，必须先有一个容器对连接进行计数，在http段加入如下代码：

"zone=" 给它一个名字，可以随便叫，这个名字要跟下面的 limit_conn 一致

$binary_remote_addr = 用二进制来储存客户端的地址，1m 可以储存 32000 个并发会话



... 省掉 N 字

http

{

limit_conn_zone $binary_remote_addr zone=addr:10m;



接下来需要对server不同的位置（location段）进行限速，比如限制每个IP并发连接数为1，则

server

{

listen 80;

server_name 192.168.11.128;

index index.html index.htm index.php;

limit_conn addr 1; #是限制每个IP只能发起1个连接 （addr 要跟 limit_conn_zone 的变量对应）

limit_rate 100k; #限速为 100KB/秒

root html;



注意事项：

limit_rate 100k; //是对每个连接限速100k。这里是对连接限速，而不是对IP限速！如果一个IP允许两个并发连接，
那么这个IP就是限速limit_rate * 2
```



## 压测 nginx性能调优
```
这边有个性能要求极高的api要上线，这个服务端是golang http模块实现的。在上线之前我们理所当然的要做压力测试。
起初是 “小白同学” 起头进行压力测试，但当我看到那压力测试的结果时，我也是逗乐了。   现象是，直接访问
Golang http api是每秒可以到3.5W的访问,  为了理论承受更强的QPS，多开了几个go http api进程端口，又在这前面
加了层nginx负载均衡，结果往nginx压测的结果是每秒才可以解决1.5w的访问量。 这结果让高级黑 “小白” 把nginx又给鄙视了。 

     虽然哥平时开发任务很饱和，又因为带几个新人的原因，有点心累。 但哥还是抽出宝贵的时间来解决nginx在压力测试下性能上
     不去的问题。 哈哈，这里肯定有人要打我了。  说实话，做运维虽然能时常碰一些负载均衡调度器，但由于很多时候配置都
     标准化了，新开一个业务线，把配置一scp，然后选择性的修改域名及location就可以了，还真是没遇到过这次的问题。 



我们在寻找性能瓶颈的是时候，会频繁的使用后面的工具进行监控，推荐大家使用tmux或者screen开启多个终端监控，用top可以看到
nginx及go api的cpu占用率，load值，run数，各个cpu核心的百分比，处理网络的中断。用dstat可以看到流量及上下文切换的测试。
  ss + netstat 查看连接数。



首先是压力测试的方法问题



以前做运维的时候，我们一般不会用简单的ab来进行压测，这样会造成压力源过热的情况，正常的针对服务端测试的方法是，分布式压力测试，
一个主机压测的结果很是不准，当然前提是 服务端的性能够高，别尼玛整个python django就用分布式压测，随便找个webbench,ab , 
boom这类的http压测就可以了。 



    关于客户端压测过热的情况有几个元素，最主要的元素是端口占用情况。首先我们需要明确几个点, 作为服务端只是消耗fd而已，
    但是客户端是需要占用端口来发起请求。 如果你自己同时作为服务端和客户端，会被受限于65535-1024的限制，1024内一般是
    常规的系统保留端口。   如果你按照65535-1024计算的话，你可以占用64511端口数，但如果你是自己压力测试nginx，然后
    nginx又反向代理几个golang http api。  那么这端口被严重的缩水了。   当你压测的数目才6w以上，很明显报错，
    不想报错，那么只能进行排队阻塞，好让客户端完成该请求。 



另外一点是nginx 配置问题。

   这一点很重要，也是最基本的要求，如果nginx worker连接数过少的化，你的请求连接就算没有被阻塞到backlog队列外，
   nginx worker也会因为过载保护不会处理新的请求。nginx的最大连接数是worker num *worker_connections, 
   默认worker_connections是1024, 直接干到10w就可以了。



在我们配置调整之后，访问的速度有明显的提升，但还是没有达到我们的预期。 接着通过lsof追了下进程，发现nginx 跟 
后端创建了大量的连接。  这很明显是没有使用http1.1长连接导致的，使用tcpdump抓包分析了下，果然是http1.0短链接，
虽然我们在sysctl内核里做了一些网络tcp回收的优化，但那也赶不上压力测试带来的频繁创建tcp的消耗。   果然在upstream加了keepalive。



COMMAND     PID        USER   FD   TYPE    DEVICE SIZE/OFF NODE NAME
python      538 ruifengyun    9u  IPv4 595559383      0t0  TCP 58.215.141.194:46665->58.215.141.83:9001 (ESTABLISHED)
test_dic4  7476 ruifengyun    5u  IPv6 660251515      0t0  TCP *:9001 (LISTEN)
test_dic4  7476 ruifengyun   10u  IPv6 660870187      0t0  TCP localhost:9001->localhost:46679 (ESTABLISHED)
test_dic4  7476 ruifengyun   13u  IPv6 660870138      0t0  TCP localhost:9001->localhost:46608 (ESTABLISHED)
test_dic4  7476 ruifengyun   14u  IPv6 660870137      0t0  TCP localhost:9001->localhost:46607 (ESTABLISHED)
test_dic4  7476 ruifengyun   22u  IPv6 660870153      0t0  TCP localhost:9001->localhost:46632 (ESTABLISHED)
test_dic4  7476 ruifengyun   23u  IPv6 660870143      0t0  TCP localhost:9001->localhost:46618 (ESTABLISHED)
test_dic4  7476 ruifengyun   27u  IPv6 660870166      0t0  TCP localhost:9001->localhost:46654 (ESTABLISHED)
test_dic4  7476 ruifengyun   73u  IPv6 660870191      0t0  TCP localhost:9001->localhost:46685 (ESTABLISHED)
test_dic4  7476 ruifengyun   85u  IPv6 660870154      0t0  TCP localhost:9001->localhost:46633 (ESTABLISHED)
test_dic4  7476 ruifengyun   87u  IPv6 660870147      0t0  TCP localhost:9001->localhost:46625 (ESTABLISHED)
....






摘录官方文档的说明如下。该参数开启与上游服务器之间的连接池，其数值为每个nginx worker可以保持的最大连接数，
默认不设置，即nginx作为客户端时keepalive未生效。

Activates cache of connections to upstream servers

The connections parameter sets the maximum number of idle keepalive connections to upstream servers 
that are retained in the cache per one worker process. When this number is exceeded, the least recently 
used connections are closed

Python


# xiaorui.cc
upstream http_backend {
    server 127.0.0.1:8080;

    keepalive 256;
}
server {
    ...

    location /http/ {
        proxy_pass http://http_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        ...
    }
}



继续进行压力测试，返现这访问量还是那样，没有什么提升，通过排除问题确认又是连接数大引起的，这长连接不生效呀。 
以前我在线上也是这么调配的，应该没问题。  最后通过nginx error log找到了原因。  这Nginx版本居然不支持keepalive 
长连接，没招，换个版本再次测试。




Python



2016/06/24 16:34:12 [error] 15419#0: *9421660 connect() failed (111: Connection refused) while connecting 
to upstream, client: 10.1.1.58, server: , request: "GET / HTTP/1.0", upstream: "http://127.0.0.1:9001/", 
host: "10.1.1.63"
2016/06/24 16:34:12 [error] 15418#0: *9423639 connect() failed (111: Connection refused) while connecting
 to upstream, client: 10.1.1.58, server: , request: "GET / HTTP/1.0", upstream: "http://127.0.0.1:9004/", 
 host: "10.1.1.63"
2016/06/24 16:34:12 [error] 15418#0: *9423639 no live upstreams while connecting to upstream, client: 
10.1.1.58, server: , request: "GET / HTTP/1.0", upstream: "http://test_servers/", host: "10.1.1.63"
2016/06/24 16:34:12 [error] 15418#0: *9393899 connect() failed (111: Connection refused) while connecting
 to upstream, client: 10.1.1.58, server: , request: "GET / HTTP/1.0", upstream: "http://127.0.0.1:9004/",
  host: "10.1.1.63"

2016/06/24 16:58:13 [notice] 26449#26449: signal process started
2016/06/24 16:58:13 [emerg] 27280#0: unknown directive "keepalive" in /etc/nginx/conf.d/test_multi.conf:7
2016/06/24 17:02:18 [notice] 3141#3141: signal process started
2016/06/24 17:02:18 [emerg] 27280#0: unknown directive "keepalive" in /etc/nginx/conf.d/test_multi.conf:7
2016/06/24 17:02:44 [notice] 4079#4079: signal process started
2016/06/24 17:02:44 [emerg] 27280#0: unknown directive "keepalive" in /etc/nginx/conf.d/test_multi.conf:7


简单描述下nginx upstream keepalive是个怎么一回事?   

默认情况下 Nginx 访问后端都是用的短连接(HTTP1.0)，一个请求来了，Nginx 新开一个端口和后端建立连接，请求结束连接回收。

如过配置了http 1.1长连接，那么Nginx会以长连接保持后端的连接，如果并发请求超过了 keepalive 指定的最大连接数，Nginx 
会启动新的连接 来转发请求，新连接在请求完毕后关闭，而且新建立的连接是长连接。



下图是nginx upstream keepalive长连接的实现原理.

首先每个进程需要一个connection pool，里面都是长连接，多进程之间是不需要共享这个连接池的。 一旦与后端服务器建立连接，
则在当前请求连接结束之后不会立即关闭连接，而是把用完的连接保存在一个keepalive connection pool里面，以后每次需要建立
向后连接的时候，只需要从这个连接池里面找，如果找到合适的连接的话，就可以直接来用这个连接，不需要重新创建socket或者发起
connect()。这样既省下建立连接时在握手的时间消耗，又可以避免TCP连接的slow start。如果在keepalive连接池找不到合适的连接
那就按照原来的步骤重新建立连接。 我没有看过nginx在连接池中查找可用连接的代码，但是我自己写过redis，mysqldb的连接池代码，
逻辑应该都是一样的。谁用谁pop，用完了再push进去，这样时间才O(1)。 

如果你的连接池的数控制在128，但因为你要应对更多的并发请求，所以临时又加了很多的连接，但这临时的连接是短连接和长连接要
看你的nginx版本，我这1.8是长连接，那他如何被收回，两地保证，一点是他会主动去释放，另一点是keepalive timeout的时间。







Golang的http模块貌似对http spdy支持不怎么好， 要不然可以直接用淘宝的tengine upstream spdy的方式连接后端Server。 
他的速度要比keepalive要好的多，毕竟省去了等待上次返回的结果的过程。
```



## nginx_rtmp hls
```
docker项目 https://github.com/brocaar/nginx-rtmp-dockerfile

ffmpeg要源码安装，ubuntu可以用apt源安装
二进制版  http://johnvansickle.com/ffmpeg/
wget http://johnvansickle.com/ffmpeg/builds/ffmpeg-git-64bit-static.tar.xz

配置rpmforce源
mkdir /data && mkdir /static
yum install ffmpeg wget pcre-devel zlib-devel openssl-devel
wget http://nginx.org/download/nginx-1.6.2.tar.gz && tar zxf nginx-1.6.2.tar.gz
wget https://github.com/arut/nginx-rtmp-module/archive/v1.1.6.tar.gz && tar zxf v1.1.6.tar.gz
cd nginx-1.6.2 && ./configure --add-module=../nginx-rtmp-module-1.1.6 --prefix=/usr/local/nginx
make && make install

nginx配置文件
daemon  off;
events {
    worker_connections 1024;
}
rtmp {
    server {
        listen 1935;
        chunk_size 4000;
        application encoder {
            live on;
            exec ffmpeg -i rtmp://localhost:1935/encoder/$name
              -c:a libfdk_aac -b:a 128k -c:v libx264 -b:v 2500k -f flv -g 30 -r 30 -s 1280x720 -preset 
              superfast -profile:v baseline rtmp://localhost:1935/hls/$name_720p2628kbs
              -c:a libfdk_aac -b:a 128k -c:v libx264 -b:v 1000k -f flv -g 30 -r 30 -s 854x480 -preset 
              superfast -profile:v baseline rtmp://localhost:1935/hls/$name_480p1128kbs
              -c:a libfdk_aac -b:a 128k -c:v libx264 -b:v 750k -f flv -g 30 -r 30 -s 640x360 -preset 
              superfast -profile:v baseline rtmp://localhost:1935/hls/$name_360p878kbs
              -c:a libfdk_aac -b:a 128k -c:v libx264 -b:v 400k -f flv -g 30 -r 30 -s 426x240 -preset 
              superfast -profile:v baseline rtmp://localhost:1935/hls/$name_240p528kbs
              -c:a libfdk_aac -b:a 64k -c:v libx264 -b:v 200k -f flv -g 15 -r 15 -s 426x240 -preset 
              superfast -profile:v baseline rtmp://localhost:1935/hls/$name_240p264kbs;
        }
        application hls {
            live on;
            hls on;
            hls_fragment_naming system;
            hls_fragment 5s;
            hls_path /data/hls;
            hls_nested on;
            hls_variant _720p2628kbs BANDWIDTH=2628000,RESOLUTION=1280x720;
            hls_variant _480p1128kbs BANDWIDTH=1128000,RESOLUTION=854x480;
            hls_variant _360p878kbs BANDWIDTH=878000,RESOLUTION=640x360;
            hls_variant _240p528kbs BANDWIDTH=528000,RESOLUTION=426x240;
            hls_variant _240p264kbs BANDWIDTH=264000,RESOLUTION=426x240;
        }
    }
}
http {
    server {
        listen 80;
        location /hls {
            types {
                application/vnd.apple.mpegurl m3u8;
                video/mp2t ts;
            }
            root /data;
            add_header Cache-Control no-cache;
            add_header Access-Control-Allow-Origin *;
        }
        location /stat {
            rtmp_stat all;
            rtmp_stat_stylesheet static/stat.xsl;
        }
        location /static {
            alias /static;
        }
        location /crossdomain.xml {
            default_type text/xml;
            return 200 '<?xml version="1.0"?>
                <!DOCTYPE cross-domain-policy SYSTEM "http://www.adobe.com/xml/dtds/cross-domain-policy.dtd">
                <cross-domain-policy>
                    <site-control permitted-cross-domain-policies="all"/>
                    <allow-access-from domain="*" secure="false"/>
                    <allow-http-request-headers-from domain="*" headers="*" secure="false"/>
                </cross-domain-policy>';
            expires 24h;
        }
    }
}


------------------------------
cat /static/stat.xsl

<?xml version="1.0" encoding="utf-8" ?>
<!--
   Copyright (C) Roman Arutyunyan
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
    <html>
        <head>
            <title>RTMP statistics</title>
        </head>
        <body>
            <xsl:apply-templates select="rtmp"/>
            <hr/>
            Generated by <a href='https://github.com/arut/nginx-rtmp-module'>
            nginx-rtmp-module</a>&#160;<xsl:value-of select="/rtmp/nginx_rtmp_version"/>,
            <a href="http://nginx.org">nginx</a>&#160;<xsl:value-of select="/rtmp/nginx_version"/>,
            pid <xsl:value-of select="/rtmp/pid"/>,
            built <xsl:value-of select="/rtmp/built"/>&#160;<xsl:value-of select="/rtmp/compiler"/>
        </body>
    </html>
</xsl:template>
<xsl:template match="rtmp">
    <table cellspacing="1" cellpadding="5">
        <tr bgcolor="#999999">
            <th>RTMP</th>
            <th>#clients</th>
            <th colspan="4">Video</th>
            <th colspan="4">Audio</th>
            <th>In bytes</th>
            <th>Out bytes</th>
            <th>In bits/s</th>
            <th>Out bits/s</th>
            <th>State</th>
            <th>Time</th>
        </tr>
        <tr>
            <td colspan="2">Accepted: <xsl:value-of select="naccepted"/></td>
            <th bgcolor="#999999">codec</th>
            <th bgcolor="#999999">bits/s</th>
            <th bgcolor="#999999">size</th>
            <th bgcolor="#999999">fps</th>
            <th bgcolor="#999999">codec</th>
            <th bgcolor="#999999">bits/s</th>
            <th bgcolor="#999999">freq</th>
            <th bgcolor="#999999">chan</th>
            <td>
                <xsl:call-template name="showsize">
                    <xsl:with-param name="size" select="bytes_in"/>
                </xsl:call-template>
            </td>
            <td>
                <xsl:call-template name="showsize">
                    <xsl:with-param name="size" select="bytes_out"/>
                </xsl:call-template>
            </td>
            <td>
                <xsl:call-template name="showsize">
                    <xsl:with-param name="size" select="bw_in"/>
                    <xsl:with-param name="bits" select="1"/>
                    <xsl:with-param name="persec" select="1"/>
                </xsl:call-template>
            </td>
            <td>
                <xsl:call-template name="showsize">
                    <xsl:with-param name="size" select="bw_out"/>
                    <xsl:with-param name="bits" select="1"/>
                    <xsl:with-param name="persec" select="1"/>
                </xsl:call-template>
            </td>
            <td/>
            <td>
                <xsl:call-template name="showtime">
                    <xsl:with-param name="time" select="/rtmp/uptime * 1000"/>
                </xsl:call-template>
            </td>
        </tr>
        <xsl:apply-templates select="server"/>
    </table>
</xsl:template>
<xsl:template match="server">
    <xsl:apply-templates select="application"/>
</xsl:template>
<xsl:template match="application">
    <tr bgcolor="#999999">
        <td>
            <b><xsl:value-of select="name"/></b>
        </td>
    </tr>
    <xsl:apply-templates select="live"/>
    <xsl:apply-templates select="play"/>
</xsl:template>
<xsl:template match="live">
    <tr bgcolor="#aaaaaa">
        <td>
            <i>live streams</i>
        </td>
        <td align="middle">
            <xsl:value-of select="nclients"/>
        </td>
    </tr>
    <xsl:apply-templates select="stream"/>
</xsl:template>
<xsl:template match="play">
    <tr bgcolor="#aaaaaa">
        <td>
            <i>vod streams</i>
        </td>
        <td align="middle">
            <xsl:value-of select="nclients"/>
        </td>
    </tr>
    <xsl:apply-templates select="stream"/>
</xsl:template>
<xsl:template match="stream">
    <tr valign="top">
        <xsl:attribute name="bgcolor">
            <xsl:choose>
                <xsl:when test="active">#cccccc</xsl:when>
                <xsl:otherwise>#dddddd</xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
        <td>
            <a href="">
                <xsl:attribute name="onclick">
                    var d=document.getElementById('<xsl:value-of select="../../name"/>-<xsl:value-of select="name"/>');
                    d.style.display=d.style.display=='none'?'':'none';
                    return false
                </xsl:attribute>
                <xsl:value-of select="name"/>
                <xsl:if test="string-length(name) = 0">
                    [EMPTY]
                </xsl:if>
            </a>
        </td>
        <td align="middle"> <xsl:value-of select="nclients"/> </td>
        <td>
            <xsl:value-of select="meta/video/codec"/>&#160;<xsl:value-of select="meta/video/profile"/>&#160;
            <xsl:value-of select="meta/video/level"/>
        </td>
        <td>
            <xsl:call-template name="showsize">
                <xsl:with-param name="size" select="bw_video"/>
                <xsl:with-param name="bits" select="1"/>
                <xsl:with-param name="persec" select="1"/>
            </xsl:call-template>
        </td>
        <td>
            <xsl:apply-templates select="meta/video/width"/>
        </td>
        <td>
            <xsl:value-of select="meta/video/frame_rate"/>
        </td>
        <td>
            <xsl:value-of select="meta/audio/codec"/>&#160;<xsl:value-of select="meta/audio/profile"/>
        </td>
        <td>
            <xsl:call-template name="showsize">
                <xsl:with-param name="size" select="bw_audio"/>
                <xsl:with-param name="bits" select="1"/>
                <xsl:with-param name="persec" select="1"/>
            </xsl:call-template>
        </td>
        <td>
            <xsl:apply-templates select="meta/audio/sample_rate"/>
        </td>
        <td>
            <xsl:value-of select="meta/audio/channels"/>
        </td>
        <td>
            <xsl:call-template name="showsize">
               <xsl:with-param name="size" select="bytes_in"/>
           </xsl:call-template>
        </td>
        <td>
            <xsl:call-template name="showsize">
                <xsl:with-param name="size" select="bytes_out"/>
            </xsl:call-template>
        </td>
        <td>
            <xsl:call-template name="showsize">
                <xsl:with-param name="size" select="bw_in"/>
                <xsl:with-param name="bits" select="1"/>
                <xsl:with-param name="persec" select="1"/>
            </xsl:call-template>
        </td>
        <td>
            <xsl:call-template name="showsize">
                <xsl:with-param name="size" select="bw_out"/>
                <xsl:with-param name="bits" select="1"/>
                <xsl:with-param name="persec" select="1"/>
            </xsl:call-template>
        </td>
        <td><xsl:call-template name="streamstate"/></td>
        <td>
            <xsl:call-template name="showtime">
               <xsl:with-param name="time" select="time"/>
            </xsl:call-template>
        </td>
    </tr>
    <tr style="display:none">
        <xsl:attribute name="id">
            <xsl:value-of select="../../name"/>-<xsl:value-of select="name"/>
        </xsl:attribute>
        <td colspan="16" ngcolor="#eeeeee">
            <table cellspacing="1" cellpadding="5">
                <tr>
                    <th>Id</th>
                    <th>State</th>
                    <th>Address</th>
                    <th>Flash version</th>
                    <th>Page URL</th>
                    <th>SWF URL</th>
                    <th>Dropped</th>
                    <th>Timestamp</th>
                    <th>A-V</th>
                    <th>Time</th>
                </tr>
                <xsl:apply-templates select="client"/>
            </table>
        </td>
    </tr>
</xsl:template>
<xsl:template name="showtime">
    <xsl:param name="time"/>
    <xsl:if test="$time &gt; 0">
        <xsl:variable name="sec">
            <xsl:value-of select="floor($time div 1000)"/>
        </xsl:variable>
        <xsl:if test="$sec &gt;= 86400">
            <xsl:value-of select="floor($sec div 86400)"/>d
        </xsl:if>
        <xsl:if test="$sec &gt;= 3600">
            <xsl:value-of select="(floor($sec div 3600)) mod 24"/>h
        </xsl:if>
        <xsl:if test="$sec &gt;= 60">
            <xsl:value-of select="(floor($sec div 60)) mod 60"/>m
        </xsl:if>
        <xsl:value-of select="$sec mod 60"/>s
    </xsl:if>
</xsl:template>
<xsl:template name="showsize">
    <xsl:param name="size"/>
    <xsl:param name="bits" select="0" />
    <xsl:param name="persec" select="0" />
    <xsl:variable name="sizen">
        <xsl:value-of select="floor($size div 1024)"/>
    </xsl:variable>
    <xsl:choose>
        <xsl:when test="$sizen &gt;= 1073741824">
            <xsl:value-of select="format-number($sizen div 1073741824,'#.###')"/> T</xsl:when>
        <xsl:when test="$sizen &gt;= 1048576">
            <xsl:value-of select="format-number($sizen div 1048576,'#.###')"/> G</xsl:when>
        <xsl:when test="$sizen &gt;= 1024">
            <xsl:value-of select="format-number($sizen div 1024,'#.##')"/> M</xsl:when>
        <xsl:when test="$sizen &gt;= 0">
            <xsl:value-of select="$sizen"/> K</xsl:when>
    </xsl:choose>
    <xsl:if test="string-length($size) &gt; 0">
        <xsl:choose>
            <xsl:when test="$bits = 1">b</xsl:when>
            <xsl:otherwise>B</xsl:otherwise>
        </xsl:choose>
        <xsl:if test="$persec = 1">/s</xsl:if>
    </xsl:if>
</xsl:template>
<xsl:template name="streamstate">
    <xsl:choose>
        <xsl:when test="active">active</xsl:when>
        <xsl:otherwise>idle</xsl:otherwise>
    </xsl:choose>
</xsl:template>
<xsl:template name="clientstate">
    <xsl:choose>
        <xsl:when test="publishing">publishing</xsl:when>
        <xsl:otherwise>playing</xsl:otherwise>
    </xsl:choose>
</xsl:template>
<xsl:template match="client">
    <tr>
        <xsl:attribute name="bgcolor">
            <xsl:choose>
                <xsl:when test="publishing">#cccccc</xsl:when>
                <xsl:otherwise>#eeeeee</xsl:otherwise>
            </xsl:choose>
        </xsl:attribute>
        <td><xsl:value-of select="id"/></td>
        <td><xsl:call-template name="clientstate"/></td>
        <td>
            <a target="_blank">
                <xsl:attribute name="href">
                    http://apps.db.ripe.net/search/query.html&#63;searchtext=<xsl:value-of select="address"/>
                </xsl:attribute>
                <xsl:attribute name="title">whois</xsl:attribute>
                <xsl:value-of select="address"/>
            </a>
        </td>
        <td><xsl:value-of select="flashver"/></td>
        <td>
            <a target="_blank">
                <xsl:attribute name="href">
                    <xsl:value-of select="pageurl"/>
                </xsl:attribute>
                <xsl:value-of select="pageurl"/>
            </a>
        </td>
        <td><xsl:value-of select="swfurl"/></td>
        <td><xsl:value-of select="dropped"/></td>
        <td><xsl:value-of select="timestamp"/></td>
        <td><xsl:value-of select="avsync"/></td>
        <td>
            <xsl:call-template name="showtime">
               <xsl:with-param name="time" select="time"/>
            </xsl:call-template>
        </td>
    </tr>
</xsl:template>
<xsl:template match="publishing">
    publishing
</xsl:template>
<xsl:template match="active">
    active
</xsl:template>
<xsl:template match="width">
    <xsl:value-of select="."/>x<xsl:value-of select="../height"/>
</xsl:template>
</xsl:stylesheet>
```
