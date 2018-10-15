## authSchema
```
下载了最新mongodb3.03版本，当使用--auth 参数命令行开启mongodb用户认证时遇到很多问题，现总结如下：
（百度上搜到的基本都是老版本的，看到db.addUser的就是，请忽略）
Windows下我做了一个bat文件，用来启动mongodb，命令行如下：
mongod --dbpath db\data --port 27017 --directoryperdb --logpath db\logs\mongodb.log --logappend --auth
最后的参数就是开启和关闭认证，如果是conf配置文件，应该是auth=true或false
1，首先关闭认证，也就是不带--auth参数，启动mongodb
2，使用命令行进入mongodb目录，输入mongo命令，默认进入test数据库
3，use userdb  切换到自己的数据库，输入db，显示userdb
4，创建用户，角色为dbOwner，数据库为userdb，命令行应该是db.createUser({user:'myuser',pwd:'123456',roles:
[{role:'dbOwner',db:'userdb'}]})
5，切换到admin数据库，use admin，db ，显示admin，db.shutdownServer()关闭服务器，填上认证参数，启动mongodb；
以前的版本此时使用mongovue就可以使用myuser登录到userdb数据库上了，但是3.0.3版本不行，打开mongodb.log文件发现如下错误

authenticate db: userdb { authenticate: 1, nonce: "xxx", user: "myuser", key: "xxx" }
2015-06-02T09:57:18.877+0800 I ACCESS   [conn2] Failed to authenticate myuser@userdb with mechanism 
MONGODB-CR: AuthenticationFailed MONGODB-CR credentials missing in the user document


此1-5步骤针对是3.0.3以前版本已经ok，如果是3.0.3，mongodb加入了SCRAM-SHA-1校验方式，需要第三方工具配合进行验证，
下面给出具体解决办法：
首先关闭认证，修改system.version文档里面的authSchema版本为3，初始安装时候应该是5，命令行如下：
> use admin
switched to db admin
>  var schema = db.system.version.findOne({"_id" : "authSchema"})
> schema.currentVersion = 3
3
> db.system.version.save(schema)
WriteResult({ "nMatched" : 1, "nUpserted" : 0, "nModified" : 1 })

不过如果你现在开启认证，仍然会提示AuthenticationFailed MONGODB-CR credentials missing in the user document
原因是原来创建的用户已经使用了SCRAM-SHA-1认证方式
> use admin
switched to db admin
> db.system.users.find()
[...]
{ "_id" : "userdb.myuser", "user" : "myuser", "db" : "userdb", "credentials" : { "SCRAM-SHA-1" :
 { "iterationCount" : 10000, "salt" : "XXXXXXXXXXXXXXXXXXXXXXXX", "storedKey" : 
 "XXXXXXXXXXXXXXXXXXXXXXXXXXX", "serverKey" : "XXXXXXXXXXXXXXXXXXXXXXXXXXX" } }, 
 "roles" : [ { "role" : "dbOwner", "db" : "userdb" } ] }

解决方式就是删除刚刚创建的用户，重新重建即可：
> use userdb
switched to db userdb
> db.dropUser("myuser")
true
>db.createUser({user:'myuser',pwd:'123456',roles:[{role:'dbOwner',db:'userdb'}]})
然后关闭服务器，开启认证，重启服务器，用mongovue连接，一切OK
```



