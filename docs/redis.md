## redis-dump
```
yum install ruby rubygems ruby-devel
gem sources --add http://gems.ruby-china.org/ --remove http://rubygems.org/
gem sources -l
gem install redis-dump

redis-dump -u 127.0.0.1:6379 > data.json (导出redis 默认数据库的数据，默认数据库为0) 
如果指定15数据库的数据： 
redis-dump -u 127.0.0.1:6379 -d 15 > data.json
redis-load -u 192.168.1.3:19000 < data.json


aof导出
开启现有 Redis 实例的 AOF 功能（如果实例已经启用 AOF 功能则忽略此步骤）
# redis-cli -h ip -p port config set appendonly yes 

通过AOF文件将数据导入到新的 Redis 实例 (假定生成的 AOF 文件名为 append.aof)
# redis-cli -h ip -p 6379 -a pass --pipe < appendonly.aof
```



## codis
```
wget https://github.com/CodisLabs/codis/releases/download/3.2.0/codis3.2.0-go1.7.5-linux.tar.gz   (二进制可执行文件)
https://github.com/CodisLabs/codis/archive/release3.2.zip (源码，包含脚本，配置文件)

需要升级glibc2.14

export LD_LIBRARY_PATH=/usr/local/glibc-2.14/lib/:$LD_LIBRARY_PATH
```



## twemproxy代理
```
https://github.com/twitter/twemproxy


需要高版本的autoconf
wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.69.tar.gz
tar -zxf autoconf-2.69.tar.gz 
cd autoconf-2.69
./configure --prefix=/usr/local/autoconf
make
make install

wget https://github.com/twitter/twemproxy/archive/master.zip
cd twemproxy-master/
/usr/local/autoconf/bin/autoreconf -fvi
./configure --prefix=/usr/local/twemproxy 
make -j 8
make install

cd /usr/local/twemproxy
mkdir run conf
vim /usr/local/twemproxy/conf/nutcracker.yml  参考官方配置
alpha:
  listen: 127.0.0.1:22121
  hash: fnv1a_64
  distribution: ketama
  auto_eject_hosts: true
  redis: true
  server_retry_timeout: 2000
  server_failure_limit: 1
  servers:
   - 127.0.0.1:7000:1
   - 127.0.0.1:7001:1

检查配置  ./sbin/nutcracker -t

启动  nutcracker -d -c /usr/local/twemproxy/conf/nutcracker.yml -p /usr/local/twemproxy/run/redisproxy.pid 
-o /usr/local/twemproxy/run/redisproxy.log
```



## sentinel哨兵
```
配置redis主从
#从的redis配置文件，需要添加
vim redis.conf
slaveof 192.168.1.5 6379

分别启动主从  nohup ./src/redis-server redis.conf &

redis-cli -h 192.168.1.5 info Replication   主从信息
# Replication
role:master #代表192.168.9.18:6379 这台redis是主
connected_slaves:1
slave0:ip=192.168.1.6,port=6379,state=online,offset=29,lag=0

sentinel.conf 配置   （sentinel集群中各个sentinel也有互相通信，通过gossip协议）
port 26379
dir /tmp
#master1 
sentinel monitor master1 192.168.1.5 6379 2
#末尾的2代表，当集群中有2个sentinel认为master死了时，才能真正认为该master已经不可用了，多个sentinel使用，单个sentinel配置为1 
sentinel down-after-milliseconds master1 10000
#sentinel会向master发送心跳PING来确认master是否存活   单位是毫秒
sentinel parallel-syncs master1 1
#在发生failover主备切换时，这个选项指定了最多可以有多少个slave同时对新的master进行同步，这个数字越小，
完成failover所需的时间就越长，但是如果这个数字越大，就意味着越多的slave因为replication而不可用。可以通过将这个值设为
 1 来保证每次只有一个slave处于不能处理命令请求的状态。
sentinel failover-timeout master1 180000
#failover超时时间，单位毫秒

#master2   可以添加多组主从的redis监听
....

./src/redis-sentinel sentinel.conf  启动
./src/redis-cli -h 192.168.1.6 -p 26379 info Sentinel   相关信息
# Sentinel
sentinel_masters:1
sentinel_tilt:0
sentinel_running_scripts:0
sentinel_scripts_queue_length:0
master0:name=master1,status=ok,address=192.168.1.5:6379,slaves=1,sentinels=1

当主的redis 服务器岩机了，sentinel自动把从的redis切换到主
当之前的主redis回复后，sentinel 会把上次主redis重新加入服务中，但是他再以不是主的redis了，变成从的reids  
：相关信息可以从redis Sentinel   的 info Sentinel 信息和日志查看

VIP漂移
VIP设置脚本

这个是在failover时执行的脚本。 
如下所示的参数会传递给脚本client-reconfig-script。
# The following arguments are passed to the script:
#
# <master-name> <role> <state> <from-ip> <from-port> <to-ip> <to-port>
第6个增加VIP，将成为一个Master，其它的则删除VIP。在failover时，仅仅使用ip命令可能会产生arp问题，
因此使用arping命令来抛出GRAP。在使用ip、arping命令时需要root权限，这里使用sudo来执行命令。

vim /var/lib/redis/failover.sh
chmod 755 /var/lib/redis/failover.sh
chown redis: /var/lib/redis/failover.sh
echo -e "redis\tALL=(ALL)\tNOPASSWD:/sbin/ip,NOPASSWD:/sbin/arping" > /etc/sudoers.d/redis
sed -i "s|Defaults.*requiretty|#Defaults\trequiretty|" /etc/sudoers
chmod 440 /etc/sudoers.d/redis

#!/bin/bash
MASTER_IP=${6}
MY_IP='192.168.0.1'   # 每个Server本身的IP
VIP='192.168.0.4'     # VIP
NETMASK='24'          # Netmask
INTERFACE='eth0'      # 接口

if [ ${MASTER_IP} = ${MY_IP} ]; then
        sudo /sbin/ip addr add ${VIP}/${NETMASK} dev ${INTERFACE}
        sudo /sbin/arping -q -c 3 -A ${VIP} -I ${INTERFACE}
        exit 0
else
        sudo /sbin/ip addr del ${VIP}/${NETMASK} dev ${INTERFACE}
        exit 0
fi
exit 1

Redis-Sentinel设置
开始设置redis-sentonel。 
你只需在第一次手工设置VIP。
vim /etc/redis-sentinel.conf
service redis-sentinel start
chkconfig redis-sentinel on
ip addr add 192.168.0.4/24 dev eth0

# sentinel.conf
port 26379
logfile /var/log/redis/sentinel.log
sentinel monitor mymaster 192.168.0.1 6379 2
sentinel down-after-milliseconds mymaster 3000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 60000
sentinel client-reconfig-script mymaster /var/lib/redis/failover.sh

结论
之后你可以尝试kill master而不是宕机来测试failover，我认为这是个比较好且容易实现的方法。 
sentinel down-after-milliseconds mymaster 3000 
大约在3秒左右会检测到redis的宕机。在更恶劣的环境，可以尝试减小这个值。
```



