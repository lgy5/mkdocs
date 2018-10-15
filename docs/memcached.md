## memcache状态
```
telnet 127.0.0.1 11211
stats
或者
获取运行状态
echo stats | nc 192.168.1.123 11200
watch "echo stats | nc 192.168.1.123 11200" (实时状态)

memcache stats命令

stats 命令的功能正如其名：转储所连接的 memcached 实例的当前统计数据。在下例中，执行stats命令显示了关于当前 memcached 实例的信息：

STAT pid 22459                                     进程ID

STAT uptime 1027046                         服务器运行秒数

STAT time 1273043062                       服务器当前unix时间戳

STAT version 1.4.4                                服务器版本

STAT pointer_size 64                           操作系统(这台服务器是64位的)

STAT rusage_user 0.040000             进程累计用户时间

STAT rusage_system 0.260000        进程累计系统时间

STAT curr_connections 10                  当前打开连接数

STAT total_connections 82                 曾打开的连接总数

STAT connection_structures 13          服务器分配的连接结构数

STAT cmd_get 54                            执行get命令总数

STAT cmd_set 34                            执行set命令总数

STAT cmd_flush 3                           指向flush_all命令总数

STAT get_hits 9                            get命中次数

STAT get_misses 45                         get未命中次数

STAT delete_misses 5                       delete未命中次数

STAT delete_hits 1                         delete命中次数

STAT incr_misses 0                         incr未命中次数

STAT incr_hits 0                           incr命中次数

STAT decr_misses 0                         decr未命中次数

STAT decr_hits 0                           decr命中次数

STAT cas_misses 0                     cas未命中次数

STAT cas_hits 0                            cas命中次数

STAT cas_badval 0                          使用擦拭次数

STAT auth_cmds 0

STAT auth_errors 0

STAT bytes_read 15785                      读取字节总数

STAT bytes_written 15222                   写入字节总数

STAT limit_maxbytes 1048576                分配的内存数（字节）

STAT accepting_conns 1                     目前接受的链接数

STAT listen_disabled_num 0

STAT threads 4                             线程数

STAT conn_yields 0

STAT bytes 0                               存储item字节数

STAT curr_items 0                          item个数

STAT total_items 34                        item总数

STAT evictions 0                           为获取空间删除item的总数
```



## magent
```
1.mkdir magent  
2.cd magent/  
3.wget http://memagent.googlecode.com/files/magent-0.5.tar.gz  （笔记附件）
4.tar zxvf magent-0.5.tar.gz  
5. /sbin/ldconfig  
6.sed -i "s#LIBS = -levent#LIBS = -levent -lm#g" Makefile  
7.vi magent.c 添加
    #include <limits.h>
8. yum install libevent-devel libevent
9.make  
10.cp magent /usr/bin/magent  



2. magent  命令参数说明：
1.-h this message  
2.-u uid  
3.-g gid  
4.-p port, default is 11211. (0 to disable tcp support)  
5.-s ip:port, set memcached server ip and port  
6.-b ip:port, set backup memcached server ip and port  
7.-l ip, local bind ip address, default is 0.0.0.0 
8.-n number, set max connections, default is 4096 
9.-D do not go to background  
10.-k use ketama key allocation algorithm  
11.-f file, unix socket path to listen on. default is off  
12.-i number, max keep alive connections for one memcached server, default is 20 
13.-v verbose 


memcached -m 1 -u root -d -l 192.168.1.219 -p 11211
memcached -m 1 -u root -d -l 192.168.1.219 -p 11212
memcached -m 1 -u root -d -l 192.168.1.219 -p 11213

magent -u root -n 51200 -l 192.168.1.219 -p 12000 -s 192.168.1.219:11211 -s 192.168.1.219:11212 -b 192.168.1.219:11213
1、分别在11211、11212、11213端口启动3个Memcached进程，在12000端口开启magent代理程序；
2、11211、11212端口为主Memcached，11213端口为备份Memcached；
3、连接上12000的magent，set key1和set key2，根据哈希算法，key1被写入11212和11213端口的Memcached，key2被写入11212
和11213端口的Memcached；
4、当11211、11212端口的Memcached死掉，连接到12000端口的magent取数据，数据会从11213端口的Memcached取出。

测试流程：
# telnet 192.168.1.219 12000
Trying 1192.168.1.219...
Connected to 192.168.1。219.
Escape character is '^]'.
stats
memcached agent v0.4
matrix 1 -> 192.168.1.219:11211, pool size 0
matrix 2 -> 192.168.1.219:11212, pool size 0
END
set key1 0 0 5
reesu                 长度为5
STORED
set key2 0 0 6
reesu1             长度为5
STORED
quit
Connection closed by foreign host.


# telnet 192.168.1.219 11211
Trying 192.168.1.219...
Connected to 192.168.1.219.
Escape character is '^]'.
get key1
END
get key2
VALUE key2 0 6
reesun1
END
quit
Connection closed by foreign host.


# telnet 192.168.1.219 11212
Trying 192.168.1.219...
Connected to 1192.168.1.219.
Escape character is '^]'.
get key1
VALUE key1 0 5
reesun
END
get key2
END
quit
Connection closed by foreign host.


# telnet 192.168.1.219 11213
Trying 192.168.1.219...
Connected to 1192.168.1.219.
Escape character is '^]'.
get key1
VALUE key1 0 5(key长度)
hello
END
get key2
VALUE key2 0 6
reesun
END
quit
Connection closed by foreign host.
```



