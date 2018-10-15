## hadoop性能测试
```
测试hdfs写
hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.7.0-tests.jar  TestDFSIO  
-write -nrFiles 10 -fileSize 1000
测试hdfs读
hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.7.0-tests.jar  TestDFSIO  
-read -nrFiles 10 -fileSize 1000
清理数据
hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.7.0-tests.jar  TestDFSIO  -clean

Total MBytes processed ： 总共需要写入的数据量 100MB
Throughput mb/sec ：总共需要写入的数据量/（每个map任务实际写入数据的执行时间之和（这个时间会远小于
Test exec time sec））＝＝》100/(map1写时间+map2写时间+...)
Average IO rate mb/sec ：（每个map需要写入的数据量/每个map任务实际写入数据的执行时间）之和/任务数
＝＝》(20/map1写时间＋20/map2写时间+...)/1000，所以这个值跟上面一个值总是存在差异。
IO rate std deviation ：上一个值的标准差
Test exec time sec ：整个job的执行时间


mapreduces测试
hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-client-jobclient-2.7.0-tests.jar mrbench 
-baseDir /tmp/mrbench -maps 100 -reduces 100 -numRuns 1
```



## spark变量
```
spark-2.0.1/conf/spark-env.sh

SPARK_WORKER_MEMORY=6g
SPARK_WORKER_CORES=8
SPARK_SSH_OPTS="-p 27005"
export JAVA_HOME="/usr/java/jre1.8.0_121/"
```