## redis命令
```
tar zxf redis-3.0.2.tar.gz
cd redis-3.0.2
make
cd src && make install
cp ../redis.conf /etc

启动
redis-server > /dev/null & 或者 redis-server redis.conf 或者 redis-server /etc/redis.conf 1>log.log 2>errlog.log 
（1为标准输出，2为错误输出）
停止 redis-cli shutdown

客户端连接 redis-cli

存值：
redis-cli set hx value
取值：
redis-cli get hx

> quit
退出连接

> dbsize
(integer) 12

当前数据库中key的数量

> info
服务器基本信息

monitor

实时转储收到的请求

config get
获取服务器的参数配置

flushdb
清空当前数据库

flushall
清除所有数据库



常规操作命令 

01  exits key              //测试指定key是否存在，返回1表示存在，0不存在 
02  del key1 key2 ....keyN //删除给定key,返回删除key的数目，0表示给定key都不存在 
03  type key               //返回给定key的value类型。返回 none 表示不存在key,string字符类型，list 链表类型 set 无序集合类型... 
04  keys pattern           //返回匹配指定模式的所有key,下面给个例子 
05  randomkey              //返回从当前数据库中随机选择的一个key,如果当前数据库是空的，返回空串 
06  rename oldkey newkey   //原子的重命名一个key,如果newkey存在，将会被覆盖，返回1表示成功，0失败。可能是oldkey不存在
或者和newkey相同 
07  renamenx oldkey newkey //同上，但是如果newkey存在返回失败 
08  dbsize                 //返回当前数据库的key数量 
09  expire key seconds     //为key指定过期时间，单位是秒。返回1成功，0表示key已经设置过过期时间或者不存在 
10  ttl key                //返回设置过过期时间的key的剩余过期秒数 -1表示key不存在或者没有设置过过期时间 
11  select db-index        //通过索引选择数据库，默认连接的数据库所有是0,默认数据库数是16个。返回1表示成功，0失败 
12  move key db-index      //将key从当前数据库移动到指定数据库。返回1成功。0 如果key不存在，或者已经在指定数据库中 
13  flushdb                //删除当前数据库中所有key,此方法不会失败。慎用 
14  flushall               //删除所有数据库中的所有key，此方法不会失败。更加慎用 
string 类型数据操作命令 

01  set key value         //设置key对应的值为string类型的value,返回1表示成功，0失败 
02  setnx key value       //同上，如果key已经存在，返回0 。nx 是not exist的意思 
03  get key               //获取key对应的string值,如果key不存在返回nil 
04  getset key value      //原子的设置key的值，并返回key的旧值。如果key不存在返回nil 
05  mget key1 key2 ... keyN            //一次获取多个key的值，如果对应key不存在，则对应返回nil。下面是个实验,首先清空当
前数据库，然后设置k1,k2.获取时k3对应返回nil 
06  mset key1 value1 ... keyN valueN   //一次设置多个key的值，成功返回1表示所有的值都设置了，失败返回0表示没有任何值被设置 
07  msetnx key1 value1 ... keyN valueN //同上，但是不会覆盖已经存在的key 
08  incr key              //对key的值做加加操作,并返回新的值。注意incr一个不是int的value会返回错误，incr一个不存在的
key，则设置key为1 
09  decr key              //同上，但是做的是减减操作，decr一个不存在key，则设置key为-1 
10  incrby key integer    //同incr，加指定值 ，key不存在时候会设置key，并认为原来的value是 0 
11  decrby key integer    //同decr，减指定值。decrby完全是为了可读性，我们完全可以通过incrby一个负值来实现同样效果，反之一样。 
12  append key value      //给指定key的字符串值追加value,返回新字符串值的长度。下面给个例子 
13  substr key start end  //返回截取过的key的字符串值,注意并不修改key的值。下标是从0开始的，接着上面例子 
list 类型数据操作命令 

01  lpush key string          //在key对应list的头部添加字符串元素，返回1表示成功，0表示key存在且不是list类型 
02  rpush key string          //同上，在尾部添加 
03  llen key                  //返回key对应list的长度，key不存在返回0,如果key对应类型不是list返回错误 
04  lrange key start end      //返回指定区间内的元素，下标从0开始，负值表示从后面计算，-1表示倒数第一个元素 ，key不存在返回空列表 
05  ltrim key start end       //截取list，保留指定区间内元素，成功返回1，key不存在返回错误 
06  lset key index value      //设置list中指定下标的元素值，成功返回1，key或者下标不存在返回错误 
07  lrem key count value      //从key对应list中删除count个和value相同的元素。count为0时候删除全部 
08  lpop key                  //从list的头部删除元素，并返回删除元素。如果key对应list不存在或者是空返回nil，如果key对
应值不是list返回错误 
09  rpop                      //同上，但是从尾部删除 
10  blpop key1...keyN timeout //从左到右扫描返回对第一个非空list进行lpop操作并返回，比如blpop list1 list2 list3 0 ,
如果list不存在list2,list3都是非空则对list2做lpop并返回从list2中删除的元素。如果所有的list都是空或不存在，则会阻塞timeout秒，
timeout为0表示一直阻塞。当阻塞时，如果有client对key1...keyN中的任意key进行push操作，则第一在这个key上被阻塞的client会立即返回。
如果超时发生，则返回nil。有点像unix的select或者poll 
11  brpop                     //同blpop，一个是从头部删除一个是从尾部删除 
12  rpoplpush srckey destkey  //从srckey对应list的尾部移除元素并添加到destkey对应list的头部,最后返回被移除的元素值，
整个操作是原子的.如果srckey是空或者不存在返回nil 
set 类型数据操作命令 

01  sadd key member                //添加一个string元素到,key对应的set集合中，成功返回1,如果元素以及在集合中返回0,key
对应的set不存在返回错误 
02  srem key member                //从key对应set中移除给定元素，成功返回1，如果member在集合中不存在或者key不存在返回0，
如果key对应的不是set类型的值返回错误 
03  spop key                       //删除并返回key对应set中随机的一个元素,如果set是空或者key不存在返回nil 
04  srandmember key                //同spop，随机取set中的一个元素，但是不删除元素 
05  smove srckey dstkey member     //从srckey对应set中移除member并添加到dstkey对应set中，整个操作是原子的。成功返回1,
如果member在srckey中不存在返回0，如果key不是set类型返回错误 
06  scard key                      //返回set的元素个数，如果set是空或者key不存在返回0 
07  sismember key member           //判断member是否在set中，存在返回1，0表示不存在或者key不存在 
08  sinter key1 key2...keyN        //返回所有给定key的交集 
09  sinterstore dstkey key1...keyN //同sinter，但是会同时将交集存到dstkey下 
10  sunion key1 key2...keyN        //返回所有给定key的并集 
11  sunionstore dstkey key1...keyN //同sunion，并同时保存并集到dstkey下 
12  sdiff key1 key2...keyN         //返回所有给定key的差集 
13  sdiffstore dstkey key1...keyN  //同sdiff，并同时保存差集到dstkey下 
14  smembers key                   //返回key对应set的所有元素，结果是无序的 
sorted set 类型数据操作命令 

01  zadd key score member        //添加元素到集合，元素在集合中存在则更新对应score 
02  zrem key member              //删除指定元素，1表示成功，如果元素不存在返回0 
03  zincrby key incr member      //增加对应member的score值，然后移动元素并保持skip list保持有序。返回更新后的score值 
04  zrank key member             //返回指定元素在集合中的排名（下标）,集合中元素是按score从小到大排序的 
05  zrevrank key member          //同上,但是集合中元素是按score从大到小排序 
06  zrange key start end         //类似lrange操作从集合中去指定区间的元素。返回的是有序结果 
07  zrevrange key start end      //同上，返回结果是按score逆序的 
08  zrangebyscore key min max    //返回集合中score在给定区间的元素 
09  zcount key min max           //返回集合中score在给定区间的数量 
10  zcard key                    //返回集合中元素个数 
11  zscore key element           //返回给定元素对应的score 
12  zremrangebyrank key min max  //删除集合中排名在给定区间的元素 
13  zremrangebyscore key min max //删除集合中score在给定区间的元素 
hash 类型数据操作命令 

01  hset key field value       //设置hash field为指定值，如果key不存在，则先创建 
02  hget key field             //获取指定的hash field 
03  hmget key filed1....fieldN //获取全部指定的hash filed 
04  hmset key filed1 value1 ... filedN valueN //同时设置hash的多个field 
05  hincrby key field integer  //将指定的hash filed 加上给定值 
06  hexists key field          //测试指定field是否存在 
07  hdel key field             //删除指定的hash field 
08  hlen key                   //返回指定hash的field数量 
09  hkeys key                  //返回hash的所有field 
10  hvals key                  //返回hash的所有value 
11  hgetall                    //返回hash的所有filed和value 


redis.conf配置文件：
引用
#是否作为守护进程运行
daemonize yes
#配置pid的存放路径及文件名，默认为当前路径下
pidfile redis.pid
#Redis默认监听端口
port 6379
#客户端闲置多少秒后，断开连接
timeout 300
#日志显示级别
loglevel verbose
#指定日志输出的文件名，也可指定到标准输出端口
logfile stdout
#设置数据库的数量，默认连接的数据库是0，可以通过select N来连接不同的数据库
databases 16
#保存数据到disk的策略
#当有一条Keys数据被改变是，900秒刷新到disk一次
save 900 1
#当有10条Keys数据被改变时，300秒刷新到disk一次
save 300 10
#当有1w条keys数据被改变时，60秒刷新到disk一次
save 60 10000
#当dump  .rdb数据库的时候是否压缩数据对象
rdbcompression yes
#dump数据库的数据保存的文件名
dbfilename dump.rdb
#Redis的工作目录
dir /home/falcon/redis-2.0.0/
###########  Replication #####################
#Redis的复制配置
# slaveof <masterip> <masterport>
# masterauth <master-password>

############## SECURITY ###########
# requirepass foobared

############### LIMITS ##############
#最大客户端连接数
# maxclients 128
#最大内存使用率
# maxmemory <bytes>

########## APPEND ONLY MODE #########
#是否开启日志功能
appendonly no
# 刷新日志到disk的规则
# appendfsync always
appendfsync everysec
# appendfsync no
################ VIRTUAL MEMORY ###########
#是否开启VM功能
vm-enabled no
# vm-enabled yes
vm-swap-file logs/redis.swap
vm-max-memory 0
vm-page-size 32
vm-pages 134217728
vm-max-threads 4
############# ADVANCED CONFIG ###############
glueoutputbuf yes
hash-max-zipmap-entries 64
hash-max-zipmap-value 512
#是否重置Hash表
activerehashing yes


spring中整合redis
看了java Clients，redis官网比较推荐Jedis，而spring对redis的客服端做了一个统一封装，支持(Jedis,  JRedis, and RJC)，
这里对说下SPRING DATA - REDIS。

1、使用maven的话那就很简单了，直接加入依赖。

2、编辑pom.xml
<repository>   
 <id>spring-milestone</id>   
 <name>Spring Maven MILESTONE Repository</name>   
 <url>http://maven.springframework.org/milestone</url>   
</repository>   

<dependency>   
 <groupId>org.springframework.data</groupId>   
 <artifactId>spring-data-redis</artifactId>   
 <version>1.0.0.RC1</version>   
</dependency>

spring配置文件里添加
<bean id="jedisConnectionFactory" class="org.springframework.data.redis.connection.jedis.JedisConnectionFactory">   
        <property name="hostName" value="localhost"/>   
        <property name="port" value="6636"/>   
</bean>   

<bean id="redisTemplate" class="org.springframework.data.redis.core.RedisTemplate">   
        <property name="connectionFactory" ref="jedisConnectionFactory"/>   
</bean>   

Java代码
@Service   
public class RedisService {   
    @Resource   
    private RedisTemplate<Serializable, Serializable> template;   

 /**  
     * 向redis里面添加key-value格式的数据  
     *  
     * @param key   key  
     * @param value value  
     */   

    public void set(final Serializable key, final Serializable value) {   
        template.execute(new RedisCallback<Object>() {   
            @Override   
            public Object doInRedis(RedisConnection connection) throws DataAccessException {   
                byte[] key_ = RedisUtil.getBytesFromObject(key);   
                byte[] value_ = RedisUtil.getBytesFromObject(value);   
                connection.set(key_, value_);   
                return true;   
            }   
        });   
    }   

 /**  
     * 根据key从redis里面取出value  
     *  
     * @param key   key  
     */   
 public Serializable get(final Serializable key) {   
        return template.execute(new RedisCallback<Serializable>() {   
            @Override   
            public Serializable doInRedis(RedisConnection connection) throws DataAccessException {   

                byte[] keyBytes = RedisUtil.getBytesFromObject(key);   
                byte[] bytes = connection.get(keyBytes);   
                return (Serializable) RedisUtil.getObjectFromBytes(bytes);   
            }   
        });   
    }   
}   

看了一点JedisConnectionFactory，之际上它只是对Jedis做了下简单了封装，再加上自己的连接池实现。
```



