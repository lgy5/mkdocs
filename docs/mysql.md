## 分表
```
d_debtor_contacts_bak的数据拆分为d_debtor_contacts_0
和d_debtor_contacts_1根据debtor_info_id取模

INSERT INTO d_debtor_contacts_0 SELECT * FROM d_debtor_contacts_bak WHERE debtor_info_id MOD 2=0;
INSERT INTO d_debtor_contacts_1 SELECT * FROM d_debtor_contacts_bak WHERE debtor_info_id MOD 2=1;

https://github.com/Qihoo360/Atlas/wiki/Atlas%E7%9A%84%E5%88%86%E8%A1%A8%E5%8A%9F%E8%83%BD%E7%AE%80%E4%BB%8B
1.使用Atlas的分表功能时，首先需要在配置文件（test.cnf）设置tables参数。
2.tables参数设置格式：数据库名.表名.分表字段.子表数量，比如你的数据库名叫school，表名叫stu，分表字段叫id，总共分为100张表，
那么就写为school.stu.id.100，如果还有其他的分表，以逗号分隔即可。用户需要手动建立100张子表（stu_0,stu_1,…stu_99，注意子表
序号是从0开始的）。且所有的子表必须在DB的同一个database里。
3.当通过Atlas执行（SELECT、DELETE、UPDATE、INSERT、REPLACE）操作时，Atlas会根据分表结果（id%100=k），定位到相应的子表
（stu_k）。例如，执行select * from stu where id=110;，Atlas会自动从stu_10这张子表返回查询结果。但如果执行SQL语句
（select * from stu;）时不带上id，则会提示执行stu 表不存在。
4.Atlas暂不支持自动建表和跨库分表的功能。
5.Atlas目前支持分表的语句有SELECT、DELETE、UPDATE、INSERT、REPLACE。
```



## 多实例
```
初始化
mysql_install_db --defaults-file=/etc/my3316.cnf --user=mysql --basedir=/data/mysql/ --datadir=/data/mysql/data3316/

多实例启动文件的启动mysql服务实质命令：
mysqld_safe --defaults-file=/etc/my3316.cnf 2>&1 /var/log/mysqld3316.log &
 
本文多实例启动文件的停止mysql服务实质命令：
mysqladmin -u root -p123456 -S /var/lib/mysql/mysql3316.sock shutdown

连接 mysql --defaults-file=/etc/my3316.cnf

配置文件要有
[client]
port = 3316
socket = /var/lib/mysql/mysql3316.sock
default-character-set=UTF8

[mysqld]
port = 3316
datadir=/data/mysql/data3316
socket=/var/lib/mysql/mysql3316.sock

```



## 数据脱敏
```
UPDATE d_debtor_info set debtor_id_num=insert(debtor_id_num, 8, 4, '****') where id=2667;
UPDATE d_debtor_info set work_telephone=insert(work_telephone, 4, 4, '****') where id=2667;

insert(debtor_id_num, 8, 4, '****')  从第8位开始，替换4位数据为****
```



## 压力测试
```
https://github.com/nuodb/sysbench
wget https://github.com/nuodb/sysbench/archive/master.zip
cd sysbench-master
./autogen.sh 
./configure --with-mysql-includes=/data/mysql/include/  --with-mysql-libs=/data/mysql/lib/ 
make

export LD_LIBRARY_PATH=/data/mysql/lib/
./sysbench/sysbench --help

常用命令参数：
 
/usr/local/sysbench-0.5/bin/sysbench
     --mysql-host=test.mysql.rds.aliyuncs.com           #数据库host
     --mysql-port=3306                                              #数据库端口
     --mysql-user=your_username                             #数据库用户名
     --mysql-password=your_password                      #数据库密码
     --mysql-socket=
     --mysql-db=your_db_for_test                              #数据库名
     --mysql-table-engine=innodb
     --oltp-tables-count=10                        #模拟的表的个数，规格越高该值越大
     --oltp-table-size=6000000                  #模拟的每张表的行数，规格越高该值越大
     --num-threads=50                              #模拟的并发数量，规格越高该值越大
     --max-requests=100000000               #最大请求次数
     --max-time=20                           #最大测试时间（与--max-requests只要有一个超过，则退出）
     --report-interval=1                     #每1秒打印一次当前的QPS等值
     --test=/tmp/sysbench-0.5/sysbench/tests/db/oltp.lua    #选用的测试脚本(lua)，此脚本可以从sysbench-0.5源代码文件目录下找
 
     [prepare | run | cleanup]           #prepare准备数据，run执行测试，cleanup清理数据
 
测试结果解读如下：
sysbench 0.5:  multi-threaded system evaluation benchmark

Running the test with following options:
Number of threads: 8
Report intermediate results every 10 second(s)
Random number generator seed is 0 and will be ignored


Threads started!
-- 每10秒钟报告一次测试结果，tps、每秒读、每秒写、99%以上的响应时长统计
[  10s] threads: 8, tps: 1111.51, reads/s: 15568.42, writes/s: 4446.13, response time: 9.95ms (99%)
[  20s] threads: 8, tps: 1121.90, reads/s: 15709.62, writes/s: 4487.80, response time: 9.78ms (99%)
[  30s] threads: 8, tps: 1120.00, reads/s: 15679.10, writes/s: 4480.20, response time: 9.84ms (99%)
[  40s] threads: 8, tps: 1114.20, reads/s: 15599.39, writes/s: 4456.30, response time: 9.90ms (99%)
[  50s] threads: 8, tps: 1114.00, reads/s: 15593.60, writes/s: 4456.70, response time: 9.84ms (99%)
[  60s] threads: 8, tps: 1119.30, reads/s: 15671.60, writes/s: 4476.50, response time: 9.99ms (99%)
OLTP test statistics:
    queries performed:
        read:                            938224    -- 读总数
        write:                           268064    -- 写总数
        other:                           134032    -- 其他操作总数(SELECT、INSERT、UPDATE、DELETE之外的操作，例如COMMIT等)
        total:                           1340320    -- 全部总数
    transactions:                        67016  (1116.83 per sec.)    -- 总事务数(每秒事务数)
    deadlocks:                           0      (0.00 per sec.)    -- 发生死锁总数
    read/write requests:                 1206288 (20103.01 per sec.)    -- 读写总数(每秒读写次数)
    other operations:                    134032 (2233.67 per sec.)    -- 其他操作总数(每秒其他操作次数)

General statistics:    -- 一些统计结果
    total time:                          60.0053s    -- 总耗时
    total number of events:              67016    -- 共发生多少事务数
    total time taken by event execution: 479.8171s    -- 所有事务耗时相加(不考虑并行因素)
    response time:    -- 响应时长统计
         min:                                  4.27ms    -- 最小耗时
         avg:                                  7.16ms    -- 平均耗时
         max:                                 13.80ms    -- 最长耗时
         approx.  99 percentile:               9.88ms    -- 超过99%平均耗时

Threads fairness:
    events (avg/stddev):           8377.0000/44.33
    execution time (avg/stddev):   59.9771/0.00


sysbench创建表的语句是：
 
CREATE TABLE sbtest (
  id int(10) unsigned NOT NULL AUTO_INCREMENT,
  k int(10) unsigned NOT NULL DEFAULT '0',
  c char(120) NOT NULL DEFAULT '',
  pad char(60) NOT NULL DEFAULT '',
  PRIMARY KEY (id),
  KEY k (k)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1

```



## mariadb安装
    https://downloads.mariadb.org/

    wget http://mirrors.neusoft.edu.cn/mariadb//mariadb-10.2.6/source/mariadb-10.2.6.tar.gz
    tar -zxf mariadb-10.2.6.tar.gz 
    cd mariadb-10.2.6
    groupadd -r mariadb
    useradd -g mariadb -r -M -s /sbin/nologin mariadb
    mkdir /etc/mariadb

    依赖  yum -y install gcc gcc-c++ make cmake ncurses ncurses libxml2 libxml2-devel openssl-devel bison bison-devel

    cmake . -DMYSQL_UNIX_ADDR=/tmp/mariadb.sock -DSYSCONFDIR=/etc/mariadb -DMYSQL_TCP_PORT=3309 -DEXTRA_CHARSETS=all 
    -DMYSQL_USER=mariadb -DCMAKE_INSTALL_PREFIX=/data/mariadb -DMYSQL_DATADIR=/data/mariadb/data  
    -DWITH_XTRADB_STORAGE_ENGINE=1 -DWITH_FEDERATEDX_STORAGE_ENGINE=1 -DWITH_ARCHIVE_STORAGE_ENGINE=1 
    -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_ARCHIVE_STPRAGE_ENGINE=1 
    -DWITH_BLACKHOLE_STORAGE_ENGINE=1 -DWIYH_READLINE=1 -DWIYH_SSL=system -DVITH_ZLIB=system -DWITH_LOBWRAP=0 
    -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci
    make -j 4
    make install

    cp support-files/my-large.cnf /etc/mariadb/my.cnf

    配置/etc/mariadb/my.cnf
    在[mysqld]模块添加下面的几行：
    log-error=/var/log/mariadb_error.log
    pid-file=/var/run/mysqld/mariadb.pid
    user=mariadb
    datadir=/data/mariadb/data
    basedir=/data/mariadb/
    新增加mysqld_safe块
    [mysqld_safe]
    log-error=/var/log/mariadb_error.log
    pid-file=/var/run/mysqld/mariadb.pid

    初始化  ./scripts/mysql_install_db --basedir=/data/mariadb/ --datadir=/data/mariadb/data/ --user=mariadb 
    --defaults-file=/etc/mariadb/my.cnf

    cp support-files/mysql.server /etc/init.d/mariadb
    chmod 755 /etc/init.d/mariadb
    vim /etc/init.d/mariadb   避免和现有的mysql冲突，如果没有mysql可以不用修改
    找到   $bindir/mysqld_safe --datadir="$datadir" --pid-file="$mysqld_pid_file_path" 
    改完   $bindir/mysqld_safe --defaults-file=/etc/mariadb/my.cnf --datadir="/data/mariadb/data" 
    --pid-file="/var/run/mysqld/mariadb.pid"   

    找到  parse_server_arguments `$print_defaults $extra_args --mysqld mysql.server`
    改为  parse_server_arguments `$print_defaults $extra_args --defaults-file=/etc/mariadb/my.cnf mysqld` 




    启动前修下目录权限
    # chown -R mariadb:mariadb /data/mariadb/

    启动MariaDB:
    # /etc/init.d/mariadb start

    注：如果启动失败，查看下/var/log/mariadb_error.log文件看报什么错，修正即可。

    设置root的密码
    #/home/local/mariadb/bin/mysqladmin -u root password '123456'

    进入MariaDB的shell下
    [root@localhost mariadb]# /data/mariadb/bin/mysql -u root -p
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    MariaDB [(none)]> show engines\G;

    MariaDB [mysql]>use mysql; //选择系统数据库mysql   
    MariaDB [mysql]>select Host,User,Password from user; //查看所有用户   
    MariaDB [mysql]>delete from user where password="";
    MariaDB [mysql]>GRANT ALL PRIVILEGES ON *.* TO root@"%" IDENTIFIED BY '123456'; //为root添加
    远程连接的能力
    MariaDB [mysql]>flush privileges;   
    MariaDB [mysql]>select Host,User,Password from user; //确认密码为空的用户是否已全部删除   
    MariaDB [mysql]>exit; 


    设置防火墙，以便局域网内的其它服务器可以访问
    vi /etc/sysconfig/iptables

    -A INPUT -m state --state NEW -m tcp -p tcp --dport 3309 -j ACCEPT

    /etc/init.d/iptables restart



