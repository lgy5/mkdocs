## 用户
```
delete from mysql.user where user="";  删除匿名用户
set password=PASSWORD('pass');      设置登录密码
FLUSH PRIVILEGES;


create user sky;
select host,user,password from mysql.user;
可以看到sky用户信息

drop user sky;
select host,user,password from mysql.user
可以看到sky用户信息没了

mysql> ? create user  看帮助

mysql>create user sky identified by "123";

查看某个用户的权限
show grants for 'sky'@'%';
USAGE 权限最小
%代表所有机器IP

提权
mysql> grant select on vfast.* to "sky"@"%";

回收权限
mysql> revoke select on vfast.* from "sky"@"%"

lab
同一用户，不同IP，不同或相同密码，对某一库的权限不同

删除一个用户例子
revoke all privileges  on *.* from "rhce"@"192.168.18.234";
drop user "rhce"@"192.168.18.234";

给192.168.18.234这台机器登陆mysql对VFAST库的操作是只读（select）权限
grant select on vfast.* to "sky"@"192.168.18.234" identified by "123";

给192.168.18.200这台机器登陆mysql对VFAST库的操作是select,insert,delete,update权限
grant select,insert,delete,update on vfast.* to "sky"@"192.168.18.200"identified by "123";

select host,password,user from user;



测试在192.168.18.234上登陆mysql

mysql -h 192.168.18.254 -u sky -p123
mysql> use vfast;
mysql> insert into H1 values(00);
正确提示  拒绝插入

在192.168.18.200上登陆mysql

mysql -h 192.168.18.254 -u sky -p123

mysql> show databases;
mysql> insert into H1 values(00);
mysql> delete from H1 where id=00;
mysql> update H1 set id=16 where id=17;  将ID=17改为等于16
mysql> select * from H1;
以上命令都可以正常执行成功

mysql> drop table H1;  执行不成功  没权限

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
权限中全局最大

GRANT ALL PRIVILEGES ON *.* TO 'kyo'@'%' identified by '123';
flush privileges  刷新权限
ALL PRIVILEGES 所有权限
*.* 所有库的所有表
kyo 登陆用户，%允许登陆的IP 其代表所有

‘123’ 登陆密码

登陆后能干什么
select  查看
ALL PRIVILEGES  所有权限

权限指定符 权限允许的操作 
　　Alter 　　　　　　修改表和索引 
　　Create 　　　　 创建数据库和表 
　　Delete 　　　　 删除表中已有的记录 
　　Drop 　　 抛弃（删除）数据库和表 
　　INDEX 　　　　 创建或抛弃索引 
　　Insert 　　　　 向表中插入新行 
　　REFERENCE 　　未用 
　　Select　　　　 检索表中的记录 
　　Update 　　　　 修改现存表记录 
　　FILE 　　　　　　读或写服务器上的文件 
　　PROCESS 　　 查看服务器中执行的线程信息或杀死线程 
　　RELOAD 　　　　重载授权表或清空日志、主机缓存或表缓存。 
　　SHUTDOWN　　 关闭服务器 
　　ALL 　　　　　　所有；ALL PRIVILEGES同义词 
　　USAGE 　　　　特殊的“无权限”权限

权限涉及三个表
mysql.user
mysql.db
mysql.tables_orive

 删除权限
revoke all privileges on *.* from 'kyo'@'%';

show grants for 'kyo'@'%';
USAGE 权限最小

忘记密码怎么办
方法一
[root@convirt ~]# vim /etc/my.cnf 
skip-grant-tables   #本地和远程登陆不管用户是谁都可以跳过密码
重启mysql 

直接不用密码登陆
mysql> flush privileges ;

mysql> GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' identified by '';  password is null

##方法二测试不成功
mysqld_safe --skip-grant-tables
即可跳过密码验证文件登陆（本地和远程都可以）
            --skip-networking   网络不可以登陆只能本地
改口令
update mysql.user set password=password('456') where user=“kyo” and host=“localhost”;
password('456')
kyo@localhost的密码改为456

password 是将密码456加密


如何下线未知用户
查看谁在登陆数据库
show full processlist 可以看到进程ID
改掉该用户的密码  然后刷新生效 杀死其登陆进程。对方就会被踢下线，在连接密码错误，无法登陆。
kill $ID 杀死用户登陆ID 强迫其重新登陆
```



## explain用法
```
explain显示了mysql如何使用索引来处理select语句以及连接表。可以帮助选择更好的索引和写出更优化的查询语句。

使用方法，在select语句前加上explain就可以了，如：

explain select * from statuses_status where id=11;


explain列的解释
table：显示这一行的数据是关于哪张表的

type：这是重要的列，显示连接使用了何种类型。从最好到最差的连接类型为const、eq_reg、ref、range、indexhe和all

possible_keys：显示可能应用在这张表中的索引。如果为空，没有可能的索引。可以为相关的域从where语句中选择一个合适的语句

key： 实际使用的索引。如果为null，则没有使用索引。很少的情况下，mysql会选择优化不足的索引。这种情况下，可以在select语句中
使用use index（indexname）来强制使用一个索引或者用ignore index（indexname）来强制mysql忽略索引

key_len：使用的索引的长度。在不损失精确性的情况下，长度越短越好

ref：显示索引的哪一列被使用了，如果可能的话，是一个常数

rows：mysql认为必须检查的用来返回请求数据的行数

extra：关于mysql如何解析查询的额外信息。将在表4.3中讨论，但这里可以看到的坏的例子是using temporary和using filesort，
意思mysql根本不能使用索引，结果是检索会很慢


extra列返回的描述的意义

distinct:一旦mysql找到了与行相联合匹配的行，就不再搜索了

not exists: mysql优化了left join，一旦它找到了匹配left join标准的行，就不再搜索了

range checked for each record（index map:#）:没有找到理想的索引，因此对于从前面表中来的每一个行组合，mysql检查使用哪个
索引，并用它来从表中返回行。这是使用索引的最慢的连接之一

using filesort: 看到这个的时候，查询就需要优化了。mysql需要进行额外的步骤来发现如何对返回的行排序。它根据连接类型以及存储
排序键值和匹配条件的全部行的行指针来排序全部行

using index: 列数据是从仅仅使用了索引中的信息而没有读取实际的行动的表返回的，这发生在对表的全部的请求列都是同一个索引的部
分的时候

using temporary 看到这个的时候，查询需要优化了。这里，mysql需要创建一个临时表来存储结果，这通常发生在对不同的列集进行
order by上，而不是group by上

where used 使用了where从句来限制哪些行将与下一张表匹配或者是返回给用户。如果不想返回表中的全部行，并且连接类型all或index，
这就会发生，或者是查询有问题不同连接类型的解释（按照效率高低的顺序排序）

system 表只有一行：system表。这是const连接类型的特殊情况

const:表中的一个记录的最大值能够匹配这个查询（索引可以是主键或惟一索引）。因为只有一行，这个值实际就是常数，因为mysql先读
这个值然后把它当做常数来对待

eq_ref:在连接中，mysql在查询时，从前面的表中，对每一个记录的联合都从表中读取一个记录，它在查询使用了索引为主键或惟一键的
全部时使用

ref:这个连接类型只有在查询使用了不是惟一或主键的键或者是这些类型的部分（比如，利用最左边前缀）时发生。对于之前的表的每一个
行联合，全部记录都将从表中读出。这个类型严重依赖于根据索引匹配的记录多少—越少越好

range:这个连接类型使用索引返回一个范围中的行，比如使用>或<查找东西时发生的情况

index: 这个连接类型对前面的表中的每一个记录联合进行完全扫描（比all更好，因为索引一般小于表数据）

all:这个连接类型对于前面的每一个记录联合进行完全扫描，这一般比较糟糕，应该尽量避免
```



## gtid主从
```
MySQL 5.6引入的GTID(Global Transaction IDs)使得其复制功能的配置、监控及管理变得更加易于实现，且更加健壮。

要在MySQL 5.6中使用复制功能，其服务配置段[mysqld]中于少应该定义如下选项：

binlog-format：二进制日志的格式，有row、statement和mixed几种类型；
    需要注意的是：当设置隔离级别为READ-COMMITED必须设置二进制日志格式为ROW，现在MySQL官方认为STATEMENT这个已经不
    再适合继续使用；但mixed类型在默认的事务隔离级别下，可能会导致主从数据不一致；
log-slave-updates、gtid-mode、enforce-gtid-consistency、report-port和report-host：用于启动GTID及满足附属的其它需求；
master-info-repository和relay-log-info-repository：启用此两项，可用于实现在崩溃时保证二进制及从服务器安全的功能；
sync-master-info：启用之可确保无信息丢失；
slave-paralles-workers：设定从服务器的SQL线程数；0表示关闭多线程复制功能；
binlog-checksum、master-verify-checksum和slave-sql-verify-checksum：启用复制有关的所有校验功能；
binlog-rows-query-log-events：启用之可用于在二进制日志记录事件相关的信息，可降低故障排除的复杂度；
log-bin：启用二进制日志，这是保证复制功能的基本前提；
server-id：同一个复制拓扑中的所有服务器的id号必须惟一；


report-host：
The host name or IP address of the slave to be reported to the master during slave registration. This value 
appears in the output of SHOW SLAVE HOSTS on the master server.

report-port:
The TCP/IP port number for connecting to the slave, to be reported to the master during slave registration.

master-info-repository:
The setting of this variable determines whether the slave logs master status and connection information to a 
FILE (master.info), or to a TABLE (mysql.slave_master_info)

relay-log-info-repository：
This option causes the server to log its relay log info to a file or a table.

log_slave_updates：
Whether updates received by a slave server from a master server should be logged to the slave's own binary 
log. Binary logging must be enabled on the slave for this variable to have any effect. 

 enforce_gtid_consistency：




一、简单主从模式配置步骤

1、配置主从节点的服务配置文件

1.1、配置master节点：
[mysqld]
binlog-format=ROW
log-bin=master-bin
log-slave-updates=true
gtid-mode=on 
enforce-gtid-consistency=true
master-info-repository=TABLE
relay-log-info-repository=TABLE
sync-master-info=1
slave-parallel-workers=2
binlog-checksum=CRC32
master-verify-checksum=1
slave-sql-verify-checksum=1
binlog-rows-query-log_events=1
server-id=1
report-port=3306
port=3306
datadir=/mydata/data
socket=/tmp/mysql.sock
report-host=master.magedu.com

1.2、配置slave节点：
[mysqld]
binlog-format=ROW
log-slave-updates=true
gtid-mode=on 
enforce-gtid-consistency=true
master-info-repository=TABLE
relay-log-info-repository=TABLE
sync-master-info=1
slave-parallel-workers=2
binlog-checksum=CRC32
master-verify-checksum=1
slave-sql-verify-checksum=1
binlog-rows-query-log_events=1
server-id=11
report-port=3306
port=3306
log-bin=mysql-bin.log
datadir=/mydata/data
socket=/tmp/mysql.sock
report-host=slave.magedu.com

2、创建复制用户

mysql> GRANT REPLICATION SLAVE ON *.* TO repluser@172.16.100.7 IDENTIFIED BY 'replpass';

说明：172.16.100.7是从节点服务器；如果想一次性授权更多的节点，可以自行根据需要修改；

3、为备节点提供初始数据集

锁定主表，备份主节点上的数据，将其还原至从节点；如果没有启用GTID，在备份时需要在master上使用show master status命令查看二
进制日志文件名称及事件位置，以便后面启动slave节点时使用。

4、启动从节点的复制线程

如果启用了GTID功能，则使用如下命令：
mysql> CHANGE MASTER TO MASTER_HOST='master.magedu.com', MASTER_USER='repluser', MASTER_PASSWORD='replpass',
 MASTER_AUTO_POSITION=1;

没启用GTID，需要使用如下命令：
slave> CHANGE MASTER TO MASTER_HOST='172.16.100.6',
-> MASTER_USER='repluser',
-> MASTER_PASSWORD='replpass',
-> MASTER_LOG_FILE='master-bin.000003',
-> MASTER_LOG_POS=1174;

二、半同步复制

1、分别在主从节点上安装相关的插件

master> INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
slave> INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';

2、启用半同步复制

在master上的配置文件中，添加
rpl_semi_sync_master_enabled=ON

在至少一个slave节点的配置文件中添加
rpl_semi_sync_slave_enabled=ON

而后重新启动mysql服务即可生效。


或者，也可以mysql服务上动态启动其相关功能：

master> SET GLOBAL rpl_semi_sync_master_enabled = ON;
slave> SET GLOBAL rpl_semi_sync_slave_enabled = ON;
slave> STOP SLAVE IO_THREAD; START SLAVE IO_THREAD;

3、确认半同步功能已经启用

master> CREATE DATABASE magedudb;
master> SHOW STATUS LIKE 'Rpl_semi_sync_master_yes_tx';

slave> SHOW DATABASES;
```



