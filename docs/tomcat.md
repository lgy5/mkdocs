## java字体和验证码问题
```
中文字体
yum install cjkuni* dejavu* -y

报错java.lang.Error: Probable fatal error:No fonts found.
缺少字体
在国外网站上找到如下方式解决：
under Ubuntu you can install fonts by
    sudo apt-get install ttf-dejavu
or if you use CentOS, you can install fonts by
    yum install dejavu*
由于是CenterOS系统，所以执行
# yum install dejavu*
安装完字体后，再访问验证码链接就能正常显示了。
```



## tomcat优化
```
内存相关，避免内存溢出，又要尽可能利用内存资源
linux修改TOMCAT_HOME/bin/catalina.sh，在前面加入
8G为例：
JAVA_OPTS="-server -Xms4G -Xmx4G  -XX:MaxNewSize=2G  -XX:+UseConcMarkSweepGC -XX:+UseParNewGC -XX:PermSize=1G 
-XX:MaxPermSize=1G  -Djava.awt.headless=true -Dfile.encoding=UTF8 -Dsun.jnu.encoding=UTF8"


-server  启用jdk 的 server 版； 
-Xms    java虚拟机初始化时的最小内存，最好接近于Xmx，避免过多内存交换
-Xmx   java虚拟机可使用的最大内存； 可用内存的80%
-Xss
每个线程的栈的大小，减少这个值可以生成更多的线程。但是操作系统对一个进程内的线程数还是有限制的，不能无限制生成。如果程序
没有报StackOverFlow，可以设置成128K。
-XX:PermSize    内存永久保留区域 
-XX:MaxPermSize   内存最大永久保留区域

windows修改TOMCAT_HOME/bin/catalina.bat，在前面加入
set JAVA_OPTS=-Xms512m -Xmx512m -Xss1024k -XX:MaxNewSize=256M -XX:MaxPermSize=1024M 参数同linux

连接并发相关：
配置文件conf/server.xml
<Connector port="8080" protocol="HTTP/1.1"
        maxHttpHeaderSize="8192"  客户端Http请求、响应的Header的最大限制
        maxThreads="1000"        客户请求最大线程数
        minSpareThreads="100"     Tomcat初始化时创建的 socket 线程数
        maxSpareThreads="1000"   Tomcat连接器的最大空闲 socket 线程数
        minProcessors="100"    最小连接线程数，用于提高系统处理性能，默认值为 10
        maxProcessors="1000"  最大连接线程数，即：并发处理的最大请求数，默认值为 75
        enableLookups="false"      禁用DNS查询
compression="on"    打开压缩功能
        compressionMinSize="2048"  启用压缩的输出内容大小，默认为2KB
compressableMimeType="text/html,text/xml,text/javascript,text/css,text/plain"
压缩类型
        connectionTimeout="20000" 
网络连接超时，0 表示永不超时，这样设置有隐患的。通常可设置为30000 毫秒
        URIEncoding="utf-8"   URL统一编码
        acceptCount="1000"  允许的最大连接数，应等于 maxProcessors ，默认值为 100
        redirectPort="8443"  重定向端口，默认即可
        disableUploadTimeout="true"/>  关闭数据上载的超时时间，默认为false
其中和最大连接数相关的参数为maxProcessors 和 acceptCount 。如果要加大并发连接数，应同时加大这两个参数，webserver允许的
最大连接数还受制于操作系统的内核参数设置，通常Windows是2000个左右，Linux是1000个左右

运行模式：
1)bio  默认的模式,性能非常低下,没有经过任何优化处理和支持.
2)nio  利用java的异步io护理技术,no blocking IO技术.
想运行在该模式下，直接修改server.xml里的Connector节点,修改protocol为
<Connector port="80" protocol="org.apache.coyote.http11.Http11NioProtocol"
    connectionTimeout="20000"
    redirectPort="8443" />    重启后,就可以生效。
3)apr 安装起来最困难,但是从操作系统级别来解决异步的IO问题,大幅度的提高性能.
必须要安装apr和native，直接启动就支持apr。下面的修改纯属多余，仅供大家扩充知识,但仍然需要安装apr和native
如nio修改模式,修改protocol为org.apache.coyote.http11.Http11AprProtocol
Apr插件提高Tomcat性能（linux）
在产品环境中，特别是直接使用Tomcat做WEB服务器的时候，应该使用Tomcat Native来提高其性能 
  要测APR给tomcat带来的好处最好的方法是在慢速网络上（模拟Internet），将Tomcat线程数开到300以上的水平，然后模拟一大堆并发请求。
  如果不配APR，基本上300个线程狠快就会用满，以后的请求就只好等待。但是配上APR之后，并发的线程数量明显下降，从原来的300可能
  会马上下降到只有几十，新的请求会毫无阻塞的进来。
  在局域网环境测，就算是400个并发，也是一瞬间就处理/传输完毕，但是在真实的Internet环境下，页面处理时间只占0.1%都不到，绝大
  部分时间都用来页面传输。如果不用APR，一个线程同一时间只能处理一个用户，势必会造成阻塞。所以生产环境下用apr是非常必要的。
(1)安装APR tomcat-native
    apr-1.3.8.tar.gz   安装在/usr/local/apr
    #tar zxvf apr-1.3.8.tar.gz
    #cd apr-1.3.8
    #./configure;make;make install
    apr-util-1.3.9.tar.gz  安装在/usr/local/apr/lib
    #tar zxvf apr-util-1.3.9.tar.gz
    #cd apr-util-1.3.9 
    #./configure --with-apr=/usr/local/apr ----with-java-home=JDK;make;make install
    #cd apache-tomcat-6.0.20/bin 
    #tar zxvf tomcat-native.tar.gz 
    #cd tomcat-native/jni/native 
    #./configure --with-apr=/usr/local/apr;make;make install
  (2)设置 Tomcat 整合 APR
    修改 tomcat 的启动 shell （startup.sh），在该文件中加入启动参数：
      CATALINA_OPTS="$CATALINA_OPTS  -Djava.library.path=/usr/local/apr/lib" 。
  (3)判断安装成功:
    如果看到下面的启动日志，表示成功。
      INFO: Loaded APR based Apache Tomcat Native library

server.xml ：
<Executor name="tomcatThreadPool" namePrefix="catalina-exec-"
        maxThreads="3000" minSpareThreads="200"/>

<Connector executor="tomcatThreadPool" port="8080" protocol="org.apache.coyote.http11.Http11AprProtocol"
               connectionTimeout="20000000"
               redirectPort="8443" URIEncoding="UTF-8"
               enableLookups="false"
               useURIValidationHack="false"
           disableUploadTimeout="false"
               maxHttpHeaderSize="65536" 
               maxPostSize="52428800"/>
```