## 临时表位置
```
mount  -t tmpfs -o size=20m  tmpfs /mnt/ramdisk
/etc/fstab
tmpfs            /mnt/ramdisk/   tmpfs    size=20m    0 0

SHOW GLOBAL VARIABLES LIKE 'tmpdir';

my.cnf
[mysqld]
max_heap_table_size=1024M   #内存表容量
tmp_table_size=1024M              #临时表容量
tmpdir=/mnt/ramdisk
```



## sqladvisor优化工具
```
美团sql优化工具
https://github.com/Meituan-Dianping/SQLAdvisor
```



## slow_kill.sh
```

#!/usr/bin/env bash
mysql --login-path=test -e "show full processlist" | grep -i select | awk '{print $1,$6}' > /script/slow.txt

while read line
do
   time1=$(echo $line | awk '{print $2}')
   if [ $time1 -gt 5  ];then    超过5s杀掉
       id=$(echo $line | awk '{print $1}')
       echo $id, $time1
       mysql --login-path=test -e "kill $id"
   fi
done < /script/slow.txt
```



## 主从不同步
```
重新做主从，完全同步
该方法适用于主从库数据相差较大，或者要求数据完全统一的情况

解决步骤如下：
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
主库设置

1.先进入主库，进行锁表，防止数据写入
使用命令：
mysql> flush tables with read lock;
注意：该处是锁定为只读状态，语句不区分大小写

同步用户，如已有不再创建
grant replication slave on *.* to 'repl'@'192.168.0.%' identified by '123456';
flush privileges;

2.进行数据备份
#把数据备份到all.sql文件
mysqldump --master-data=2 --single-transaction -R --triggers -A > all.sql
其中--master-data=2代表备份时刻记录master的Binlog位置和Position
       --single-transaction意思是获取一致性快照
       -R意思是备份存储过程和函数
       --triggres的意思是备份触发器
        -A代表备份所有的库。更多信息请自行mysqldump --help查看。
这里注意一点：数据库备份一定要定期进行，可以用shell脚本或者python脚本，都比较方便，确保数据万无一失

3.查看主库备份时的binlog名称和位置，MASTER_LOG_FILE和MASTER_LOG_POS：

[root@192.168.0.50 ~]# head -n 30 all.sql | grep 'CHANGE MASTER TO'
-- CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000010', MASTER_LOG_POS=112;

4  解锁主数据库的锁表操作
[root@master ~]# mysql -uroot -p    (本命令在主数据库服务器上执行)
mysql> unlock tables;
Query OK, 0 rows affected (0.00 sec)

5 .把mysql备份文件传到从库机器，进行数据恢复
#使用scp命令
[root@server01 mysql]# scp all.sql root@192.168.128.101:/tmp/

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
从库设置  注意配置文件 server-id
5.停止从库的状态
mysql> stop slave;

6.然后到从库执行mysql命令，导入数据备份
mysql> source /tmp/mysql.bak.sql

7.设置从库同步，注意该处的同步点，就是主库show master status信息里的| File| Position两项
CHANGE MASTER TO MASTER_HOST='192.168.0.50',MASTER_USER='repl', MASTER_PASSWORD='123456',
MASTER_LOG_FILE='mysql-bin.000010',MASTER_LOG_POS=112;

8.重新开启从同步
mysql> start slave;

9.查看同步状态
mysql> show slave status\G  查看：

Slave_IO_Running: Yes
Slave_SQL_Running: Yes
Seconds_Behind_Master: 0   变为0说明都同步完毕

好了，同步完成啦。
```



## mysql安装
```
ftp://mirror.switch.ch/mirror/mysql/Downloads/
国内 http://mirrors.sohu.com/mysql/


yum install rpm-build gperf ncurses-devel cmake  libaio-devel
rpm -ivh MySQL-5.6.30-1.el6.src.rpm

cd ./rpmbuild/SPECS/
rpmbuild -bb mysql.spec --define='runselftest 0'
cd ../RPMS/x86_64/  里面是编译好的rpm包

源码安装
wget http://mirrors.sohu.com/mysql/MySQL-5.6/mysql-5.6.34.tar.gz
 
yum -y install make gcc-c++ cmake bison-devel  ncurses-devel
groupadd mysql
useradd -g mysql mysql
 
cmake \
-DCMAKE_INSTALL_PREFIX=/data/mysql/ \
-DMYSQL_DATADIR=/data/mysql/data \
-DSYSCONFDIR=/etc \
-DWITH_MYISAM_STORAGE_ENGINE=1 \
-DWITH_INNOBASE_STORAGE_ENGINE=1 \
-DWITH_MEMORY_STORAGE_ENGINE=1 \
-DWITH_READLINE=1 \
-DMYSQL_UNIX_ADDR=/var/lib/mysql/mysql.sock \
-DMYSQL_TCP_PORT=3306 \
-DENABLED_LOCAL_INFILE=1 \
-DWITH_PARTITION_STORAGE_ENGINE=1 \
-DEXTRA_CHARSETS=all \
-DDEFAULT_CHARSET=utf8 \
-DDEFAULT_COLLATION=utf8_general_ci
 
make && make install
 
cp cp support-files/my-default.cnf /etc/my.cnf
##config file edit
vim /etc/my.cnf
skip-name-resolve=1
 
cp support-files/mysql.server /etc/init.d/mysql
chmod 755 /etc/init.d/mysql
 
chown mysql.mysql /data/mysql/ -R
##init mysql datadir
chmod 755 scripts/mysql_install_db
scripts/mysql_install_db --user=mysql --basedir=/data/mysql/ --datadir=/data/mysql/data/
 
/etc/init.d/mysql start

运行sql  /data/mysql/bin/mysql
delete from mysql.user where user="";  删除匿名用户
set password=PASSWORD('pass');      设置登录密码
FLUSH PRIVILEGES;
```



## 主从Last_SQL_error
```
由于字符集编码问题，导致slave上insert中文时出错。

处理过程为:
1. 先停止slave
MySQL>stop slave;

2. 跳过slave上的1个错误
mysql>set  global sql_slave_skip_counter=1;

3.在slave上手工插入一条数据
mysql>insert into  ...

4.启动slave
mysql>start slave;

5.过了一段时间，待Seconds_Behind_Master为0后
mysql>pager grep -i -E  'Running|Seconds'
mysql>show slave status\G
             Slave_IO_Running: Yes
            Slave_SQL_Running: Yes
        Seconds_Behind_Master: 0
      Slave_SQL_Running_State: Slave has read all relay log; waiting for the slave I/O thread to update it
1 row in set (0.00 sec)

6.检查同步表的数据，发现slave比master少一条
mysql>select count(1)  from test;


此时master上业务已经停止更新test表中的数据。


检查master上的binlog：
# at 666
#141121 14:23:38 server id 150  end_log_pos 755 CRC32 0x10a3f34c        Query   thread_id=411   exec_time=0    
 error_code=0
SET TIMESTAMP=1416551018/*!*/;
BEGIN
/*!*/;
# at 755
#141121 14:23:38 server id 150  end_log_pos 865 CRC32 0xca82b435        Query   thread_id=411   exec_time=0   
  error_code=0
SET TIMESTAMP=1416551018/*!*/;
insert into test values('北京')
/*!*/;
# at 865
#141121 14:23:38 server id 150  end_log_pos 975 CRC32 0xd377f37e        Query   thread_id=411   exec_time=0  
   error_code=0
SET TIMESTAMP=1416551018/*!*/;
insert into test values(‘上海’)
/*!*/;
# at 975
#141121 14:23:38 server id 150  end_log_pos 1006 CRC32 0x91c3fc01       Xid = 2745705
COMMIT/*!*/;
发现在一个BEGIN/insert/COMMIT中插入了多条数据，而我只在slave上插入了一条。
所以数据会比master上少一条。去slave上查找，果然找不到这个事物中插入的另一条记录。
这是因为如果跳过的event在一个事物内，则整个事物的event都会被跳过。

所以在使用set  global sql_slave_skip_counter=1; 时要注意以下几点：
1. 检查跳过的event是否在一个事物中
2. 跳过slave上的event进行后续处理后要检查数据的一致性。
3. 最好能在master的binglog上查看一下跳过的evnet到底做了写什么。
```



## 慢查询
```
long_query_time=10  超过该配置时间的 SQL 语句将会被记录，时间是秒
slow_query_log=1   表示开启慢查询记录

#以前版本的参数格式跟5.6的不一致
slow_query_log_file=/data/mysql/data/mysql-master-slow.log
#将所有没有使用带索引的查询语句全部写到慢查询日志中
log_queries_not_using_indexes=1

show variables like '%slow%';
show variables like '%index%';


写入到表 mysql.slow_log
select @@global.log_output;
set @@global.log_output='TABLE';
```