## xtrabackup
    使用Xtrabackup进行MySQL备份：

    一、安装

    1、简介
    Xtrabackup是由percona提供的mysql数据库备份工具，据官方介绍，这也是世界上惟一一款开源的能够对innodb和xtradb数据库进行热备
    的工具。特点：
    (1)备份过程快速、可靠；
    (2)备份过程不会打断正在执行的事务；
    (3)能够基于压缩等功能节约磁盘空间和流量；
    (4)自动实现备份检验；
    (5)还原速度快；

    2、安装
    其最新版的软件可从 http://www.percona.com/software/percona-xtrabackup/ 获得。本文基于RHEL5.8的系统，因此，直接下载相
    应版本的rpm包安装即可，这里不再演示其过程。
    wget https://www.percona.com/downloads/XtraBackup/Percona-XtraBackup-2.4.8/binary/redhat/6/x86_64/percona-
    xtrabackup-24-2.4.8-1.el6.x86_64.rpm
    yum install libev -y
    rpm -ivh percona-xtrabackup-24-2.4.8-1.el6.x86_64.rpm 


    二、备份的实现

    1、完全备份

    # innobackupex --user=DBUSER --password=DBUSERPASS  /path/to/BACKUP-DIR/

    如果要使用一个最小权限的用户进行备份，则可基于如下命令创建此类用户：
    mysql> CREATE USER ’bkpuser’@’localhost’ IDENTIFIED BY ’s3cret’;
    mysql> REVOKE ALL PRIVILEGES, GRANT OPTION FROM ’bkpuser’;
    mysql> GRANT RELOAD, LOCK TABLES, REPLICATION CLIENT ON *.* TO ’bkpuser’@’localhost’;
    mysql> FLUSH PRIVILEGES;

    使用innobakupex备份时，其会调用xtrabackup备份所有的InnoDB表，复制所有关于表结构定义的相关文件(.frm)、以及MyISAM、MERGE、
    CSV和ARCHIVE表的相关文件，同时还会备份触发器和数据库配置信息相关的文件。这些文件会被保存至一个以时间命令的目录中。

    在备份的同时，innobackupex还会在备份目录中创建如下文件：
    (1)xtrabackup_checkpoints —— 备份类型（如完全或增量）、备份状态（如是否已经为prepared状态）和LSN(日志序列号)范围信息；

    每个InnoDB页(通常为16k大小)都会包含一个日志序列号，即LSN。LSN是整个数据库系统的系统版本号，每个页面相关的LSN能够表明此页面最
    近是如何发生改变的。

    (2)xtrabackup_binlog_info —— mysql服务器当前正在使用的二进制日志文件及至备份这一刻为止二进制日志事件的位置。

    (3)xtrabackup_binlog_pos_innodb —— 二进制日志文件及用于InnoDB或XtraDB表的二进制日志文件的当前position。

    (4)xtrabackup_binary —— 备份中用到的xtrabackup的可执行文件；

    (5)backup-my.cnf —— 备份命令用到的配置选项信息；

    在使用innobackupex进行备份时，还可以使用--no-timestamp选项来阻止命令自动创建一个以时间命名的目录；如此一来，innobackupex
    命令将会创建一个BACKUP-DIR目录来存储备份数据。

    2、准备(prepare)一个完全备份


    一般情况下，在备份完成后，数据尚且不能用于恢复操作，因为备份的数据中可能会包含尚未提交的事务或已经提交但尚
    未同步至数据文件中的事务。因此，此时数据文件仍处理不一致状态。“准备”的主要作用正是通过回滚未提交的事务及同步已经提交的事务至
    数据文件也使得数据文件处于一致性状态。


    innobakupex命令的--apply-log选项可用于实现上述功能。如下面的命令：

    # innobackupex --apply-log  /path/to/BACKUP-DIR
    如果执行正确，其最后输出的几行信息通常如下：
    xtrabackup: starting shutdown with innodb_fast_shutdown = 1
    120407  9:01:36  InnoDB: Starting shutdown...
    120407  9:01:40  InnoDB: Shutdown completed; log sequence number 92036620
    120407 09:01:40  innobackupex: completed OK!

    在实现“准备”的过程中，innobackupex通常还可以使用--use-memory选项来指定其可以使用的内存的大小，默认通常为100M。如果有足够
    的内存可用，可以多划分一些内存给prepare的过程，以提高其完成速度。


    3、从一个完全备份中恢复数据

    innobackupex命令的--copy-back选项用于执行恢复操作，其通过复制所有数据相关的文件至mysql服务器DATADIR目录中来执行恢
    复过程。innobackupex通过backup-my.cnf来获取DATADIR目录的相关信息。

    # innobackupex --copy-back  /path/to/BACKUP-DIR
    如果执行正确，其输出信息的最后几行通常如下：
    innobackupex: Starting to copy InnoDB log files
    innobackupex: in '/backup/2012-04-07_08-17-03'
    innobackupex: back to original InnoDB log directory '/mydata/data'
    innobackupex: Finished copying back files.

    120407 09:36:10  innobackupex: completed OK!

    请确保如上信息的最行一行出现“innobackupex: completed OK!”。

    当数据恢复至DATADIR目录以后，还需要确保所有数据文件的属主和属组均为正确的用户，如mysql，否则，在启动mysqld之前还需要事先修改
    数据文件的属主和属组。如：

    # chown -R  mysql:mysql  /mydata/data/


    4、使用innobackupex进行增量备份

    每个InnoDB的页面都会包含一个LSN信息，每当相关的数据发生改变，相关的页面的LSN就会自动增长。这正是InnoDB表可以进行增量备份的
    基础，即innobackupex通过备份上次完全备份之后发生改变的页面来实现。

    要实现第一次增量备份，可以使用下面的命令进行：

    # innobackupex --incremental /backup --incremental-basedir=BASEDIR

    其中，BASEDIR指的是完全备份所在的目录，此命令执行结束后，innobackupex命令会在/backup目录中创建一个新的以时间命名的目录以
    存放所有的增量备份数据。另外，在执行过增量备份之后再一次进行增量备份时，其--incremental-basedir应该指向上一次的增量备份所在的目录。

    需要注意的是，增量备份仅能应用于InnoDB或XtraDB表，对于MyISAM表而言，执行增量备份时其实进行的是完全备份。

    “准备”(prepare)增量备份与整理完全备份有着一些不同，尤其要注意的是：
    (1)需要在每个备份(包括完全和各个增量备份)上，将已经提交的事务进行“重放”。“重放”之后，所有的备份数据将合并到完全备份上。
    (2)基于所有的备份将未提交的事务进行“回滚”。

    于是，操作就变成了：
    # innobackupex --apply-log --redo-only BASE-DIR

    接着执行：
    # innobackupex --apply-log --redo-only BASE-DIR --incremental-dir=INCREMENTAL-DIR-1

    而后是第二个增量：
    # innobackupex --apply-log --redo-only BASE-DIR --incremental-dir=INCREMENTAL-DIR-2

    其中BASE-DIR指的是完全备份所在的目录，而INCREMENTAL-DIR-1指的是第一次增量备份的目录，INCREMENTAL-DIR-2指的是第二次增量
    备份的目录，其它依次类推，即如果有多次增量备份，每一次都要执行如上操作；

    5、Xtrabackup的“流”及“备份压缩”功能

    Xtrabackup对备份的数据文件支持“流”功能，即可以将备份的数据通过STDOUT传输给tar程序进行归档，而不是默认的直接保存至某备份目
    录中。要使用此功能，仅需要使用--stream选项即可。如：

    # innobackupex --stream=tar  /backup | gzip > /backup/`date +%F_%H-%M-%S`.tar.gz

    甚至也可以使用类似如下命令将数据备份至其它服务器：
    # innobackupex --stream=tar  /backup | ssh user@www.magedu.com  "cat -  > /backups/`date +%F_%H-%M-%S`.tar" 

    此外，在执行本地备份时，还可以使用--parallel选项对多个文件进行并行复制。此选项用于指定在复制时启动的线程数目。当然，在实际
    进行备份时要利用此功能的便利性，也需要启用innodb_file_per_table选项或共享的表空间通过innodb_data_file_path选项存储在
    多个ibdata文件中。对某一数据库的多个文件的复制无法利用到此功能。其简单使用方法如下：
    # innobackupex --parallel  /path/to/backup

    同时，innobackupex备份的数据文件也可以存储至远程主机，这可以使用--remote-host选项来实现：
    # innobackupex --remote-host=root@www.magedu.com  /path/IN/REMOTE/HOST/to/backup



    6、导入或导出单张表

    默认情况下，InnoDB表不能通过直接复制表文件的方式在mysql服务器之间进行移植，即便使用了innodb_file_per_table选项。而使
    用Xtrabackup工具可以实现此种功能，不过，此时需要“导出”表的mysql服务器启用了innodb_file_per_table选项（严格来说，是要
    “导出”的表在其创建之前，mysql服务器就启用了innodb_file_per_table选项），并且“导入”表的服务器同时启用了
    innodb_file_per_table和innodb_expand_import选项。

    (1)“导出”表
    导出表是在备份的prepare阶段进行的，因此，一旦完全备份完成，就可以在prepare过程中通过--export选项将某表导出了：
    # innobackupex --apply-log --export /path/to/backup

    此命令会为每个innodb表的表空间创建一个以.exp结尾的文件，这些以.exp结尾的文件则可以用于导入至其它服务器。

    (2)“导入”表
    要在mysql服务器上导入来自于其它服务器的某innodb表，需要先在当前服务器上创建一个跟原表表结构一致的表，而后才能实现将表导入：
    mysql> CREATE TABLE mytable (...)  ENGINE=InnoDB;

    然后将此表的表空间删除：
    mysql> ALTER TABLE mydatabase.mytable  DISCARD TABLESPACE;

    接下来，将来自于“导出”表的服务器的mytable表的mytable.ibd和mytable.exp文件复制到当前服务器的数据目录，然后使用如下命令将其“导入”：
    mysql> ALTER TABLE mydatabase.mytable  IMPORT TABLESPACE;




    7、使用Xtrabackup对数据库进行部分备份

    Xtrabackup也可以实现部分备份，即只备份某个或某些指定的数据库或某数据库中的某个或某些表。但要使用此功能，必须启用
    innodb_file_per_table选项，即每张表保存为一个独立的文件。同时，其也不支持--stream选项，即不支持将数据通过管道传输
    给其它程序进行处理。

    此外，还原部分备份跟还原全部数据的备份也有所不同，即你不能通过简单地将prepared的部分备份使用--copy-back选项直接复制回数据
    目录，而是要通过导入表的方向来实现还原。当然，有些情况下，部分备份也可以直接通过--copy-back进行还原，但这种方式还原而来
    的数据多数会产生数据不一致的问题，因此，无论如何不推荐使用这种方式。

    (1)创建部分备份

    创建部分备份的方式有三种：正则表达式(--include), 枚举表文件(--tables-file)和列出要备份的数据库(--databases)。

    (a)使用--include
    使用--include时，要求为其指定要备份的表的完整名称，即形如databasename.tablename，如：
    # innobackupex --include='^mageedu[.]tb1'  /path/to/backup

    (b)使用--tables-file
    此选项的参数需要是一个文件名，此文件中每行包含一个要备份的表的完整名称；如：
    # echo -e 'mageedu.tb1\nmageedu.tb2' > /tmp/tables.txt
    # innobackupex --tables-file=/tmp/tables.txt  /path/to/backup

    (c)使用--databases
    此选项接受的参数为数据名，如果要指定多个数据库，彼此间需要以空格隔开；同时，在指定某数据库时，也可以只指定其中的某张表。此外，
    此选项也可以接受一个文件为参数，文件中每一行为一个要备份的对象。如：
    # innobackupex --databases="mageedu testdb"  /path/to/backup


    (2)整理(preparing)部分备份
    prepare部分备份的过程类似于导出表的过程，要使用--export选项进行：
    # innobackupex --apply-log --export  /pat/to/partial/backup

    此命令执行过程中，innobackupex会调用xtrabackup命令从数据字典中移除缺失的表，因此，会显示出许多关于“表不存在”类的警告信息。
    同时，也会显示出为备份文件中存在的表创建.exp文件的相关信息。

    (3)还原部分备份
    还原部分备份的过程跟导入表的过程相同。当然，也可以通过直接复制prepared状态的备份直接至数据目录中实现还原，不要此时要求数据目
    录处于一致状态。