## 双namenode ha
```
http://blog.csdn.net/carl810224/article/details/52160418
http://blog.leanote.com/post/lh1649896772@163.com/Hadoop
%E4%BC%AA%E5%88%86%E5%B8%83%E5%BC%8F%E9%9B%86%E7%BE%A4%E6%90%AD%E5%BB%BA%EF%BC%88%E6%B5%8B%E8%AF%95%EF%BC%89



Hadoop0           JDK/Zookeeper/Hadoop   namenode/zkfc/journalnode/resourcemanager/QuoqumPeerMain
Hadoop1          JDK/Zookeeper/Hadoop                      namenode/zkfc/journalnode/resourcemanager/QuoqumPeerMain
Hadoop2        JDK/Zookeeper/Hadoop
datanode//journalnode/nodemanager/QuoqumPeerMain

wget http://mirrors.aliyun.com/apache/zookeeper/zookeeper-3.4.6/zookeeper-3.4.6.tar.gz
cd zookeeper-3.4.6/
cp conf/zoo_sample.cfg  conf/zoo.cfg
vim conf/zoo.cfg
tickTime=2000   //客户端心跳时间（毫秒）
initLimit=10     //循序心跳间隔的最大时间
syncLimit=5     //同步时限
dataDir=/usr/local/zookeeper-3.4.6/data   //数据存储目录
dataLogDir=/usr/local/zookeeper-3.4.6/data/log   //数据日志存储目录
clientPort=2181     //端口号
maxClientCnxns=2000    //连接zookeeper的最大数量
server.1=hadoop0:2888:3888     //设置zookeeper的节点
server.2=hadoop1:2888:3888
server.3=hadoop2:2888:3888

mkdir -p data/log
echo '1' > data/myid  其它两个节点后分别修改内容为2和3，以此类推
启动命令  ./bin/zkServer.sh start

修改hadoop配置文件
cd hadoop-2.7.0/etc/hadoop/
vim hadoop-env.sh
按如下内容进行配置（具体配置情况需按照生产环境和条件进行配置）:
export JAVA_HOME=/home/hadoop/apache/jdk1.8.0_101    //设置jdk路径
export HADOOP_SSH_OPTS="-p 27005"   ssh端口
export HADOOP_HEAPSIZE=1024      //设置Hadoop位置文本的大小
export HADOOP_NAMENODE_OPTS="-Xmx1024m
-Dhadoop.security.logger=${HADOOP_SECURITY_LOGGER:-INFO,RFAS}
-Dhdfs.audit.logger=${HDFS_AUDIT_LOGGER:-INFO,NullAppender} $HADOOP_NAMENODE_OPTS"     
//设置Namenode内存大小，此处根据实际情况设定其大小
export HADOOP_DATANODE_OPTS="-Xmx1024m
-Dhadoop.security.logger=ERROR,RFAS $HADOOP_DATANODE_OPTS   //设置Datanode内存大小
export HADOOP_PORTMAP_OPTS="-Xmx1024m $HADOOP_PORTMAP_OPTS"   //修改至1024m

指定slaves
vi etc/hadoop/slaves
hadoop1
hadoop2

配置core-site.xml:
vim core-site.xml
<configuration>
  <!-- 指定hdfs的nameservices名称为mycluster，与hdfs-site.xml的HA配
置相同 -->
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://mycluster</value>
  </property>
<!-- 设置zookeeper集群的配置和端口 -->
  <property>
    <name>ha.zookeeper.quorum</name>
    <value> hadoop0:2181,hadoop1:2181,hadoop2:2181</value>
  </property>
  指定缓存文件存储的路径和大小（可以设置的大一些，单位：字节）
  <property>
    <name>hadoop.tmp.dir</name>
    <value> /usr/local/hadoop-2.7.0/tmp</value>
  </property>
  <property>
    <name>io.file.buffer.size</name>
    <value>131072</value>
  </property>
  <!-- 配置hdfs文件被永久删除前保留的时间（单位：分钟），默认值为0，表明垃圾回收站功能关闭 -->
  <property>
    <name>fs.trash.interval</name>
    <value>10080</value>
  </property>
</configuration>

配置hdfs-site.xml:
vim hdfs-site.xml
<configuration>
<!-- 数据备份的个数 -->
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
<!-- 关闭权限验证 -->
  <property>
    <name>dfs.permissions.enabled</name>
    <value>false</value>
  </property>
<!-- 开启WebHDFS功能（基于REST的接口服务） -->
  <property>
    <name>dfs.webhdfs.enabled</name>
    <value>true</value>
  </property>
 <!-- //////////////以下为HDFS HA的配置////////////// -->
  <!-- 指定hdfs的nameservices名称为mycluster -->
  <property>
    <name>dfs.nameservices</name>
    <value>mycluster</value>
  </property>
<!-- 指定mycluster的两个namenode的名称分别为nn1,nn2 -->
  <property>
    <name>dfs.ha.namenodes.mycluster</name>
    <value>nn1,nn2</value>
  </property>
 <!-- 配置nn1,nn2的rpc通信端口 -->
  <property>
    <name>dfs.namenode.rpc-address.mycluster.nn1</name>
    <value> hadoop0:8020</value>
  </property>
  <property>
    <name>dfs.namenode.rpc-address.mycluster.nn2</name>
    <value> hadoop1:8020</value>
  </property>
  <!-- 配置nn1,nn2的http通信端口 -->
  <property>
    <name>dfs.namenode.http-address.mycluster.nn1</name>
    <value>hadoop0:50070</value>
  </property>
  <property>
    <name>dfs.namenode.http-address.mycluster.nn2</name>
    <value>hadoop1:50070</value>
  </property>
  <!-- 指定namenode元数据存储在journalnode中的路径,至少3个journalnode-->
  <property>
    <name>dfs.namenode.shared.edits.dir</name>
    <value> qjournal://hadoop0:8485;hadoop1:8485;hadoop2:8485/mycluster</value>
  </property>
  <!-- 指定HDFS客户端连接active namenode的java类 -->
  <property>
    <name>dfs.client.failover.proxy.provider.mycluster</name>
  <value>org.apache.hadoop.hdfs.server.namenode.ha.ConfiguredFailoverProxyProvider</value>
  </property>
  <!-- 配置隔离机制为ssh -->
  <property>
    <name>dfs.ha.fencing.methods</name>
    <value>sshfence(spark:27005)</value>    用户名和ssh端口
  </property>
  <!-- 指定秘钥的位置 -->
  <property>
    <name>dfs.ha.fencing.ssh.private-key-files</name>
    <value>/root/.ssh/id_dsa</value>
  </property>
  <!-- 指定journalnode日志文件存储的路径 -->
  <property>
    <name>dfs.journalnode.edits.dir</name>
    <value>/usr/local/hadoop-2.7.0/tmp/journal</value>
  </property>
  <!-- 开启自动故障转移 -->
  <property>
    <name>dfs.ha.automatic-failover.enabled</name>
    <value>true</value>
  </property>
</configuration>

配置mapred-site.xml:
cp mapred-site.xml.template mapred-site.xml
vim mapred-site.xml
<configuration>
  <!-- 指定MapReduce计算框架使用YARN -->
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
  <!-- 指定jobhistory server的rpc地址 -->
  <property>
    <name>mapreduce.jobhistory.address</name>
    <value>hadoop0:10020</value>
  </property>
  <!-- 指定jobhistory server的http地址 -->
  <property>
    <name>mapreduce.jobhistory.webapp.address</name>
    <value>hadoop0:19888</value>
  </property>
  <!-- 开启uber模式（针对小作业的优化） -->
  <property>
    <name>mapreduce.job.ubertask.enable</name>
    <value>true</value>
  </property>
  <!-- 配置启动uber模式的最大map数 -->
  <property>
    <name>mapreduce.job.ubertask.maxmaps</name>
    <value>3</value>
  </property>
  <!-- 配置启动uber模式的最大reduce数 -->
  <property>
    <name>mapreduce.job.ubertask.maxreduces</name>
    <value>1</value>
  </property>
</configuration>

配置yarn-site.xml文件:
vim yarn-site.xml
<configuration>
NodeManager上运行的附属服务，需配置成mapreduce_shuffle才可运行MapReduce程序
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <!-- 配置Web Application Proxy安全代理（防止yarn被攻击） -->
  <property>
    <name>yarn.web-proxy.address</name>
    <value>hadoop1:8888</value>
  </property>
  <!-- 开启日志 -->
  <property>
    <name>yarn.log-aggregation-enable</name>
    <value>true</value>
  </property>
  <!-- 配置nodemanager可用的资源内存 -->
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>4096</value>
  </property>
  <!-- 配置nodemanager可用的资源CPU -->
  <property>
    <name>yarn.nodemanager.resource.cpu-vcores</name>
    <value>4</value>
  </property>
  <!-- //////////////以下为YARN HA的配置////////////// -->
  <!-- 开启YARN HA -->
  <property>
    <name>yarn.resourcemanager.ha.enabled</name>
    <value>true</value>
  </property>
  <!-- 启用自动故障转移 -->
  <property>
    <name>yarn.resourcemanager.ha.automatic-failover.enabled</name>
    <value>true</value>
  </property>
  <!-- 指定YARN HA的名称 -->
  <property>
    <name>yarn.resourcemanager.cluster-id</name>
    <value>yarncluster</value>
  </property>
  <!-- 指定两个resourcemanager的名称 -->
  <property>
    <name>yarn.resourcemanager.ha.rm-ids</name>
    <value>rm1,rm2</value>
  </property>
  <!-- 配置rm1，rm2的主机 -->
  <property>
    <name>yarn.resourcemanager.hostname.rm1</name>
    <value>hadoop0</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname.rm2</name>
    <value>hadoop1</value>
  </property>

  <!-- 配置YARN的http端口 -->
  <property>
    <name>yarn.resourcemanager.webapp.address.rm1</name>
    <value>hadoop0:8088</value>
  </property>
  <property>
    <name>yarn.resourcemanager.webapp.address.rm2</name>
    <value>hadoop1:8088</value>
  </property>
  <!-- 配置zookeeper的地址 -->
  <property>
    <name>yarn.resourcemanager.zk-address</name>
    <value>hadoop0:2181</value>
  </property>
  <!-- 配置zookeeper的存储位置 -->
  <property>
    <name>yarn.resourcemanager.zk-state-store.parent-path</name>
    <value>/rmstore</value>
  </property>
  <!-- 开启yarn resourcemanager restart -->
  <property>
    <name>yarn.resourcemanager.recovery.enabled</name>
    <value>true</value>
  </property>
  <!-- 配置resourcemanager的状态存储到zookeeper中 -->
  <property>
    <name>yarn.resourcemanager.store.class</name>
    <value>org.apache.hadoop.yarn.server.resourcemanager.recovery.ZKRMStateStore</value>
  </property>
  <!-- 开启yarn nodemanager restart -->
  <property>
    <name>yarn.nodemanager.recovery.enabled</name>
    <value>true</value>
  </property>
  <!-- 配置nodemanager IPC的通信端口 -->
  <property>
    <name>yarn.nodemanager.address</name>
    <value>0.0.0.0:45454</value>
  </property>
</configuration>

Hadoop集群初始化
zookeeper
echo 1 > /usr/local/zookeeper-3.4.6/data/myid
echo 2 > /usr/local/zookeeper-3.4.6/data/myid
echo 3 > /usr/local/zookeeper-3.4.6/data/myid

在所有节点上启动zookeeper集群：cd /usr/local/zookeeper-3.4.6/ && ./bin/zkServer.sh start
            查看zookeeper状态:  ./bin/zkServer.sh status

在hadoop0上格式化zkfc：     ./bin/hdfs zkfc -formatZK
在所有节点上启动journalnode：./sbin/hadoop-daemon.sh start journalnode

在Hadoop0 格式化hdfs   ./bin/hdfs namenode -format
将格式化后hadoop0节点nameode元数据目录复制到hadoop1节点
scp -r tmp/dfs hadoop1:/usr/local/hadoop-2.7.0/tmp/

启动hadoop集群
先每个节点ssh一般，接受key
在hadoop0启动dfs：./sbin/start-dfs.sh
会开启以下进程：
namenode                              (hadoop0,hadoop1)
journalnode                            (hadoop0,hadoop1,hadoop2)
DFSZKFailoverController                             (hadoop0,hadoop1)
datanode                                (hadoop1,hadoop2)  slave文件指定的

在hadoop1启动YARN  ./sbin/start-yarn.sh
执行后在hadoop1启动ResourceManager  (hadoop1,hadoop2) 启动NodeManager

在hadoop0启动容灾的ResourceManager  ./sbin/yarn-daemon.sh start resourcemanager

在hadoop1启动YARN的安全代理
yarn-daemon.sh start proxyserver
注：proxyserver充当防火墙的角色，提高访问集群的安全性

在hadoop0启动YARN的历史任务 ./sbin/mr-jobhistory-daemon.sh start historyserver
查看namenode状态  http://hadoop0:50070     http://hadoop1:50070
```