## 集群认证
```
继mongodb3.2复制集和shard集群之后的用户认证登陆。
1：关于mongos登录权限认证配置

[mongodb@node1 keyfile]$ openssl rand -base64 741 > /data/keyfile/zxl
[mongodb@node1 keyfile]$ chmod 600 /data/keyfile/zxl
2：把/data/keyfile/zxl文件拷贝到各个机器/data/keyfile/目录下即可
切记属主和组以及文件权限600
3：创建用户
[mongodb@node1 config]$ mongo --port 10005
MongoDB shell version: 3.2.3
connecting to: 127.0.0.1:10005/test
mongos> use admin
switched to db admin
db.createUser(
  {
    user: "zxl",
    pwd: "123",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
db.createUser( {
    user: "zxl",
    pwd: "123",
    roles: [ { role: "root", db: "admin" } ]
});
mongos> db.auth('zxl','123')
注：userAdminAnyDatabase：只在admin数据库中可用，赋予用户所有数据库的userAdmin权限，root：
只在admin数据库中可用。超级账号，超级权限，其实 创建一个userAdminAnyDatabase角色就可以，然后可以创建N个用户角色。。。
4：关闭三台机器上的mongod和configsvr以及mongos服务
[mongodb@node1 keyfile]$ netstat -ntpl|grep mongo|awk '{print $NF}'|awk -F'/' '{print $1}'|xargs kill
5：修改三台机器上的shard1.conf、shard2.conf、shard3.conf、configsvr.conf、mongos.conf配置文件中的内容，
分别去掉注释内容即可
#security:
#  keyFile: "/data/keyfile/zxl"
#  clusterAuthMode: "keyFile"
去掉注释
security:
  keyFile: "/data/keyfile/zxl"
  clusterAuthMode: "keyFile"
启动三台机器上的shard1、shard2、shard3以及configsvr和mongos节点
[mongodb@node1 ~]$ mongod -f /data/config/shard1.conf
[mongodb@node1 ~]$ mongod -f /data/config/shard2.conf
[mongodb@node1 ~]$ mongod -f /data/config/shard3.conf
[mongodb@node1 logs]$ mongod -f /data/config/configsvr.conf
[mongodb@node1 logs]$ mongos -f /data/config/mongos.conf
登录mongos
[mongodb@node1 config]$ mongo --port 10005
MongoDB shell version: 3.2.3
connecting to: 127.0.0.1:10005/test
mongos> use admin
switched to db admin
mongos> db.auth('zxl','123')
mongos> sh.enableSharding("av")//启用shard分片
{ "ok" : 1 }
mongos> sh.shardCollection("av.xxoo",{name:1})//设置集合的名字以及字段，默认自动建立索引，av库，xxoo集合
{ "collectionsharded" : "av.xxoo", "ok" : 1 }


总结内容如下：
系统时间和防火墙，切记
#security.keyFile： 格式与security.authorization相同，功能与--keyFile相同。
--keyFile <file>: 主要用于分片集群与副本集相互之间的授权使用，在单机情况下只要用到auth，
如果是在集群(分片+副本集)环境下，就必须要用到该参数；
因为之前我就创建了一个userAdminAnyDatabase角色，所以创建一个root角色的账户。如下
[mongodb@node1 config]$ mongo 192.168.75.128:10005/admin -u zxl -p 123 --authenticationDatabase admin
MongoDB shell version: 3.2.3
connecting to: 192.168.75.128:10005/admin
mongos> show dbs
ad      0.000GB
admin   0.000GB
config  0.001GB
mongos> db.createUser({user: "root",pwd: "123456",roles: [ "root" ]})
Successfully added user: { "user" : "root", "roles" : [ "root" ] }
mongos> db.auth("root","123456")
mongos>
bye
认证登陆
[mongodb@node1 config]$ mongo 192.168.75.128:10005/admin -u root -p 123456 --authenticationDatabase
MongoDB shell version: 3.2.3
connecting to: 192.168.75.128:10005/admin
mongos> show dbs
ad      0.000GB
admin   0.000GB
av      0.000GB
config  0.001GB
```



## 集群安装
```
https://www.mongodb.com/download-center#community

下载后解压 三台服务器都配置

mkdir conf data log pid

cat conf/shard11.conf
dbpath=/usr/local/mongodb/data/shard11
logpath=/usr/local/mongodb/log/shard11.log
pidfilepath=/usr/local/mongodb/pid/shard11.pid
directoryperdb=true
logappend=true
replSet=shard1
port=10011
fork=true
shardsvr=true
journal=true


cat conf/shard21.conf
dbpath=/usr/local/mongodb/data/shard21
logpath=/usr/local/mongodb/log/shard21.log
pidfilepath=/usr/local/mongodb/pid/shard21.pid
directoryperdb=true
logappend=true
replSet=shard2
port=10021
fork=true
shardsvr=true
journal=true

cat conf/config.conf
dbpath=/usr/local/mongodb/data/config
logpath=/usr/local/mongodb/log/config.log
pidfilepath=/usr/local/mongodb/pid/config.pid
directoryperdb=true
logappend=true
port=10031
fork=true
configsvr=true
replSet=configRS
journal=true

cat conf/route.conf
configdb=configRS/192.168.1.5:10031,192.168.1.6:10031,192.168.1.2:10031
pidfilepath=/usr/local/mongodb/pid/route.pid
port=10040
logpath=/usr/local/mongodb/log/route.log
logappend=true
fork=true

在每一台服务器分别启动配置服务器
./bin/mongod -f conf/config.conf

连接到任意一台配置服务器上
./bin/mongo --port 10031 --host 127.0.0.1
创建配置服务器副本集    host为其他服务器的 config角色
rs.initiate({_id:"configRS",configsvr:true,members:[{_id:0,host:"192.168.1.5:10031"},
{_id:1,host:"192.168.1.6:10031"},{_id:2,host:"192.168.1.2:10031"}]})

在每一台服务器分别启动分片及副本集   可以有多个shard分片
./bin/mongod -f conf/shard11.conf 
./bin/mongod -f conf/shard21.conf

连接任意一台分片服务器
shard1
./bin/mongo --port 10011 --host 127.0.0.1
运行  rs.initiate({_id:"shard1",members:[{_id:0,host:"192.168.1.5:10011"},{_id:1,host:"192.168.1.6:10011"},
{_id:2,host:"192.168.1.2:10011"}]})    arbiterOnly:true 参数为角色是仲裁节点

shard2
./bin/mongo --port 10021 --host 127.0.0.1
运行 rs.initiate({_id:"shard2",members:[{_id:0,host:"192.168.1.5:10021"},{_id:1,host:"192.168.1.6:10021"},
{_id:2,host:"192.168.1.2:10021"}]})


在每一台服务器分别启动路由服务 
./bin/mongos -f conf/route.conf
./bin/mongos  --host 127.0.0.1--port 10040
use admin
db.runCommand({addshard:"shard1/192.168.1.5:10011,192.168.1.6:10011,192.168.1.2:10011"})
db.runCommand({addshard:"shard2/192.168.1.5:10021,192.168.1.6:10021,192.168.1.2:10021"})
db.runCommand({ listshards:1 })  查看配置是否生效(仲裁不被列出 )
db.runCommand({enablesharding:"friends"});   # friends 库开启shard
db.runCommand( { shardcollection : "friends.user",key : {id: 1},unique : true } )  # user 表来做分片,
片键为 id 且唯一  #1个分片 保存了1条，另一个分片保存了剩下的所有记录
db.runCommand( { shardcollection : "friends.user",key : {id: "hashed"} } )        #保证数据分布均衡

插入数据测试
use runoob  建立库
db.runoob.insert({"name":"菜鸟教程"})
show dbs
db.runoob.find();  列出数据

rs.status()  shard config 执行
db.status()  route执行
```