## 优化建议
```
1.对查询进行优化，应尽量避免全表扫描，首先应考虑在 where 及 order by 涉及的列上建立索引。

缺省情况下建立的索引是非群集索引，但有时它并不是最佳的。在非群集索引下，数据在物理上随机存放在数据页上。合理的索引设计
要建立在对各种查询的分析和预测上。一般来说：

a.有大量重复值、且经常有范围查询( > ,< ,> =,< =)和 order by、group by 发生的列，可考虑建立集群索引;

  b.经常同时存取多列，且每列都含有重复值可考虑建立组合索引， 选择度高的列建议作为索引的第一个字段

c.组合索引要尽量使关键查询形成索引覆盖，其前导列一定是使用最频繁的列。索引虽有助于提高性能但 不是索引越多越好，恰好相反
过多的索引会导致系统低效。用户在表中每加进一个索引，维护索引集合就 要做相应的更新工作。

2.应尽量避免在 where 子句中对字段进行 null 值判断，否则将导致引擎放弃使用索引而进行全表扫描，

Sql 代码 : select id from t where num is null;
可以在 num 上设置默认值 0,确保表中 num 列没有 null 值，然后这样查询：

Sql 代码 : select id from t where num=0;
3.应尽量避免在 where 子句中使用!=或<>操作符，否则将引擎放弃使用索引而进行全表扫描。

4.应尽量避免在 where 子句中使用 or 来连接条件，否则将导致引擎放弃使用索引而进行全表扫描，

Sql 代码 : select id from t where num=10 or num=20;
可以这样查询：

Sql 代码 : select id from t where num=10 union all select id from t where num=20;
5.in 和 not in 也要慎用，否则会导致全表扫描，如：

Sql 代码 : select id from t where num in(1,2,3);
对于连续的数值，能用 between 就不要用 in 了：

Sql 代码 : select id from t where num between 1 and 3;
6.下面的查询也将导致全表扫描：

Sql 代码 : select id from t where name like '%c%';
若要提高效率，可以考虑全文检索。

7.如果在 where 子句中使用参数，也会导致全表扫描。因为 SQL 只有在运行时才会解析局部变量，但优 化程序不能将访问计划的选择推迟
到运行时;它必须在编译时进行选择。然 而，如果在编译时建立访问计 划，变量的值还是未知的，因而无法作为索引选择的输入项。如下面语
句将进行全表扫描：

Sql 代码 : select id from t where num=@num ;
可以改为强制查询使用索引：

Sql 代码 : select id from t with(index(索引名)) where num=@num ;
8.应尽量避免在 where 子句中对字段进行表达式操作， 这将导致引擎放弃使用索引而进行全表扫描。

Sql 代码 : select id from t where num/2=100;
可以这样查询：

Sql 代码 : select id from t where num=100*2;
9.应尽量避免在 where 子句中对字段进行函数操作，这将导致引擎放弃使用索引而进行全表扫描。如：

Sql 代码 : select id from t where substring(name,1,3)='abc';#name 以 abc 开头的 id
应改为：

Sql 代码 : select id from t where name like 'abc%';
10.不要在 where 子句中的“=”左边进行函数、算术运算或其他表达式运算，否则系统将可能无法正确使用 索引。

11.在使用索引字段作为条件时，如果该索引是复合索引，那么必须使用到该索引中的第一个字段作为条件 时才能保证系统使用该索引， 否则
该索引将不会 被使用， 并且应尽可能的让字段顺序与索引顺序相一致。

12.不要写一些没有意义的查询，如需要生成一个空表结构：

Sql 代码 : select col1,col2 into #t from t where 1=0;
这类代码不会返回任何结果集，但是会消耗系统资源的，应改成这样：

Sql 代码 : create table #t(…);
13.很多时候用 exists 代替 in 是一个好的选择：

Sql 代码 : select num from a where num in(select num from b);
用下面的语句替换：

Sql 代码 : select num from a where exists(select 1 from b where num=a.num);
14.并不是所有索引对查询都有效，SQL 是根据表中数据来进行查询优化的，当索引列有大量数据重复时， SQL 查询可能不会去利用索引，如
一表中有字段 ***,male、female 几乎各一半，那么即使在 *** 上建 了索引也对查询效率起不了作用。

15.索引并不是越多越好，索引固然可以提高相应的 select 的效率，但同时也降低了 insert 及 update 的效率，因为 insert 或 update 
时有可能会重建索引，所以怎样建索引需要慎重考虑，视具体情况而定。一个表的索引数最好不要超过 6 个，若太多则应考虑一些不常使用到的列
上建的索引是否有必要。

16.应尽可能的避免更新 clustered 索引数据列， 因为 clustered 索引数据列的顺序就是表记录的物理存储顺序，一旦该列值改变将导致整个
表记录的顺序的调整，会耗费相当大的资源。若应用系统需要频繁更新 clustered 索引数据列，那么需要考虑是否应将该索引建为 clustered 索引。

17.尽量使用数字型字段，若只含数值信息的字段尽量不要设计为字符型，这会降低查询和连接的性能，并 会增加存储开销。这是因为引擎在处理查
询和连接时会逐个比较字符串中每一个字符，而对于数字型而言 只需要比较一次就够了。

18.尽可能的使用 varchar/nvarchar 代替 char/nchar , 因为首先变长字段存储空间小， 可以节省存储空间， 其次对于查询来说，在一个
相对较小的字段内搜索效率显然要高些。

19.任何地方都不要使用 select * from t ,用具体的字段列表代替“*”,不要返回用不到的任何字段。

20.尽量使用表变量来代替临时表。如果表变量包含大量数据，请注意索引非常有限(只有主键索引)。

21.避免频繁创建和删除临时表，以减少系统表资源的消耗。

22.临时表并不是不可使用，适当地使用它们可以使某些例程更有效，例如，当需要重复引用大型表或常用 表中的某个数据集时。但是，对于一次
性事件， 最好使用导出表。

23.在新建临时表时，如果一次性插入数据量很大，那么可以使用 select into 代替 create table,避免造成大量 log ,以提高速度;如果数
据量不大，为了缓和系统表的资源，应先 create table,然后 insert.

24.如果使用到了临时表， 在存储过程的最后务必将所有的临时表显式删除， 先 truncate table ,然后 drop table ,这样可以避免系统表
的较长时间锁定。

25.尽量避免使用游标，因为游标的效率较差，如果游标操作的数据超过 1 万行，那么就应该考虑改写。

26.使用基于游标的方法或临时表方法之前，应先寻找基于集的解决方案来解决问题，基于集的方法通常更 有效。


27.与临时表一样，游标并不是不可使用。对小型数据集使用 FAST_FORWARD 游标通常要优于其他逐行处理方法，尤其是在必须引用几个表才能
获得所需的数据时。在结果集中包括“合计”的例程通常要比使用游标执行的速度快。如果开发时 间允许，基于游标的方法和基于集的方法都可以
尝试一下，看哪一种方法的效果更好。

28.在所有的存储过程和触发器的开始处设置 SET NOCOUNT ON ,在结束时设置 SET NOCOUNT OFF .无需在执行存储过程和触发器的每个语句
后向客户端发送 DONE_IN_PROC 消息。

29.尽量避免大事务操作，提高系统并发能力。

30.定期分析表和检查表。

分析表的语法：ANALYZE [LOCAL | NO_WRITE_TO_BINLOG] TABLE tb1_name[, tbl_name]...
以上语句用于分析和存储表的关键字分布，分析的结果将可以使得系统得到准确的统计信息，使得SQL能够生成正确的执行计划。如果用户感觉实
际执行计 划并不是预期的执行计划，执行一次分析表可能会解决问题。在分析期间，使用一个读取锁定对表进行锁定。这对于MyISAM，DBD和
InnoDB表有作 用。

例如分析一个数据表：analyze table table_name
检查表的语法：CHECK TABLE tb1_name[,tbl_name]...[option]...option = {QUICK | FAST | MEDIUM | EXTENDED | CHANGED}
检查表的作用是检查一个或多个表是否有错误，CHECK TABLE 对MyISAM 和 InnoDB表有作用，对于MyISAM表，关键字统计数据被更新

CHECK TABLE 也可以检查视图是否有错误，比如在视图定义中被引用的表不存在。

31.定期优化表。

优化表的语法：OPTIMIZE [LOCAL | NO_WRITE_TO_BINLOG] TABLE tb1_name [,tbl_name]...

如果删除了表的一大部分，或者如果已经对含有可变长度行的表(含有 VARCHAR、BLOB或TEXT列的表)进行更多更改，则应使用OPTIMIZE TABLE
命令来进行表优化。这个命令可以将表中的空间碎片进行合并，并且可以消除由于删除或者更新造成的空间浪费，但OPTIMIZE TABLE 命令只对
MyISAM、 BDB 和InnoDB表起作用。

例如： optimize table table_name
注意： analyze、check、optimize执行期间将对表进行锁定，因此一定注意要在MySQL数据库不繁忙的时候执行相关的操作。32.存储引擎的
选择如果数据表需要事务处理，应该考虑使用InnoDB，因为它完全符合ACID特性。如果不需要事务处理，使用默认存储引擎MyISAM是比较明智的。


MyISAM适合于一些需要大量查询的应用，但其对于有大量写操作并不是很好。甚至你只是需要update一个字段，整个表都会被锁起来，而别的
进程，就算是读进程都
无法操作直到读操作完成。另外，MyISAM 对于 SELECT COUNT(*) 这类的计算是超快无比的。 

InnoDB 的趋势会是一个非常复杂的存储引擎，对于一些小的应用，它会比 MyISAM 还慢。他是它支持“行锁” ，于是在写操作比较多的时候，
会更优秀。并且，他还支持更多的高级应用，比如：事务。


33、定期用explain优化慢查询中的SQL语句

34、EXPLAIN 你的 SELECT 查询 

使用 EXPLAIN 关键字可以让你知道MySQL是如何处理你的SQL语句的。这可以帮你分析你的查询语句或是表结构的性能瓶颈。 

EXPLAIN 的查询结果还会告诉你你的索引主键被如何利用的，你的数据表是如何被搜索和排序的……等等，等等。 

挑一个你的SELECT语句（推荐挑选那个最复杂的，有多表联接的），把关键字EXPLAIN加到前面。你可以使用phpmyadmin来做这个事。然后，
你会看到一张表格。下面的这个示例中，我们忘记加上了group_id索引，并且有表联接：

当我们为 group_id 字段加上索引后：

我们可以看到，前一个结果显示搜索了 7883 行，而后一个只是搜索了两个表的 9 和 16 行。查看rows列可以让我们找到潜在的性能问题。 

35、 当只要一行数据时使用 LIMIT 1 

当你查询表的有些时候，你已经知道结果只会有一条结果，但因为你可能需要去fetch游标，或是你也许会去检查返回的记录数。 

在这种情况下，加上 LIMIT 1 可以增加性能。这样一样，MySQL数据库引擎会在找到一条数据后停止搜索，而不是继续往后查少下一条符合记录
的数据。 

下面的示例，只是为了找一下是否有“中国”的用户，很明显，后面的会比前面的更有效率。（请注意，第一条中是Select *，第二条是Select 1）

复制代码
// 没有效率的：
$r = mysql_query("SELECT * FROM user WHERE country = 'China'");
if (mysql_num_rows($r) > 0) {
// ...}

// 有效率的：
$r = mysql_query("SELECT 1 FROM user WHERE country = 'China' LIMIT 1");
if (mysql_num_rows($r) > 0) {
// ...
}
复制代码


36. 在Join表的时候使用相同类型的列，并将其索引 

如果你的应用程序有很多 JOIN 查询，你应该确认两个表中Join的字段是被建过索引的。这样，MySQL内部会启动为你优化Join的SQL语句的机制。 

而且，这些被用来Join的字段，应该是相同的类型的。例如：如果你要把 DECIMAL 字段和一个 INT 字段Join在一起，MySQL就无法使用它们
的索引。对于那些STRING类型，还需要有相同的字符集才行。（两个表的字符集有可能不一样）
// 在state中查找company
$r = mysql_query("SELECT company_name FROM users
LEFT JOIN companies ON (users.state = companies.state)
WHERE users.id = $user_id"); 
两个 state 字段应该是被建过索引的，而且应该是相当的类型，相同的字符集。

37、千万不要 ORDER BY RAND() 

想打乱返回的数据行？随机挑一个数据？真不知道谁发明了这种用法，但很多新手很喜欢这样用。但你确不了解这样做有多么可怕的性能问题。 

如 果你真的想把返回的数据行打乱了，你有N种方法可以达到这个目的。这样使用只让你的数据库的性能呈指数级的下降。这里的问题是：MySQL
会不得不去执行 RAND()函数（很耗CPU时间），而且这是为了每一行记录去记行，然后再对其排序。就算是你用了Limit 1也无济于事（因为要排序） 

下面的示例是随机挑一条记录


复制代码
// 千万不要这样做：
$r = mysql_query("SELECT username FROM user ORDER BY RAND() LIMIT 1");

// 这要会更好：
$r = mysql_query("SELECT count(*) FROM user");
$d = mysql_fetch_row($r);
$rand = mt_rand(0,$d[0] - 1);
$r = mysql_query("SELECT username FROM user LIMIT $rand, 1");
复制代码

38. 永远为每张表设置一个ID 

我们应该为数据库里的每张表都设置一个ID做为其主键，而且最好的是一个INT型的（推荐使用UNSIGNED），并设置上自动增加的 
AUTO_INCREMENT标志。 

就算是你 users 表有一个主键叫 “email”的字段，你也别让它成为主键。使用 VARCHAR 类型来当主键会使用得性能下降。另外，在你
的程序中，你应该使用表的ID来构造你的数据结构。 

而且，在MySQL数据引擎下，还有一些操作需要使用主键，在这些情况下，主键的性能和设置变得非常重要，比如，集群，分区…… 

在 这里，只有一个情况是例外，那就是“关联表”的“外键”，也就是说，这个表的主键，通过若干个别的表的主键构成。我们把这个情况
叫做“外键”。比如：有一 个“学生表”有学生的ID，有一个“课程表”有课程ID，那么，“成绩表”就是“关联表”了，其关联了学生表和
课程表，在成绩表中，学生ID和课程ID叫 “外键”其共同组成主键。



39. 从 PROCEDURE ANALYSE() 取得建议 

PROCEDURE ANALYSE() 会让 MySQL 帮你去分析你的字段和其实际的数据，并会给你一些有用的建议。只有表中有实际的数据，这些
建议才会变得有用，因为要做一些大的决定是需要有数据作为基础的。 

例 如，如果你创建了一个 INT 字段作为你的主键，然而并没有太多的数据，那么，PROCEDURE ANALYSE()会建议你把这个字段的类型
改成 MEDIUMINT 。或是你使用了一个 VARCHAR 字段，因为数据不多，你可能会得到一个让你把它改成 ENUM 的建议。这些建议，都
是可能因为数据不够多，所以决策做得就不够准。 

在phpmyadmin里，你可以在查看表时，点击 “Propose table structure” 来查看这些建议

一定要注意，这些只是建议，只有当你的表里的数据越来越多时，这些建议才会变得准确。一定要记住，你才是最终做决定的人。



40. 字段尽可能的使用 NOT NULL约束 
       除非你有一个很特别的原因去使用 NULL 值，你应该总是让你的字段保持 NOT NULL。这看起来好像有点争议，请往下看。 

首先，问问你自己“Empty”和“NULL”有多大的区别（如果是INT，那就是0和NULL）？如果你觉得它们之间没有什么区别，那么你就不要
使用NULL。（你知道吗？在 Oracle 里，NULL 和 Empty 的字符串是一样的！) 

不要以为 NULL 不需要空间，其需要额外的空间，并且，在你进行比较的时候，你的程序会更复杂。 当然，这里并不是说你就不能使
用NULL了，现实情况是很复杂的，依然会有些情况下，你需要使用NULL值。 

下面摘自MySQL自己的文档： 

“NULL columns require additional space in the row to record whether their values are NULL. For MyISAM tables,
 each NULL column takes one bit extra, rounded up to the nearest byte.” 
如果你要保存 NULL,手动去设置它，而不是把它设为默认值。 建议用用0、特殊值或空串代替NULL值


41. Prepared Statements 
Prepared Statements很像存储过程，是一种运行在后台的SQL语句集合，我们可以从使用 prepared statements 获得很多好处，无论
是性能问题还是安全问题。 

Prepared Statements 可以检查一些你绑定好的变量，这样可以保护你的程序不会受到“SQL注入式”攻击。当然，你也可以手动地检查你
的这些变量，然而，手动的检查容易出问题， 而且很经常会被程序员忘了。当我们使用一些framework或是ORM的时候，这样的问题会好一些。 

在性能方面，当一个相同的查询被使用多次的时候，这会为你带来可观的性能优势。你可以给这些Prepared Statements定义一些参数，
而MySQL只会解析一次。 

虽然最新版本的MySQL在传输Prepared Statements是使用二进制形势，所以这会使得网络传输非常有效率。 

当然，也有一些情况下，我们需要避免使用Prepared Statements，因为其不支持查询缓存。但据说版本5.1后支持了。 

42. 把IP地址存成 UNSIGNED INT 
很 多程序员都会创建一个 VARCHAR(15) 字段来存放字符串形式的IP而不是整形的IP。如果你用整形来存放，只需要4个字节，并且你可
以有定长的字段。而且，这会为你带来查询上的优势，尤其是当 你需要使用这样的WHERE条件：IP between ip1 and ip2。 

我们必需要使用UNSIGNED INT，因为 IP地址会使用整个32位的无符号整形。 

而你的查询，你可以使用 INET_ATON() 来把一个字符串IP转成一个整形，并使用 INET_NTOA() 把一个整形转成一个字符串IP。在PHP中，
也有这样的函数 ip2long() 和 long2ip()。 
1 $r = "UPDATE users SET ip = INET_ATON('{$_SERVER['REMOTE_ADDR']}') WHERE user_id = $user_id";

43. 固定长度的表会更快 
       如 果表中的所有字段都是“固定长度”的，整个表会被认为是 “static” 或 “fixed-length”。 例如，表中没有如下类型的字段： 
       VARCHAR，TEXT，BLOB。只要你包括了其中一个这些字段，那么这个表就不是“固定长度静态表”了，这样，MySQL 引擎会用另一种方
       法来处理。 

       固定长度的表会提高性能，因为MySQL搜寻得会更快一些，因为这些固定的长度是很容易计算下一个数据的偏移量的，所以读取的自然
       也会很快。而如果字段不是定长的，那么，每一次要找下一条的话，需要程序找到主键。 

       并且，固定长度的表也更容易被缓存和重建。不过，唯一的副作用是，固定长度的字段会浪费一些空间，因为定长的字段无论你用
       不用，他都是要分配那么多的空间。 

使用“垂直分割”技术（见下一条），你可以分割你的表成为两个一个是定长的，一个则是不定长的。 
45. 垂直分割表 
       “垂直分割”是一种把数据库中的表按列变成几张表的方法，这样可以降低表的复杂度和字段的数目，从而达到优化的目的。（以前，
       在银行做过项目，见过一张表有100多个字段，很恐怖）

       示 例一：在Users表中有一个字段是家庭地址，这个字段是可选字段，相比起，而且你在数据库操作的时候除了个人信息外，你并不
       需要经常读取或是改写这个字 段。那么，为什么不把他放到另外一张表中呢？ 这样会让你的表有更好的性能，大家想想是不是，大
       量的时候，我对于用户表来说，只有用户ID，用户名，口令，用户角色等会被经常使用。小一点的表总是会有 好的性能。 

       示例二： 你有一个叫 “last_login” 的字段，它会在每次用户登录时被更新。但是，每次更新时会导致该表的查询缓存被清空。所
       以，你可以把这个字段放到另一个表中，这样就不会影响你对用户 ID，用户名，用户角色的不停地读取了，因为查询缓存会帮你增加很
       多性能。 

另外，你需要注意的是，这些被分出去的字段所形成的表，你不会经常性地去Join他们，不然的话，这样的性能会比不分割时还要差，而且，会
是极数级的下降。

46. 拆分大的 DELETE 或 INSERT 语句 
         如果你需要在一个在线的网站上去执行一个大的 DELETE 或 INSERT 查询，你需要非常小心，要避免你的操作让你的整个网站停止相
         应。因为这两个操作是会锁表的，表一锁住了，别的操作都进不来了。 

       Apache 会有很多的子进程或线程。所以，其工作起来相当有效率，而我们的服务器也不希望有太多的子进程，线程和数据库链接，这是
       极大的占服务器资源的事情，尤其是内存。 

       如果你把你的表锁上一段时间，比如30秒钟，那么对于一个有很高访问量的站点来说，这30秒所积累的访问进程/线程，数据库链接，打开
       的文件数，可能不仅仅会让你泊WEB服务Crash，还可能会让你的整台服务器马上掛了。 

所以，如果你有一个大的处理，你定你一定把其拆分，使用 LIMIT 条件是一个好的方法。下面是一个示例：


复制代码
while (1) {
//每次只做1000条
mysql_query("DELETE FROM logs WHERE log_date <= '2009-11-01' LIMIT 1000");
if (mysql_affected_rows() == 0) {
// 没得可删了，退出！break;
}
// 每次都要休息一会儿
usleep(50000);
}
复制代码

47. 越小的列会越快 
对于大多数的数据库引擎来说，硬盘操作可能是最重大的瓶颈。所以，把你的数据变得紧凑会对这种情况非常有帮助，因为这减少了对硬盘的访问。 

参看 MySQL 的文档 Storage Requirements 查看所有的数据类型。 

如果一个表只会有几列罢了（比如说字典表，配置表），那么，我们就没有理由使用 INT 来做主键，使用 MEDIUMINT, SMALLINT 或是更小的 
TINYINT 会更经济一些。如果你不需要记录时间，使用 DATE 要比 DATETIME 好得多。 

当然，你也需要留够足够的扩展空间，不然，你日后来干这个事，你会死的很难看，参看Slashdot的例子（2009年11月06 日），一个简单的
ALTER TABLE语句花了3个多小时，因为里面有一千六百万条数据。 


48. 使用一个对象关系映射器（Object Relational Mapper） 
    使用 ORM (Object Relational Mapper)，你能够获得可靠的性能增涨。一个ORM可以做的所有事情，也能被手动的编写出来。但是，这需
    要一个高级专家。 

ORM 的最重要的是“Lazy Loading”，也就是说，只有在需要的去取值的时候才会去真正的去做。但你也需要小心这种机制的副作用，因为这很有可
能会因为要去创建很多很多小的查 询反而会降低性能。 ORM 还可以把你的SQL语句打包成一个事务，这会比单独执行他们快得多得多。 

49. 小心“永久链接” 
“永 久链接”的目的是用来减少重新创建MySQL链接的次数。当一个链接被创建了，它会永远处在连接的状态，就算是数据库操作已经结束了。而且，
自从我们的 Apache开始重用它的子进程后——也就是说，下一次的HTTP请求会重用Apache的子进程，并重用相同的 MySQL 链接。 


50、范围列(>,<,between and)可以用到索引，但是范围列后面的列无法用到索引。同时，索引最多用于一个范围列，因此如果查询条件中有两个范
围列则无法全用到索引

51、如果需要在大字段上建立索引，可以考虑使用前缀索引。

建立前缀索引的语法为：

ALTER TABLE table_name ADD KEY(column_name(prefix_length));
 52、 将大字段、访问频率低的字段拆分到单独的表中存储，分离冷热数据，有利于有效利用缓存，防止读入无用的冷数据，较少磁盘IO,同时保证热
 数据常驻内存提高缓存命中率。

53、 MYSQL的新增和修改列的操作相当于重建表，表设计要一步到位，尽量避免大表的DDL操作。 （TIPS:可以预定义一些列留作将来业务扩展，
如：当前只需要10个字段，考虑到未来发展，可以预留10个字段，表上总共创建20个字段）

54、为了降低索引维护成本，禁止冗余索引，增大IO压力。（a,b,c）、（a,b），后者为冗余索引。可以利用前缀索引来达到加速目的，减轻维护
负担。

55、WHERE子句中的数据扫描不超过表总数据量的30%

如何选择prefix_length的长度，具体参考：前缀索引，一种优化索引大小的解决方案



补充：

》、在海量查询时尽量少用格式转换。

》、任何对列的操作都将导致表扫描，它包括数据库教程函数、计算表达式等等，查询时要尽可能将操作移 至等号右边。

》、IN、OR 子句常会使用工作表，使索引失效。如果不产生大量重复值，可以考虑把子句拆开。拆开的子 句中应该包含索引。

》、尽量少用 CLOB、TEXT、BLOB大类型

》、如果你的数据只有你所知的少量的几个。最好使用 ENUM 类型

ENUM 类型是非常快和紧凑的。在实际上，其保存的是 TINYINT，但其外表上显示为字符串。这样一来，用这个字段来做一些选项列表变得
相当的完美。 
如果你有一个字段，比如“性别”，“国家”，“民族”，“状态”或“部门”，你知道这些字段的取值是有限而且固定的，那么，你应该使用 ENUM 而
不是 VARCHAR。 
MySQL也有一个“建议”（见第十条）告诉你怎么去重新组织你的表结构。当你有一个 VARCHAR 字段时，这个建议会告诉你把其改成 ENUM 类型。
使用 PROCEDURE ANALYSE() 你可以得到相关的建议。

》、合理用运分库、分表与分区表提高数据存放和提取速度。具体参考：Mysql分表和分区的区别、分库分表区别




下面是简单版，只是对上面的知识点浓缩，方便记忆：
复制代码
索引：
考虑在 where 及 order by 涉及的列上建立索引
经常同时存取多列，且每列都含有重复值可考虑建立组合索引，且查询越频繁的字段放前面
按需使用聚集与非聚集索引，聚集不适合频繁更新、适合范围查询( > ,< ,> =,< =)和 order by、group by ，
注意复合索引的顺序，选择性高的建议放前面
不要在数据选择性不高的字段建立索引
索引控制在6个以内为好
大字段可以考虑使用前缀索引
去除冗余索引

where子句的操作：
尽量避免在 where 子句中对字段进行 null 值判断、!=或<>操作符、 or 来连接条件、in 和 not in、like时%在前面、使用参数，如
where num=@num、
表达式操作，如where num/2=100、函数操作(“=”左边进行函数)，如substring(name,1,3)='abc';#name、算术运算或其他表达式运算
exists 代替 in
一个查询中避免多个范围查询
WHERE子句中的数据扫描不超过表总数据量的30%

表结构：
能用数字和枚举类型就不用其他类型
使用 varchar/nvarchar 代替 char/nchar 
字段尽可能的使用 NOT NULL
把IP地址存成 UNSIGNED INT
固定长度的表会更快
越小的列会越快


临时表：
可用变量就不要用临时表
避免频繁创建和删除临时表
需要重复引用大型表或常用 表中的某个数据集时可用临时表
新建临时表时，如果一次性插入数据量很大，用 select into 代替 create table
注意删除临时表，先 truncate table ,然后 drop table

其他：
不使用select *
大量数据时不适合用游标处理
在所有的存储过程和触发器的开始处设置 SET NOCOUNT ON ,在结束时设置 SET NOCOUNT OFF
定期ANALYZE、CHECK 、OPTIMIZE 表
EXPLAIN 你的 SELECT 查询
善用LIMIT 避免一次性查询大量数据
在Join表的时候使用相同类型的列，并将其索引
千万不要 ORDER BY RAND()
除了关联表 永远为每张表设置一个ID
Prepared Statements
小心“永久链接”
尽量避免大事务操作
拆分大的 DELETE 或 INSERT 或 insert .. into .. select.. 语句 减少锁表时间
使用orm
使用缓存，例如一级缓存，二级缓存、redis、memcace分布式
合理用运分库、分表与分区表提高数据存放和提取速度
复制代码


附：

mysql 慢查询查看方案

  truncate table  mysql.slow_log;

select db, query_TIME, lock_time, rows_examined, sql_text from mysql.slow_log

来源： http://blog.csdn.net/xyw591238/article/details/51965389
```