## 测试例子
```
测试wordcount
vi a.txt
hello you
hello me
 
cd /usr/local/hadoop-2.7.0/
./bin/hdfs dfs -put a.txt /
./bin/hdfs dfs -rm -r /out/   删除之前的结果 
./bin/hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.0.jar wordcount /a.txt /out
./bin/hdfs dfs -text /out/part-r-00000  查看结果
```



## hadoop安装
```
真实服务器hadoop集群所有需要配置ssh互信
ssh-keygen -t rsa
ssh-copy-id -i .ssh/id_rsa.pub '-p 27005 root@192.168.3.129'
 
 
需要先构建一个hadoop的基础镜像，使用dockerfile文件方式进行构建。
先构建一个具备ssh功能的镜像，方便后期使用。（但是这样对于容器的安全性会有影响）
注意：这个镜像中的root用户的密码是root
#http://mirrors.aliyun.com/apache/hadoop/core/hadoop-2.7.0/hadoop-2.7.0.tar.gz
 
FROM daocloud.io/centos:6
EXPOSE 22
ENV JAVA_HOME /usr/lib/jvm/jre-1.8.0-openjdk.x86_64/
ADD epel-6.repo /etc/yum.repos.d/epel.repo
RUN yum install supervisor java-1.8.0-openjdk openssh-server openssh-clients rsync -y
RUN sed -i 's/UsePAM yes/UsePAM no/g' /etc/ssh/sshd_config
RUN ssh-keygen -t dsa -f /etc/ssh/ssh_host_dsa_key
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN ssh-keygen -t dsa -P '' -f ~/.ssh/id_dsa
RUN cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys
RUN echo "root:root" | chpasswd
COPY supervisord.conf /etc/supervisord.conf
ADD hadoop-2.7.0.tar.gz /usr/local/
CMD ["/usr/bin/supervisord"]
 
supervisord.conf关键配置
[supervisord]
nodaemon=true   前台模式
[program:sshd]
command=/usr/sbin/sshd –D
 
 
准备搭建一个具有三个节点的集群，一主两从
主节点：hadoop0 ip：192.168.2.10
从节点1：hadoop1 ip：192.168.2.11
从节点2：hadoop2 ip：192.168.2.12
 
vi /etc/hosts
172.17.0.119    hadoop0
172.17.0.120    hadoop1
172.17.0.121    hadoop2
 
修改hadoop配置
进入到 etc/hadoop目录
指定slaves
vi etc/hadoop/slaves
hadoop1
hadoop2
 
修改目录下的配置文件core-site.xml、hdfs-site.xml、yarn-site.xml、mapred-site.xml
(1)hadoop-env.sh
export JAVA_HOME=/usr/lib/jvm/jre-1.8.0-openjdk.x86_64/
 
(2)core-site.xml
<configuration>
        <property>
                <name>fs.defaultFS</name>
                <value>hdfs://hadoop0:9000</value>
        </property>
        <property>
                <name>hadoop.tmp.dir</name>
                <value>/usr/local/hadoop/tmp</value>
        </property>
         <property>
                 <name>fs.trash.interval</name>
                 <value>1440</value>
        </property>
</configuration>
 
(3)hdfs-site.xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
    <property>
        <name>dfs.permissions</name>
        <value>false</value>
    </property>
</configuration>
 
(4)yarn-site.xml
<configuration>
        <property>
                <name>yarn.nodemanager.aux-services</name>
                <value>mapreduce_shuffle</value>
        </property>
        <property>
                <name>yarn.log-aggregation-enable</name>
                <value>true</value>
        </property>
</configuration>
 
(5)修改文件名：cp mapred-site.xml.template mapred-site.xml
vi mapred-site.xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
 
(6)指定resourcemanager的地址，修改文件yarn-site.xml
<property>
    <description>The hostname of the RM.</description>
    <name>yarn.resourcemanager.hostname</name>
    <value>hadoop0</value>
  </property>
 
(7)格式化
进入到/usr/local/hadoop目录下
1、执行格式化命令
 
bin/hdfs namenode –format   会清空hdfs所有数据，第一次配置运行
注意：在执行的时候会报错，是因为缺少which命令，安装即可
 
执行下面命令安装
yum install -y which
 
格式化操作不能重复执行。如果一定要重复格式化，带参数-force即可。
(8)启动伪分布hadoop
命令：sbin/start-all.sh
第一次启动的过程中需要输入yes确认一下。
 
使用jps，检查进程是否正常启动？能看到下面几个进程表示伪分布启动成功
hadoop0
4643 Jps
4073 NameNode
4216 SecondaryNameNode
4381 ResourceManager
 
hadoop1
456 NodeManager
589 Jps
388 DataNode
 
(9)停止伪分布hadoop
命令：sbin/stop-all.sh
 
docker run -d --name hadoop0 --hostname hadoop0 -p 50070:50070 -p 8088:8088 hadoop:v3 /usr/bin/supervisord
docker run -d --name hadoop1 --hostname hadoop1 hadoop:v3 /usr/bin/supervisord
docker run -d --name hadoop2 --hostname hadoop2 hadoop:v3 /usr/bin/supervisord
```