## java项目监控
```
javamelody
https://github.com/javamelody/javamelody/wiki/UserGuide#javamelody-setup
```



## java时间不一致
```
tomcat日志时间和系统不一样

jre是从/etc/sysconfig/clock这个文件中 获取时区信息的。

附clock文件内容：

ZONE="Asia/Shanghai"
UTC=false
ARC=false

ZONE -- 时区
UTC  -- 表明时钟设置为UTC。 
ARC  -- 仅用于alpha表明使用ARC。　　　　　　
```



## redis session共享
```
https://github.com/jcoleman/tomcat-redis-session-manager

切换选择不同版本  附件是java1.6  tomcat7
https://github.com/izerui/tomcat-redis-session-manager   tomca7  java1.7 

安装好redis   2.8版本以上

grandle构建      ../gradle-2.1/bin/gradle build
build.gradle
apply plugin: 'java'
version = '1.1'

repositories {
  mavenCentral()
}

dependencies {
  compile group: 'org.apache.tomcat', name: 'tomcat-catalina', version: '7.0.67'
  compile group: 'redis.clients', name: 'jedis', version: '2.5.2'
  compile group: 'org.apache.commons', name: 'commons-pool2', version: '2.2'
  // testCompile group: 'junit', name: 'junit', version: '4.+'
}



tomcat  conf/context.xml
<Valve className="com.radiadesign.catalina.session.RedisSessionHandlerValve" />   路径根据
tomcat-redis-session jar包文件路径修改
    <Manager className="com.radiadesign.catalina.session.RedisSessionManager" 
         host="192.168.1.5" 
         port="6379" 
         database="0" 
         maxInactiveInterval="60" />

 tomca7  java1.7 

<Valve className="com.orangefunction.tomcat.redissessions.RedisSessionHandlerValve" />
     <Manager className="com.orangefunction.tomcat.redissessions.RedisSessionManager"
      host="localhost"
      port="6379"
      database="0"
      maxInactiveInterval="60"
      sessionPersistPolicies="PERSIST_POLICY_1,PERSIST_POLICY_2,.."    session保存策略，可选项
      sentinelMaster="SentinelMasterName"                 redis集群主节点名称
      sentinels="sentinel-host-1:port,sentinel-host-2:port,.."/>          redis集群列表配置     



java.lang.IllegalArgumentException: setAttribute: Non-serializable attribute registerLoginUser
session需要序列化
```



## java进程使用cpu过高
```
根据top命令，发现PID为28555的Java进程占用CPU高达200%，出现故障。
通过ps aux | grep PID命令，可以进一步确定是tomcat进程出现了问题。但是，怎么定位到具体线程或者代码呢？
首先显示线程列表:
ps -mp pid -o THREAD,tid,time
1
找到了耗时最高的线程28802，占用CPU时间快两个小时了！
其次将需要的线程ID转换为16进制格式：
printf "%x\n" tid
2
最后打印线程的堆栈信息：
jstack pid |grep tid -A 30
```



## 日志切割
```
logroute处理  最简单
cat /etc/logrotate.d/tomcat
/usr/local/tomcat_pingtai/logs/catalina.out {
   copytruncate   拷贝后截断，把当前log拷贝后截断。可以理解为把内容拷贝走作为备份,然后清空当前文件
   daily      按天切割
   dateext     日期格式
   rotate 30   保留30个，之前的删除
   missingok    在日志轮循期间，任何错误将被忽略，例如“文件无法找到”之类的错误
   notifempty    如果日志文件为空，轮循不会进行
}


1. 下载安装 cronolog，它的主页 http://cronolog.org . 下载的是源码，安装过程就是 ./configure, make, make install，
最后一步可直接把 src/cronolog 执行文件拷入到某个适合的目录，如 /usr/local/sbin/ 目录

或者 yum install cronolog -y

2. 编辑 bin/catalina.sh 文件

    1）找到下面行并把它用 # 注释掉

touch "$CATALINA_BASE"/logs/catalina.out
Tomcat7 的 bin/catalina.sh 文件要注释的行是  touch "$CATALINA_OUT"

    2）删除下面的行，有两处，并添加新的

>> "$CATALINA_BASE"/logs/catalina.out 2>&1 &   
    为

2>&1 | /usr/sbin/cronolog "$CATALINA_BASE/logs/catalina-%Y-%m-%d.out" &

Tomcat7 的 bin/catalina.sh 中是需要替换行是

>> "$CATALINA_OUT" 2>&1 "&"
替换后该行的内容与上面是一样的。

为什么 Tomcat7 后会有所不同，因为在它的 catalina.sh 文件中有如下定义
CATALINA_OUT="$CATALINA_BASE"/logs/catalina.out

3. 保存 catalina.sh 文件，重启 Tomcat 即可。

以后看到 $TOMCAT_HOME/logs/ 下的就是 catalina-2012-09-16.out, catalina-2012-09-17.out ...... 一系列文件，
将不会产生 catalina.out 文件了
```



## oracle jdk
```
rpm -ivh jdk-7u79-linux-x64.rpm 
/etc/profile 添加  或者家目录的环境变量
export JAVA_HOME=/usr/java/latest/
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar

. /etc/profile
java -version
```