## web管理
```
https://github.com/erikdubbelboer/phpRedisAdmin
https://github.com/nrk/predis

cd  /var/www/html/
wget https://github.com/erikdubbelboer/phpRedisAdmin/archive/master.zip
unzip master.zip
rm -f master.zip
cd phpRedisAdmin
wget  https://github.com/nrk/predis/archive/v1.1.zip   解压放到上面包里，重命名为vendor
unzip v1.1.zip
rm -f v1.1.zip
mv predis-1.1  vendor

vim  phpRedisAdmin/includes/config.sample.inc.php   配置连接的redis地址,（可以配置从库，这样就是个只读的redis）

如果确少php驱动，可以安装
yum search redis | grep php
php-nrk-Predis.noarch : PHP client library for Redis
php-pecl-redis.x86_64 : Extension for communicating with the Redis key-value
php-redis.x86_64 : Extension for communicating with the Redis key-value store

http://ip/phpredis/ 

  
```



## redis cluster
```
一:关于redis cluster
1:redis cluster的现状
reids-cluster计划在redis3.0中推出，可以看作者antirez的声明:http://antirez.com/news/49 (ps:跳票了好久，今年貌似加快速度了),
目前的最新版本是redis3 beta2(2.9.51).
作者的目标:Redis Cluster will support up to ~1000 nodes. 赞...
目前redis支持的cluster特性(已亲测):
1):节点自动发现
2):slave->master 选举,集群容错
3):Hot resharding:在线分片
4):进群管理:cluster xxx
5):基于配置(nodes-port.conf)的集群管理
6):ASK 转向/MOVED 转向机制.
2:redis cluster 架构
1)redis-cluster架构图

架构细节:
(1)所有的redis节点彼此互联(PING-PONG机制),内部使用二进制协议优化传输速度和带宽.
(2)节点的fail是通过集群中超过半数的节点检测失效时才生效.
(3)客户端与redis节点直连,不需要中间proxy层.客户端不需要连接集群所有节点,连接集群中任何一个可用节点即可
(4)redis-cluster把所有的物理节点映射到[0-16383]slot上,cluster 负责维护node<->slot<->value
2) redis-cluster选举:容错

(1)领着选举过程是集群中所有master参与,如果半数以上master节点与master节点通信超过(cluster-node-timeout),认为当前master节点挂掉.
(2):什么时候整个集群不可用(cluster_state:fail),当集群不可用时,所有对集群的操作做都不可用，收到((error) CLUSTERDOWN
 The cluster is down)错误
    a:如果集群任意master挂掉,且当前master没有slave.集群进入fail状态,也可以理解成进群的slot映射[0-16383]不完成时进入fail状态.
    b:如果进群超过半数以上master挂掉，无论是否有slave集群进入fail状态.
二:redis cluster的使用
1:安装redis cluster
1):安装redis-cluster依赖:redis-cluster的依赖库在使用时有兼容问题,在reshard时会遇到各种错误,请按指定版本安装.
(1)确保系统安装zlib,否则gem install会报(no such file to load -- zlib)

#download:zlib-1.2.6.tar  ./configure  make  make install


 (1)安装ruby:version(1.9.2)
# ruby1.9.2   cd /path/ruby  ./configure -prefix=/usr/local/ruby  make  make install  sudo cp ruby /usr/local/bin
(2)安装rubygem:version(1.8.16)

# rubygems-1.8.16.tgz  cd /path/gem  sudo ruby setup.rb  sudo cp bin/gem /usr/local/bin
(3)安装gem-redis:version(3.0.0)

gem install redis --version 3.0.0  #由于源的原因，换成阿里的源https://ruby.taobao.org/ $ gem sources --add 
https://ruby.taobao.org/ --remove https://rubygems.org/$ gem sources -l*** CURRENT SOURCES ***
 https://ruby.taobao.org# 请确保只有 ruby.taobao.org$ gem install rails
2)安装redis-cluster
cd /path/redis  make  sudo cp /opt/redis/src/redis-server /usr/local/bin  sudo cp /opt/redis/src/redis-cli 
/usr/local/bin  sudo cp /opt/redis/src/redis-trib.rb /usr/local/bin
2:配置redis cluster
1)redis配置文件结构:

 使用包含(include)把通用配置和特殊配置分离,方便维护.
2)redis通用配置.

#GENERAL  daemonize no  tcp-backlog 511  timeout 0  tcp-keepalive 0  loglevel notice  databases 16  
dir /opt/redis/data  slave-serve-stale-data yes  #slave只读  slave-read-only yes  #not use default  
repl-disable-tcp-nodelay yes  slave-priority 100  #打开aof持久化  appendonly yes  #每秒一次aof写  
appendfsync everysec  #关闭在aof rewrite的时候对新的写操作进行fsync  no-appendfsync-on-rewrite yes  
auto-aof-rewrite-min-size 64mb  lua-time-limit 5000  #打开redis集群  cluster-enabled yes  
#节点互连超时的阀值  cluster-node-timeout 15000  cluster-migration-barrier 1  slowlog-log-slower-than 10000  
slowlog-max-len 128  notify-keyspace-events ""  hash-max-ziplist-entries 512  hash-max-ziplist-value 64 
 list-max-ziplist-entries 512  list-max-ziplist-value 64  set-max-intset-entries 512  zset-max-ziplist-entries 128 
  zset-max-ziplist-value 64  activerehashing yes  client-output-buffer-limit normal 0 0 0 
   client-output-buffer-limit slave 256mb 64mb 60  client-output-buffer-limit pubsub 32mb 8mb 60 
    hz 10  aof-rewrite-incremental-fsync yes
3)redis特殊配置.

#包含通用配置  include /opt/redis/redis-common.conf  #监听tcp端口  port 6379  #最大可用内存  maxmemory 100m  
#内存耗尽时采用的淘汰策略:  # volatile-lru -> remove the key with an expire set using an LRU algorithm  
# allkeys-lru -> remove any key accordingly to the LRU algorithm  # volatile-random -> remove a random 
key with an expire set  # allkeys-random -> remove a random key, any key  # volatile-ttl -> remove the key
 with the nearest expire time (minor TTL)  # noeviction -> don't expire at all, just return an error on
  write operations  maxmemory-policy allkeys-lru  #aof存储文件  appendfilename "appendonly-6379.aof"  
  #rdb文件,只用于动态添加slave过程  dbfilename dump-6379.rdb  #cluster配置文件(启动自动生成)  
  cluster-config-file nodes-6379.conf  #部署在同一机器的redis实例，把<span style="font-size: 1em; 
  line-height: 1.5;">auto-aof-rewrite搓开，防止瞬间fork所有redis进程做rewrite,占用大量内存</span>  
  auto-aof-rewrite-percentage 80-100
3:cluster 操作
cluster集群相关命令,更多redis相关命令见文档:http://redis.readthedocs.org/en/latest/
集群  CLUSTER INFO 打印集群的信息  CLUSTER NODES 列出集群当前已知的所有节点（node），以及这些节点的相关信息。  
节点  CLUSTER MEET <ip> <port> 将 ip 和 port 所指定的节点添加到集群当中，让它成为集群的一份子。  CLUSTER FORGET <node_id> 
从集群中移除 node_id 指定的节点。  CLUSTER REPLICATE <node_id> 将当前节点设置为 node_id 指定的节点的从节点。 
 CLUSTER SAVECONFIG 将节点的配置文件保存到硬盘里面。  槽(slot)  CLUSTER ADDSLOTS <slot> [slot ...] 将一个或多
 个槽（slot）指派（assign）给当前节点。  CLUSTER DELSLOTS <slot> [slot ...] 移除一个或多个槽对当前节点的指派。
   CLUSTER FLUSHSLOTS 移除指派给当前节点的所有槽，让当前节点变成一个没有指派任何槽的节点。 
    CLUSTER SETSLOT <slot> NODE <node_id> 将槽 slot 指派给 node_id 指定的节点，如果槽已经指派给另一个节点，
    那么先让另一个节点删除该槽>，然后再进行指派。  CLUSTER SETSLOT <slot> MIGRATING <node_id> 将本节点的槽
     slot 迁移到 node_id 指定的节点中。  CLUSTER SETSLOT <slot> IMPORTING <node_id> 从 node_id 指定的节点
     中导入槽 slot 到本节点。  CLUSTER SETSLOT <slot> STABLE 取消对槽 slot 的导入（import）或者迁移（migrate）。  
     键  CLUSTER KEYSLOT <key> 计算键 key 应该被放置在哪个槽上。  CLUSTER COUNTKEYSINSLOT <slot> 
     返回槽 slot 目前包含的键值对数量。  CLUSTER GETKEYSINSLOT <slot> <count> 返回 count 个 slot 槽中的键。
4:redis cluster 运维操作
1)初始化并构建集群
(1)#启动集群相关节点（必须是空节点）,指定配置文件和输出日志

redis-server /opt/redis/conf/redis-6380.conf > /opt/redis/logs/redis-6380.log 2>&1 & redis-server
 /opt/redis/conf/redis-6381.conf > /opt/redis/logs/redis-6381.log 2>&1 & redis-server /opt/redis/conf/redis-6382.conf
> /opt/redis/logs/redis-6382.log 2>&1 & redis-server /opt/redis/conf/redis-7380.conf > /opt/redis/logs/redis-7380.log
   2>&1 & redis-server /opt/redis/conf/redis-7381.conf > /opt/redis/logs/redis-7381.log 2>&1 & redis-server 
   /opt/redis/conf/redis-7382.conf > /opt/redis/logs/redis-7382.log 2>&1 &
(2):使用自带的ruby工具(redis-trib.rb)构建集群

#redis-trib.rb的create子命令构建  #--replicas 则指定了为Redis Cluster中的每个Master节点配备几个Slave节点  
#节点角色由顺序决定,先master之后是slave(为方便辨认,slave的端口比master大1000)  redis-trib.rb create --replicas 
1 10.10.34.14:6380 10.10.34.14:6381 10.10.34.14:6382 10.10.34.14:7380 10.10.34.14:7381 10.10.34.14:7382
(3):检查集群状态,

#redis-trib.rb的check子命令构建  #ip:port可以是集群的任意节点  redis-trib.rb check 1 10.10.34.14:6380
最后输出如下信息,没有任何警告或错误，表示集群启动成功并处于ok状态
 [OK] All nodes agree about slots configuration. 
>>> Check for open slots... 
>>> Check slots coverage... 
[OK] All 16384 slots covered. 

redis-cli -c -p 6379  ( -c  集群模式)

2):添加新master节点
(1)添加一个master节点:创建一个空节点（empty node），然后将某些slot移动到这个空节点上,这个过程目前需要人工干预
a):根据端口生成配置文件(ps:establish_config.sh是我自己写的输出配置脚本)
 sh establish_config.sh 6386 > conf/redis-6386.conf  
b):启动节点
 nohup redis-server /opt/redis/conf/redis-6386.conf > /opt/redis/logs/redis-6386.log 2>&1 & 
c):加入空节点到集群
add-node  将一个节点添加到集群里面， 第一个是新节点ip:port, 第二个是任意一个已存在节点ip:port
redis-trib.rb add-node 10.10.34.14:6386 10.10.34.14:6381   
node:新节点没有包含任何数据， 因为它没有包含任何slot。新加入的加点是一个主节点， 当集群需要将某个从节点升级为新的主节点时，
 这个新节点不会被选中
d):为新节点分配slot
redis-trib.rb reshard 10.10.34.14:6386  #根据提示选择要迁移的slot数量(ps:这里选择500)  How many slots 
do you want to move (from 1 to 16384)? 500  #选择要接受这些slot的node-id  What is the receiving node ID?
 f51e26b5d5ff74f85341f06f28f125b7254e61bf  #选择slot来源:  #all表示从所有的master重新分配，  #或者数据要提取
 slot的master节点id,最后用done结束  Please enter all the source node IDs.    Type 'all' to use all the 
 nodes as source nodes for the hash slots.    Type 'done' once you entered all the source nodes IDs. 
  Source node #1:all  #打印被移动的slot后，输入yes开始移动slot以及对应的数据.  #Do you want to proceed with
   the proposed reshard plan (yes/no)? yes  #结束
3):添加新的slave节点
a):前三步操作同添加master一样
b)第四步:redis-cli连接上新节点shell,输入命令:cluster replicate 对应master的node-id
 cluster replicate 2b9ebcbd627ff0fd7a7bbcc5332fb09e72788835  
note:在线添加slave 时，需要dump整个master进程，并传递到slave，再由 slave加载rdb文件到内存，rdb传输过程中Master
可能无法提供服务,整个过程消耗大量io,小心操作.
例如本次添加slave操作产生的rdb文件
 -rw-r--r-- 1 root root  34946 Apr 17 18:23 dump-6386.rdb 
-rw-r--r-- 1 root root  34946 Apr 17 18:23 dump-7386.rdb 
4):在线reshard 数据:
对于负载/数据均匀的情况，可以在线reshard slot来解决,方法与添加新master的reshard一样，只是需要reshard的master节点是老节点.
5):删除一个slave节点

#redis-trib del-node ip:port '<node-id>' redis-trib.rb del-node 10.10.34.14:7386 
'c7ee2fca17cb79fe3c9822ced1d4f6c5e169e378'

a):删除master节点之前首先要使用reshard移除master的全部slot,然后再删除当前节点(目前只能把被删除
master的slot迁移到一个节点上)
#把10.10.34.14:6386当前master迁移到10.10.34.14:6380上  redis-trib.rb reshard 10.10.34.14:6380  
#根据提示选择要迁移的slot数量(ps:这里选择500)  How many slots do you want to move (from 1 to 16384)? 
500(被删除master的所有slot数量)  #选择要接受这些slot的node-id(10.10.34.14:6380)  What is the receiving 
node ID? c4a31c852f81686f6ed8bcd6d1b13accdc947fd2 (ps:10.10.34.14:6380的node-id)  Please enter all the
 source node IDs.    Type 'all' to use all the nodes as source nodes for the hash slots.    Type 'done' 
 once you entered all the source nodes IDs.  Source node #1:f51e26b5d5ff74f85341f06f28f125b7254e61bf
 (被删除master的node-id)  Source node #2:done  #打印被移动的slot后，输入yes开始移动slot以及对应的数据.  
 #Do you want to proceed with the proposed reshard plan (yes/no)? yes
b):删除空master节点
redis-trib.rb del-node 10.10.34.14:6386 'f51e26b5d5ff74f85341f06f28f125b7254e61bf'   
```