## 5.6明文密码问题
```
mysql -uroot -pxxx -e "show slave status\G"  会提示   Warning: Using a password on the command line interface 
can be insecure.

5.6以上版本才有mysql_config_editor

创建一个login-path
mysql_config_editor set --login-path=test --user=root --password --host=localhost
Enter password:

创建好后，.mylogin.cnf将保存在用户的家目录下，该文件是不可读的，它类似于选项组，包含单个身份的验证信息

mysql --login-path=test  直接登陆
mysql --login-path=test -e "show slave status\G"  也没有错误提示

查看.mylogin.cnf里写了什么
mysql_config_editor print --all
mysql_config_editor print --login-path=test

删除.mylogin.cnf，则可以使用
mysql_config_editor remove --login-path=test
```



## 备份
```
备份函数和触发器
mysqldump --master-data=2 --single-transaction -R --triggers -A > all.sql
其中--master-data=2代表备份时刻记录master的Binlog位置和Position，--single-transaction意思是获取一致性快照，
-R意思是备份存储过程和函数，--triggres的意思是备份触发器，-A代表备份所有的库

查看主库备份时的binlog名称和位置，MASTER_LOG_FILE和MASTER_LOG_POS：
head -n 30 all.sql | grep 'CHANGE MASTER TO'
-- CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000010', MASTER_LOG_POS=112;

mysql < /data/all.sql

============================================
备份分为冷备和热备

冷备份
因为mysql中库即目录（database is folder）所以冷备份其实就是备份整个目录。
停掉mysql服务，直接将当前目录（/var/lib/mysql）下的东西都拷贝到其他地方就行，恢复的时候直接拷回来就行了，并且将所
有者和组都改为musql。备份还原都需要需要停止服务
myisam engine 的将目录直接拷贝（三个文件  xt701.frm记录表结构 xt701.myd 存放数据  xt701.myi 存放索引）
innodb engine的需要将innodb及相关日志文件考走，不考日志恢复的时候起不来服务

热备份
mysql自带mysqldump command
备份mysqldump -u root -p xxxx xt701 > xt701.bak.sql  这里的xt701是库名

还原
先去数据库建立同名库 xt701
mysql -u root -p xxx < xt701.bak.sql

第三方软件
mydumper soft

mysqldump

Usage: mysqldump [OPTIONS] database [tables]
OR     mysqldump [OPTIONS] --databases [OPTIONS] DB1 [DB2 DB3...]
OR     mysqldump [OPTIONS] --all-databases [OPTIONS]

全备
[root@convirt tmp]# mysqldump -A -x > quanbei.sql

备份某个库
[root@convirt tmp]# mysqldump vfast > vvv.sql
[root@convirt tmp]# mysqldump --databases vfast > /opt/5.sql

备份单表  vfast库的T6表
mysqldump -x vfast T6 > /opt/t6.sql

vfast库名
恢复单个库
1）先去建库
2）导入备份文件

mysql> create database vfast;
Query OK, 1 row affected (0.00 sec)

mysql> exit
Bye
[root@convirt tmp]# mysql vfast < vvv.sql
#同时备份多个库  vfast  and test
[root@instructor ~]# mysqldump --database vfast test > /opt/backup/vfast_no2.sql

增量备份单表 

[root@convirt tmp]#   mysqldump --lock-tables --flush-logs --master-data=1 vfast test > /opt/1.sql
or
[root@convirt tmp]#  mysqldump --lock-tables --flush-logs --master-data=2 vfast test > /opt/3.sql
mysql> flush logs; 结束当前binlog开启新binlog

导出单个数据表结构和数据
mysqldump -h localhost -uroot -p123456  database table > dump.sql
mysqldump test H1 > 1.sql  到处test库H1表数据

备份表结构
[root@convirt tmp]# mysqldump --no-data --databases vfast > bb.sql

恢复

[root@convirt tmp]# mysql -u root -p [database name]  < [backup file name]


基于日志备份
vim /etc/my.cnf
log-bin=binlog  启用二进制日志
log-bin-index=binlog.index  建立二进制日志索引
sync-binlog=1 (1代表立刻写到磁盘，0代表先在内存后写到磁盘)

expire_logs_days=10  binlog　日志文件10天过期
max_binlog_size=2G 指定binlog大小
binlog_do_db = 库名  指定只记录那个库的binlog

如何删除binlog
mysql> show master logs; 显示本机binlog
mysql> purge binary logs to 'binlog.000004'; 删除前3个

二进制日志 备份与恢复

参考日志http://www.jb51.net/article/45023.htm
定义条件截断binlog日志
例如恢复到binlog.000003
mysqlbinlog /var/lib/mysql/binlog.000003 |mysql
将binlog 日志导出成sql语句
mysqlbinlog /var/lib/mysql/binlog.000007 > 7.sql

同时导入多个binlog二进制日志
mysqlbinlog /var/lib/mysql/binlog.[0-10]* > 7.sql
--start-datatime 和--stop-datatime 选项可以用来指定从二进制日志的某个时间点来进行恢复。
-–start-position=#               指定开始和结束position
-–stop-position=# 

[root@convirt mysql]#  /usr/local/mysql/bin/mysqlbinlog --start-position=370 --stop-position=440  
/var/lib/mysql/mysql-bin.000002

--start-position=370 --stop-position=440 这里面数字从哪儿来的呢？
[root@convirt mysql]#  mysqlbinlog /usr/local/mysql/bin/mysqlbinlog

# at 370
#100929 21:35:25 server id 1  end_log_pos 440 Query    thread_id=1    exec_time=0    error_code=0
SET TIMESTAMP=1285767325/*!*/;

从某个时间点开始还原【不需要提前删表】
mysqlbinlog binlog.[0-10]* --start-datetime="2014-03-02 10:30:00" |mysql

导入到某个时间点之前 【先删表，后还原】
mysqlbinlog /var/lib/mysql/binlog.[0-7]* --stop-datetime="2014-02-26 11:38:58" |mysql
```