## 多tomcat管理脚本
    #!/bin/bash  
    # author: Sean Chow (seanlook7@gmail.com)
    # 
    #  
    # chkconfig: 345 80 15  
    # description: Multiple tomcats service management script.  

    # Source function library.  
    . /etc/rc.d/init.d/functions  
    # 第几个tomcat
    tcNo=$1
    tcName=tomcat$1
    basedir=/apps/test/$tcName
    tclog=${basedir}/logs/catalina.$(date +%Y-%m-%d).out
    RETVAL=0  

    start(){
            checkrun  
            if [ $RETVAL -eq 0 ]; then  
                    echo "-- Starting tomcat..."  
                    $basedir/bin/startup.sh  
                    touch /var/lock/subsys/${tcNo}
                    checklog 
                    status
            else  
                    echo "-- tomcat already running"  
            fi  
    }  
    # 停止某一台tomcat，如果是重启则带re参数，表示不查看日志，等待启动时再提示查看  
    stop(){
            checkrun  
            if [ $RETVAL -eq 1 ]; then  
                    echo "-- Shutting down tomcat..."  
                    $basedir/bin/shutdown.sh  
                    if [ "$1" != "re" ]; then
                      checklog
                    else
                      sleep 5
                    fi
                    rm -f /var/lock/subsys/${tcNo} 
                    status
            else  
                    echo "-- tomcat not running"  
            fi  
    }  

    status(){
            checkrun
            if [ $RETVAL -eq 1 ]; then
                    echo -n "-- Tomcat ( pid "  
                    ps ax --width=1000 |grep ${tcName}|grep "org.apache.catalina.startup.Bootstrap start" |
                       awk '{printf $1 " "}'
                    echo -n ") is running..."  
                    echo  
            else
                    echo "-- Tomcat is stopped"  
            fi
            #echo "---------------------------------------------"  
    }
    # 查看tomcat日志，带vl参数
    log(){
            status
            checklog yes
    }
    # 如果tomcat正在运行，强行杀死tomcat进程，关闭tomcat
    kill(){
            checkrun
            if [ $RETVAL -eq 1 ]; then
                read -p "-- Do you really want to kill ${tcName} progress?[no])" answer
                case $answer in
                    Y|y|YES|yes|Yes)
                        ps ax --width=1000 |grep ${tcName}|grep "org.apache.catalina.startup.Bootstrap start" | 
                                                                               awk '{printf $1 " "}'|xargs kill -9  
                        status
                    ;;
                    *);;
                esac
            else
                echo "-- exit with $tcName still running..."
            fi
    }
    checkrun(){  
            ps ax --width=1000 |grep ${tcName}| grep "[o]rg.apache.catalina.startup.Bootstrap start" | 
                            awk '{printf $1 " "}' | wc | awk '{print $2}' >/tmp/tomcat_process_count.txt  
            read line < /tmp/tomcat_process_count.txt  
            if [ $line -gt 0 ]; then  
                    RETVAL=1  
                    return $RETVAL  
            else  
                    RETVAL=0  
                    return $RETVAL  
            fi  
    }  
    # 如果是直接查看日志viewlog，则不提示输入[yes]，否则就是被stop和start调用，需提示是否查看日志
    checklog(){
            answer=$1
            if [ "$answer" != "yes" ]; then
                read -p "-- See Catalina.out log to check $2 status?[yes])" answer
            fi
            case $answer in
                Y|y|YES|yes|Yes|"")
                    tail -f ${tclog}
                ;;
                *)
                #    status
                #    exit 0
                ;;
            esac
    }
    checkexist(){
            if [ ! -d $basedir ]; then
                echo "-- tomcat $basedir does not exist."
                exit 0
            fi
    }


    case "$2" in  
    start)  
            checkexist
            start  
            exit 0
            ;;  
    stop)  
            checkexist
            stop  
            exit 0
            ;;  
    restart)  
            checkexist
            stop re 
            start 
            exit 0
            ;;  
    status)  
            checkexist
            status  
            #$basedir/bin/catalina.sh version  
            exit 0
            ;;  
    log)
            checkexist
            log
            exit 0
            ;;
    kill)
            checkexist
            status
            kill
            exit 0
            ;;
    *)  
            echo "Usage: $0 {start|stop|restart|status|log|kill}"  
            echo "       service tomcat {0|1|..} {start|stop|restart|status|log|kill}"  
            esac  

    exit 0
    使用说明：

    使用前设定好baseDir（多tomcat所在路径），各tomcat命名如tomcat0、tomcat1…
    脚本名字为tomcat，放到/etc/init.d/下，并基于可执行权限chmod +x /etc/init.d/tomcat
    执行用户不允许用root，特别是在线上环境
    已处理其他错误参数输入，可用于正式环境
    你也可以修改tcName来适应管理一个tomcat服务的情形
    使用，以下针对tomcat0（/apps/test/tomcat0）

    service tomcat 0 start   启动，默认回车会查看启动日志；已启动则仅输出进程号
    service tomcat 0 stop    停止，默认回车会查看日志；已停止则无动作；无法停止，则提示是否`kill`（默认No）
    service tomcat 0 restart 重启tomcat，有日志输出
    service tomcat 0 status  查看tomcat是否启动
    service tomcat 0 log     使用`tail -f`命令实时查看日志
    service tomcat 0 kill    直接`kill`tomcat进程；尽量少用
    TO-DO
    加入service tomcat 0 clean命令来清除work和tmp目录，正在运行的不允许清除。

    这个脚本最近（2014/11/13）在使用过程中发现一个新的问题，因为服务器上tomcat一直开启着监控端口7091，所
    以在service tomcat 1 start失败以后，7091端口就被占用了，但使用service tomcat 1 status状态时stopped，
    其实还是有这个失败的tomcat进程，但用service tomcat 1 kill会失败。脚本里在考虑这个功能的话就有点臃肿了，还是老实结合手动管理吧。



## tomcat跳转
```
我们输入http://10.138.16.232:8080，访问的是tomcat的首页，我们只需要对tomcat的首页进行加工即可。修改方法如下：
 
修改原有tomcat页面；  /usr/local/tomcat/webapps/ROOT/index.html  用js跳转
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<script language="javascript">
    window.location.href="/abc";  #也可以是完整url
</script>
</html>
```