## MyISAM InnoDB
```
MyISAM  和 InnoDB

构成上的区别：

        每个MyISAM在磁盘上存储成三个文件。第一个文件的名字以表的名字开始，扩展名指出文件类型。 .frm文件存储表定义。

  数据文件的扩展名为.MYD (MYData)，索引文件的扩展名是.MYI (MYIndex)。

        基于磁盘的资源是InnoDB表空间数据文件和它的日志文件，InnoDB 表的大小只受限于操作系统文件的大小，一般为 2GB

  事务处理上方面:

        MyISAM类型的表强调的是性能，其执行数度比InnoDB类型更快，但是不提供事务支持

        InnoDB提供事务支持事务，外部键等高级数据库功能


  SELECT   UPDATE,INSERT，Delete操作
        如果执行大量的SELECT，MyISAM是更好的选择

1.如果你的数据执行大量的INSERT或UPDATE，出于性能方面的考虑，应该使用InnoDB表

2.DELETE   FROM table时，InnoDB不会重新建立表，而是一行一行的删除。

3.LOAD   TABLE FROM MASTER操作对InnoDB是不起作用的，解决方法是首先把InnoDB表改成MyISAM表，导入数据后再改成InnoDB表，
但是对于使用的额外的InnoDB特性（例如外键）的表不适用
```



## MySQL优化三板斧
    首先从CPU说起。

    你仔细检查的话，有些服务器上会有的一个有趣的现象：你cat /proc/cpuinfo时，会发现CPU的频率竟然跟它标称的频率不一样：

    #cat /proc/cpuinfo 
    processor : 5
    model name : Intel(R) Xeon(R) CPU E5-2620 0 @2.00GHz
     ...
    cpu MHz : 1200.000
    这个是Intel E5-2620的CPU，他是2.00G * 24的CPU，但是，我们发现第5颗CPU的频率为1.2G。

    这是什么原因呢？

    这些其实都源于CPU最新的技术：节能模式。操作系统和CPU硬件配合，系统不繁忙的时候，为了节约电能和降低温度，它会将CPU降频。
    这对环保人士和抵制地球变暖来说是一个福音，但是对MySQL来说，可能是一个灾难。

    为了保证MySQL能够充分利用CPU的资源，建议设置CPU为最大性能模式。这个设置可以在BIOS和操作系统中设置，当然，在BIOS中设置该选
    项更好，更彻底。由于各种BIOS类型的区别，设置为CPU为最大性能模式千差万别，我们这里就不具体展示怎么设置了。

    二、内存
    然后我们看看内存方面，我们有哪些可以优化的。

    i) 我们先看看numa
    非一致存储访问结构 (NUMA ： Non-Uniform Memory Access) 也是最新的内存管理技术。它和对称多处理器结构 (SMP ：
     Symmetric Multi-Processor) 是对应的。简单的队别如下：



    如图所示，详细的NUMA信息我们这里不介绍了。但是我们可以直观的看到：SMP访问内存的都是代价都是一样的；但是在NUMA架构下，
    本地内存的访问和非 本地内存的访问代价是不一样的。对应的根据这个特性，操作系统上，我们可以设置进程的内存分配方式。目前支持
    的方式包括：

    --interleave=nodes
    --membind=nodes
    --cpunodebind=nodes
    --physcpubind=cpus
    --localalloc
    --preferred=node
    简而言之，就是说，你可以指定内存在本地分配，在某几个CPU节点分配或者轮询分配。除非 是设置为--interleave=nodes轮询分配方式，
    即内存可以在任意NUMA节点上分配这种方式以外。其他的方式就算其他NUMA节点上还有内 存剩余，Linux也不会把剩余的内存分配给这个进程，
    而是采用SWAP的方式来获得内存。有经验的系统管理员或者DBA都知道SWAP导致的数据库性能 下降有多么坑爹。

    所以最简单的方法，还是关闭掉这个特性。

    关闭特性的方法，分别有：可以从BIOS，操作系统，启动进程时临时关闭这个特性。

    a) 由于各种BIOS类型的区别，如何关闭NUMA千差万别，我们这里就不具体展示怎么设置了。

    b) 在操作系统中关闭，可以直接在/etc/grub.conf的kernel行最后添加numa=off，如下所示：

    kernel /vmlinuz-2.6.32-220.el6.x86_64 ro root=/dev/mapper/VolGroup-root   rd_NO_LUKS 
    LANG=en_US.UTF-8 rd_LVM_LV=VolGroup/root rd_NO_MD quiet   SYSFONT=latarcyrheb-sun16 rhgb 
    crashkernel=auto rd_LVM_LV=VolGroup/swap  rhgb crashkernel=auto quiet KEYBOARDTYPE=pc 
    KEYTABLE=us rd_NO_DM numa=off   
    另外可以设置 vm.zone_reclaim_mode=0尽量回收内存。

    c) 启动MySQL的时候，关闭NUMA特性：

    numactl --interleave=all  mysqld &
    当然，最好的方式是在BIOS中关闭。

    ii) 我们再看看vm.swappiness。
    vm.swappiness是操作系统控制物理内存交换出去的策略。它允许的值是一个百分比的值，最小为0，最大运行100，该值默认为60。
    vm.swappiness设置为0表示尽量少swap，100表示尽量将inactive的内存页交换出去。

    具体的说：当内存基本用满的时候，系统会根据这个参数来判断是把内存中很少用到的inactive 内存交换出去，还是释放数据的cache。
    cache中缓存着从磁盘读出来的数据，根据程序的局部性原理，这些数据有可能在接下来又要被读 取；inactive 内存顾名思义，
    就是那些被应用程序映射着，但是“长时间”不用的内存。

    我们可以利用vmstat看到inactive的内存的数量：

    #vmstat -an 1 
     procs -----------memory---------- ---swap-- -----io---- --system-- -----cpu----- 
     r b swpd free  inact  active si so bi bo in cs us sy id wa st 
     1 0 0 27522384 326928 1704644 0 0 0 153 11 10 0 0 100 0 0 
     0 0 0 27523300 326936 1704164 0 0 0 74 784 590 0 0 100 0 0 
     0 0 0 27523656 326936 1704692 0 0 8 8 439 1686 0 0 100 0 0 
     0 0 0 27524300 326916 1703412 0 0 4 52 198 262 0 0 100 0 0
    通过/proc/meminfo 你可以看到更详细的信息：

    #cat /proc/meminfo | grep -i inact 
     Inactive: 326972 kB 
     Inactive(anon): 248 kB 
     Inactive(file): 326724 kB
    这里我们对不活跃inactive内存进一步深入讨论。 Linux中，内存可能处于三种状态：free，active和inactive。众所周知，
    Linux Kernel在内部维护了很多LRU列表用来管理内存，比如LRU_INACTIVE_ANON, LRU_ACTIVE_ANON, LRU_INACTIVE_FILE ,
     LRU_ACTIVE_FILE, LRU_UNEVICTABLE。其中LRU_INACTIVE_ANON, LRU_ACTIVE_ANON用来管理匿名页，LRU_INACTIVE_FILE ,
      LRU_ACTIVE_FILE用来管理page caches页缓存。系统内核会根据内存页的访问情况，不定时的将活跃active内存被移到inactive列表中，
      这些inactive的内存可以被 交换到swap中去。

    一般来说，MySQL，特别是InnoDB管理内存缓存，它占用的内存比较多，不经常访问的内存也会不少，这些内存如果被Linux错误的交换出去了，
    将 浪费很多CPU和IO资源。 InnoDB自己管理缓存，cache的文件数据来说占用了内存，对InnoDB几乎没有任何好处。

    所以，我们在MySQL的服务器上最好设置vm.swappiness=0。

    我们可以通过在sysctl.conf中添加一行：

    echo "vm.swappiness = 0" >>/etc/sysctl.conf
    并使用sysctl -p来使得该参数生效。

    三、文件系统
    最后，我们看一下文件系统的优化

    i) 我们建议在文件系统的mount参数上加上noatime，nobarrier两个选项。
    用noatime mount的话，文件系统在程序访问对应的文件或者文件夹时，不会更新对应的access time。一般来说，Linux会给文件记录
    了三个时间，change time, modify time和access time。

    我们可以通过stat来查看文件的三个时间：

    stat libnids-1.16.tar.gz 
     File: `libnids-1.16.tar.gz' 
     Size: 72309 Blocks: 152 IO Block: 4096 regular file 
     Device: 302h/770d Inode: 4113144 Links: 1 
     Access: (0644/-rw-r--r--) Uid: ( 0/ root) Gid: ( 0/ root) 
      Access  : 2008-05-27 15:13:03.000000000 +0800 
     Modify: 2004-03-10 12:25:09.000000000 +0800 
     Change: 2008-05-27 14:18:18.000000000 +0800
    其中access time指文件最后一次被读取的时间，modify time指的是文件的文本内容最后发生变化的时间，change time指的是文件的
    inode最后发生变化(比如位置、用户属性、组属性等)的时间。一般来说，文件都是读多写少，而且我们也很少关心某一个文件最近什 么时间被访问了。

    所以，我们建议采用noatime选项，这样文件系统不记录access time，避免浪费资源。

    现在的很多文件系统会在数据提交时强制底层设备刷新cache，避免数据丢失，称之为write barriers。但是，其实我们数据库服务器底
    层存储设备要么采用RAID卡，RAID卡本身的电池可以掉电保护；要么采用Flash卡，它也有自我保 护机制，保证数据不会丢失。所以我们
    可以安全的使用nobarrier挂载文件系统。设置方法如下：

    对于ext3, ext4和 reiserfs文件系统可以在mount时指定barrier=0；对于xfs可以指定nobarrier选项。

    ii) 文件系统上还有一个提高IO的优化万能钥匙，那就是deadline。
    在 Flash技术之前，我们都是使用机械磁盘存储数据的，机械磁盘的寻道时间是影响它速度的最重要因素，直接导致它的每秒可做
    的IO(IOPS)非常有限， 为了尽量排序和合并多个请求，以达到一次寻道能够满足多次IO请求的目的，Linux文件系统设计了多种IO调度
    策略，已适用各种场景和存储设备。

    Linux的IO调度策略包括：Deadline scheduler，Anticipatory scheduler，Completely Fair Queuing(CFQ)，NOOP。每种调度策
    略的详细调度方式我们这里不详细描述，这里我们主要介绍CFQ和Deadline，CFQ是Linux内 核2.6.18之后的默认调度策略，它声称对每一个 IO
     请求都是公平的，这种调度策略对大部分应用都是适用的。但是如果数据库有两个请求，一个请求3次IO，一个请求10000次IO，由于绝对公平，
     3次IO 的这个请求都需要跟其他10000个IO请求竞争，可能要等待上千个IO完成才能返回，导致它的响应时间非常慢。并且如果在处理的过程中，
     又有很多IO请 求陆续发送过来，部分IO请求甚至可能一直无法得到调度被“饿死”。而deadline兼顾到一个请求不会在队列中等待太久导致饿死，
     对数据库这种应用来 说更加适用。

    实时设置，我们可以通过

    echo deadline >/sys/block/sda/queue/scheduler
    来将sda的调度策略设置为deadline。

    我们也可以直接在/etc/grub.conf的kernel行最后添加elevator=deadline来永久生效。

    总结
    CPU方面：

    关闭电源保护模式

    内存：

    vm.swappiness = 0

    关闭numa

    文件系统：

    用noatime，nobarrier挂载系统

    IO调度策略修改为deadline。


    来源： http://os.51cto.com/art/201407/446750.htm



## mycat
```
http://www.mycat.org.cn/
https://github.com/MyCATApache/Mycat-download