## 主从同步
```
mysql数据库同步方法

1、主库创建/etc/my.cnf，修改
里边的键值增加
server-id=1
log-bin=logbin

2、主库增加用户，用于从库读取主库日志。
mysql> grant replication slave,reload,super on *.* to 'slave'@'10.255.254.109' identified by "123456";
mysql> flush privileges;

3、从库连接主库进行测试。mysql -u slave -p123456 -h 192.168.0.1
如果连接成功说明主库配置成功

4、停从库，修改从库/etc/my.cnf，增加选项：
server-id=2
master_host=10.255.254.129
master_user=slave
master_password=123456
relay_log=/var/lib/mysql/mysql-relay-bin
relay_log_index=/var/lib/mysql/mysql-relay-bin.index

5、启动从库，进行主从库数据同步
/opt/mysql/share/mysql/mysql start
/opt/mysql/bin/mysql -u root -p 
mysql>load data from master;
说明：这一步也可以用数据库倒入或者直接目录考过来。


6、进行测试：
①主库查看当前存在的库
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema | 
| mysql              |  
| test               | 
+--------------------+
3 rows in set (0.01 sec)
②从库查看当前存在库
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema | 
| mysql              |  
| test               | 
+--------------------+
3 rows in set (0.01 sec)
说明两者中的数据保持了一致性
③主库创建表，
mysql> create database xxx;
Query OK, 1 row affected (0.00 sec)
打开从库，察看：
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| information_schema | 
| mysql              |  
| test               |
| xxx                |       | 
+--------------------+
4 rows in set (0.01 sec)

说明主从数据库创建成功。
7、主从数据库相关命令：
slave stop; slave start ; 开始停止从数据库。
show slave status\G; 显示从库状态信息
show master status\G;显示主库状态信息
purge master logs to ’binlog.000004’; 此命令非常小心，删除主数据库没用的二进制日志文件。如果误删除，那么从库就没有办法自动更新了。
change master；从服务器上修改参数使用

另外，如果你当前操作的从库以前曾经与其他服务器建立过主从关系，你可能会发现即使你在my.cnf文件中更改了主服务器的位置，但是MSQL仍然
在试图连接就旧的主服务器的现象。发生这种问题的时候，我们可以通过清除master.info这个缓存文件或者在mysql中通过命令来进行设置。
方式如下：
a、删除master.info方法
这个文件位于数据文件存放目录里。默认是在/var/lib/mysql中的。你可以直接
将其删除，然后重新启动服务器。

b、mysql命令方法
如果你不方便重新启动服务器的话，那么就只能使用mysql命令来帮助你做到。
首先登录到主服务器上，查看当前服务器状态：
mysql> show master status\G;
+---------------+----------+--------------+------------------+
| File | Position | Binlog_Do_DB | Binlog_Ignore_DB |
+---------------+----------+--------------+------------------+
| mysql-bin.003 | 73 | test | manual,mysql |
+---------------+----------+--------------+------------------+
记录下File和Position的值。然后登录从服务器，进行如下操作：
mysql> slave stop;
mysql> CHANGE MASTER TO
-> MASTER_HOST='master_host_name', //主服务器的IP地址
-> MASTER_USER='replication_user_name', //同步数据库的用户
-> MASTER_PASSWORD='replication_password', //同步数据库的密码
-> MASTER_LOG_FILE='recorded_log_file_name', //主服务器二进制日志的文件名(前面要求记
录的参数)
-> MASTER_LOG_POS=recorded_log_position; //日志文件的开始位置(前面要求记录的参数)
mysql> slave start;

AB复制注意事项：
1.第一次启动slave库以后  show slave status \G;  
检查  两个线程  I／O   SQL 是否是YES状态

2.测试
添加或删除数据 （主服务器）   查看辅助的是否同步


如果不同步
    1）查看辅助的sql日志    tailf /var/log/mysqld.log
     140304 11:59:18 [Note] Slave I/O thread: connected to master 'slave@192.168.18.254:3306',  replication 
     started in log 'binlog.000011' at position 294

       ＃从服务器是否可以顺利到达主服务器
            如果发现你的用户名密码有错误  /etc/my.cnf   /var/lib/mysql/master.info

 2)查看sql线程是否报错
           140304 11:59:08 [Note] Slave SQL thread initialized, starting replication in log 'binlog.000011' at
            position 294, relay log '/var/lib/mysql/mysql-relay-bin.000001' position: 4

           手动去执行同步
                1）mysql> slave stop;
                2)mysql> CHANGE MASTER TO MASTER_HOST='192.168.18.254',MASTER_USER='slave',MASTER_PASSWORD='123456',
                MASTER_LOG_FILE='binlog.000011';

                3)  mysql > slave start;
如果出现开始同步  且AB同步后数据不一致

备份主库   去  手动同步到一致状态   再去执行手动同步中的1 ，2， 3步


需要注意的问题
MySQL Replication 大家都非常熟悉了，我也不会写怎么搭建以及复制的原理，网上相关文章非常多，大家可以自己去搜寻。我在这里就是想
总结一下mysql主从复制需要注意的地方。有人说主从复制很简单嘛，就是master，slave的server_id不一样就搞定。确实，简单的来说就是
这么简单。但是真正在生产环境我们需要注意的太多了。首先说说主库宕机或者从库宕机后复制中断的问题。

虽然很多知识点或许我博客其他文章中都有提到过，或者重复了，但是我还是想总结一下。

主库意外宕机

如果没有设置主库的sync_binlog选项，就可能在奔溃前没有将最后的几个二进制日志事件刷新到磁盘中。备库I/O线程因此也可一直处于读
不到尚未写入磁盘的事件的状态中。当主库从新启动时，备库将重连到主库并再次尝试去读该事件，但主库会告诉备库没有这个二进制日志偏
移量。解决这个问题的方法是指定备库从下一个二进制日志的开头读日志。但是一些事件将永久丢失。可以使用前面文章提到的工具来检查主
从数据一致以及修复pt-table-checksum。即使开启了sync_binlog，myisam表的数据仍然可能在奔溃的时候损坏。对于innodb表，如果
innodb_flush_log_at_trx_commit没有设置为1，也可能丢失数据，但是数据不会损坏。

因此主库的参数建议开启

sync_binlog=1
innodb-flush-log-at-trx-commit=1
MySQL 5.6版本之前存在一个bug，即当启用上述两个参数时，会使得InnoDB存储引擎的group commit失效，从而导致在写密集的环境中性
能的急剧下降。group commit是什么？这是一个知识点，那为什么sync_binlog=1,innodb-flush-log-at-trx-commit=1

会导致组提交失败？这又是一个知识点，大家可以查阅相关资料。

因此，我们常常在性能和数据一致性中做了妥协，通常将参数innodb-flush-log-at-trx-commit设置为2，而这就导致了master不再是
crash safe的，主从数据可能会不一致。关于innodb_flush_log_at_trx_commit的有效值为0,1,2。我这里简单提一下，因为很多知识
点是有连贯性的，往往提到这个问题而又涉及到另外的问题^_^

0代表当提交事务时，并不将事务的重做日志写入磁盘上的日志文件，而是等待主线程每秒的刷新。当宕机时，丢失1秒的事务。

1和2有点相同，但是不同的地方在于：1表示在执行commit时将重做日志缓冲同步写到磁盘，即伴有fsync的调用。2表示将重做日志异步写
到磁盘，即写到文件系统的缓存中。由操作系统控制刷新。因此不能完全保证在执行commit时肯定会写入重做日志文件，只是有这个动作的发生。

因此为了保证事务的ACID中的持久性，必须将innodb_flush_log_at_trx_commit设置为1，也就是每当有事务提交时，就必须确保事务都
已经写入重做日志文件。那么当数据库因为意外发生宕机时，可以通过重做日志文件恢复，并保证可以恢复已经提交的事务。而将该参数设
置为0或者2，都有可能发生恢复时部分事务的丢失。不同之处在于，设置为2时，当mysql数据库发生宕机而操作系统及服务器并没有发生宕
机时，由于此时未写入磁盘的事务日志保存在文件系统缓存中，当恢复时同样能保证数据不丢失。

对于性能与安全我们都要的情况下，我们肯定会使用RAID，并且开启Write Back功能，而且RAID卡提供电池备份单元（BBU,Battery 
Backup Unit），关于这块的知识，童鞋们可以自行查阅相关资料。

备库意外宕机：

当备库在一次非计划的关闭后重启时，会去读master.info文件以找到上次停止复制的位置。不幸的是，该文件可能并没有同步写到磁盘，
因为该信息是在缓存中，可能并没有刷新到磁盘文件master.info。文件中存储的信息可能是错误的，备库可能会尝试重新执行一些二进制
日志事件，这可能导致主键冲突，就是我们常常看见的1062错误。除非能确定备库在哪里停止（很难），否则唯一的办法就是忽略那些错误。

在从库导致复制中断有两方面的原因，即replication中的SQL thread和IO thread。首先来看SQL thread，其主要完成两个操作：

1.运行relay log中对应的事务信息
2.更新relay-info.log文件

更新relay-info.log文件是为了记录已经执行relay log中的位置，当slave重启后可以根据这个位置继续同步relay log。但是，这里
用户会发现这两个操作不是在一个事务中，一个是数据库操作，一个是文件操作，因此不能达到原子的效果。此外，MySQL数据库默认对于
文件relay-info.log是写入到操作系统缓存，因此在发生宕机时可能导致大量的已更新位置的丢失，从而导致重复执行SQL语句，最终的现
象就是主从数据不一致。MySQL 5.5新增了参数sync_relay_log_info,可以控制每次事务更新relay-info.log后就进行一次fdatasync操作，
这加重了系统负担，而且即使这样也可能存在最后一个事务丢失的情况。

IO thread用于同步master上的二进制日志，但是其在crash时依然会导致数据不一致的情况发生。IO thread将收到的二进制日志写入到
relay log，每个二进制日志由多个log event组成，所以每接受到一个log event就需要更新master-info.log。和relay-info.log一样，
其也是写入操作系统缓存，参数sync_master_info可以控制fdatasync的时间。由于IO thread的更新不能像SQL thread一样进行放到一个事
务进行原子操作，因此其是对数据一致性会产生影响，设想一个log event传送到了relay log中两次的情形。
不过好在从MySQL 5.5版本开始提供了参数relay_log_recovery，当发生crash导致重连master时，其不根据master-info.log的信息进行重
连，而是根据relay-info中执行到master的位置信息重新开始拉master上的日志数据（不过需要确保日志依然存在于master上，否则就。。。）
so，mysql 5.5版本的从库推荐配置参数：

sync_master_info = 1
sync_relay_log = 1
sync_relay_log_info = 1
read_only          #从库只读，但是有super权限的依然可以写入
relay_log_recovery = 1
skip_slave_start   # 默认启动从库就开启了同步，io线程和sql线程都运行了，该参数是需要手动执行start slave方可启动同步
复制过滤选项

常常看见很多同学在主库进行过滤选项设置，当然这也有好处，减少了带宽，但是在主库设置过滤选项是非常危险的操作，因为无论是显示要过滤
的或者要同步的，二进制日志只记录你设置的，其他的是不会记录的。当主库有数据需要用到binlog恢复时，你就准备哭吧。所以通常在备库进行
过滤选项设置。比如忽略某个库，同步所有库，或者同步某一个库，当然这会浪费带宽，但是和安全比起来，这点浪费不算什么。有时候安全与性
能往往需要我们自己平衡。

还有就是跨库更新，如果我们在备库是这样设置的，比如同步yayun这个库

replicate_do_db=yayun
主库记录如下：

复制代码
mysql> select *  from t1;
+----+-------+
| id | name  |
+----+-------+
|  1 | yayun |
|  2 | atlas |
|  3 | mysql |
+----+-------+
3 rows in set (0.00 sec)

mysql>
复制代码
备库记录如下：

复制代码
mysql> select * from t1;
+----+-------+
| id | name  |
+----+-------+
|  1 | yayun |
|  2 | atlas |
|  3 | mysql |
+----+-------+
3 rows in set (0.00 sec)

mysql>
复制代码
现在我们在主库插入一条记录

复制代码
mysql> use test;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> insert into yayun.t1 (name) values ('good yayun');
Query OK, 1 row affected (0.01 sec)

mysql> select  * from yayun.t1; 
+----+------------+
| id | name       |
+----+------------+
|  1 | yayun      |
|  2 | atlas      |
|  3 | mysql      |
|  5 | good yayun |
+----+------------+
4 rows in set (0.00 sec)

mysql>
复制代码
查看备库：

复制代码
mysql> select * from t1;
+----+-------+
| id | name  |
+----+-------+
|  1 | yayun |
|  2 | atlas |
|  3 | mysql |
+----+-------+
3 rows in set (0.00 sec)

mysql>
复制代码
怎么回事？怎么没有同步？这就是跨库更新带来的问题，比如下面的更新：

use test
insert into yayun.t1 (name) values ('good yayun')
当然你会说哪个2B会这么干啊，呵呵，有时2B还是有的。所以我们还有另外2个过滤复制参数

replicate_wild_do_table
replicate_wild_ignore_table
一个是要同步的表，一个是不同步的表，通常我们可以这样写

replicate_wild_do_table=yayun.%
表示同步yayun库下面的所有表，这样就解决的跨库更新的问题。

复制格式的问题

通常推荐使用ROW格式，为什么使用？看看我前面文章MySQL数据恢复和复制对InnoDB锁机制的影响

不要用Seconds_Behind_Master来衡量MySQL主备的延迟时间

这个后续我会写相关文章解释为什么不要用该参数衡量主备的延迟时间。



总结：

上面所提到的参数都是最大限度保证主从数据一致，以及主库宕机，从库宕机复制不会中断，但是性能会打折扣，所以需要我们自己去衡量，
或者做妥协。
```