## nginx+tomat ssl
```
nginx tomcat reverse proxy schema
nginx config

daemon off;
worker_processes  2;
error_log /var/log/nginx_error.log info;
user bananos staff;
events {
    worker_connections  1024;
}
http {
    include /opt/nginx/conf/mime.types;
    default_type application/octet-stream;
    log_format main '$remote_addr - $remote_user [$time_local] "$request" $status $bytes_sent "$http_referer" 
           "$http_user_agent" "$gzip_ratio"';
    ignore_invalid_headers on;
    index index.html;
    client_header_timeout 240;
    client_body_timeout 240;
    send_timeout 240;
    client_max_body_size 100m;
    proxy_buffer_size 128k;
    proxy_buffers 8 128k;
    upstream tomcat_server {
    # Tomcat is listening on default 8080 port
        server 127.0.0.1:8080 fail_timeout=0;
    }
    server {
        server_name localhost;
        listen 443;
        ssl on;
        ssl_session_timeout 5m;
        ssl_protocols SSLv2 SSLv3 TLSv1;
        #make sure you already have this certificate pair!
        ssl_certificate /var/certs/server.crt;
        ssl_certificate_key /var/certs/server.key;
        ssl_session_cache shared:SSL:10m;
    # www-root, we're serving static files from here, accessible via https://localhost/
        location / {
            root  /var/www;
            index index.html index.htm;
        }
    # Our endpoint for tomcat reverse-proxy, assuming your endpoint java-servlet knows
    # how to handle http://localhost/gadgets  requests
        location /gadgets {
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto https;
            proxy_redirect off;
            proxy_connect_timeout      240;
            proxy_send_timeout         240;
            proxy_read_timeout         240;
            # note, there is not SSL here! plain HTTP is used
       proxy_pass http://tomcat_server;
        }
     }
}

Tomcat config
And here the magic begins, the main point to not miss here is

Tomcat needs to be explicitly told that it’s being proxied through 443(SSL) port!

Here is a sample Tomcat config which is usually found at


{$CATALINA_HOME}/conf/server.xml


<?xml version='1.0' encoding='utf-8'?>
<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<!-- Note:  A "Server" is not itself a "Container", so you may not
     define subcomponents such as "Valves" at this level.
     Documentation at /docs/config/server.html
 -->
<Server port="8005" shutdown="SHUTDOWN">
  <!-- Security listener. Documentation at /docs/config/listeners.html
  <Listener className="org.apache.catalina.security.SecurityListener" />
  -->
  <!--APR library loader. Documentation at /docs/apr.html -->
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <!--Initialize Jasper prior to webapps are loaded. Documentation at /docs/jasper-howto.html -->
  <Listener className="org.apache.catalina.core.JasperListener" />
  <!-- Prevent memory leaks due to use of particular java/javax APIs-->
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />

  <!-- Global JNDI resources
       Documentation at /docs/jndi-resources-howto.html
  -->

<!--  <GlobalNamingResources>-->
    <!-- Editable user database that can also be used by
         UserDatabaseRealm to authenticate users
    -->
<!--
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              description="User database that can be updated and saved"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources> -->

  <!-- A "Service" is a collection of one or more "Connectors" that share
       a single "Container" Note:  A "Service" is not itself a "Container",
       so you may not define subcomponents such as "Valves" at this level.
       Documentation at /docs/config/service.html
   -->
  <Service name="Catalina">

    <!--The connectors can use a shared executor, you can define one or more named thread pools-->
    <!--
    <Executor name="tomcatThreadPool" namePrefix="catalina-exec-"
        maxThreads="150" minSpareThreads="4"/>
    -->

    <!-- A "Connector" represents an endpoint by which requests are received
         and responses are returned. Documentation at :
         Java HTTP Connector: /docs/config/http.html (blocking & non-blocking)
         Java AJP  Connector: /docs/config/ajp.html
         APR (HTTP/AJP) Connector: /docs/apr.html
         Define a non-SSL HTTP/1.1 Connector on port 8080
    -->
    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443"
           proxyName="localhost"
               proxyPort="443"
               scheme="https"
                />
    <!-- A "Connector" using the shared thread pool-->
    <!--
    <Connector executor="tomcatThreadPool"
               port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" />
    -->
    <!-- Define a SSL HTTP/1.1 Connector on port 8443
         This connector uses the JSSE configuration, when using APR, the
         connector should be using the OpenSSL style configuration
         described in the APR documentation -->
    <!--
    <Connector port="8443" protocol="HTTP/1.1" SSLEnabled="true"
               maxThreads="150" scheme="https" secure="true"
               clientAuth="false" sslProtocol="TLS" />
    -->

    <!-- Define an AJP 1.3 Connector on port 8009 -->
  <!--  <Connector port="8009" protocol="AJP/1.3" redirectPort="8443" />-->

    <!-- An Engine represents the entry point (within Catalina) that processes
         every request.  The Engine implementation for Tomcat stand alone
         analyzes the HTTP headers included with the request, and passes them
         on to the appropriate Host (virtual host).
         Documentation at /docs/config/engine.html -->

    <!-- You should set jvmRoute to support load-balancing via AJP ie :
    <Engine name="Catalina" defaultHost="localhost" jvmRoute="jvm1">
    -->
    <Engine name="Catalina" defaultHost="localhost">

      <!--For clustering, please take a look at documentation at:
          /docs/cluster-howto.html  (simple how to)
          /docs/config/cluster.html (reference documentation) -->
      <!--
      <Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"/>
      -->        

      <!-- Use the LockOutRealm to prevent attempts to guess user passwords
           via a brute-force attack -->
<!--      <Realm className="org.apache.catalina.realm.LockOutRealm"> -->
        <!-- This Realm uses the UserDatabase configured in the global JNDI
             resources under the key "UserDatabase".  Any edits
             that are performed against this UserDatabase are immediately
             available for use by the Realm.  -->
<!--        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"    resourceName="UserDatabase"/>-->
<!--      </Realm>-->

      <Host name="localhost"  appBase="webapps"   unpackWARs="true" autoDeploy="true">

        <!-- SingleSignOn valve, share authentication between web applications
             Documentation at: /docs/config/valve.html -->
        <!--
        <Valve className="org.apache.catalina.authenticator.SingleSignOn" />
        -->

        <!-- Access log processes all example.
             Documentation at: /docs/config/valve.html
             Note: The pattern used is equivalent to using pattern="common" -->

        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log." suffix=".txt"
               pattern="%h %l %u %t "%r" %s %b" resolveHosts="false"/>

      </Host>
    </Engine>
  </Service>
</Server>

As it turned out proxyPort property was the key to proxying Tomcat via Nginx.
```