读写分离中间件

涉及到的配置文件：
1.conf/server.xml
主要配置的是mycat的用户名和密码，mycat的用户名和密码和mysql的用户名密码是分开的，应用连接mycat就用这个用户名和密码。

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mycat:server SYSTEM "server.dtd">
<mycat:server xmlns:mycat="http://org.opencloudb/">
  <system>
    <!--
    <property name="processors">32</property>
    <property name="processorExecutor">32</property>
    <property name="serverPort">8066</property>
    <property name="managerPort">9066</property>
    -->
  </system>
  <user name="root">
    <property name="password">root</property>
    <property name="schemas">数据库名称</property>
  </user>
</mycat:server>
2.conf/schema.xml
主要配置主从库的数据库连接地址信息，schema里面不能配置table的定义，如果配置了就会检查sql的语法，目前mycat还有很多问题。


<?xml version="1.0"?>
<!DOCTYPE mycat:schema SYSTEM "schema.dtd">
<mycat:schema xmlns:mycat="http://org.opencloudb/">

  <schema name="数据库名称" checkSQLschema="false" dataNode="dn1">
  </schema>

  <dataNode name="dn1" dataHost="localhost1" database="数据库名称" />
  <dataHost name="localhost1" maxCon="1000" minCon="100" balance="1"      dbType="mysql" dbDriver="native">
    <heartbeat>select user()</heartbeat>
    <!-- can have multi write hosts -->
    <writeHost host="10.1.3.50" url="10.1.3.50:3306" user="数据库用户名"  password="数据库密码">
      <!-- can have multi read hosts -->           
      <readHost host="10.1.3.5" url="10.1.3.5:3306" user="数据库用户名" password="数据库密码" />
      <readHost host="10.1.3.6" url="10.1.3.6:3306" user="数据库用户名" password="数据库密码" />
    </writeHost>       
    <!--writeHost host="10.1.3.34" url="10.1.3.34:3306" user="数据库用户名"  password="数据库密码"-->
      <!-- can have multi read hosts -->           
      <!--readHost host="10.1.3.7" url="10.1.3.7:3306" user="数据库用户名" password="数据库密码" /-->
      <!--readHost host="10.1.3.8" url="10.1.3.8:3306" user="数据库用户名" password="数据库密码" /-->
    <!--/writeHost-->
  </dataHost>
</mycat:schema>
高可用性以及读写分离
MyCAT的读写分离机制如下：
• 事务内的SQL，全部走写节点，除非某个select语句以注释/*balance*/开头
• 自动提交的select语句会走读节点，并在所有可用读节点中间随机负载均衡
• 当某个主节点宕机，则其全部读节点都不再被使用，因为此时，同步失败，数据已经不是最新的，MYCAT会采用另外一个主节点所对应的
全部读节点来实现select负载均衡。
• 当所有主节点都失败，则为了系统高可用性，自动提交的所有select语句仍将提交到全部存活的读节点上执行，此时系统的很多页面还是
能出来数据，只是用户修改或提交会失败。

dataHost的balance属性设置为：
• 0，不开启读写分离机制
• 1，全部的readHost与stand by writeHost参与select语句的负载均衡，简单的说，当双主双从模式(M1->S1，M2->S2，并且M1与 M2
互为主备)，正常情况下，M2,S1,S2都参与select语句的负载均衡。
• 2，所有的readHost与writeHost都参与select语句的负载均衡，也就是说，当系统的写操作压力不大的情况下，所有主机都可以承担负载均衡。
一个dataHost元素，表明进行了数据同步的一组数据库，DBA需要保证这一组数据库服务器是进行了数据同步复制的。writeHost相当于
Master DB Server，而旗下的readHost则是与从数据库同步的Slave DB Server。当dataHost配置了多个writeHost的时候，任何一个
writeHost宕机，Mycat 都会自动检测出来，并尝试切换到下一个可用的writeHost。

MyCAT支持高可用性的企业级特性，根据您的应用特性，可以配置如下几种策略：
• 后端数据库配置为一主多从，并开启读写分离机制。
• 后端数据库配置为双主双从（多从），并开启读写分离机制
• 后端数据库配置为多主多从，并开启读写分离机制
后面两种配置，具有更高的系统可用性，当其中一个写节点（主节点）失败后，Mycat会侦测出来（心跳机制）并自动切换到下一个写节点，
MyCAT在任何时候，只会往一个写节点写数据。
```


## 常用sql
```
yum install mysql mysql-server -y
如果是第一次启动会初始化数据库  会在默认目录（/var/lib/mysql）下创建默认数据库文件夹。
/etc/init.d/mysqld start

批量替换数据
UPDATE tablename SET 字段名=REPLACE(字段名, 'HTML', '.YOUKU');

库
create database vfast;
drop database vfast;
use vfast;
show databases;

flush tables with read lock;  全局读锁定
unlock tables;

表
show tables;
create table rhce (id int);
alter table rhce rename cbd;                      修改表名
alter table cbd add sex enum('Y','N');        增加字段  sex 
alter table cbd drop id;                               删除字段  id         
alter table cbd modify name char(16);       修改字段name的类型char（16）
or
alter table vfast_user change name name enum('B','G');
alter table cbd change name mingzi char(26);　改变列名name为mingzi 类型为char(26)
show warnings \G;                                        显示mysql警告
show create table cbd;                                    显示表cbd的创建过程
desc cbd;                                                      显示cbd表的所有字段 
drop table cbd;

数据
数据类型
char     字符串   空间预先分配
varchar  字符串（空间占用更合理，每次存取数据都用CPU计算，所以更耗CPU） 空间后分配
int     整形  一个整数，支持 -2147493648到2147493647
bigint 大数据整形  一个大整数，支持 -9223372036854775808到9223372036854775807
float 浮点型（小数点） 一个小的菜单精度浮点数。支持 -3.402823466E+38到-1.175494351E-38
date  年月日
time  时分秒
datetime 存储年月日时分秒
blob   存储二进制
text   存储文本
enum    单选
set     多选
timestamp  自动插入当天前时间

select * from xt701; 
insert into xt701 (name,ID,yuwen)  values('lin',1007,99);
 or
insert into xt701 values('zhang',1001,80,70,90),('li',1002,90,98,19),('zhao',1003,68,67,90);
select name,id from xt701 where shuxue>=80;
注意：同时插入多条记录比单条插入执行起来更快些！！
update xt701 set shuxue=80 where id=1007 and shuxue is NULL;
批量替换数据
update 3m_recording_meeting m set m.play_url=REPLACE (m.play_url,'127.0.0.1','saas.3mang.com')   
where m.play_url like '%127.0.0.1%'

truncate   删除所有数据 （打碎表后重建新表）  删除速度快于delete
delete     逐行删除数据
delete from xt701;
truncate xt701;
delete from xt701 where yingyu=80;
select * from T1 where YUWEN between 70 and 90;


向表中导入数据
awk -F: '{print $1 ',' $3 ',' $4 ',' $NF}' /etc/passwd > /tmp/user

create table H2 ( NAME char(15), PASSWORD char(50), UID int(5), GID int(5), MIAOSHU varchar(100),
 HOME varchar(100), SHELL varchar(100));
load data infile '/etc/passwd' into table H2 fields terminated by ':';

mysql函数
sum  求和
max   取最大值
min   取最小值
avg   取平均值
count  统计
```


## 中间件对比
```
mysql中间件研究
Atlas，cobar，TDDL，mycat，heisenberg,Oceanus,vitess,OneProxy

来源： http://songwie.com/articlelist/44

mysql-proxy是官方提供的mysql中间件产品可以实现负载平衡，读写分离，failover等，但其不支持大数据量的分库分表且性能较差。
下面介绍几款能代替其的mysql开源中间件产品，Atlas，cobar，tddl，让我们看看它们各自有些什么优点和新特性吧。

Atlas


Atlas是由 Qihoo 360, Web平台部基础架构团队开发维护的一个基于MySQL协议的数据中间层项目。它是在mysql-proxy 0.8.2版本的基础上，
对其进行了优化，增加了一些新的功能特性。360内部使用Atlas运行的mysql业务，每天承载的读写请求数达几十亿条。
Altas架构：
Atlas是一个位于应用程序与MySQL之间，它实现了MySQL的客户端与服务端协议，作为服务端与应用程序通讯，同时作为客户端与MySQL通讯。
它对应用程序屏蔽了DB的细节，同时为了降低MySQL负担，它还维护了连接池。



以下是一个可以参考的整体架构，LVS前端做负载均衡，两个Altas做HA,防止单点故障。


Altas的一些新特性：
1.主库宕机不影响读
主库宕机，Atlas自动将宕机的主库摘除，写操作会失败，读操作不受影响。从库宕机，Atlas自动将宕机的从库摘除，对应用没有影响。
在mysql官方的proxy中主库宕机，从库亦不可用。
2.通过管理接口，简化管理工作，DB的上下线对应用完全透明，同时可以手动上下线。
图1是手动添加一台从库的示例。
图1


3.自己实现读写分离
（1）为了解决读写分离存在写完马上就想读而这时可能存在主从同步延迟的情况，Altas中可以在SQL语句前增加 /*master*/ 就可以
将读请求强制发往主库。
（2）如图2中，主库可设置多项，用逗号分隔，从库可设置多项和权重，达到负载均衡。
图2

4.自己实现分表（图3）
（1）需带有分表字段。
（2）支持SELECT、INSERT、UPDATE、DELETE、REPLACE语句。
（3）支持多个子表查询结果的合并和排序。
图3 

这里不得不吐槽Atlas的分表功能，不能实现分布式分表，所有的子表必须在同一台DB的同一个database里且所有的子表必须事先建好，
Atlas没有自动建表的功能。
5.之前官方主要功能逻辑由使用lua脚本编写，效率低，Atlas用C改写，QPS提高，latency降低。
6.安全方面的提升
（1）通过配置文件中的pwds参数进行连接Atlas的用户的权限控制。
（2）通过client-ips参数对有权限连接Atlas的ip进行过滤。
（3）日志中记录所有通过Altas处理的SQL语句，包括客户端IP、实际执行该语句的DB、执行成功与否、执行所耗费的时间 ，如下面例子（图4）。
图4

7.平滑重启
通过配置文件中设置lvs-ips参数实现平滑重启功能，否则重启Altas的瞬间那些SQL请求都会失败。该参数前面挂接的lvs的物理网卡的ip，注
意不是虚ip。平滑重启的条件是至少有两台配置相同的Atlas且挂在lvs之后。
source：https://github.com/Qihoo360/Atlas

alibaba.cobar

Cobar是阿里巴巴（B2B）部门开发的一种关系型数据的分布式处理系统，它可以在分布式的环境下看上去像传统数据库一样为您提供海量
数据服务。那么具体说说我们为什么要用它，或说cobar--能干什么？以下是我们业务运行中会存在的一些问题：
1.随着业务的进行数据库的数据量和访问量的剧增，需要对数据进行水平拆分来降低单库的压力，而且需要高效且相对透明的来屏蔽掉水平拆分的细节。
2.为提高访问的可用性，数据源需要备份。
3.数据源可用性的检测和failover。
4.前台的高并发造成后台数据库连接数过多，降低了性能，怎么解决。 

针对以上问题就有了cobar施展自己的空间了，cobar中间件以proxy的形式位于前台应用和实际数据库之间，对前台的开放的接口是mysq
l通信协议。将前台SQL语句变更并按照数据分布规则转发到合适的后台数据分库，再合并返回结果，模拟单库下的数据库行为。 

Cobar应用举例
应用架构：