## nativecodeloader警告
```
WARN util.NativeCodeLoader: Unable to load native-hadoop library for your platform.

直接在log4j日志中去除告警信息。在//usr/local/hadoop-2.5.2/etc/hadoop/log4j.properties文件中添加
log4j.logger.org.apache.hadoop.util.NativeCodeLoader=ERROR
```



## ambrai快速部署
```
Ambari是 Apache Software Foundation 中的一个顶级项目。Ambari可以创建、管理、监控 Hadoop 的集群。
包括整个Hadoop生态圈（例如 Hive，Hbase，Sqoop，Zookeeper 等）。无论是初学者像快速部署一套Hadoop环境，
还是用于生产的自动化部署，Ambari都可以满足。
     你可以在官网http://ambari.apache.org/获取最新的Ambari的内容，目前Ambari还支持流行的 Spark，Storm 
     等计算框架，Kafka消息队列、以及资源调度平台 YARN 等。
    Ambari 自身也是一个分布式架构的软件，主要由两部分组成：Ambari Server 和 Ambari Agent。我们可以通过 
    Ambari Server 通知 Ambari Agent 安装对应的软件；甚至连Ambari Agent我们都可以在Web界面上来进行安装和部署。
    Ambari Agent 会定时地发送各个机器每个项目组件的当前状态给 Ambari Server，并在Web界面上进行展示汇总，
    方面我们及时掌握集群状态。

基础环境准备
    本次实验环境还是使用两台虚拟机来实现，有条件的读者建议使用三台虚拟机来做。首先我们要实现
    Ambari Server到各个节点之间的SSH无密码登录。
在所有节点都执行ssh-keygen -t rsa 生成Key
[root@linux-node1 ~]# ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/root/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /root/.ssh/id_rsa.
Your public key has been saved in /root/.ssh/id_rsa.pub.
    虽然除了Server端之外其它节点可以不执行，但是ssh-keygen命令会帮我们创建相应的目录并设置权限，不在需要我们手动操作。

将Ambari Server的公钥scp到其它节点上
[root@linux-node1 ~]# scp .ssh/id_rsa.pub 192.168.56.12:/root/.ssh/authorized_keys
设置权限
[root@linux-node2 ~]# chmod 600 ~/.ssh/authorized_keys
测试连接
[root@linux-node1 ~]# ssh 192.168.56.12
Last login: Sat Apr  2 16:42:46 2016 from 192.168.56.1[root@linux-node2 ~]#
设置完毕无密码登录后，我们就可以开始部署ambari-server了。

安装jdk
    由于ambari安装过程中的jdk下载比较缓慢，所以我们可以直接使用yum仓库里面的openjdk
[root@linux-node1 ~]# yum install -y java-1.8.0
部署ambari-server
    ambari-server的部署比较简单，很多实用实用默认即是最好的选择。
安装ambari-server
[root@test-node3 ~]# cd /etc/yum.repos.d/
# wget http://public-repo-1.hortonwor ... .repo# yum install -y ambari-server

注意：在国内的用户要有心里准备，ambari-server这个包有354M，下载比较慢。

设置ambari-server

    安装完毕后，需要使用ambari-server setup命令进行设置，均可以使用默认设置，直接回车即可。
[root@linux-node1 ~]# ambari-server setup
Using python  /usr/bin/python2
Setup ambari-server
Checking SELinux...
SELinux status is 'disabled'
Customize user account for ambari-server daemon [y/n] (n)? 
Adjusting ambari-server permissions and ownership...
Checking firewall status...
Redirecting to /bin/systemctl status  iptables.service

Checking JDK...[1] Oracle JDK 1.8 + Java Cryptography Extension (JCE) Policy Files 8[2] Oracle JDK 1.7 
+ Java Cryptography Extension (JCE) Policy Files 7[3] Custom JDK
===========================================================================
Enter choice (1): 3
WARNING: JDK must be installed on all hosts and JAVA_HOME must be valid on all hosts.
WARNING: JCE Policy files are required for configuring Kerberos security. If you plan to use Kerberos,
please make sure JCE Unlimited Strength Jurisdiction Policy Files are valid on all hosts.
Path to JAVA_HOME: /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.77-0.b03.el7_2.x86_64/jre/
Validating JDK on Ambari Server...done.
Completing setup...
Configuring database...
Enter advanced database configuration [y/n] (n)?
Configuring database...
Default properties detected. Using built-in database.
Configuring ambari database...
Checking PostgreSQL...
Running initdb: This may take upto a minute.
Initializing database ... OK
About to start PostgreSQL
Configuring local database...
Connecting to local database...done.
Configuring PostgreSQL...
Restarting PostgreSQL
Extracting system views...
ambari-admin-2.2.0.0.1310.jar
......
Adjusting ambari-server permissions and ownership...
Ambari Server 'setup' completed successfully.

1)    检测SELinux2)    询问是否自定义用户，默认否-（可以安装完毕之后再进行用户管理。）3)    检测iptables选择JDK版本，
默认Oracle JDK 1.8。如果你已经安装了jdk，可以选择自定义jdk。如果你是yum安装的openjdk，那么路径位于
/usr/lib/jvm/java-1.8.0-openjdk-xxx.x86_64/jre/4)    目录下。5)    询问是否打开高级的数据库配置，默认-否

启动ambari-server
[root@linux-node1 ~]# ambari-server start
查看监听端口
[root@linux-node1 ~]# netstat -ntlp | grep 8080
tcp6       0      0 :::8080                 :::*                    LISTEN      24168/java

访问ambari server

现在可以在浏览器访问你的ambari server了。注意端口是8080。
http://192.168.56.11:8080/

默认的用户名和密码都是admin


创建Hadoop集群

登录 Ambari 之后，点击按钮“Launch Install Wizard”，就可以开始创建属于自己的大数据平台。
```