## mongo命令
```
以下实例我们创建了数据库 runoob:
> use runoob
switched to db runoob
> db
runoob
>
如果你想查看所有数据库，可以使用 show dbs 命令：
> show dbs
local  0.078GB
test   0.078GB
>
可以看到，我们刚创建的数据库 runoob 并不在数据库的列表中， 要显示它，我们需要向 runoob 数据库插入一些数据。
> db.collection.insert({"name":"菜鸟教程"})       collection集合插入数据
WriteResult({ "nInserted" : 1 })
> show dbs
local   0.078GB
runoob  0.078GB
test    0.078GB
>
MongoDB 中默认的数据库为 test，如果你没有创建新的数据库，集合将存放在 test 数据库中。


导入导出
dos2unix e_client_order.json
sed 's/},/}\n/g' e_client_order.json  > 1.json
./bin/mongoimport --db weituofang --collection lecture --file 1.json --port 10040


./bin/mongoexport -d weituofang -c yinghui1 -o yinghui1.json --port 10040
```



## 缩减shard集群
```
MongoDB中缩减Shard集群(删除一个Shard)--删除一个分片
关键字：MongoDB中缩减Shard集群(删除一个Shard)--删除一个分片

对MongoDB的Shard集群来说，添加一个分片很简单，AddShard就可以了。

但是缩减集群(删除分片)这种一般很少用到。由于某服务器挂了，所以想送修之前必须把它上面的数据自动迁移到其他Shard上。

以下内容翻译自：http://docs.mongodb.org/manual/tutorial/remove-shards-from-cluster/

1、执行RemoveShard命令
db.runCommand( { removeshard: "your_shard_name" } ) 
{ msg : "draining started successfully" , state: "started" , shard :"mongodb0" , ok : 1 } 
“注意：该命令至少执行两次才能成功删除，执行到state为completed才真正删除，否则就是没用删除成功，
该分片处于"draining" : true状态，该状态下不但该分片没用删除成功，而且还影响接下来删除其他分片操作，
遇到该状态再执行一次removeshard即可，最好就是删除分片时一直重复执行删除命令，直到state为completed；

还有一个需要注意的地方就是：被成功删除的分片如果想要再加入集群时，必须将data数据目录清理干净才可以再加入集群，
否则即使能加入成功也不会存储数据，集合都不会被创建

另外：在删除分片的时有可能整个过程出现无限"draining" : true状态，等多久还是这样，而且分片上面的块一个
都没有移动到别的分片，解决办法是：在config的config数据库的shard集合中找到该分片的信息，并将draining字段
由True改为False,再继续试着删除操作”

上面这句会立即返回，实际在后台执行。

2、查看迁移状态
我们可以反复执行上面语句，查看执行结果。
db.runCommand( { removeshard: "your_shard_name" } ) { msg: "draining ongoing" , 
state: "ongoing" , remaining: { chunks: 42, dbs : 1 }, ok: 1 }
从上面可以看到，正在迁移，还剩下42块没迁移完。
当remain为0之后，这一步就结束了。

3、移出非Shard数据（如果开始就知道是primary可以直接执行 步骤3和4即可，1和2不需要执行）
如果你要删除的Shard分片恰好是primary，那么执行这一步，否则请跳过！
db.runCommand( { movePrimary: "数据库名称", to: "分片名称" })

这次就不是立即返回了，需要很久，然后会返回如下：
{ "primary" : "mongodb1", "ok" : 1 }

4、最后的清理
上面步骤都完成后，还需要再执行一次RemoveShard，清理残余数据。
db.runCommand( { removeshard: "mongodb0" } )
执行成功后，会如下结果：
{ msg: "remove shard completed succesfully" , stage: "completed", host: "mongodb0", ok : 1 }

显示completed后，就可以安心的关闭mongod的进程了。
来源： http://www.myexception.cn/go/1862417.html
```



## web管理mongo
```
https://github.com/iwind/rockmongo

安装lamp
和  yum install php-pecl-mongo
cd /var/ww/html
下载解压  https://github.com/iwind/rockmongo/archive/master.zip

vim rockmongo-master/config.php  修改连接的mongo

访问 http://ip/rockmongo-master/index.php
```