应用介绍：
1.通过Cobar提供一个名为test的数据库，其中包含t1,t2两张表。后台有3个MySQL实例(ip:port)为其提供服务，分别为：A,B,C。
2.期望t1表的数据放置在实例A中，t2表的数据水平拆成四份并在实例B和C中各自放两份。t2表的数据要具备HA功能，即B或者C实例其中
一个出现故障，不影响使用且可提供完整的数据服务。
cabar优点总结：
1.数据和访问从集中式改变为分布：
（1）Cobar支持将一张表水平拆分成多份分别放入不同的库来实现表的水平拆分
（2）Cobar也支持将不同的表放入不同的库
（3） 多数情况下，用户会将以上两种方式混合使用
注意！：Cobar不支持将一张表，例如test表拆分成test_1,test_2, test_3.....放在同一个库中，必须将拆分后的表分别放入不同
的库来实现分布式。
2.解决连接数过大的问题。
3.对业务代码侵入性少。
4.提供数据节点的failover,HA：
(1)Cobar的主备切换有两种触发方式，一种是用户手动触发，一种是Cobar的心跳语句检测到异常后自动触发。那么，当心跳检测到主机
异常，切换到备机，如果主机恢复了，需要用户手动切回主机工作，Cobar不会在主机恢复时自动切换回主机，除非备机的心跳也返回异常。
(2)Cobar只检查MySQL主备异常，不关心主备之间的数据同步，因此用户需要在使用Cobar之前在MySQL主备上配置双向同步。
cobar缺点：
开源版本中数据库只支持mysql，并且不支持读写分离。
source：http://code.alibabatech.com/wiki/display/cobar/Home

TDDL

淘宝根据自己的业务特点开发了TDDL（Taobao Distributed Data Layer 外号:头都大了 ©_Ob）框架，主要解决了分库分表对应用的
透明化以及异构数据库之间的数据复制，它是一个基于集中式配置的 jdbc datasource实现，具有主备，读写分离，动态数据库配置等功能。
TDDL所处的位置（tddl通用数据访问层，部署在客户端的jar包，用于将用户的SQL路由到指定的数据库中）：


淘宝很早就对数据进行过分库的处理， 上层系统连接多个数据库，中间有一个叫做DBRoute的路由来对数据进行统一访问。DBRoute对
数据进行多库的操作、数据的整合，让上层系统像操作一个数据库一样操作多个库。但是随着数据量的增长，对于库表的分法有了更高
的要求，例如，你的商品数据到了百亿级别的时候，任何一个库都无法存放了，于是分成2个、4个、8个、16个、32个……直到1024个、
2048个。好，分成这么多，数据能够存放了，那怎么查询它？这时候，数据查询的中间件就要能够承担这个重任了，它对上层来说，
必须像查询一个数据库一样来查询数据，还要像查询一个数据库一样快（每条查询在几毫秒内完成），TDDL就承担了这样一个工作。
在外面有些系统也用DAL（数据访问层） 这个概念来命名这个中间件。
下图展示了一个简单的分库分表数据查询策略：

主要优点：
1.数据库主备和动态切换
2.带权重的读写分离
3.单线程读重试
4.集中式数据源信息管理和动态变更
5.剥离的稳定jboss数据源
6.支持mysql和oracle数据库
7.基于jdbc规范，很容易扩展支持实现jdbc规范的数据源
8.无server,client-jar形式存在，应用直连数据库
9.读写次数,并发度流程控制，动态变更
10.可分析的日志打印,日志流控，动态变更
TDDL必须要依赖diamond配置中心（diamond是淘宝内部使用的一个管理持久配置的系统，目前淘宝内部绝大多数系统的配置，
由diamond来进行统一管理，同时diamond也已开源）。
TDDL动态数据源使用示例说明：http://rdc.taobao.com/team/jm/archives/1645
diamond简介和快速使用：http://jm.taobao.org/tag/diamond%E4%B8%93%E9%A2%98/
TDDL源码：https://github.com/alibaba/tb_tddl 
TDDL复杂度相对较高。当前公布的文档较少，只开源动态数据源，分表分库部分还未开源，还需要依赖diamond，不推荐使用。
终其所有，我们研究中间件的目的是使数据库实现性能的提高。具体使用哪种还要经过深入的研究，严谨的测试才可决定。



MyCAT

http://www.org.cn/

https://github.com/myCATApache


什么是MyCAT?简单的说，MyCAT就是： 一个彻底开源的，面向企业应用开发的“大数据库集群” 支持事务、ACID、可以替代Mysql
的加强版数据库 ? 一个可以视为“Mysql”集群的企业级数据库，用来替代昂贵的Oracle集群 ? 一个融合内存缓存技术、Nosql技术、
HDFS大数据的新型SQL Server ? 结合传统数据库和新型分布式数据仓库的新一代企业级数据库产品 ? 一个新颖的数据库中间件产品。

目标

低成本的将现有的单机数据库和应用平滑迁移到“云”端，解决数据存储和业务规模迅速增长情况下的数据瓶颈问题。

关键特性

1. 支持 SQL 92标准 支持Mysql集群，可以作为Proxy使用 支持JDBC连接ORACLE、DB2、SQL Server，将其模拟为MySQL Server
使用 支持galera for mysql集群，percona-cluster或者mariadb cluster，提供高可用性数据分片集群，自动故障切换，高可用性 。

2. 支持读写分离。

3. 支持Mysql双主多从，以及一主多从的模式 。

4. 支持全局表。

5. 支持数据自动分片到多个节点，用于高效表关联查询 。

6. 垮裤join，支持独有的基于E-R 关系的分片策略，实现了高效的表关联查询多平台支持，部署和实施简单。

优势

基于阿里开源的Cobar产品而研发，Cobar的稳定性、可靠性、优秀的架构和性能，以及众多成熟的使用案例使得MyCAT一开始就拥有
一个很好的起点，站在巨人的肩膀上，我们能看到更远。广泛吸取业界优秀的开源项目和创新思路，将其融入到MyCAT的基因中，使得
MyCAT在很多方面都领先于目前其他一些同类的开源项目，甚至超越某些商业产品。MyCAT背后有一只强大的技术团队，其参与者都是
5年以上资深软件工程师、架构师、DBA等，优秀的技术团队保证了MyCAT的产品质量。 MyCAT并不依托于任何一个商业公司，因此不像
某些开源项目，将一些重要的特性封闭在其商业产品中，使得开源项目成了一个摆设，目前在持续维护更新。

长期规划

在支持Mysql的基础上，后端增加更多的开源数据库和商业数据库的支持，包括原生支持PosteSQL、FireBird等开源数据库，以及通过
JDBC等方式间接支持其他非开源的数据库如Oracle、DB2、SQL Server等实现更为智能的自我调节特性，如自动统计分析SQL，
自动创建和调整索引，根据数据表的读写频率，自动优化缓存和备份策略等实现更全面的监控管理功能与HDFS集成，提供SQL命令，
将数据库装入HDFS中并能够快速分析集成优秀的开源报表工具，使之具备一定的数据分析的能力。



heisenberg

强大好用的mysql分库分表中间件,来自百度

其优点： 分库分表与应用脱离，分库表如同使用单库表一样 减少db 连接数压力 热重启配置 可水平扩容 遵守Mysql原生协议 
读写分离 无语言限制，mysqlclient,c,java等都可以使用 Heisenberg服务器通过管理命令可以查看，如连接数，线程池，结点等，
并可以调整 采用velocity的分库分表脚本进行自定义分库表，相当的灵活

qq群：150720285 邮箱:brucest0078@gmail.com

https://github.com/songwie/heisenberg



分库分表与应用脱离，分库表如同使用单库表一样
减少db 连接数压力
热重启配置
可水平扩容
遵守Mysql原生协议
无语言限制，mysqlclient,c,java等都可以使用
Heisenberg服务器通过管理命令可以查看，如连接数，线程池，结点等，并可以调整

Oceanus:

Oceanus致力于打造一个功能简单、可依赖、易于上手、易于扩展、易于集成的解决方案，甚至是平台化系统。拥抱开源，提供各类
插件机制集成其他开源项目，新手可以在几分钟内上手编程，分库分表逻辑不再与业务紧密耦合，扩容有标准模式，减少意外错误的发生。

Oceanus内部名词定义

datanode：数据源节点。为一个数据源命名，配置链接属性、报警实现

namenode：数据源的簇。为一组数据源命名，指定这组数据源的负载方式、访问模式、权重

table：映射表。匹配解析sql中的table名称，命中table标签的name属性值后，会执行约定的路由逻辑

bean：实体。由其他标签引用，实体类必须有无参的构造函数

tracker：监控埋点。涉及到计算和IO的功能点都有监控点，自定义一个埋点实现类，当功能耗时超出预期时会执行其中的回调函数，
便于监控和优化系统

为什么说Oceanus是非常易用的

Oceanus在设计时非常注重使用者的评价，配置结构近乎于和使用者交流约定业务规则，便于不同的人看同一套配置，互相理解流程。
当配置文件编写 完成后，编码就变得更加简单，只调用Oceanus客户端的几个方法就可以实现数据库操作，不再关心HA、报警、负载均衡、
性能监控等问题。良好的用户视 觉减少了分库分表在业务场景中的耦合度，对于编码者就像只对一个table操作，Oceanus负责进行sql解析、
路由、sql重写。

如提交：    select * from user； 改写成：    select * from user0;            select * from user1;            
select * from user2;            select * from user3;
分发给不同的库(或者同库)执行，用户视觉如图：github

开源集成

“接地气，拥抱开源” 是Oceanus的设计原则之一，可以很好的集成到mybatis和hibernate中，只要引用其中的插件，编写Oceanus配置
文件，然后改写各 自的DataSource实现或ConnectionProvider即可做到集成。这样既用到了熟悉的ORM，又借助Oceanus实现了分库分表等功 能。

待开发

不得不说Oceanus在设计上非常灵活，使得每一个细小的功能点都有极高的切入价值，比如Cache机制、全局的ID生成规则、资源可视化监控
等等，把其中某一个点做得足够好，都会为整体产品带来质的提升，简化实际生产环境中的配套系统研发维护成本。

vitess:

谷歌开发的数据库中间件，集群基于ZooKeeper管理，通过RPC方式进行数据处理，总体分为，server，command line，gui监控 3部分。
https://github.com/youtube/vitess




OneProxy

 OneProxy是由原支付宝首席架构师楼方鑫开发，目前由楼方鑫创立的杭州平民软件公司（@平民架构）提供技术支持。它保留了
 MySQL-Proxy 0.8.4官方版本上其协议处理和软件框架，然后对软件做了大量优化，极大增强了系统的并发能力。目前已有多家公司
 在生成环境中使用，其中包括了支付、电商等行业。

     OneProxy的主要功能有：
1. 垂直分库
2. 水平分表
3. Proxy集群【暂无文档】
4. 读高可用
5. 读写分离（master不参与读）
6. 读写分离（master参与读）
7. 写高可用
8. 读写随机
9. SQL检查
10. SQL统计【暂无文档】
11. 任务队列监控【暂无文档】
12. 连接池管理【暂无文档】

最新博文在http://www.cnblogs.com/youge-OneSQL/articles/4208583.html
重要概念
     Server Group
     在OneProxy中，一组主从复制的MySQL集群被称为Server Group。如图. A所示，有Server Group A和Server Group B。
     A
                                                            图. A
     在OneProxy中，垂直分库和水平分表的实现思路都是建立在Server Group的概念上。为了更好地说明，我们假设以下场景。
     A）Server Group A中有三张表table X, table Y, table Z，其中应用对table X操作非常频繁，占用大量I/O带宽，
     严重影响了应用对tableY, tableZ的操作效率。
              B
                                                                      图. B
     解决方案1.0：把table X移到另一组数据库，即Server Group B中（如图C所示），然后通过修改OneProxy的配置来改变
     table X的路由规则，无须改动应用。
C

                                                                      图. C
     B）在使用了解决方案1.0后，系统的I/O压力得到缓解。由于后期业务越来越多，Server Group B的写入压力越来越大，
     响应时间变慢。
     解决方案2.0 : 把Server Group B中的table X水平拆分，将X_00, X_01留在Server Group B中，把X_02，X_03留在
     Server Group C中，如图D所示
