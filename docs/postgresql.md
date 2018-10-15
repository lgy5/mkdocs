## 多实例
```
PostgreSQL是支持多实例的，下面我们介绍启动两个实例的方法。首先新建两个数据文件目录：

cd /opt/PostgreSQL/9.3.5/data/
mkdir pgdata1
mkdir pgdata2
chown postgres pgdata1
chown postgres pgdata2
然后新建两个实例：

su postgres
initdb -D /opt/PostgreSQL/9.3.5/data/pgdata1 --locale=zh_CN.UTF8
initdb -D /opt/PostgreSQL/9.3.5/data/pgdata2 --locale=zh_CN.UTF8
修改pgdata1和pgdata2目录下的postgresql.conf文件中的port参数，分别将其值设置为5433和5434，下一步就可以启动两个实例了，命令如下：

pg_ctl -D /opt/PostgreSQL/9.3.5/data/pgdata1 start
pg_ctl -D /opt/PostgreSQL/9.3.5/data/pgdata2 start
进入两个实例分别使用如下命令：

psql -p 5433
psql -p 5434

来源： https://mos.meituan.com/library/33/postgresql-source-based-installation/
```



## pg同步
```
数据库的热备归档+流复制模式配置


首先先做主备数据库之间的信任关系，使两台服务器之间互相访问不需要密码验证。
主服务器上 在root
postgresql 两个用户下分别生成证书

在主机A上执行如下命令来生成配对密钥：

ssh-keygen -t rsa 

按照提示操作，注意，不要输入passphrase。提示信息如下
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
The key fingerprint is:
ff:8e:85:68:85:94:7c:2c:46:b1:e5:2d:41:5c:e8:9b  root@localhost.domain



将 .ssh 目录中的 id_rsa.pub 文件复制到 主机B 的 ~/.ssh/ 目录中，并改名为  authorized_keys。

scp .ssh/id_rsa.pub 192.168.2.91:/root/.ssh/authorized_keys

备注：scp id_rsa.pub postgres@192.168.2.92:/home/postgres/.ssh/authorized_keys

以后从A主机scp到B主机就不需要密码了。




使用上面的操作，反过来再建立B连接A不需要密码验证，方法是把B的公钥id_rsa.pub 改名放到A的.ssh目录下。

如果用户名不相同，需要把访问者用户的公钥放到被访问者服务器用户目录下的.ssh目录，并把公钥id_rsa.pub的内容添加到
authorized_keys 用户中。

cat id_rsa.pub >> 目录/authorized_keys


主库操作：

修改：vim /usr/local/pgsql/data/pg_hba.conf

添加：

local    all            all                                     trust
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             192.168.2.0/24          trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
host    replication     postgres        192.168.2.0/24          trust
host    replication     postgres        ::1/128                 trust


编辑vim /usr/local/pgsql/data/postgresql.conf

max_wal_senders = 5
wal_keep_segments = 1000
wal_sender_timeout = 60s
hot_standby = on
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_file_mode = 0600
log_rotation_age = 1d
log_rotation_size = 20MB
client_min_messages = notice
log_min_messages = warning
log_min_error_statement = error
log_min_duration_statement = 60
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 1000
pg_stat_statements.track = top
pg_stat_statements.track_utility = true
pg_stat_statements.save = true
log_checkpoints = on
log_connections = on
log_lock_waits = on
log_statement = 'ddl'
log_timezone = 'PRC'


在/data目录下创建存放归档日志的目录

mkdir archivedir

chown postgres.postgres archivedir



创建存储数据库基础备份的目录/data

mkidr pgbackup

chown postgres.postgres pgbackup


以上操作完毕后，重启postgresql数据库。

/etc/init.d/postgresql restart
/usr/local/pgsql/bin/pg_ctl restart -D /usr/local/pgsql/data/


创建数据库基础本分：

进入postgresql 用户：

su -l postgres

[postgres@AY131021150028549089Z ~]$ psql

postgres=# SELECT pg_start_backup('basebak20151209');

pg_start_backup

-----------------

0/8000028

(1 row)


postgres=# \q

[postgres@AY131021150028549089Z ~]$ exit

[root@AY131021150028549089Z data]# cd pgbackup/

[root@AY131021150028549089Z pgbackup]# tar zvcf base201510_data.tar.gz /data 复制数据库数据目录并压缩成文件

[root@AY131021150028549089Z data]# su -l postgres

[postgres@AY131021150028549089Z ~]$ psql

postgres=# SELECT pg_stop_backup();

NOTICE: pg_stop_backup complete, all required WAL segments have been archived

pg_stop_backup

----------------         

0/8000230

(1 row)


postgres=# \q




[root@AY131021150028549089Z data]# cd pgbackup/

[root@AY131021150028549089Z pgbackup]# chown postgres.postgres base20131112_data.tar.gz




    备库上的操作：

在/data下创建 pgbackup目录

mkdir archivedir

chown postgres.postgres archivedir


创建存储数据库基础备份的目录

mkdir pgbackup

chown postgres.postgres pgbackup


以上操作完毕后，停止postgresql数据库。

/etc/init.d/postgresql stop 停止当前备用数据库的运行
su


su -l postgres

cd /data/pgbackup

scp 192.168.2.91:/data/pgbackup/base20131112_data.tar.gz ./  复制主库的基本库备份文件


[postgres@AY131021150027813b05Z pgbackup]$ tar zvxf base20131112_data.tar.gz -C ../  解压缩并复制到备库数据目录中去

cd /data/data/pg_xlog

[postgres@AY131021150027813b05Z pg_xlog]$ rm -f 0*

[postgres@AY131021150027813b05Z archive_status]$ rm -f 0*

cd /data/data

rm postmaster.pid

cp /usr/local/pgsql/share/recovery.conf.sample ./recovery.conf




编辑recover.conf文件

restore_command = 'scp 10.161.166.25:/data/archivedir/%f "%p" 2> /dev/null'

recovery_target_timeline = 'latest'

standby_mode = 'on'

primary_conninfo = 'host=172.31.2.150 port=5432 user=postgres'

trigger_file = '/tmp/trigger_file0'


chown postgres.postgres recovery.conf权限

修改完成后，重启数据库

/etc/rc.d/init.d/postgres start
```