## mha
```
安装Mysql，配置主从


配置MHA
   建立ssh无密码登录环境
ssh-keygen -t rsa
ssh-copy-id -i .ssh/id_rsa.pub '-p 27005 root@192.168.3.129'
ssh-copy-id -i .ssh/id_rsa.pub '-p 27005 root@192.168.3.128'
ssh-copy-id -i .ssh/id_rsa.pub '-p 27005 root@192.168.3.132'

ssh 连接测试看是否还需要密码

安装MHA node
  所有节点安装
   yum install perl-DBD-MySQL -y
   rpm -ivh mha4mysql-node-0.56-0.el6.noarch.rpm
会生成几个脚本文件
  /usr/bin/apply_diff_relay_logs
/usr/bin/filter_mysqlbinlog
/usr/bin/purge_relay_logs
/usr/bin/save_binary_logs


设置relay log的清除方式
在每个slave节点上：
  Sql>  set global relay_log_purge=0;
       show variables like "%relay_log_purge%";
 注意：MHA在发生切换的过程中，从库的恢复过程中依赖于relay log的相关信息，所以这里要将relay log的自动清除设置为OFF，
 采用手动清除relay log的方式。

设置定期清理relay脚本（两台slave服务器）
cat purge_relay_log.sh 
#!/bin/bash
user=root
passwd=1
port=3306
log_dir='/var/log'
purge='/usr/bin/purge_relay_logs'

if [ ! -d $log_dir ]
then
   mkdir $log_dir -p
fi

$purge --user=$user --password=$passwd --disable_relay_log_purge --port=$port --workdir=$work_dir >> 
$log_dir/purge_relay_logs.log 2>&1

crontab -l
0 4 * * * /bin/bash /root/purge_relay_log.sh
安装MHA Manager
每台服务器配置 : 
/etc/hosts  和mha配置文件对应
192.168.3.129    server1
192.168.3.128    server2
192.168.3.132    server3
修改ssh默认连接端口
vim ~/.ssh/config
 Port 27005
cd ~/.ssh && chmod 600 config


安装MHA Node软件包，和上面的方法一样
安装依赖  
yum install perl-DBD-MySQL perl-Config-Tiny perl-Log-Dispatch perl-Parallel-ForkManager perl-Time-HiRes -y
rpm -ivh mha4mysql-manager-0.56-0.el6.noarch.rpm

mkdir -p /etc/masterha
cat  /etc/masterha/app1.cnf
[server default]
manager_workdir=/var/log/masterha/app1
manager_log=/var/log/masterha/app1/manager.log
master_binlog_dir=/data/mysql/data/    #设置master 保存binlog的位置
master_ip_failover_script= /usr/local/bin/master_ip_failover
#master_ip_online_change_script=
password=123456    #监控用户，统一使用主从复制用户
user=root
ping_interval=1
remote_workdir=/tmp
repl_password=123456    #设置复制用户的密码
repl_user=slave
report_script=/usr/local/send_report    #设置发生切换后发送的报警的脚本
secondary_check_script=/usr/bin/masterha_secondary_check -s server3 -s server2            
#shutdown_script=""      #设置故障发生后关闭故障主机脚本（该脚本的主要作用是关闭主机放在发生脑裂,这里没有使用）
ssh_user=root  
ssh_port=27005


[server1]
hostname=192.168.3.129
port=3306

[server2]
hostname=192.168.3.128
port=3306
candidate_master=1   #设置为候选master，如果设置该参数以后，发生主从切换以后将会将此从库提升为主库，即使这个主库不是集
群中事件最新的slave
check_repl_delay=0   #默认情况下如果一个slave落后master 100M的relay logs的话，MHA将不会选择该slave作为一个新的master，
因为对于这个slave的恢复需要花费很长时间，通过设置check_repl_delay=0,MHA触发切换在选择一个新的master的时候将会忽略复制延时，
这个参数对于设置了candidate_master=1的主机非常有用，因为这个候选主在切换的过程中一定是新的master

[server3]
hostname=192.168.3.132
port=3306

vim /usr/bin/masterha_secondary_check  72行修改默认ssh端口 

切换脚本:  /usr/local/bin/master_ip_failover   
(主mysql添加ifconfig eth0:1 192.168.3.130/24)

masterha_check_ssh --conf=/etc/masterha/app1.cnf   检查ssh
masterha_check_repl --conf=/etc/masterha/app1.cnf   检查mysql状态
masterha_check_status --conf=/etc/masterha/app1.cnf 检查MHA Manager的状态

确认检查都正常后开启MHA
nohup masterha_manager --conf=/etc/masterha/app1.cnf --remove_dead_master_conf --ignore_last_failover < /dev/null >
 /var/log/masterha/mha.log 2>&1 &  开启MHA Manager监控
    --remove_dead_master_conf      该参数代表当发生主从切换后，老的主库的ip将会从配置文件中移除。
--manger_log                            日志存放位置
--ignore_last_failover                 在缺省情况下，如果MHA检测到连续发生宕机，且两次宕机间隔不足8小时的话，则不会进行
Failover，之所以这样限制是为了避免ping-pong效应

开启MHA后不要重启主mysql，也会导致切换

masterha_stop --conf=/etc/masterha/app1.cnf  关闭MHA Manage监控


之前主库宕机后不要再切换，配置成和新主库主从同步，加入mha集群，
注意需要运行sql：set global relay_log_purge=0;


模拟测试
  yum install sysbench –y
  sysbench --test=oltp --oltp-table-size=1000000 --oltp-read-only=off --init-rng=on --num-threads=16 --max-requests=0
   --oltp-dist-type=uniform --max-time=1800 --mysql-user=root --mysql-socket=/var/lib/mysql/mysql.sock 
   --mysql-password=1 --db-driver=mysql --mysql-table-engine=innodb --oltp-test-mode=complex prepare  生成测试数据

  sysbench --test=oltp --oltp-table-size=1000000 --oltp-read-only=off --init-rng=on --num-threads=16 --max-requests=0 
  --oltp-dist-type=uniform --max-time=180 --mysql-user=root --mysql-socket=/var/lib/mysql/mysql.sock 
  --mysql-password=1 --db-driver=mysql --mysql-table-engine=innodb --oltp-test-mode=complex run    压力测试
```