D
```

## atlas_keepalived
    背景描述
    目前我们的高可用DB的代理层采用的是360开源的Atlas，从上线以来，已稳定运行2个多月。无论是从性能上，还是稳定性上，
    相比其他开源组件（amoeba、cobar、MaxScale、MySQL-Proxy等），还是很出色的。

    当初我们之所以选择Atlas，主要看中它有以下优点：
    (1)、基于mysql-proxy-0.8.2进行修改，代码完全开源；
    (2)、比较轻量级，部署配置也比较简单；
    (3)、支持DB读写分离；
    (4)、支持从DB读负载均衡，并自动剔除故障从DB；
    (5)、支持平滑上下线DB；
    (6)、具备较好的安全机制（IP过滤、账号认证）；
    (7)、版本更新、问题跟进、交流圈子都比较活跃。

    在测试期间以及线上问题排查过程中，得到了360 Atlas作者朱超的热心解答，在此表示感谢。有关更多Atlas的介绍，我就不一一例举，
    可以参考以下链接：
    https://github.com/Qihoo360/Atlas/blob/master/README_ZH.md

    2、总体架构图
    wKioL1Sw6iagbaHjAAJX6OZk-GM940.jpg

    3、系统环境
    CentOS 6.3 x86_64

    需注意的地方
    (1)、本次安装不使用系统默认的glib库，之前的yum安装只是为了先解决依赖库的问题；
    (2)、LUA库的版本不能太高，为5.1.x即可；
    (3)、glib库的版本也不能太高，为glib-2.32.x即可；
    (4)、对于编译不成功的情况，注意查看下面的说明。


    yum install glib glib-devel ncurses readline lua  libevent libevent-devel openssl openssl-devel -y

    https://github.com/Qihoo360/Atlas/wiki/

    从https://github.com/Qihoo360/Atlas/releases 页面下载最新版RPM包，然后执行：
    sudo rpm –i Atlas-XX.el6.x86_64.rpm安装。 

    Atlas运行需要依赖一个配置文件（test.cnf）。在运行Atlas之前，需要对该文件进行配置。Atlas的安装目录是/usr/local/mysql-proxy，
    进入安装目录下的conf目录，可以看到已经有一个名为test.cnf的默认配置文件，我们只需要修改里面的某些配置项，不需要从头写一个配置文件。

    1.配置范例及说明如下：
    [mysql-proxy]

    (必备，默认值即可)管理接口的用户名
    admin-username = user
    (必备，默认值即可)管理接口的密码
    admin-password = pwd
    (必备，根据实际情况配置)主库的IP和端口
    proxy-backend-addresses = 192.168.0.12:3306
    (非必备，根据实际情况配置)从库的IP和端口，@后面的数字代表权重，用来作负载均衡，若省略则默认为1，可设置多项，用逗号分隔。
    如果想让主库也能分担读请求的话，只需要将主库信息加入到下面的配置项中。
    proxy-read-only-backend-addresses = 192.168.0.13:3306,192.168.0.14:3306
    (必备，根据实际情况配置)用户名与其对应的加密过的MySQL密码，密码使用PREFIX/bin目录下的加密程序encrypt加密，用户名与密码
    之间用冒号分隔。主从数据库上需要先创建该用户并设置密码（用户名和密码在主从数据库上要一致）。比如用户名为myuser，密码为mypwd，
    执行./encrypt mypwd结果为HJBoxfRsjeI=。如果有多个用户用逗号分隔即可。则设置如下行所示：
    pwds = myuser: HJBoxfRsjeI=,myuser2:HJBoxfRsjeI=
    （必备，默认值即可)Atlas的运行方式，设为true时为守护进程方式，设为false时为前台方式，一般开发调试时设为false，线上运行时
    设为true
    daemon = true
    (必备，默认值即可)设置Atlas的运行方式，设为true时Atlas会启动两个进程，一个为monitor，一个为worker，monitor在worker意外退
    出后会自动将其重启，设为false时只有worker，没有monitor，一般开发调试时设为false，线上运行时设为true
    keepalive = true
    (必备，根据实际情况配置)工作线程数，推荐设置成系统的CPU核数的2至4倍
    event-threads = 4
    (必备，默认值即可)日志级别，分为message、warning、critical、error、debug五个级别
    log-level = message
    (必备，默认值即可)日志存放的路径
    log-path = /usr/local/mysql-proxy/log
    (必备，根据实际情况配置)SQL日志的开关，可设置为OFF、ON、REALTIME，OFF代表不记录SQL日志，ON代表记录SQL日志，该模式下日志
    刷新是基于缓冲区的，当日志填满缓冲区后，才将日志信息刷到磁盘。REALTIME用于调试，代表记录SQL日志且实时写入磁盘，默认为OFF
    sql-log = OFF
    (可选项，可不设置）慢日志输出设置。当设置了该参数时，则日志只输出执行时间超过sql-log-slow（单位：ms)的日志记录。不设置该
    参数则输出全部日志。
    sql-log-slow = 10
    (可选项，可不设置）关闭不活跃的客户端连接设置。当设置了该参数时，Atlas会主动关闭经过'wait-timeout'时间后一直未活跃的连接。单位：秒
    wait-timeout = 10
    (必备，默认值即可)Atlas监听的工作接口IP和端口
    proxy-address = 0.0.0.0:1234
    (必备，默认值即可)Atlas监听的管理接口IP和端口 admin-address = 0.0.0.0:2345
    (可选项，可不设置)分表设置，此例中person为库名，mt为表名，id为分表字段，3为子表数量，可设置多项，以逗号分隔，若不分表则不
    需要设置该项，子表需要事先建好，子表名称为表名_数字，数字范围为[0,子表数-1]，如本例里，子表名称为mt_0、mt_1、mt_2
    tables = person.mt.id.3
    (可选项，可不设置)默认字符集，若不设置该项，则默认字符集为latin1
    charset = utf8
    (可选项，可不设置)允许连接Atlas的客户端的IP，可以是精确IP，也可以是IP段，以逗号分隔，若不设置该项则允许所有IP连接，否则
    只允许列表中的IP连接
    client-ips = 127.0.0.1, 192.168.1
    (可选项，极少需要)Atlas前面挂接的LVS的物理网卡的IP(注意不是虚IP)，若有LVS且设置了client-ips则此项必须设置，否则可以不设置
    lvs-ips = 192.168.1.1

    2. 重要配置说明
    以下几项配置参数对性能和正常运行起到重要作用，需要正确设置。
    (1)线程数
    event-threads项设置，过小无法充分发挥多核CPU的性能，过大造成不必要的线程切换开销，推荐设置为CPU的核数。
    (2)最小空闲连接数(2.x以上版本不需要该项，1.x版本需要)
    min-idle-connections项设置，过小则在高并发下会有报错，过大虽然不报错但在测试时不容易看出读写分离效果，推荐设置为比客户端
    的并发峰值稍大，详见《配置参数详解》。上面的配置范例是针对Atlas 2.X版本，没有该选项。对于Atlas 1.X版本的配置文件，需要加入
    该配置选项。
    3. 可选配置说明
    以下几项可以设置，也可以使用默认值，区别不大。
    (1)Atlas的工作端口
    proxy-address项配置，例如proxy-address = 0.0.0.0:1234代表客户端应该使用1234这个端口连接Atlas来发送SQL请求。
    (2)Atlas的管理端口
    admin-address项配置，例如admin-address = 0.0.0.0:2345代表DBA应该使用2345这个端口连接Atlas来执行运维管理操作。
    (3)管理接口的用户名和密码
    admin-username项和admin-password项设置，这两项是用来进入Atlas的管理界面的，与后端连接的MySQL没有关系，所以可以任意设
    置，不需要MySQL在配置上做任何改动。
    (4)日志级别
    以log-level项配置，分为message、warning、critical、error、debug五个级别
    (5)日志路径
    以log-path项配置，如log-path = /usr/local/mysql-proxy/log。

    进入/usr/local/mysql-proxy/bin目录，执行下面的命令启动、重启或停止Atlas。
    (1). sudo ./mysql-proxyd test start，启动Atlas。
    (2). sudo ./mysql-proxyd test restart，重启Atlas。
    (3). sudo ./mysql-proxyd test stop，停止Atlas。
    注意：
    (1). 运行文件是：mysql-proxyd(不是mysql-proxy)。
    (2). test是conf目录下配置文件的名字，也是配置文件里instance项的名字，三者需要统一。
    (3). 可以使用ps -ef | grep mysql-proxy查看Atlas是否已经启动或停止。
    执行命令：mysql -h127.0.0.1 -P1234 -u用户名 -p密码，如果能连上则证明Atlas初步测试正常，可以再尝试发几条SQL语句看看执行
    结果是否正确。
    进入Atlas的管理界面的命令：mysql -h127.0.0.1 -P2345 -uuser -ppwd，进入后执行:select * from help;查看管理DB的各类命令。

    Atlas高可用【Keepalived】
    (1)、主节点配置
    # vim /etc/keepalived/keepalived.conf

    global_defs {
        notification_email {
            lovezym5@126.com
        }

        notification_email_from lovezym5@126.com
        smtp_server 127.0.0.1
        smtp_connect_timeout 30
        router_id dbproxy1
    }

    vrrp_script chk_mysql_proxy_health {
        script "/data/scripts/keepalived_check_mysql_proxy.sh"
        interval 1
        weight -2
    }

    vrrp_instance VI_1 {
        state MASTER
        interface eth1
        virtual_router_id 51
        priority 100
        advert_int 1
        smtp_alert

        authentication {
            auth_type PASS
            auth_pass 123456
        }

        virtual_ipaddress {
            10.209.6.115
        }

        track_script {
            chk_mysql_proxy_health
        }

        notify_master "/data/scripts/notify.sh master"
        notify_bakcup "/data/scripts/notify.sh backup"
        notify_fault "/data/scripts/notify.sh fault"
    }
    (2)、备用节点配置
    # vim /etc/keepalived/keepalived.conf

    global_defs {
        notification_email {
            lovezym5@126.com
        }

        notification_email_from lovezym5@126.com
        smtp_server 127.0.0.1
        smtp_connect_timeout 30
        router_id dbproxy2
    }

    vrrp_script chk_mysql_proxy_health {
        script "/data/scripts/keepalived_check_mysql_proxy.sh"
        interval 1
        weight -2
    }

    vrrp_instance VI_1 {
        state BACKUP
        interface eth1
        virtual_router_id 51
        priority 90
        advert_int 1
        smtp_alert

        authentication {
            auth_type PASS
            auth_pass 123456
        }

        virtual_ipaddress {
            10.209.6.115
        }

        track_script {
            chk_mysql_proxy_health
        }

        notify_master "/data/scripts/notify.sh master"
        notify_bakcup "/data/scripts/notify.sh backup"
        notify_fault "/data/scripts/notify.sh fault"
    }
    (3)、VIP切换通知脚本
    # vim /data/scripts/notify.sh

    #!/bin/sh
    PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin

    KEEPALIVE_CONF="/etc/keepalived/keepalived.conf"

    VIP=`grep -A 1 virtual_ipaddress ${KEEPALIVE_CONF} | tail -1 | sed 's/\t//g; s/ //g'`
    ETH1_ADDR=`/sbin/ifconfig eth1 | awk '/inet addr:/{print $2}' | awk -F: '{print $2}'`

    MONITOR="/usr/local/oms/agent/alarm/BusMonitorAgent"
    TOKEN="ha_monitor"

    function notify() {
        TITLE="$ETH1_ADDR to be $1: $VIP floating"
        CONTENT="vrrp transition, $ETH1_ADDR changed to be $1"
        ${MONITOR} -c 2 -f ${TOKEN} -t "${TITLE}" -i "${CONTENT}"
    }

    case "$1" in
    master)
        notify master
        exit 0
        ;;

    backup)
        notify backup
        exit 0
        ;;

    fault)
        notify fault
        exit 0
        ;;

    *)
        echo 'Usage: `basename $0` {master|backup|fault}'
        exit 1
        ;;
    esac
    (4)、DB中间层进程检查脚本
    # vim /data/scripts/keepalived_check_mysql_proxy.sh

    #!/bin/sh
    PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin

    if [[ `pgrep mysql-proxy | wc -l` -eq 0 ]]; then
        /sbin/service mysql-proxy start && sleep 5
        [[ -z `pgrep mysql-proxy` ]] && /sbin/service keepalived stop
    fi
    # chmod +x /data/scripts/*.sh
    # service keepalived start
    wKioL1Sw72OBWcdcAABQovflyow736.jpg
    # ip addr show eth1
    wKiom1Sw7r3S6v6_AACfXZvxonQ064.jpg
    # ps aux | grep keepalive[d]
    wKiom1Sw7tnzsSOAAABqz91YIVo562.jpg

    ==========================================================================================
    三、其他设置
    ==========================================================================================
    1、Atlas服务监控
    # vim /usr/local/mysql-proxy/bin/check_service.sh

    #!/bin/sh
    PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin

    [[ $# -ne 3 ]] && echo "$0 端口号 协议类型 服务名" && exit 1

    SRV_PORT=$1  ## 端口号
    SRV_PROT=$2  ## 协议类型
    SRV_NAME=$3  ## 服务名

    MONITOR="/usr/local/oms/agent/alarm/BusMonitorAgent"
    TOKEN="ha_monitor"

    TITLE="${SRV_NAME}服务异常监控"
    CONTENT="${SRV_NAME}服务发生异常，已自动拉起！"

    ## 是否已正确扫描
    SCAN_FLAG=0

    function RESTART_SRV_AND_ALERT() 
    {
        local CUR_SRV_NAME

        [[ $# -ne 1 ]] && exit 1
        CUR_SRV_NAME=$1

        TMP_SRV_NAME=`echo ${CUR_SRV_NAME} | tr '[A-Z]' '[a-z]'`
        [[ ! -f /etc/init.d/${TMP_SRV_NAME} ]] && TMP_SRV_NAME="${TMP_SRV_NAME}d"

        killall -9 ${TMP_SRV_NAME}

        if [[ -z `ps aux | grep ${TMP_SRV_NAME} | grep -v grep` ]]; then
            /sbin/service ${TMP_SRV_NAME} start >/dev/null 2>&1
        fi

        ${MONITOR} -c 2 -f ${TOKEN} -t "${TITLE}" -i "${CONTENT}"
        rm -f `pwd`/connect_error.log
    }

    ETH1_ADDR=`/sbin/ifconfig eth1 | awk -F ':' '/inet addr/{print $2}' | sed 's/[a-zA-Z ]//g'`
    TMP_SRV_PROT=`echo ${SRV_PROT} | tr '[A-Z]' '[a-z]'`

    if [[ "${TMP_SRV_PROT}" == "tcp" ]]; then
        PROT_OPT="S"
    elif [[ "${TMP_SRV_PROT}" == "udp" ]]; then
        PROT_OPT="U"
    else
        echo "未知的协议类型！" && exit 1
    fi

    ## 最多扫描3次，成功一次即可，以避免网络抖动而导致误判
    for ((i=0; i<3; i++)); do
        RETVAL=`/usr/bin/nmap -n -s${PROT_OPT} -p ${SRV_PORT} ${ETH1_ADDR} | grep open`
        [[ -n "${RETVAL}" ]] && SCAN_FLAG=1;break || sleep 10
    done

    ## 1、针对Atlas服务端口不通的情况，也就是服务彻底挂掉
    [[ ${SCAN_FLAG} -ne 1 ]] && RESTART_SRV_AND_ALERT ${SRV_NAME}

    ## 2、检查Atlas服务是否正常工作，也就是服务端口正常，但访问异常的情况【高权限DB用户】
    mysqladmin -h${ETH1_ADDR} -uhealth_check1 -p123456 --connect-timeout=15 --shutdown-timeout=15 ping
    [[ $? -ne 0 ]] && RESTART_SRV_AND_ALERT ${SRV_NAME}

    ## 3、检查Atlas服务是否正常工作，也就是服务端口正常，高权限DB用户访问也正常，但低权限
    ##    DB用户访问异常的情况【低权限DB用户】
    mysqladmin -h${ETH1_ADDR} -uhealth_check2 -p123456 --connect-timeout=15 --shutdown-timeout=15 ping
    [[ $? -ne 0 ]] && RESTART_SRV_AND_ALERT ${SRV_NAME}
    2、Atlas访问日志切割
    # vim /data/scripts/cut_and_clear_access_log.sh

    #!/bin/sh
    # 切割Atlas的访问日志，同时清理15天之前的日志
    #
    PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin

    ## mysql-proxy日志路径
    LOGPATH="/usr/local/mysql-proxy/log"

    [[ `/sbin/ip addr show eth1 | grep inet | wc -l` -eq 2 ]] || exit 1 
    cd ${LOGPATH}

    ## 日志切割
    HISTORY_LOG_PATH=`date -d '-1 hour' +"%Y-%m-%d/sql_mysql-proxy_%H.log"`
    [[ -d `dirname ${HISTORY_LOG_PATH}` ]] || mkdir -p `dirname ${HISTORY_LOG_PATH}`
    cp -a sql_mysql-proxy.log ${HISTORY_LOG_PATH}

    echo > sql_mysql-proxy.log

    ## 日志清理
    HISTORY_LOG_PATH=`date -d '15 days ago' +'%Y-%m-%d'`
    [[ -d ${HISTORY_LOG_PATH} ]] && rm -rf ${HISTORY_LOG_PATH}
    3、crontab内容添加
    # touch /var/lock/check_service.lock
    # echo 'touch /var/lock/check_service.lock' >> /etc/rc.d/rc.local
    # crontab -uroot -e
    1
    2
    * * * * * (flock --timeout=0 /var/lock/check_service.lock /usr/local/mysql-proxy/bin/check_service.sh 
    3306 tcp mysql-proxy >/dev/null 2>&1)
    00 * * * * /data/scripts/cut_and_clear_access_log.sh >/dev/null 2>&1
    4、平滑设置功能
    # mysql -h10.209.6.101 -P3307 -usysadmin -p'admin2356!@()'
    wKioL1Sw8S_gXZOuAALgQK7R39c195.jpg


## my.cnf
```
以下选项会被MySQL客户端应用读取。
注意只有MySQL附带的客户端应用程序保证可以读取这段内容。
如果你想你自己的MySQL应用程序获取这些值。
需要在MySQL客户端库初始化的时候指定这些选项。