## redis-monitor
```
https://github.com/LittlePeng/redis-monitor
```



## RDB和AOF
```
RDB和AOF
RDB方式按照一定的时间间隔对数据集创建基于时间点的快照。
AOF方式记录Server收到的写操作到日志文件，在Server重启时通过回放这些写操作来重建数据集。该方式类似于MySQL中基于语句格式的
binlog。当日志变大时Redis可在后台重写日志。
若仅期望数据在Server运行期间存在则可禁用两种持久化方案。在同一Redis实例中同时开启AOF和RDB方式的数据持久化方案也是可以的。
该情况下Redis重启时AOF文件将用于重建原始数据集，因为叫RDB方式而言，AOF方式能最大限度的保证数据完整性。

两钟方案各自的优缺点
RDB优点
RDB是Redis数据集的基于时间点的紧凑的副本，非常适合于备份场景。比如每个小时对RDB文件做一次小的归档，每天对RDB文件做一次大的
归档，每月对RDB文件做一次更大的归档。这样可以在必要的时刻选择不同的备份版本进行数据恢复。
由于是一个紧凑的文件，易于传输到远程数据中心或Amazon S3，因此RDB非常适合于灾难恢复。
RDB方式的开销较低，在该种方式下Redis父进程所要做的仅是开辟一个子进程来做剩下的事情。
与AOF相比RDB在数据集较大时能够以更快的速度恢复。

RDB缺点
若需在Redis停止工作时（例如意外断电）尽可能保证数据不丢失，那么RDB不是最好的方案。例如，通常会每隔5分钟或者更长的时间来创建
一次快照，如若Redis没有被正确的关闭就可能丢失最近几分钟的数据。
RDB方式需经常调用fork()函数以开辟子进程来实现持久化。在数据集较大、CPU性能不够强悍时fork()调用可能很耗时从而会导致Re
dis在几毫秒甚至一秒中的时间内不能服务clients。AOF也需要调用fork()但却可以在不影响数据持久性的条件下调整重写logs的频率。

AOF优点
使用AOF方式时Redis持久化更可靠：有三种不同的fsync策略供选择：no fsync at all、fsync every second、 fsync at every query。
默认为fsync every second此时的写性能仍然很好，且最坏的情况下可能丢失一秒钟的写操作。
AOF日志是append only方式产生的日志，因此不存在随机访问问题以及意外断电时造成的损毁问题。即使出于某种原因（如磁盘满）日志以一个
写了一半的命令结尾，仍可以使用redis-check-aof工具快速进行修复。
当AOF日志逐渐变大后，Redis可在后台自动的重写AOF日志。当Redis在继续追加旧的AOF日志文件时重写日志是完全安全的。Redis利用可以重
建当前数据集的最少的命令产生一个全新的日志文件，一旦新的日志文件创建完成Redis开始向新的日志文件追加日志。
AOF日志的格式易于理解易于解析。这在某些场景非常有用。比如，不下心使用FLUSHALL命令清空了所有的数据，同时AOF日志没有发生重写操作
，那么就可以简单的通过停止Redis Server移除日志中的最后一条FLUSHALL命令重启Redis Server来恢复数据。

AOF缺点
同样的数据集AOF文件要比RDB文件大很多。
根据使用的fsync方式不同AOF可能比RDB慢很多。在使用no fsync at all时AOF的性能基本与RDB持平，在使用fsync every second时性能有
所下降但仍然较高，在使用 fsync at every query时性能较低。然而RDB方式却能在高负载的情况下保证延迟尽可能小。
一些特定的命令可能存在bug从而导致重载AOF日志时不能重建出完全一样的数据集。这样的bugs非常非常罕见，已经通过测试套件做了充分的测
试。这种类型的bugs对于RDB来说几乎是不可能的。说的更清晰一点：Redis AOF增量的更新既存的状态而RDB快照每次都重新创建，从概念上讲
RDB方式更加健壮。然而，需要注意两点：每次AOF日志被Redis重写的时候日志由包含数据集的实际数据重新生成，与追加AOF文件的方式相比该
方式能有效减少bugs出现的概率；现实的应用场景中还未收到过任何用户关于AOF损毁的报告。

如何选择持久化方式？
取决于具体的应用场景，通常，两种方式可同时使用。若比较关心数据但仍能忍受几分钟的数据丢失，那么可以简单的使用RDB方式。有许多用户
只使用AOF方式，不建议这种做法，一方面以一定时间间隔创建RDB快照是创建数据备份并快速恢复数据的极好的办法，一方面可以避免AOF方式
可能存在的bugs。出于上述原因，将来可能将AOF和RDB方式合二为一。

RDB持久化设置
默认情况下Redis在磁盘上创建二进制格式的命名为dump.rdb的数据快照。可以通过配置文件配置每隔N秒且数据集上至少有M个变化时创建快照、
是否对数据进行压缩、快照名称、存放快照的工作目录。redis 2.4.10的默认配置如下：
[plain] view plain copy 在CODE上查看代码片派生到我的代码片
#900秒后且至少1个key发生变化时创建快照 
save 900 1 
#300秒后且至少10个key发生变化时创建快照 
save 300 10 
#60秒后且至少10000个key发生变化时创建快照 
save 60 10000 
#可通过注释所有save开头的行来禁用RDB持久化 
#创建快照时对数据进行压缩 
rdbcompression yes 
#快照名称 
dbfilename dump.rdb 
#存放快照的目录（AOF文件也会被存放在此目录） 
dir /var/lib/redis/ 
关于配置参数的详细信息可参阅redis.conf中的说明。

除了通过配置文件进行设置外也可以通过手工执行命令来创建快照
SAVE命令执行一个同步操作，以RDB文件的方式保存实例中所有数据的快照。一般不在生产环境直接使用SAVE 命令，因为会阻塞所有的
客户端的请求，可以使用BGSAVE命令代替。BGSAVE后台创建数据快照。命名执行结果的状态码会立即返回。Redis开辟一个子进程，父进程
继续相应客户端请求，子进程保存DB到磁盘后退出。客户端可通过执行LASTSAVE命令检查操作是否成功。

创建RDB快照的工作流程
Redis需dump数据集到磁盘时会执行下列过程：
Redis forks一个子进程；
子进程写数据集到临时的RDB文件；
子进程写完新的RDB文件后替换旧的RDB文件。
该方式使Redis可以利用copy-on-write机制的好处。

AOF持久化设置
利用快照的持久化方式不是非常可靠，当运行Redis的计算机停止工作、意外掉电、意外杀掉了Redis进程那么最近写入Redis的数据将会
丢。

对于某些应用这或许不成问题，但对于持久化要求非常高的应用场景快照方式不是理想的选择。AOF文件是一个替代方案，用以最大限度
的持久化数据。同样，可以通过配置文件来开闭AOF：
[plain] view plain copy 在CODE上查看代码片派生到我的代码片
#关闭AOF 
appendonly no 
#打开AOF 
appendonly yes 
当设置appendonly为yes后，每次Redis接收到的改变数据集的命令都会被追加到AOF文件。重启Redis后会重放AOF文件来重建数据。
还可以通过配置文件配置AOF文件名、调用fsync的频率、调用fsync的行为、重写AOF的条件。redis 2.4.10的默认配置如下：
[plain] view plain copy 在CODE上查看代码片派生到我的代码片
#默认AOF文件名 
appendfilename appendonly.aof 
#每秒调用一次fsync刷新数据到磁盘 
appendfsync everysec 
#当进程中BGSAVE或BGREWRITEAOF命令正在执行时不阻止主进程中的fsync()调用（默认为no，当存在延迟问题时需调整为yes） 
no-appendfsync-on-rewrite no 
#当AOF增长率为100%且达到了64mb时开始自动重写AOF 
auto-aof-rewrite-percentage 100 
auto-aof-rewrite-min-size 64mb 
各参数含义可参阅redis.conf中详细说明。

几点说明
日志重写
随着Redis接收到的命令的增加AOF文件会变得越来越大。Redis支持日志重写特性，可以在不影响响应客户端的前提下在后台重构AOF文
件。当在Redis中执行BGREWRITEAOF后Redis将使用构建数据集所需的最少的命令来重构日志文件。Redis2.2中需要经常手动运行
BGREWRITEAOF,Redis2.2开始支持自动触发日志重写。

日志重写同样使用copy-on-write机制，流程大致如下：
Redis开辟一个子进程；
子进程在临时文件中写新的AOF文件；
父进程将所有新的更改缓存在memory中（同时新更改被写入旧的AOF，这样即使重写操作失败了也是安全的）；
在子进程重写好临时AOF后父进程收到一个信号并追加memory中缓冲的更改到子进程产生的临时文件的末尾；
Redis进行文件重命名用新的文件替换旧的文件并开始追加新的数据到新文件。

fsync调用模式
该模式决定了Redis刷新数据到磁盘的频率，有三个可选项：
no fsync at all 全由操作系统决定刷数据的时机。最快但最不安全。
fsync every second 每秒一次刷新。足够快，最多可丢失一秒的数据。
fsync at every query 每次记录一条新的命令到AOF便刷一次数据到磁盘。最慢但最安全。
默认策略（也是默认策略）为fsync every second

AOF损坏时的对策
若在写AOF文件时Server崩溃则可能导致AOF文件损坏而不能被Redis载入。可通过如下步骤修复：
创建一个AOF文件的备份；
使用redis-check-aof工具修复原始的AOF文件；
$ redis-check-aof --fix
使用diff -u 检查备份文件和修复后文件的异同（可选步骤）；
使用修复后的AOF文件重启Redis。

如何由RDB持久化转换到AOF持久化？
Redis >=2.2时
创建最近的RDB文件的备份；
将备份保存在安全的位置；
发起如下命令；
$redis-cli config set appendonly yes
$redis-cli config set save ""（可选，若不执行RDB和AOF方式将并存）
确认数据库包含相同的keys；
确认write操作被正确追加到了AOF文件。
注意事项：记得修改redis.conf中对应的配置以免Redis Server重启后通过命令进行的配置更新丢失而重新使用旧的配置文件中配置。

Redis2.0时
创建最近的RDB文件的备份；
将备份存放在安全的位置；
停止数据库上的所有写操作；
发起 redis-cli bgrewriteaof命令创建AOF文件；
当AOF文件生成后停止Redis Server；
编辑redis.conf开启AOF持久化；
重启Redis Server；
确认数据库包含相同的keys；
确认write操作被正确追加到了AOF文件。

AOF与RDB之间的相互影响
Redis2.4以上的版本会确保在RDB快照创建时不触发AOF重写或者在AOF重写时不允许BGSAVE操作，以避免Redis后台进程同时做繁重
的磁盘I/O操作。
当创建RDB快照时对于用户使用BGREWRITEAOF明确发起的日志重写操作server会立刻回应一个ok状态码告知用户操作将回被执行，当且
仅当快照创建完成后重写操作开始被执行。
在同时使用了AOF和RDB方式的情况下，Redis重启后会优先使用AOF文件来重构原始数据集。

备份Redis 数据
务必做好数据备份以防意外丢失。Redis是备份友好的，可在数据库运行时拷贝RDB文件。建议的备份方案：
创建一个cron作业在一个目录中每小时创建一次RDB快照在另一目录中每天创建一次RDB快照；
cron作业每次运行的时候使用find命令确保过时的RDB快照文件被清理掉（可以通过在快照命中包含数据和时间信息来进行标记）；
确保将RDB快照转移到外部的数据中心或者至少是运行Redis实例的物理机之外的机器（至少每天一次）。

灾难恢复
在Redis中灾难恢复和数据备份基本上是同样的过程。可考虑将备份分布到不同的远程数据中心以最大限度的避免数据丢失。几种低成
本的灾难恢复计划：
Amazon S3或其它类似服务是很好的选择。可将每天会每小时的RDB快照以加密的方式（可使用gpg -c加密）传输到S3。确保将密码存
储在不同的安全的地方。建议使用不同的存储服务以提高数据安全性。
使用SCP命令将快照传输到远程服务器。最简单和安全的方式：获取一个小的远程VPS，在其上安装ssh，生成无密码的ssh client 
key添加到VPS的authorized_keys文件，此后便可使用SCP传输备份到VPS了。建议搞两个不同的VPS以提高安全性。

需要注意的是，文件传输完成后一定要校验文件的完整性正确性。可通过MD5或SHA1进行验证。另外需要搭建一套告警系统，当
备份传输发生问题时能及时的告知。
```