## tomcat内存溢出
```
Tomcat内存溢出的原因
　　在生产环境中tomcat内存设置不好很容易出现内存溢出。造成内存溢出是不一样的，当然处理方式也不一样。
　　这里根据平时遇到的情况和相关资料进行一个总结。常见的一般会有下面三种情况：
　　1.OutOfMemoryError： Java heap space
　　2.OutOfMemoryError： PermGen space
　　3.OutOfMemoryError： unable to create new native thread.
　　Tomcat内存溢出解决方案
　　对于前两种情况，在应用本身没有内存泄露的情况下可以用设置tomcat jvm参数来解决。（-Xms -Xmx -XX：PermSize -XX：MaxPermSize）
　　最后一种可能需要调整操作系统和tomcat jvm参数同时调整才能达到目的。
　　第一种：是堆溢出。
　　原因分析：
JVM堆的设置是指java程序运行过程中JVM可以调配使用的内存空间的设置.JVM在启动的时候会自动设置Heap size的值，
其初始空间(即-Xms)是物理内存的1/64，最大空间(-Xmx)是物理内存的1/4。可以利用JVM提供的-Xmn -Xms -Xmx等选项可进行设置。
Heap size 的大小是Young Generation 和Tenured Generaion 之和。
在JVM中如果98％的时间是用于GC且可用的Heap size 不足2％的时候将抛出此异常信息。
Heap Size 最大不要超过可用物理内存的80％，一般的要将-Xms和-Xmx选项设置为相同，而-Xmn为1/4的-Xmx值。
　　没有内存泄露的情况下，调整-Xms -Xmx参数可以解决。
　　-Xms：初始堆大小
　　-Xmx：最大堆大小
　　但堆的大小受下面三方面影响：
　　1.相关操作系统的数据模型（32-bt还是64-bit）限制；（32位系统下，一般限制在1.5G~2G；我在2003 server 系统下
（物理内存：4G和6G，jdk：1.6）测试 1612M，64位操作系统对内存无限制。）
　　2.系统的可用虚拟内存限制；
　　3.系统的可用物理内存限制。
　　堆的大小可以使用 java -Xmx***M version 命令来测试。支持的话会出现jdk的版本号，不支持会报错。
　　-Xms -Xmx一般配置成一样比较好比如set JAVA_OPTS= -Xms1024m -Xmx1024m

其初始空间(即-Xms)是物理内存的1/64，最大空间(-Xmx)是物理内存的1/4。可以利用JVM提供的-Xmn -Xms -Xmx等选项可
进行设置
实例，以下给出1G内存环境下java jvm 的参数设置参考：
JAVA_OPTS="-server -Xms800m -Xmx800m  -XX:PermSize=64M -XX:MaxNewSize=256m -XX:MaxPermSize=128m 
-Djava.awt.headless=true "
JAVA_OPTS="-server -Xms768m -Xmx768m -XX:PermSize=128m -XX:MaxPermSize=256m -XX:
NewSize=192m -XX:MaxNewSize=384m"
CATALINA_OPTS="-server -Xms768m -Xmx768m -XX:PermSize=128m -XX:MaxPermSize=256m
-XX:NewSize=192m -XX:MaxNewSize=384m"

服务器为1G内存：JAVA_OPTS="-server -Xms800m -Xmx800m -XX:PermSize=64M -XX:MaxNewSize=256m 
-XX:MaxPermSize=128m -Djava.awt.headless=true "
服务器为64位、2G内存: JAVA_OPTS='-server -Xms1024m -Xmx1536m -XX:PermSize=128M -XX:MaxNewSize=256m
 -XX:MaxPermSize=256m'

-------------------解决方案1：-----------------------------
前提：是执行startup.bat启动tomcat的方式
Linux服务器：
在/usr/local/apache-tomcat-5.5.23/bin 目录下的catalina.sh
添加：JAVA_OPTS='-Xms512m -Xmx1024m'
或者 JAVA_OPTS="-server -Xms800m -Xmx800m   -XX:MaxNewSize=256m"
或者 CATALINA_OPTS="-server -Xms256m -Xmx300m"
Windows服务器：
在catalina.bat最前面加入
set JAVA_OPTS=-Xms128m -Xmx350m
或者set CATALINA_OPTS=-Xmx300M -Xms256M
（区别是一个直接设置jvm内存， 另一个设置tomcat内存，CATALINA_OPTS似乎可以与JAVA_OPTS不加区别的使用）
基本参数说明
-client，-server
这两个参数用于设置虚拟机使用何种运行模式，一定要作为第一个参数，client模式启动比较快，但运行时性能和内存管理
效率不如server模式，通常用于客户端应用程序。相反，server模式启动比client慢，但可获得更高的运行性能。
在windows上，缺省的虚拟机类型为client模式，如果要使用server模式，就需要在启动虚拟机时加-server参数，以获得更
高性能，对服务器端应用，推荐采用server模式，尤其是多个CPU的系统。在Linux，Solaris上缺省采用server模式。
此外，在多cup下，建议用server模式

-Xms<size>
设置虚拟机可用内存堆的初始大小，缺省单位为字节，该大小为1024的整数倍并且要大于1MB，可用k(K)或m(M)为单位来设置较大的
内存数。初始堆大小为2MB。加“m”说明是MB，否则就是KB了。
例如：-Xms6400K，-Xms256M
-Xmx<size>
设置虚拟机 的最大可用大小，缺省单位为字节。该值必须为1024整数倍，并且要大于2MB。可用k(K)或m(M)为单位来设置较大的内存
数。缺省堆最大值为64MB。
例如：-Xmx81920K，-Xmx80M
当应用程序申请了大内存运行时虚拟机抛出java.lang.OutOfMemoryError: Java heap space错误，就需要使用-Xmx设置较大的可用内存堆。
PermSize/MaxPermSize：定义Perm段的尺寸，即永久保存区域的大小，PermSize为JVM启动时初始化Perm的内存大小；MaxPermSize为
最大可占用的Perm内存大小。在用户生产环境上一般将这两个值设为相同，以减少运行期间系统在内存申请上所花的开销。

如果用startup.bat启动tomcat,OK设置生效.够成功的分配200M内存.
-------------------解决方案2：------------------------
前提：是执行startup.bat启动tomcat的方式
手动设置Heap size
Windows服务器：
修改TOMCAT_HOME/bin/catalina.bat，在“echo "Using CATALINA_BASE: $CATALINA_BASE"”上面加入以下行：
Java代码
set JAVA_OPTS=%JAVA_OPTS% -server -Xms800m -Xmx800m -XX:MaxNewSize=256m 

    注：JAVA_OPTS是保留先前设置。
Linux服务器：
修改TOMCAT_HOME/bin/catalina.sh
在“echo "Using CATALINA_BASE: $CATALINA_BASE"”上面加入以下行：
JAVA_OPTS="$JAVA_OPTS -server -Xms800m -Xmx800m -XX:MaxNewSize=256m"

注：$JAVA_OPTS是保留先前设置。
-------------------解决方案3：-----------------------------
前提：是执行windows的系统服务启动tomcat的方式
但是如果不是执行startup.bat启动tomcat而是利用windows的系统服务启动tomcat服务,上面的设置就不生效了,
就是说set JAVA_OPTS=-Xms128m -Xmx350m 没起作用.上面分配200M内存就OOM了..
windows服务执行的是bin\tomcat.exe.他读取注册表中的值,而不是catalina.bat的设置.

解决办法:
修改注册表HKEY_LOCAL_MACHINE\SOFTWARE\Apache Software Foundation\Tomcat Service Manager\Tomcat5\Parameters\JavaOptions
原值为
-Dcatalina.home="C:\ApacheGroup\Tomcat 5.0"
-Djava.endorsed.dirs="C:\ApacheGroup\Tomcat 5.0\common\endorsed"
-Xrs
加入 -Xms300m -Xmx350m
重起tomcat服务,设置生效
-------------------解决方案4：-----------------------------
前提：是执行windows的系统服务启动tomcat的方式
在安装tomcat时若有勾选"NT Service(NT/2000/XP only)"
则安装完成后在安装目录的"bin"目录里会有一个tomcat.exe的档案
先把tomcat的服务停掉
在命令列模式下（运行里输入CMD）
将目录切换到tomcat的bin目录
用下面的命令把服务移除

tomcat -uninstall "Apache Tomcat 4.1"

接下来，写个批处理。
内容如下
set SERVICENAME=Apache Tomcat 4.1
set CATALINA_HOME=E:\Tomcat 4.1.24
set CLASSPATH=D:\j2sdk1.4.1_01\lib
set JAVACLASSPATH=%CLASSPATH%
set JAVACLASSPATH=%JAVACLASSPATH%;�TALINA_HOME%\bin\bootstrap.jar
set JAVACLASSPATH=%JAVACLASSPATH%;�TALINA_HOME%\common\lib\servlet.jar
set JAVACLASSPATH=%JAVACLASSPATH%;%JAVA_HOME%\lib\tools.jar
tomcat.exe -install "%SERVICENAME%" "%JAVA_HOME%\jre\bin\server\jvm.dll" -Djava.class.path="%JAVACLASSPATH%" 
-Dcatalina.home="�TALINA_HOME%" -Xms512m -Xmx768m -start org.apache.catalina.startup.Bootstrap -params start 
-stop org.apache.catalina.startup.Bootstrap -params stop -out "�TALINA_HOME%\logs\stdout.log" -err "�TALINA_HOME%\
logs\stderr.log"

注意，从 tomcat.exe -install开始的是最后一行！不要手工回车换行把这一行分成了好几段。保存后在命令行下执行这个bat文件，注
意执行的时候将“服务”窗口关闭。

第二种：永久保存区域溢出
　原因分析：
PermGen space的全称是Permanent Generation space,是指内存的永久保存区域，这块内存主要是被JVM存放Class和Meta信息的,
Class在被Loader时就会被放到PermGen space中，它和存放类实例(Instance)的Heap区域不同,GC(Garbage Collection)不会在
主程序运行期对PermGen space进行清理，所以如果你的应用中有很CLASS的话,就很可能出现PermGen space错误，这种错误常见在
web服务器对JSP进行pre compile的时候。如果你的WEB APP下都用了大量的第三方jar, 其大小超过了jvm默认的大小(4M)那么就会
产生此错误信息了。但目前的hibernate和spring项目中也很容易出现这样的问题。可能是由于这些框架会动态class，而且jvm的gc
是不会清理PemGen space的，超过了jvm默认的大小(4M)，导致内存溢出。
　　建议：将相同的第三方jar文件移置到tomcat/shared/lib目录下，这样可以达到减少jar 文档重复占用内存的目的。
这一个一般是加大-XX：PermSize -XX：MaxPermSize 来解决问题。
　　-XX：PermSize 永久保存区域初始大小
　　-XX：PermSize 永久保存区域初始最大值
　　这一般结合第一条使用，比如 set JAVA_OPTS= -Xms1024m -Xmx1024m -XX：PermSize=128M -XX：PermSize=256M
　　有一点需要注意：java -Xmx***M version 命令来测试的最大堆内存是 -Xmx与 -XX：PermSize的和 比如系统支持最大的jvm堆
大小事1.5G，那 -Xmx1024m -XX：PermSize=768M 是无法运行的。
-----------------解决方案1：-------------------------
Linux服务器：
在catalina.sh的第一行增加：
JAVA_OPTS=
-Xms64m
-Xmx256m
-XX:PermSize=128M
-XX:MaxNewSize=256m
-XX:MaxPermSize=256m
或者
在“echo "Using CATALINA_BASE:   $CATALINA_BASE"”上面加入以下行：
JAVA_OPTS="-server -XX:PermSize=64M -XX:MaxPermSize=128m
Windows服务器：
在catalina.bat的第一行增加：
set JAVA_OPTS=-Xms64m -Xmx256m -XX:PermSize=128M -XX:MaxNewSize=256m -XX:MaxPermSize=256m
-----------------解决方案2：------------------------
修改TOMCAT_HOME/bin/catalina.bat（Linux下为catalina.sh），在Java代码
“echo "Using CATALINA_BASE: $CATALINA_BASE"”上面加入以下行：  
set JAVA_OPTS=%JAVA_OPTS% -server -XX:PermSize=128M -XX:MaxPermSize=512m 

“echo "Using CATALINA_BASE: $CATALINA_BASE"”上面加入以下行：
set JAVA_OPTS=%JAVA_OPTS% -server -XX:PermSize=128M -XX:MaxPermSize=512m

catalina.sh下为：
Java代码
JAVA_OPTS="$JAVA_OPTS -server -XX:PermSize=128M -XX:MaxPermSize=512m"

JAVA_OPTS="$JAVA_OPTS -server -XX:PermSize=128M -XX:MaxPermSize=512m"

　　第三种：无法创建新的线程。
　　这种现象比较少见，也比较奇怪，主要是和jvm与系统内存的比例有关。
　　这种怪事是因为JVM已经被系统分配了大量的内存（比如1.5G），并且它至少要占用可用内存的一半。有人发现，在线程个数很多的
情况下，你分配给JVM的内存越多，那么，上述错误发生的可能性就越大。
　　原因分析
（从这个blog中了解到原因：http://hi.baidu.com/hexiong/blog/item/16dc9e518fb10c2542a75b3c.html）：
　　每一个32位的进程最多可以使用2G的可用内存，因为另外2G被操作系统保留。这里假设使用1.5G给JVM，那么还余下500M可用内存。
这500M内存中的一部分必须用于系统dll的加载，那么真正剩下的也许只有400M，现在关键的地方出现了：当你使用Java创建一个线程，
在JVM的内存里也会创建一个Thread对象，但是同时也会在操作系统里创建一个真正的物理线程（参考JVM规范），操作系统会在余下的 
400兆内存里创建这个物理线程，而不是在JVM的1500M的内存堆里创建。在jdk1.4里头，默认的栈大小是256KB，但是在jdk1.5里头，
默认的栈大小为1M每线程，因此，在余下400M的可用内存里边我们最多也只能创建400个可用线程。
　　这样结论就出来了，要想创建更多的线程，你必须减少分配给JVM的最大内存。还有一种做法是让JVM宿主在你的JNI代码里边。
　　给出一个有关能够创建线程的最大个数的估算公式：
　　（MaxProcessMemory - JVMMemory - ReservedOsMemory） / （ThreadStackSize） = Number of threads
　　对于jdk1.5而言，假设操作系统保留120M内存：
　　1.5GB JVM： （2GB-1.5Gb-120MB）/（1MB） = ~380 threads
　　1.0GB JVM： （2GB-1.0Gb-120MB）/（1MB） = ~880 threads
　　在2000/XP/2003的boot.ini里头有一个启动选项，好像是：/PAE /3G ，可以让用户进程最大内存扩充至3G，这时操作系统只能
占用最多1G的虚存。那样应该可以让JVM创建更多的线程。
　　因此这种情况需要结合操作系统进行相关调整。
　　因此：我们需要结合不同情况对tomcat内存分配进行不同的诊断才能从根本上解决问题。

检测当前JVM内存使用情况：
System.out.println("JVM MAX MEMORY: " + Runtime.getRuntime().maxMemory()/1024/1024+"M");
System.out.println("JVM IS USING MEMORY:" + Runtime.getRuntime().totalMemory()/1024/1024+"M");
System.out.println("JVM IS FREE MEMORY:" + Runtime.getRuntime().freeMemory()/1024/1024+"M");

这三个方法都是说JVM的内存使用情况而不是操作系统的内存；
　　maxMemory()这个方法返回的是java虚拟机（这个进程）能构从操作系统那里挖到的最大的内存，以字节为单位，如果在运行java程序的时
候，没有添加-Xmx参数，那么就是64兆，也就是说maxMemory()返回的大约是64*1024*1024字节，这是java虚拟机默认情况下能从操作系统
那里挖到的最大的内存。如果添加了-Xmx参数，将以这个参数后面的值为准，例如java -cp ClassPath -Xmx512m ClassName，那么最大内
存就是512*1024*0124字节。

　　totalMemory()这个方法返回的是java虚拟机现在已经从操作系统那里挖过来的内存大小，也就是java虚拟机这个进程当时所占用的所有
内存。如果在运行java的时候没有添加-Xms参数，那么，在java程序运行的过程的，内存总是慢慢的从操作系统那里挖的，基本上是用多少
挖多少，直挖到maxMemory()为止，所以totalMemory()是慢慢增大的。如果用了-Xms参数，程序在启动的时候就会无条件的从操作系统中
挖-Xms后面定义的内存数，然后在这些内存用的差不多的时候，再去挖。

　　freeMemory()是什么呢，刚才讲到如果在运行java的时候没有添加-Xms参数，那么，在java程序运行的过程的，内存总是慢慢的从操作
系统那里挖的，基本上是用多少挖多少，但是java虚拟机100％的情况下是会稍微多挖一点的，这些挖过来而又没有用上的内存，实际上就
是freeMemory()，所以freeMemory()的值一般情况下都是很小的，但是如果你在运行java程序的时候使用了-Xms，这个时候因为程序在
启动的时候就会无条件的从操作系统中挖-Xms后面定义的内存数，这个时候，挖过来的内存可能大部分没用上，所以这个时候freeMemory()可
能会有些
--------------------解决方案--------------------------
JVM堆大小的调整
　　Sun HotSpot 1.4.1使用分代收集器，它把堆分为三个主要的域：新域、旧域以及永久域。Jvm生成的所有新对象放在新域中。一旦对象
经历了一定数量的垃圾收集循环后，便获得使用期并进入旧域。在永久域中jvm则存储class和method对象。就配置而言，永久域是一个独立
域并且不认为是堆的一部分。
　　下面介绍如何控制这些域的大小。可使用-Xms和-Xmx 控制整个堆的原始大小或最大值。
　　下面的命令是把初始大小设置为128M：
　　java –Xms128m
　　–Xmx256m为控制新域的大小，可使用-XX:NewRatio设置新域在堆中所占的比例。
　　下面的命令把整个堆设置成128m，新域比率设置成3，即新域与旧域比例为1：3，新域为堆的1/4或32M：
java –Xms128m –Xmx128m
–XX:NewRatio =3可使用-XX:NewSize和-XX:MaxNewsize设置新域的初始值和最大值。
　　下面的命令把新域的初始值和最大值设置成64m:
java –Xms256m –Xmx256m –Xmn64m
　　永久域默认大小为4m。运行程序时，jvm会调整永久域的大小以满足需要。每次调整时，jvm会对堆进行一次完全的垃圾收集。
　　使用-XX:MaxPerSize标志来增加永久域搭大小。在WebLogic Server应用程序加载较多类时，经常需要增加永久域的最大值。当jvm加
载类时，永久域中的对象急剧增加，从而使jvm不断调整永久域大小。为了避免调整，可使用-XX:PerSize标志设置初始值。
　　下面把永久域初始值设置成32m，最大值设置成64m。
java -Xms512m -Xmx512m -Xmn128m -XX:PermSize=32m -XX:MaxPermSize=64m
　　默认状态下，HotSpot在新域中使用复制收集器。该域一般分为三个部分。第一部分为Eden，用于生成新的对象。另两部分称为救助空
间，当Eden充满时，收集器停止应用程序，把所有可到达对象复制到当前的from救助空间，一旦当前的from救助空间充满，收集器则把可
到达对象复制到当前的to救助空间。From和to救助空间互换角色。维持活动的对象将在救助空间不断复制，直到它们获得使用期并转入旧
域。使用-XX:SurvivorRatio可控制新域子空间的大小。
　　同NewRation一样，SurvivorRation规定某救助域与Eden空间的比值。比如，以下命令把新域设置成64m，Eden占32m，每个救助域各占16m：
java -Xms256m -Xmx256m -Xmn64m -XX:SurvivorRation =2
　　如前所述，默认状态下HotSpot对新域使用复制收集器，对旧域使用标记－清除－压缩收集器。在新域中使用复制收集器有很多意义，
因为应用程序生成的大部分对象是短寿命的。理想状态下，所有过渡对象在移出Eden空间时将被收集。如果能够这样的话，并且移出Eden空
间的对象是长寿命的，那么理论上可以立即把它们移进旧域，避免在救助空间反复复制。但是，应用程序不能适合这种理想状态，因为它们有
一小部分中长寿命的对象。最好是保持这些中长寿命的对象并放在新域中，因为复制小部分的对象总比压缩旧域廉价。为控制新域中对象的复
制，可用-XX:TargetSurvivorRatio控制救助空间的比例（该值是设置救助空间的使用比例。如救助空间位1M，该值50表示可用500K）。
该值是一个百分比，默认值是50。当较大的堆栈使用较低的sruvivorratio时，应增加该值到80至90，以更好利用救助空间。用
-XX:maxtenuring threshold可控制上限。
　　为放置所有的复制全部发生以及希望对象从eden扩展到旧域，可以把MaxTenuring Threshold设置成0。设置完成后，实际上就不再
使用救助空间了，因此应把SurvivorRatio设成最大值以最大化Eden空间，设置如下：
java … -XX:MaxTenuringThreshold=0 –XX:SurvivorRatio＝50000 …
垃圾回收描述：
垃圾回收分多级，0级为全部(Full)的垃圾回收，会回收OLD段中的垃圾；1级或以上为部分垃圾回收，只会回收Young中的垃圾，内存溢出
通常发生于OLD段或Perm段垃圾回收后，仍然无内存空间容纳新的Java对象的情况。
当一个URL被访问时，内存申请过程如下：
A. JVM会试图为相关Java对象在Eden中初始化一块内存区域
B. 当Eden空间足够时，内存申请结束。否则到下一步
C. JVM试图释放在Eden中所有不活跃的对象（这属于1或更高级的垃圾回收）；释放后若Eden空间仍然不足以放入新对象，则试图将部
分Eden中活跃对象放入Survivor区/OLD区
D. Survivor区被用来作为Eden及OLD的中间交换区域，当OLD区空间足够时，Survivor区的对象会被移到Old区，否则会被保留在Survivor区
E. 当OLD区空间不够时，JVM会在OLD区进行完全的垃圾收集（0级）
F. 完全垃圾收集后，若Survivor及OLD区仍然无法存放从Eden复制过来的部分对象，导致JVM无法在Eden区为新对象创建内存区域，
则出现”out of memory错误”
Java堆相关参数：
ms/mx：定义YOUNG+OLD段的总尺寸，ms为JVM启动时YOUNG+OLD的内存大小；mx为最大可占用的YOUNG+OLD内存大小。在用户生产环境
上一般将这两个值设为相同，以减少运行期间系统在内存申请上所花的开销。
NewSize/MaxNewSize：定义YOUNG段的尺寸，NewSize为JVM启动时YOUNG的内存大小；MaxNewSize为最大可占用的YOUNG内存大小。在
用户生产环境上一般将这两个值设为相同，以减少运行期间系统在内存申请上所花的开销。
PermSize/MaxPermSize：定义Perm段的尺寸，PermSize为JVM启动时Perm的内存大小；MaxPermSize为最大可占用的Perm内存大小。
在用户生产环境上一般将这两个值设为相同，以减少运行期间系统在内存申请上所花的开销。
SurvivorRatio：设置Survivor空间和Eden空间的比例
例：
MEM_ARGS="-Xms512m -Xmx512m -XX:NewSize=256m -XX:MaxNewSize=256m -XX:PermSize=128m -XX:MaxPermSize=128m 
-XX:SurvivorRatio=6"
在上面的例子中：
YOUNG+OLD: 512M
YOUNG: 256M
Perm: 128M
Eden: YOUNG*6/(6+1+1)=192M
Survivor: YOUNG/(6+1+1)=32M
Java堆的总尺寸=YOUNG+OLD+Perm=640M
```



## 多java版本
```
update-alternatives --config java
alternatives --config java

--disaplay java

```