[client]
password=[your_password]
port=@MYSQL_TCP_PORT@
socket=@MYSQL_UNIX_ADDR@

***应用定制选项***


MySQL服务端

[mysqld]

一般配置选项
port=@MYSQL_TCP_PORT@
socket=@MYSQL_UNIX_ADDR@

skip-name-resolve
选项就能禁用DNS解析，连接速度会快很多。不过，这样的话就不能在MySQL的授权表中使用主机名了而只能用ip格式

back_log是操作系统在监听队列中所能保持的连接数,
队列保存了在MySQL连接管理器线程处理之前的连接.
如果你有非常高的连接率并且出现”connectionrefused”报错,
你就应该增加此处的值.
检查你的操作系统文档来获取这个变量的最大值.
如果将back_log设定到比你操作系统限制更高的值,将会没有效果
back_log=300

不在TCP/IP端口上进行监听.
如果所有的进程都是在同一台服务器连接到本地的mysqld,
这样设置将是增强安全的方法
所有mysqld的连接都是通过Unixsockets或者命名管道进行的.
注意在windows下如果没有打开命名管道选项而只是用此项
(通过“enable-named-pipe”选项)将会导致mysql服务没有任何作用!
skip-networking

MySQL服务所允许的同时会话数的上限
其中一个连接将被SUPER权限保留作为管理员登录.
即便已经达到了连接数的上限.
max_connections=3000
每个客户端连接最大的错误允许数量,如果达到了此限制.
这个客户端将会被MySQL服务阻止直到执行了”FLUSHHOSTS”或者服务重启
非法的密码以及其他在链接时的错误会增加此值.
查看“Aborted_connects”状态来获取全局计数器.
max_connect_errors=30

所有线程所打开表的数量.
增加此值就增加了mysqld所需要的文件描述符的数量
这样你需要确认在[mysqld_safe]中“open-files-limit”变量设置打开文件数量允许至少4096
table_cache=4096

允许外部文件级别的锁.打开文件锁会对性能造成负面影响
所以只有在你在同样的文件上运行多个数据库实例时才使用此选项(注意仍会有其他约束!)
或者你在文件层面上使用了其他一些软件依赖来锁定MyISAM表
external-locking

服务所能处理的请求包的最大大小以及服务所能处理的最大的请求大小(当与大的BLOB字段一起工作时相当必要)
每个连接独立的大小.大小动态增加
max_allowed_packet=32M

在一个事务中binlog为了记录SQL状态所持有的cache大小
如果你经常使用大的,多声明的事务,你可以增加此值来获取更大的性能.
所有从事务来的状态都将被缓冲在binlog缓冲中然后在提交后一次性写入到binlog中
如果事务比此值大,会使用磁盘上的临时文件来替代.
此缓冲在每个连接的事务第一次更新状态时被创建
binlog_cache_size=4M

独立的内存表所允许的最大容量.
此选项为了防止意外创建一个超大的内存表导致永尽所有的内存资源.
max_heap_table_size=128M

排序缓冲被用来处理类似ORDERBY以及GROUPBY队列所引起的排序
如果排序后的数据无法放入排序缓冲,
一个用来替代的基于磁盘的合并分类会被使用
查看“Sort_merge_passes”状态变量.
在排序发生时由每个线程分配
sort_buffer_size=16M

此缓冲被使用来优化全联合(fullJOINs不带索引的联合).
类似的联合在极大多数情况下有非常糟糕的性能表现,
但是将此值设大能够减轻性能影响.
通过“Select_full_join”状态变量查看全联合的数量
当全联合发生时,在每个线程中分配
join_buffer_size=16M

我们在cache中保留多少线程用于重用
当一个客户端断开连接后,如果cache中的线程还少于thread_cache_size,
则客户端线程被放入cache中.
这可以在你需要大量新连接的时候极大的减少线程创建的开销
(一般来说如果你有好的线程模型的话,这不会有明显的性能提升.)
thread_cache_size=16

此允许应用程序给予线程系统一个提示在同一时间给予渴望被运行的线程的数量.
此值只对于支持thread_concurrency()函数的系统有意义(例如SunSolaris).
你可可以尝试使用[CPU数量]*(2..4)来作为thread_concurrency的值
thread_concurrency=8

查询缓冲常被用来缓冲SELECT的结果并且在下一次同样查询的时候不再执行直接返回结果.
打开查询缓冲可以极大的提高服务器速度,如果你有大量的相同的查询并且很少修改表.
查看“Qcache_lowmem_prunes”状态变量来检查是否当前值对于你的负载来说是否足够高.
注意:在你表经常变化的情况下或者如果你的查询原文每次都不同,
查询缓冲也许引起性能下降而不是性能提升.
query_cache_size=128M

只有小于此设定值的结果才会被缓冲
此设置用来保护查询缓冲,防止一个极大的结果集将其他所有的查询结果都覆盖.
query_cache_limit=4M

被全文检索索引的最小的字长.
你也许希望减少它,如果你需要搜索更短字的时候.
注意在你修改此值之后,
你需要重建你的FULLTEXT索引
ft_min_word_len=8

如果你的系统支持memlock()函数,你也许希望打开此选项用以让运行中的mysql在在内存高度紧张的时候,数据在内存中保持锁定并且防
止可能被swappingout
此选项对于性能有益
memlock

当创建新表时作为默认使用的表类型,
如果在创建表示没有特别执行表类型,将会使用此值
default_table_type=MYISAM

线程使用的堆大小.此容量的内存在每次连接时被预留.
MySQL本身常不会需要超过64K的内存
如果你使用你自己的需要大量堆的UDF函数
或者你的操作系统对于某些操作需要更多的堆,
你也许需要将其设置的更高一点.
thread_stack=512K

设定默认的事务隔离级别.可用的级别如下:
READ-UNCOMMITTED,READ-COMMITTED,REPEATABLE-READ,SERIALIZABLE
transaction_isolation=REPEATABLE-READ

内部(内存中)临时表的最大大小
如果一个表增长到比此值更大,将会自动转换为基于磁盘的表.
此限制是针对单个表的,而不是总和.
tmp_table_size=128M

打开二进制日志功能.
在复制(replication)配置中,作为MASTER主服务器必须打开此项
如果你需要从你最后的备份中做基于时间点的恢复,你也同样需要二进制日志.
log-bin=mysql-bin