## pg安装
```
yum install postgresql-server postgresql -y
/etc/init.d/postgresql initdb
/etc/init.d/postgresql restart
/var/lib/pgsql/data/postgresql.conf  配置文件
vim  /var/lib/pgsql/data/pg_hba.conf 添加，可以远程访问
host    all    all    0.0.0.0/0    md5

su - postgres
psql  登录

第一件事是使用\password命令，为postgres用户设置一个密码。
\password postgres
第二件事是创建数据库用户dbuser（刚才创建的是Linux系统用户），并设置密码。
CREATE USER dbuser WITH PASSWORD 'password';
第三件事是创建用户数据库，这里为exampledb，并指定所有者为dbuser。
CREATE DATABASE exampledb OWNER dbuser;
第四件事是将exampledb数据库的所有权限都赋予dbuser，否则dbuser只能登录控制台，没有任何数据库操作权限。
GRANT ALL PRIVILEGES ON DATABASE exampledb to dbuser;
最后，使用\q命令退出控制台（也可以直接按ctrl+D）。
\q
第二种方法，使用shell命令行。
添加新用户和新数据库，除了在PostgreSQL控制台内，还可以在shell命令行下完成。这是因为PostgreSQL提供了
命令行程序createuser和createdb。还是以新建用户dbuser和数据库exampledb为例。
首先，创建数据库用户dbuser，并指定其为超级用户。
sudo -u postgres createuser --superuser dbuser
然后，登录数据库控制台，设置dbuser用户的密码，完成后退出控制台。
sudo -u postgres psql
\password dbuser
\q
接着，在shell命令行下，创建数据库exampledb，并指定所有者为dbuser。
sudo -u postgres createdb -O dbuser exampledb
三、登录数据库
添加新用户和新数据库以后，就要以新用户的名义登录数据库，这时使用的是psql命令。
psql -U dbuser -d exampledb -h 127.0.0.1 -p 5432
上面命令的参数含义如下：-U指定用户，-d指定数据库，-h指定服务器，-p指定端口。
输入上面命令以后，系统会提示输入dbuser用户的密码。输入正确，就可以登录控制台了。
psql命令存在简写形式。如果当前Linux系统用户，同时也是PostgreSQL用户，则可以省略用户名（-U参数的部分）。举
例来说，我的Linux系统用户名为ruanyf，且PostgreSQL数据库存在同名用户，则我以ruanyf身份登录Linux系统后，
可以直接使用下面的命令登录数据库，且不需要密码。
psql exampledb
此时，如果PostgreSQL内部还存在与当前系统用户同名的数据库，则连数据库名都可以省略。比如，假定存在一个叫做ruanyf
的数据库，则直接键入psql就可以登录该数据库。
psql
另外，如果要恢复外部数据，可以使用下面的命令。
psql exampledb < exampledb.sql
四、控制台命令
除了前面已经用到的\password命令（设置密码）和\q命令（退出）以外，控制台还提供一系列其他命令。
\h：查看SQL命令的解释，比如\h select。
\?：查看psql命令列表。
\l：列出所有数据库。
\c [database_name]：连接其他数据库。
\d：列出当前数据库的所有表格。
\d [table_name]：列出某一张表格的结构。
\du：列出所有用户。
\e：打开文本编辑器。
\conninfo：列出当前数据库和连接的信息。
五、数据库操作
基本的数据库操作，就是使用一般的SQL语言。
# 创建新表
CREATE TABLE user_tbl(name VARCHAR(20), signup_date DATE);
# 插入数据
INSERT INTO user_tbl(name, signup_date) VALUES('张三', '2013-12-22');
# 选择记录
SELECT * FROM user_tbl;
# 更新数据
UPDATE user_tbl set name = '李四' WHERE name = '张三';
# 删除记录
DELETE FROM user_tbl WHERE name = '李四' ;
# 添加栏位
ALTER TABLE user_tbl ADD email VARCHAR(40);
# 更新结构
ALTER TABLE user_tbl ALTER COLUMN signup_date SET NOT NULL;
# 更名栏位
ALTER TABLE user_tbl RENAME COLUMN signup_date TO signup;
# 删除栏位
ALTER TABLE user_tbl DROP COLUMN email;
# 表格更名
ALTER TABLE user_tbl RENAME TO backup_tbl;
# 删除表格
DROP TABLE IF EXISTS backup_tbl;
```