## mysql优化
```
mysql调优

clint---> httpd---> php --->mysql

解压缩： tar fzxv mysqlreport-3.5.tgz (汇报工具，通过这个工具可以观察到一些数据)
    cd mysqlreport-3.5
    cp mysqlreport /usr/bin
    mysqlreport  --user root --password 123 (有用户名和密码的前提下)
    #yum serach  DBI -y
    #yum install perl-DBD-MySQL -y
           mysqlreport --outfile /tmp/mysql 写入到文件中
    vim /tmp/mysql
Myisam引擎
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Key---->Mysam引擎的索引
    Read hit ---->命中率（越高代表着效率很高）
    调整key_buffer 
    方法1：
    show variables like '%key%';
    set global key_buffer_size=16777216;
    方法2：必须要重新启动服务
    vim /etc/my.cnf
    key_buffer_size=16777216
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Qusetion
        Total 分类
        DMS        由增、删、改、查、替换

        Slow 10 s  当你的工作在10S内没有完成，即作慢查询
        vim /etc/my.cnf
        log-slow-queries=/tmp/slow.log 慢速日志存放的位置
         long-query-time=20          超出多长时间算作慢速查询
        注：如果没有必要去定位slow，就不需要开启，因为开启会增加IO

        Qc Hits    查询缓存 
        调整Query Cache
        show variables like '%query%';
        set global query_cache_size=8384512;
        mysqlreport
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    SELECT and Sort 
          Sort 用来作排序的内存多大，他对应的是每一个线程
        mysql是以线程方式工作的，这个数值设置大了，可以增加排序的效率
        show variables like '%sort%';
        set global sort_buffer_size='2097144';
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Table locks
        Waited  这个数值越小越好
        show full processlist;
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Tables    增快表访问的速度
        open     当前打开了多少表
        opend     一共打开了多少表
        show variables like '%table%';
        table_cache
        set global table_cache=128; 把表的文件描述符写入到内存中了
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Connections
        Max used  最大连接数
        show variables like '%max%';
        set global max_connections=100;
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Created Temp    创建临时表（排序、索引）
        show variables like '%tmp%';
        tmpdir    /tmp/  临时表创建的位置
        tmp_table_size 如果创建临时表的大小超过32M将会把数据写入到磁盘中
        Disk table 值变大的时候
        解决方法：1、增大临时表的大小 2、优化查询语句
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Threads    线程缓存，减少从需要到产生的时间
        show variables like '%thread%';
        thread_cache_size
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    Bytes    和网络相关的
        Sent        发送的流量
        Recevied    接收的流量
        单位是：B

InnoDB引擎  
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    InnoDB Buffer Pool 
    Usage    越大越好
    show variables like '%innodb%';
    set global innodb_buffer_pool_size=8388608;
    注：建议大小设置为整个内存的80%
    Pages    单位：16K
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
InnoDB与网络
    back_log 请求队列中能够排队的大小，如果增大并发数，则这个数必须要调大
    tcp.max_syn_backlog
    somaxconn

    一次消息传输量的最大值
    show variables like '%max_allowed_packet%';
    default 1M

    show variables like '%timeout%';
    connect_timeout     连线时的超时时间

    interactive_timeout 处于回会话空闲的timeout，连接上来什么都不执行的超时时间
    wait_timeout 

    net_read_timeout
    net_write_timeout  处于数据交互阶段超时时间 
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
Innodb与IO相关的
    show variables like '%innodb_flush_log%';
    innodb_flush_log_at_trx_commit
    0 最不安全，但是效率是最高，每隔一秒钟会把数据写入到硬盘上，如果断电或者数据库服务坏了，数据就丢失了
    1 最安全，数据会时时的写到硬盘上
    2 先写到操作系统的内存中，再写入到磁盘中，mysql进程死了，数据不丢，但是断电了，数据就丢失了

    绕过操作系统的缓存，直接将数据写入到磁盘中，好处是节省了内存
    vim /etc/my.cnf
    innodb_flush_medthod=O_DIRECT
    /etc/init.d/mysqld restart
    \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
InnoDB与cpu
    主频高
    核心
    taskset 绑定



select table_schema as 'DBname', sum(data_length + index_length) / 1024/ 1024  as 'DB size(MB)', sum(data_free) 
/1024/1024  as 'free space (MB)' from information_schema.tables group by table_schema;


mysql  vm 
ey_buffer  (myisam)
query_cache_size 
sort_buffer_size
table_cache
tmp_table_size
thread_cache_size
innodb_buffer_pool_size (innodb)


mysql net

back_log
max_connections
/proc/sys/net/core/somaxconn
/proc/sys/net/ipv4/tcp_max_syn_backlog

connect_timeout     连线时的超时时间

interactive_timeout 处于回会话空闲的timeout，连接上来什么都不执行的超时时间
wait_timeout 

net_read_timeout
net_write_timeout  处于数据交互阶段超时时间 

max_allowed_packet  (1M)



mysql io
innodb_flush_log_at_trx_commit
    0 最不安全，但是效率是最高，每隔一秒钟会把数据写入到硬盘上，如果断电或者数据库服务坏了，数据就丢失了
    1 最安全，数据会时时的写到硬盘上
    2 先写到操作系统的内存中，再写入到磁盘中，mysql进程死了，数据不丢，但是断电了，数据就丢失了


innodb_flush_medthod=O_DIRECT



mysql cpu
```