如果你在使用链式从服务器结构的复制模式(A->B->C),
你需要在服务器B上打开此项.
此选项打开在从线程上重做过的更新的日志,
并将其写入从服务器的二进制日志.
log_slave_updates

打开全查询日志.所有的由服务器接收到的查询(甚至对于一个错误语法的查询)
都会被记录下来.这对于调试非常有用,在生产环境中常常关闭此项.
log

将警告打印输出到错误log文件.如果你对于MySQL有任何问题
你应该打开警告log并且仔细审查错误日志,查出可能的原因.
log_warnings

记录慢速查询.慢速查询是指消耗了比“long_query_time”定义的更多时间的查询.
如果log_long_format被打开,那些没有使用索引的查询也会被记录.
如果你经常增加新查询到已有的系统内的话.一般来说这是一个好主意,
log_slow_queries

所有的使用了比这个时间(以秒为单位)更多的查询会被认为是慢速查询.
不要在这里使用”1″,否则会导致所有的查询,甚至非常快的查询页被记录下来(由于MySQL目前时间的精确度只能达到秒的级别).
long_query_time=6

在慢速日志中记录更多的信息.
一般此项最好打开.
打开此项会记录使得那些没有使用索引的查询也被作为到慢速查询附加到慢速日志里
log_long_format

此目录被MySQL用来保存临时文件.例如,
它被用来处理基于磁盘的大型排序,和内部排序一样.
以及简单的临时表.
如果你不创建非常大的临时文件,将其放置到swapfs/tmpfs文件系统上也许比较好
另一种选择是你也可以将其放置在独立的磁盘上.
你可以使用”;”来放置多个路径
他们会按照roud-robin方法被轮询使用.
tmpdir=/tmp

***主从复制相关的设置

唯一的服务辨识号,数值位于1到2^32-1之间.
此值在master和slave上都需要设置.
如果“master-host”没有被设置,则默认为1,但是如果忽略此选项,MySQL不会作为master生效.
server-id=1

复制的Slave(去掉master段的注释来使其生效)

为了配置此主机作为复制的slave服务器,你可以选择两种方法:

1)使用CHANGEMASTERTO命令(在我们的手册中有完整描述)-
语法如下:

CHANGEMASTERTOMASTER_HOST=,MASTER_PORT=,
MASTER_USER=,MASTER_PASSWORD=;

你需要替换掉,,等被尖括号包围的字段以及使用master的端口号替换(默认3306).

例子:

CHANGEMASTERTOMASTER_HOST=’125.564.12.1′,MASTER_PORT=3306,
MASTER_USER=’joe’,MASTER_PASSWORD=’secret’;

或者

2)设置以下的变量.不论如何,在你选择这种方法的情况下,然后第一次启动复制(甚至不成功的情况下,
例如如果你输入错密码在master-password字段并且slave无法连接),
slave会创建一个master.info文件,并且之后任何对于包含在此文件内的参数的变化都会被忽略
并且由master.info文件内的内容覆盖,除非你关闭slave服务,删除master.info并且重启slave服务.
由于这个原因,你也许不想碰一下的配置(注释掉的)并且使用CHANGEMASTERTO(查看上面)来代替

所需要的唯一id号位于2和2^32–1之间
(并且和master不同)
如果master-host被设置了.则默认值是2
但是如果省略,则不会生效
server-id=2

复制结构中的master–必须
master-host=

当连接到master上时slave所用来认证的用户名–必须
master-user=

当连接到master上时slave所用来认证的密码–必须
master-password=

master监听的端口.
可选–默认是3306
master-port=

使得slave只读.只有用户拥有SUPER权限和在上面的slave线程能够修改数据.
你可以使用此项去保证没有应用程序会意外的修改slave而不是master上的数据
read_only

***MyISAM相关选项

关键词缓冲的大小,一般用来缓冲MyISAM表的索引块.
不要将其设置大于你可用内存的30%,
因为一部分内存同样被OS用来缓冲行数据
甚至在你并不使用MyISAM表的情况下,你也需要仍旧设置起8-64M内存由于它同样会被内部临时磁盘表使用.
key_buffer_size=128M

用来做MyISAM表全表扫描的缓冲大小.
当全表扫描需要时,在对应线程中分配.
read_buffer_size=8M

当在排序之后,从一个已经排序好的序列中读取行时,行数据将从这个缓冲中读取来防止磁盘寻道.
如果你增高此值,可以提高很多ORDERBY的性能.
当需要时由每个线程分配
read_rnd_buffer_size=64M

MyISAM使用特殊的类似树的cache来使得突发插入
(这些插入是,INSERT…SELECT,INSERT…VALUES(…),(…),…,以及LOADDATA
INFILE)更快.此变量限制每个进程中缓冲树的字节数.
设置为0会关闭此优化.
为了最优化不要将此值设置大于“key_buffer_size”.
当突发插入被检测到时此缓冲将被分配.
bulk_insert_buffer_size=256M

此缓冲当MySQL需要在REPAIR,OPTIMIZE,ALTER以及LOADDATAINFILE到一个空表中引起重建索引时被分配.
这在每个线程中被分配.所以在设置大值时需要小心.
myisam_sort_buffer_size=256M

MySQL重建索引时所允许的最大临时文件的大小(当REPAIR,ALTERTABLE或者LOADDATAINFILE).
如果文件大小比此值更大,索引会通过键值缓冲创建(更慢)
myisam_max_sort_file_size=10G

如果被用来更快的索引创建索引所使用临时文件大于制定的值,那就使用键值缓冲方法.
这主要用来强制在大表中长字串键去使用慢速的键值缓冲方法来创建索引.
myisam_max_extra_sort_file_size=10G

如果一个表拥有超过一个索引,MyISAM可以通过并行排序使用超过一个线程去修复他们.
这对于拥有多个CPU以及大量内存情况的用户,是一个很好的选择.
myisam_repair_threads=1

自动检查和修复没有适当关闭的MyISAM表.
myisam_recover

默认关闭Federated
skip-federated

***BDB相关选项***

如果你运行的MySQL服务有BDB支持但是你不准备使用的时候使用此选项.这会节省内存并且可能加速一些事.
skip-bdb

***INNODB相关选项***

如果你的MySQL服务包含InnoDB支持但是并不打算使用的话,
使用此选项会节省内存以及磁盘空间,并且加速某些部分
skip-innodb

附加的内存池被InnoDB用来保存metadata信息
如果InnoDB为此目的需要更多的内存,它会开始从OS这里申请内存.
由于这个操作在大多数现代操作系统上已经足够快,你一般不需要修改此值.
SHOWINNODBSTATUS命令会显示当先使用的数量.
innodb_additional_mem_pool_size=64M

InnoDB使用一个缓冲池来保存索引和原始数据,不像MyISAM.
这里你设置越大,你在存取表里面数据时所需要的磁盘I/O越少.
在一个独立使用的数据库服务器上,你可以设置这个变量到服务器物理内存大小的80%
不要设置过大,否则,由于物理内存的竞争可能导致操作系统的换页颠簸.
注意在32位系统上你每个进程可能被限制在2-3.5G用户层面内存限制,
所以不要设置的太高.
innodb_buffer_pool_size=6G

InnoDB将数据保存在一个或者多个数据文件中成为表空间.
如果你只有单个逻辑驱动保存你的数据,一个单个的自增文件就足够好了.
其他情况下.每个设备一个文件一般都是个好的选择.
你也可以配置InnoDB来使用裸盘分区–请参考手册来获取更多相关内容
innodb_data_file_path=ibdata1:10M:autoextend

设置此选项如果你希望InnoDB表空间文件被保存在其他分区.
默认保存在MySQL的datadir中.
innodb_data_home_dir=

用来同步IO操作的IO线程的数量.Thisvalueis
此值在Unix下被硬编码为4,但是在Windows磁盘I/O可能在一个大数值下表现的更好.
innodb_file_io_threads=4

如果你发现InnoDB表空间损坏,设置此值为一个非零值可能帮助你导出你的表.
从1开始并且增加此值知道你能够成功的导出表.
innodb_force_recovery=1

在InnoDb核心内的允许线程数量.
最优值依赖于应用程序,硬件以及操作系统的调度方式.
过高的值可能导致线程的互斥颠簸.
innodb_thread_concurrency=16

如果设置为1,InnoDB会在每次提交后刷新(fsync)事务日志到磁盘上,
这提供了完整的ACID行为.
如果你愿意对事务安全折衷,并且你正在运行一个小的食物,你可以设置此值到0或者2来减少由事务日志引起的磁盘I/O
0代表日志只大约每秒写入日志文件并且日志文件刷新到磁盘.
2代表日志写入日志文件在每次提交后,但是日志文件只有大约每秒才会刷新到磁盘上.
innodb_flush_log_at_trx_commit=2
（说明：如果是游戏服务器，建议此值设置为2；如果是对数据安全要求极高的应用，建议设置为1；设置为0性能最高，但如果发生故障，
数据可能会有丢失的危险！默认值1的意思是每一次事务提交或事务外的指令都需要把日志写入（flush）硬盘，这是很费时的。特别是使用电
池供电缓存（Batterybackedupcache）时。设成2对于很多运用，特别是从MyISAM表转过来的是可以的，它的意思是不写入硬盘而是写入
系统缓存。日志仍然会每秒flush到硬盘，所以你一般不会丢失超过1-2秒的更新。设成0会更快一点，但安全方面比较差，即使MySQL挂了
也可能会丢失事务的数据。而值2只会在整个操作系统挂了时才可能丢数据。）

加速InnoDB的关闭.这会阻止InnoDB在关闭时做全清除以及插入缓冲合并.
这可能极大增加关机时间,但是取而代之的是InnoDB可能在下次启动时做这些操作.
innodb_fast_shutdown

用来缓冲日志数据的缓冲区的大小.
当此值快满时,InnoDB将必须刷新数据到磁盘上.
由于基本上每秒都会刷新一次,所以没有必要将此值设置的太大(甚至对于长事务而言)

innodb_log_buffer_size=16M

在日志组中每个日志文件的大小.
你应该设置日志文件总合大小到你缓冲池大小的25%~100%
来避免在日志文件覆写上不必要的缓冲池刷新行为.
不论如何,请注意一个大的日志文件大小会增加恢复进程所需要的时间.
innodb_log_file_size=512M

在日志组中的文件总数.
通常来说2~3是比较好的.
innodb_log_files_in_group=3

InnoDB的日志文件所在位置.默认是MySQL的datadir.
你可以将其指定到一个独立的硬盘上或者一个RAID1卷上来提高其性能
innodb_log_group_home_dir

在InnoDB缓冲池中最大允许的脏页面的比例.
如果达到限额,InnoDB会开始刷新他们防止他们妨碍到干净数据页面.
这是一个软限制,不被保证绝对执行.
innodb_max_dirty_pages_pct=90

InnoDB用来刷新日志的方法.
表空间总是使用双重写入刷新方法
默认值是“fdatasync”,另一个是“O_DSYNC”.
innodb_flush_method=O_DSYNC

在被回滚前,一个InnoDB的事务应该等待一个锁被批准多久.
InnoDB在其拥有的锁表中自动检测事务死锁并且回滚事务.
如果你使用LOCKTABLES指令,或者在同样事务中使用除了InnoDB以外的其他事务安全的存储引擎
那么一个死锁可能发生而InnoDB无法注意到.
这种情况下这个timeout值对于解决这种问题就非常有帮助.
innodb_lock_wait_timeout=120

[mysqldump]
不要在将内存中的整个结果写入磁盘之前缓存.在导出非常巨大的表时需要此项
quick

max_allowed_packet=32M

[mysql]
no-auto-rehash

仅仅允许使用键值的UPDATEs和DELETEs.
safe-updates

[isamchk]
key_buffer=2048M
sort_buffer_size=2048M
read_buffer=32M
write_buffer=32M

[myisamchk]
key_buffer=2048M
sort_buffer_size=2048M
read_buffer=32M
write_buffer=32M

[mysqlhotcopy]
interactive-timeout

[mysqld_safe]
增加每个进程的可打开文件数量.
警告:确认你已经将全系统限制设定的足够高!
打开大量表需要将此值设大
open-files-limit=8192
```