## Redis的复制及集群搭建
```
Redis的复制及Redis优缺点和集群搭建
Redis复制流程概述
Redis的复制功能是完全建立在之前我们讨论过的基于内存快照的持久化策略基础上的，也就是说无论你的持久化策略选择的是什么，
只要用到了 Redis的复制功能，就一定会有内存快照发生，那么首先要注意你的系统内存容量规划，原因可以参考我上一篇文章中提到
的Redis磁盘IO问题。
Redis复制流程在Slave和Master端各自是一套状态机流转，涉及的状态信息是：
Slave 端：
REDIS_REPL_NONE
REDIS_REPL_CONNECT
REDIS_REPL_CONNECTED 
Master端：
REDIS_REPL_WAIT_BGSAVE_START
REDIS_REPL_WAIT_BGSAVE_END
REDIS_REPL_SEND_BULK
REDIS_REPL_ONLINE
整个状态机流程过程如下：
Slave端在配置文件中添加了slave of指令，于是Slave启动时读取配置文件，初始状态为REDIS_REPL_CONNECT。
Slave端在定时任务serverCron(Redis内部的定时器触发事件)中连接Master，发送sync命令，然后阻塞等待master发送回其内存
快照文件(最新版的Redis已经不需要让Slave阻塞)。
Master端收到sync命令简单判断是否有正在进行的内存快照子进程，没有则立即开始内存快照，有则等待其结束，当快照完成后会
将该文件发送给Slave端。
Slave端接收Master发来的内存快照文件，保存到本地，待接收完成后，清空内存表，重新读取Master发来的内存快照文件，重建整
个内存表数据结构，并最终状态置位为 REDIS_REPL_CONNECTED状态，Slave状态机流转完成。
Master端在发送快照文件过程中，接收的任何会改变数据集的命令都会暂时先保存在Slave网络连接的发送缓存队列里（list数据结构），
待快照完成后，依次发给Slave,之后收到的命令相同处理，并将状态置位为 REDIS_REPL_ONLINE。
整个复制过程完成，流程如下图所示：



Redis复制机制的缺陷
从上面的流程可以看出，Slave从库在连接Master主库时，Master会进行内存快照，然后把整个快照文件发给Slave，也就是没有象M
ySQL那样有复制位置的概念，即无增量复制，这会给整个集群搭建带来非常多的问题。
比如一台线上正在运行的Master主库配置了一台从库进行简单读写分离，这时Slave由于网络或者其它原因与Master断开了连接，那么
当 Slave进行重新连接时，需要重新获取整个Master的内存快照，Slave所有数据跟着全部清除，然后重新建立整个内存表，一方面S
lave恢复的 时间会非常慢，另一方面也会给主库带来压力。
所以基于上述原因，如果你的Redis集群需要主从复制，那么最好事先配置好所有的从库，避免中途再去增加从库。
Cache还是Storage
在我们分析过了Redis的复制与持久化功能后，我们不难得出一个结论，实际上Redis目前发布的版本还都是一个单机版的思路，主要的
问题集中在，持久化方式不够成熟，复制机制存在比较大的缺陷，这时我们又开始重新思考Redis的定位：Cache还是Storage？
如果作为Cache的话，似乎除了有些非常特殊的业务场景，必须要使用Redis的某种数据结构之外，我们使用Memcached可能更合适，毕
竟Memcached无论客户端包和服务器本身更久经考验。
如果是作为存储Storage的话，我们面临的最大的问题是无论是持久化还是复制都没有办法解决Redis单点问题，即一台Redis挂掉了，没
有太好的办法能够快速的恢复，通常几十G的持久化数据，Redis重启加载需要几个小时的时间，而复制又有缺陷，如何解决呢？
Redis可扩展集群搭建1. 主动复制避开Redis复制缺陷。
既然Redis的复制功能有缺陷，那么我们不妨放弃Redis本身提供的复制功能，我们可以采用主动复制的方式来搭建我们的集群环境。
所谓主动复制是指由业务端或者通过代理中间件对Redis存储的数据进行双写或多写，通过数据的多份存储来达到与复制相同的目的，
主动复制不仅限于 用在Redis集群上，目前很多公司采用主动复制的技术来解决MySQL主从之间复制的延迟问题，比如Twitter还专门
开发了用于复制和分区的中间件 gizzard(https://github.com/twitter/gizzard) 。
主动复制虽然解决了被动复制的延迟问题，但也带来了新的问题，就是数据的一致性问题，数据写2次或多次，如何保证多份数据的一致
性呢？如果你的应用 对数据一致性要求不高，允许最终一致性的话，那么通常简单的解决方案是可以通过时间戳或者vector clock等
方式，让客户端同时取到多份数据并进行校验，如果你的应用对数据一致性要求非常高，那么就需要引入一些复杂的一致性算法比如
Paxos来保证 数据的一致性，但是写入性能也会相应下降很多。
通过主动复制，数据多份存储我们也就不再担心Redis单点故障的问题了，如果一组Redis集群挂掉，我们可以让业务快速切换到另一
组Redis上，降低业务风险。
2. 通过presharding进行Redis在线扩容。
通过主动复制我们解决了Redis单点故障问题，那么还有一个重要的问题需要解决：容量规划与在线扩容问题。
我们前面分析过Redis的适用场景是全部数据存储在内存中，而内存容量有限，那么首先需要根据业务数据量进行初步的容量规划，比
如你的业务数据需 要100G存储空间，假设服务器内存是48G，那么根据上一篇我们讨论的Redis磁盘IO的问题，我们大约需要3~4台服
务器来存储。这个实际是对现有 业务情况所做的一个容量规划，假如业务增长很快，很快就会发现当前的容量已经不够了，Redis里
面存储的数据很快就会超过物理内存大小，那么如何进行 Redis的在线扩容呢？
Redis的作者提出了一种叫做presharding的方案来解决动态扩容和数据分区的问题，实际就是在同一台机器上部署多个Redis实例的
方式，当容量不够时将多个实例拆分到不同的机器上，这样实际就达到了扩容的效果。
拆分过程如下：
在新机器上启动好对应端口的Redis实例。
配置新端口为待迁移端口的从库。
待复制完成，与主库完成同步后，切换所有客户端配置到新的从库的端口。
配置从库为新的主库。
移除老的端口实例。
重复上述过程迁移好所有的端口到指定服务器上。
以上拆分流程是Redis作者提出的一个平滑迁移的过程，不过该拆分方法还是很依赖Redis本身的复制功能的，如果主库快照数据文件
过大，这个复制的过程也会很久，同时会给主库带来压力。所以做这个拆分的过程最好选择为业务访问低峰时段进行。
Redis复制的改进思路
我们线上的系统使用了我们自己改进版的Redis,主要解决了Redis没有增量复制的缺陷，能够完成类似Mysql Binlog那样可以通过从
库请求日志位置进行增量复制。
我们的持久化方案是首先写Redis的AOF文件，并对这个AOF文件按文件大小进行自动分割滚动，同时关闭Redis的Rewrite命令，然后
 会在业务低峰时间进行内存快照存储，并把当前的AOF文件位置一起写入到快照文件中，这样我们可以使快照文件与AOF文件的位置保持
 一致性，这样我们得到 了系统某一时刻的内存快照，并且同时也能知道这一时刻对应的AOF文件的位置，那么当从库发送同步命令时，

 我们首先会把快照文件发送给从库，然后从库会取 出该快照文件中存储的AOF文件位置，并将该位置发给主库，主库会随后发送该位置
 之后的所有命令，以后的复制就都是这个位置之后的增量信息了。



Redis与MySQL的结合
目前大部分互联网公司使用MySQL作为数据的主要持久化存储，那么如何让Redis与MySQL很好的结合在一起呢？我们主要使用了一种基
于MySQL作为主库，Redis作为高速数据查询从库的异构读写分离的方案。
为此我们专门开发了自己的MySQL复制工具，可以方便的实时同步MySQL中的数据到Redis上。



（MySQL-Redis 异构读写分离）
总结：
Redis的复制功能没有增量复制，每次重连都会把主库整个内存快照发给从库，所以需要避免向在线服务的压力较大的主库上增加从库。
Redis 的复制由于会使用快照持久化方式，所以如果你的Redis持久化方式选择的是日志追加方式(aof),那么系统有可能在同一时刻
既做aof日志文件的同步 刷写磁盘，又做快照写磁盘操作，这个时候Redis的响应能力会受到影响。所以如果选用aof持久化，则加从
库需要更加谨慎。
可以使用主动复制和presharding方法进行Redis集群搭建与在线扩容。
本文加上之前的2篇文章基本将Redis的最常用功能和使用场景与优化进行了分析和讨论，实际Redis还有很多其它辅助的一些功能，
Redis的作者也在不断尝试新的思路，这里就不一一列举了，有兴趣的朋友可以研究下
```