## 清除数据
```
危险命令
flush_all                                            这个最简单的命令仅用于清理缓存中的所有名称/值对。
调用flush_all的时刻，数据所占的内存并不会被释放，但会被标记为过期，是不能再被取得了，你后来添加的值，
会根据需要逐渐占用掉之前的空间，所以，实际应用场景里，不需要做特殊处理。
```



## key操作
```
1. cmd上登录memcache

> telnet 127.0.0.1 11211

2. 列出所有keys

stats items // 这条是命令
STAT items:7:number 1 
 STAT items:7:age 188
 END

3. 通过itemid获取key
接下来基于列出的items id，本例中为7，第2个参数为列出的长度，0为全部列出

 stats cachedump 7 0 // 这条是命令
 ITEM Sess_sidsvpc1473t1np08qnkvhf6j2 [183 b; 1394527347 s]
 END

4. 通过get获取key值
上面的stats cachedump命令列出了我的session key，接下来就用get命令查找对应的session值

get Sess_sidsvpc1473t1np08qnkvhf6j2 //这条是命令
VALUE
Sess_sidsvpc1473t1np08qnkvhf6j2 1440 1
 83
 Sess_|a:5:{s:6:"verify";s:32:"e70981fd305170c41a5632b2a24bbcaa";s:3:"uid";s:1:"1
 ";s:8:"username";s:5:"admin";s:9:"logintime";s:19:"2014-03-11 16:24:25";s:7:"log
 inip";s:9:"127.0.0.1";}

```



## memcache安装
```
yum安装
yum install memcached memcached-devel -y
vim /etc/sysconfig/memcached 
PORT="11211"
USER="memcached"
MAXCONN="1024"   最大连接数
CACHESIZE="128"  最大内存使用 （M）
OPTIONS=""

/etc/init.d/memcached start

源码
Memcached：
wget http://memcached.googlecode.com/files/memcached-1.4.4.tar.gz
tar -xzvf memcached-1.4.4.tar.gz
cd memcached-1.4.4
./configure --prefix=/usr/local/memcached --with-libevent=/usr/local/libevent
make
make install
ln -s /usr/local/libevent/lib/libevent-1.4.so.2 /usr/lib/

memcached -m 500 -u root -d -l 192.168.1.219 -p 11211
memcached常用启动参数描述:
-d：启动一个守护进程，
-m：分配给Memcache使用的内存数量，单位是MB，默认是64MB，
-u：运行Memcache的用户
-l：监听的服务器IP地址
-p：设置Memcache监听的端口，默认是11211注：-p(p为小写)
-c：设置最大并发连接数，默认是1024
-P：设置保存Memcache的pid文件注：-P(P为大写)
-h 显示帮助

连接到 memcached：
telnet ip 端口，如telnet 192.168.100.11 11211
stats查看状态，flush_all:清楚缓存
查看memcached状态的基本命令，通过这个命令可以看到如下信息：
STAT pid 22459                             进程ID
STAT uptime 1027046                        服务器运行秒数
STAT time 1273043062                       服务器当前unix时间戳
STAT version 1.4.4                         服务器版本
STAT pointer_size 64                       操作系统字大小(这台服务器是64位的)
STAT rusage_user 0.040000                  进程累计用户时间
STAT rusage_system 0.260000                进程累计系统时间
STAT curr_connections 10                   当前打开连接数
STAT total_connections 82                  曾打开的连接总数
STAT connection_structures 13              服务器分配的连接结构数
STAT cmd_get 54                            执行get命令总数
STAT cmd_set 34                            执行set命令总数
STAT cmd_flush 3                           指向flush_all命令总数
STAT get_hits 9                            get命中次数
STAT get_misses 45                         get未命中次数
STAT delete_misses 5                       delete未命中次数
STAT delete_hits 1                         delete命中次数
STAT incr_misses 0                         incr未命中次数
STAT incr_hits 0                           incr命中次数
STAT decr_misses 0                         decr未命中次数
STAT decr_hits 0                           decr命中次数
STAT cas_misses 0                          cas未命中次数
STAT cas_hits 0                            cas命中次数
STAT cas_badval 0                          使用擦拭次数
STAT auth_cmds 0
STAT auth_errors 0
STAT bytes_read 15785                      读取字节总数
STAT bytes_written 15222                   写入字节总数
STAT limit_maxbytes 1048576                分配的内存数（字节）
STAT accepting_conns 1                     目前接受的链接数
STAT listen_disabled_num 0               
STAT threads 4                             线程数
STAT conn_yields 0
STAT bytes 0                               存储item字节数
STAT curr_items 0                          item个数
STAT total_items 34                        item总数
STAT evictions 0                           为获取空间删除item的总数

获取运行状态
echo stats | nc 192.168.1.123 11200
watch "echo stats | nc 192.168.1.123 11200" (实时状态)
```