## 编码
    查看   show variables like "%char%";
              SHOW VARIABLES LIKE 'character_set_%';
              SHOW VARIABLES LIKE 'collation_%';


    SET NAMES 'utf8';
    它相当于下面的三句指令：
    SET character_set_client = utf8;
    SET character_set_results = utf8;
    SET character_set_connection = utf8;

    创建数据库
    mysql> create database name character set utf8;

    创建表
    CREATE TABLE `type` (
    `id` int(10) unsigned NOT NULL auto_increment,
    `flag_deleted` enum('Y','N') character set utf8 NOT NULL default 'N',
    `flag_type` int(5) NOT NULL default '0',
    `type_name` varchar(50) character set utf8 NOT NULL default '',
    PRIMARY KEY (`id`)
    ) DEFAULT CHARSET=utf8;

    修改数据库成utf8的.
    mysql> alter database name character set utf8;

     修改表默认用utf8.
    mysql> alter table type character set utf8;

    修改字段用utf8
    mysql> alter table type modify type_name varchar(50) CHARACTER SET utf8;

    /etc/my.cnf
    --在 [mysqld] 标签下加上三行
    character-set-server=utf8
    #####default-character-set=utf8(旧版本)
    lower_case_table_names = 1 //表名不区分大小写（此与编码无关）

    --在 [mysql] 标签下加上一行
    default-character-set = utf8

    --在 [mysql.server]标签下加上一行
    default-character-set = utf8

    --在 [mysqld_safe]标签下加上一行
    default-character-set = utf8

    --在 [client]标签下加上一行
    default-character-set = utf8
    重新启动MySql服务
