## 时区问题
```
docker run -d  -v /etc/localtime:/etc/localtime:ro -v /etc/sysconfig/clock:/etc/sysconfig/clock:ro

挂在宿主机的时区文件

由于共享内核，无法单独修改docker容器的时间
```



## 命令
```
yum install docker
systemctl start docker

docker run -d --hostname wwwtest --name wwwtest -p 28080:8080 
--add-host=mlivetest.dachuizichan.com:127.0.0.1 
--add-host=db.dachuizichan.com:192.168.1.18 
--add-host=atlastest.dachuizichan.com:192.168.1.16 
--add-host=hprpt2livetest.eucp.b2m.cn:127.0.0.1 
--add-host=smtplivetest.exmail.qq.com:183.232.93.197 
--add-host=redis.dachuizichan.com:172.17.0.168 -v /dachui:/dachui 
-v /tomcat/war/wwwtest:/usr/local/tomcat/webapps/DaChui -v 
/tomcat/log/wwwtest:/usr/local/tomcat/log 
-v /etc/localtime:/etc/localtime:ro -v /etc/sysconfig/clock:/etc/sysconfig/clock:ro 
tomcat:v6 /usr/bin/supervisord

镜像
docker pull centos6.6  拉取镜像
docker images         查看镜像
docker save -o ubuntu_14.04.tar ubuntu:14.04      存出镜像
docker load --input ubuntu_14.04.tar                 载入镜像
docker commit  0b2616b0e5a8 ouruser 提交镜像
docker rmi training/sinatra        移除本地镜像

实例
docker run -t -i -p 8000:80 centos6.6 /bin/bash  运行实例，映射端口
docker ps   查看实例
docekr status id  实例状态
docker stop  id 停止实例
docker restart id  重启实例
docker rm -f id  删除实例
docker export 7691a814370e > ubuntu.tar  导出实例
cat ubuntu.tar | sudo docker import - test/ubuntu:v1.0  倒入实例

docker logs -f --tail=10 wwwtest  查看日志  
#ENTRYPOINT ["/usr/local/tomcat/bin/catalina.sh", "run"]  类似这种把日志打印到前台

慎用
Delete all containers

docker rm $(docker ps -a -q)
Delete all images

docker rmi $(docker images -q)
```



## docker-regisrty
```
yum install -y python-devel libevent-devel python-pip gcc xz-devel  swig openssl-devel
pip install docker-registry
cd /usr/lib/python2.6/site-packages/config
cp config_sample.yml config.yml

存储位置 /tmp/registry
启动：
gunicorn -b 0.0.0.0:5000  docker_registry.wsgi:application
or
gunicorn --access-logfile - --error-logfile - -k gevent -b 0.0.0.0:5000 -w 4 
--max-requests 
100 docker_registry.wsgi:application

docker tag a4e2366f858c 192.168.10.49:5000/pingtai-0508  a4e2366f858c 为imageid



注意 需要https验证：修改/etc/sysconfig/docker
 增加：
DOCKER_OPTS="--insecure-registry 192.168.10.49:5000"
  将 $exec -d $other_args &>> $logfile &改成$exec -d $DOCKER_OPTS &>> $logfile &
  重新启动docker，再次push就OK了
  service docker restart
```



## dockerfile
```
FROM ubuntu:trusty

ENV DEBIAN_FRONTEND noninteractive
ENV PATH $PATH:/usr/local/nginx/sbin

EXPOSE 1935
EXPOSE 80

# create directories
RUN mkdir /src /config /logs /data /static

# update and upgrade packages
RUN apt-get update && \
  apt-get upgrade -y && \
  apt-get clean && \
  apt-get install -y --no-install-recommends build-essential \
  wget software-properties-common && \
# ffmpeg
  add-apt-repository ppa:mc3man/trusty-media && \
  apt-get update && \
  apt-get install -y --no-install-recommends ffmpeg && \
# nginx dependencies
  apt-get install -y --no-install-recommends libpcre3-dev \
  zlib1g-dev libssl-dev wget && \
  rm -rf /var/lib/apt/lists/*

# get nginx source
WORKDIR /src
RUN wget http://nginx.org/download/nginx-1.6.2.tar.gz && \
  tar zxf nginx-1.6.2.tar.gz && \
  rm nginx-1.6.2.tar.gz && \
# get nginx-rtmp module
  wget https://github.com/arut/nginx-rtmp-module/archive/v1.1.6.tar.gz && \
  tar zxf v1.1.6.tar.gz && \
  rm v1.1.6.tar.gz

# compile nginx
WORKDIR /src/nginx-1.6.2
RUN ./configure --add-module=/src/nginx-rtmp-module-1.1.6 \
  --conf-path=/config/nginx.conf \
  --error-log-path=/logs/error.log \
  --http-log-path=/logs/access.log && \
  make && \
  make install

ADD nginx.conf /config/nginx.conf
ADD static /static

WORKDIR /
CMD "nginx"
```



## 国内镜像
```
docker pull daocloud.io/centos:6
docker pull daocloud.io/centos:7

docker run -ti daocloud.io/centos:6 /bin/bash  拉取images并运行

https://dashboard.daocloud.io/packages
```



## centos6安装
```
CentOS 6.5(64位)及以后
在运行CentOS 6.5及以后版本时，需要内核版本>=2.6.32-431，因为这些内核包含了运行Docker
的一些特定修改。
$ uname -r
2.6.32-431.17.1.el6.x86_64


Device Mapper
Docker默认使用AUFS作为存储驱动，但是AUFS并没有被包括在Linux的主线内核中。CentOS中可以
使用Device Mapper作为存储驱动，
这是在2.6.9内核版本引入的新功能。我们需要先确认是否启用该功能:

$ ls -l /sys/class/misc/device-mapper
lrwxrwxrwx 1 root root 0 May  1 20:55 /sys/class/misc/device-mapper -> 
../../devices/virtual/misc/device-mapper
如果没有检测到Device Mapper，需要安装device-mapper软件包:

$ sudo yum install -y device-mapper
然后重新加载dm_mod内核模块:

$ sudo modprobe dm_mod

配置epel源
需要注意的是，CentOS6.5中，已经有一个同名docker的可执行系统程序包。所以Docker RPM包
命名为docker-io，我们先卸掉docker。

$ sudo yum -y remove docker
第三步 Install Docker-IO
最后需要安装docker-io的RPM包。
$ sudo yum -y install docker-io
```



## harbor仓库
```
用过Docker的知道拥有一个Docker Registry是多么的重要，但是官方自带的免费的Docker Registry
除了没有管理页面，
甚至连一些运维必备的功能都是缺失的，所以一直在寻找一个Registry的管理工具，直到看到了Harbor。


Harbor简介

Harbor是一个用于存储和分发Docker镜像的企业级Registry服务器，通过添加一些企业必需的
功能特性，例如安全、标识和管理等，
扩展了开源Docker Distribution。作为一个企业级私有Registry服务器，Harbor提供了
更好的性能和安全。
提升用户使用Registry构建和运行环境传输镜像的效率。Harbor支持安装在多个Registry节点的
镜像资源复制，
镜像全部保存在私有Registry中，确保数据和知识产权在公司内部网络中管控。另外，Harbor也
提供了高级的安全特性，诸如用户管理，
访问控制和活动审计等。
Harbor官方网站：http://vmware.github.io/harbor/

Harbor部署实战

Harbor是由Vmware中国研发团队负责开发的开源企业级Docker Registry，不仅仅解决了我们直接使用
Docker Registry的功能确实，
更解决了我们在生产使用Docker Registry面临的高可用、镜像仓库直接复制、镜像仓库性能等运维痛点。
# cd /usr/local/
# git clone https://github.com/vmware/harbor

部署目录
    harbor部署的所有文件均在Deploy目录下
# cd harbor/Deploy/
# ls
config
db
docker-compose.yml #docker compose模板
docker-compose.yml.photon
harbor.cfg   #harbor配置文件
（省略部分输出） 
Harbor的每个组件都是以Docker容器的形式构建的，使用Docker Compose来对它进行部署。你可以查看
docker-compose.yml文件，
可以发现Harbor有6个容器组成：
harbor_ui：harbor的核心服务。
harbor_log：运行着rsyslog的容器，进行日志收集。
harbor_mysql：由官方mysql镜像构成的数据库容器
nginx：使用Nginx做反向代理
registry：官方的Docker registry
harbor_jobservice：Harbor的任务管理服务。

为Harbor配置https访问

    默认情况下Harbor是使用http进行访问，官方提供了自签名证书的方法，不过生产环境还是
    建议购买SSL证书。
1.配置证书
如果你没有SSL证书，那么也不要使用网上复杂的自签名证书的步骤了。可以来这里申请一个
免费的SSL证书。https://buy.wosign.com/free/#ssl
[root@mysql-yxpopoDeploy]# cd config/nginx/
将两个证书文件放置到cert目录下。
xxx.xxx.com.crt（证书公钥）
xxx.xxx.com.key（证书私钥）

2.修改Nginx配置文件
http://www.wosign.com/Docdownload/Nginx%20SSL%E8%AF%81%E4%B9%A6%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97.pdf

# cp nginx.https.conf nginx.conf
server {
    listen443 ssl;
   server_name registry.unixhot.com;
# SSL
    ssl_certificate/etc/nginx/cert/1_registry.unixhot.com_bundle.crt;
ssl_certificate_key/etc/nginx/cert/2_registry.unixhot.com.key;
ssl_protocols TLSv1.1 TLSv1.2;
   ssl_ciphersAESGCM:ALL:!DH:!EXPORT:!RC4:+HIGH:!MEDIUM:!LOW:!aNULL:!eNULL;
   ssl_prefer_server_ciphers on;
   ssl_session_cache shared:SSL:10m;
#配置访问80端口的请求，转到443端口
server {
      listen80;
     server_name registry.unixhot.com;
      rewrite^/(.*) https://$server_name:443/$1 permanent;
  }

#配置ACL，限制访问（如果你准备放置在外围，又想限制IP访问）
  allow127.0.0.1;
  allow192.168.0.0/16;
  deny all;

Harbor配置
Harbor的配置项比较少，在harbor.cfg里面。

[root@mysql-yxpopo Deploy]# vim harbor.cfg
hostname = registry.unixhot.com
ui_url_protocol = https
harbor_admin_password = unixhot.com

构建并启动Harbor
[root@mysql-yxpopo Deploy]# ./prepare
Generated configuration file: ./config/ui/env
Generated configuration file: ./config/ui/app.conf
Generated configuration file:./config/registry/config.yml
Generated configuration file: ./config/db/env
Generated configuration file:./config/jobservice/env
Clearing the configuration file:./config/ui/private_key.pem
Clearing the configuration file:./config/registry/root.crt
Generated configuration file:./config/ui/private_key.pem
Generated configuration file:./config/registry/root.crt
The configuration files are ready, please usedocker-compose to start the service.

使用DockerCompose启动服务
[root@mysql-yxpopo Deploy]# docker-compose up -d
现在你就可以访问https://xxx.xxx.com，打开Harbor的管理界面。使用默认的账号admin/你
设置的密码，进行登录。

登录后的第一件事情永远都是修改默认密码。然后你就可以在项目管理中，新建和管理项目了。
不过默认情况下创建的项目library是公开的，
如果你要使用这个项目，而且域名放在公网上，请取消公开。
现在，你就可以登录Harbor快乐的玩耍了。
# docker login registry.unixhot.com
Username: admin
Password:
Email: admin@unixhot.com
WARNING: login credentials saved in/root/.docker/config.json
Login Succeeded
```



## kubernetes
```
kubernetes

rc           replication controller
pod       pause
proxy
service
labels

master
node

etcd              存储

kube-apiserver
kube-scheduler
kube-controller-manager

kubelet
kube-proxy
docker


yum -y install kubernetes-1.2.0 docker-1.8.2 docker-selinux-1.8.2

lvs fullnat
nginx

docker logs
fluentd
glusterfs

hostPath
emptyDir

cAdvisor
heapster+influxdb+grafana
flannel  host-gw

calico      网络解决方案
fluentd     日志收集
nginx转发，使用Python实现rolling-update，并更新nginx配置
heapster    监控
calico    
环境    
kubernetes:    1.2.0
docker:        1.8.2
centos:        7.2.1503
calico:        0.20.0
Master安装    
yum -y install kubernetes-1.2.0
wget 
https://github.com/projectcalico/calico-containers/releases/download/v0.20.0/calicoctl
chmod +x calicoctl
mv calicoctl /usr/bin
docker pull calico/node:v0.20.0 
cat > /etc/network-environment << EOF
# This host's IPv4 address (the source IP address used to reach other nodes
# in the Kubernetes cluster).
DEFAULT_IPV4=<KUBERNETES_MASTER> 
# IP and port of etcd instance used by Calico
ETCD_AUTHORITY=<KUBERNETES_MASTER>:6666
EOF
wget -N -P /etc/systemd 
https://raw.githubusercontent.com/projectcalico/calico-cni/k8s-1.1-docs/samples/kub
ernetes/common/calico-node.service
systemctl enable /etc/systemd/calico-node.service
systemctl start calico-node.service
Node安装
wget 
https://github.com/projectcalico/calico-containers/releases/download/v0.20.0/calicoctl
chmod +x calicoctl
mv calicoctl /usr/bin
docker pull calico/node:v0.20.0
cat > /etc/network-environment << EOF
# This host's IPv4 address (the source IP address used to reach other nodes
# in the Kubernetes cluster).
DEFAULT_IPV4=<KUBERNETES_MASTER> 
# IP and port of etcd instance used by Calico
ETCD_AUTHORITY=<KUBERNETES_MASTER>:6666 
EOF
wget -N -P /etc/systemd 
https://raw.githubusercontent.com/projectcalico/calico-cni/k8s-1.1-docs/samples/kubernetes/co
mmon/calico-node.service
systemctl enable /etc/systemd/calico-node.service
systemctl start calico-node.service
mkdir -p /opt/cni/bin/
wget -N -P /opt/cni/bin/ https://github.com/projectcalico/calico-cni/releases/download/v1.0.0/calico
wget -N -P /opt/cni/bin/ https://github.com/projectcalico/calico-cni/releases/download/v1.0.0/calico-ipam
chmod +x /opt/cni/bin/calico /opt/cni/bin/calico-ipam
# Make the directory structure.
mkdir -p /etc/cni/net.d 
# Make the network configuration file 
cat >/etc/cni/net.d/10-calico.conf <<EOF
{
    "name": "calico-k8s-network",
    "type": "calico", 
    "etcd_authority": "<KUBERNETES_MASTER>:6666",
    "log_level": "info",
    "ipam": { 
       "type": "calico-ipam"
    } 
}
EOF
配置kubelet
vim /etc/kubernetes/kubelet
# Add your own!
KUBELET_ARGS="--network-plugin=cni --network-plugin-dir=/etc/cni/net.d"
calico配置访问外网 
[root@vm-docker-c7-80 ~]# calicoctl pool show
 +----------------+---------+
  |   IPv4 CIDR    | Options |
 +----------------+---------+
  | 192.168.0.0/16 |         |
 +----------------+---------+
 +--------------------------+---------+
  |        IPv6 CIDR         | Options |
 +--------------------------+---------+
  | fd80:24e2:f998:72d6::/64 |         |
 +--------------------------+---------+
 [root@vm-docker-c7-80 ~]# calicoctl pool add 192.168.0.0/16 --nat-outgoing
 [root@vm-docker-c7-80 ~]# calicoctl pool show
  +----------------+--------------+
   |   IPv4 CIDR    |   Options    |
  +----------------+--------------+
   | 192.168.0.0/16 | nat-outgoing |
  +----------------+--------------+
  +--------------------------+---------+
   |        IPv6 CIDR         | Options |
  +--------------------------+---------+
   | fd80:24e2:f998:72d6::/64 |         |
  +--------------------------+---------+
[root@vm-docker-c7-80 ~]# kubectl get pods
NAME      READY   STATUS    RESTARTSAGE
 test1     1/1       Running   0          3h
test2     1/1       Running   0          3h
[root@vm-docker-c7-80 ~]# kubectl exec -it test1 ping www.baidu.com
 PING www.baidu.com (61.135.169.125): 56 data bytes
64 bytes from 61.135.169.125: seq=0 ttl=54 time=2.535 ms
 64 bytes from 61.135.169.125: seq=1 ttl=54 time=2.309 ms
 ^C
 --- www.baidu.com ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
 round-trip min/avg/max = 2.309/2.422/2.535 ms

flannel 
环境： 
kubernetes      v1.2.0
flannel         0.5.3
centos          7.1
kernel          4.2.3
docker          1.8.2
安装：    
yum -y install flanneld etcd kubernetes
vim /etc/etcd/etcd.conf
ETCD_LISTEN_CLIENT_URLS="http://0.0.0.0:2379"
ETCD_ADVERTISE_CLIENT_URLS="http://0.0.0.0:2379" 
vim /etc/sysconfig/flanneld
FLANNEL_ETCD="http://127.0.0.1:2379"
FLANNEL_ETCD_KEY="/flannel/network"
FLANNEL_OPTIONS="-iface=br1"

设置flannel所提供的网段，并写入etcd：
etcdctl set /flanneld/network/config '{"Network": "10.0.0.0/22", "Backend": {"Type": “host-gw”}}’
```



## bashrc_docker
    wget -P ~ https://github.com/yeasy/docker_practice/raw/master/
    _local/.bashrc_docker;
    $ echo "[ -f ~/.bashrc_docker ] && . ~/.bashrc_docker" >> ~/.bashrc; source ~/.bashrc
    这个文件中定义了很多方便使用 Docker 的命令，例如  docker-pid  可以获取某
    个容器的 PID；而  docker-enter  可以进入容器或直接在容器内执行命令。

    cd /root/
    vim .bashrc_docker
    # Some useful commands to use docker.
    # Author: yeasy@github
    # Created:2014-09-25

    alias docker-pid="sudo docker inspect --format '{{.State.Pid}}'"
    alias docker-ip="sudo docker inspect --format '{{ .NetworkSettings.IPAddress }}'"

    #the implementation refs from https://github.com/jpetazzo/nsenter/blob/master/docker-enter
    function docker-enter() {
        #if [ -e $(dirname "$0")/nsenter ]; then
        #Change for centos bash running
        if [ -e $(dirname '$0')/nsenter ]; then
            # with boot2docker, nsenter is not in the PATH but it is in the same folder
            NSENTER=$(dirname "$0")/nsenter
        else
            # if nsenter has already been installed with path notified, here will be clarified
            NSENTER=$(which nsenter)
            #NSENTER=nsenter
        fi
        [ -z "$NSENTER" ] && echo "WARN Cannot find nsenter" && return

        if [ -z "$1" ]; then
            echo "Usage: `basename "$0"` CONTAINER [COMMAND [ARG]...]"
            echo ""
            echo "Enters the Docker CONTAINER and executes the specified COMMAND."
            echo "If COMMAND is not specified, runs an interactive shell in CONTAINER."
        else
            PID=$(sudo docker inspect --format "{{.State.Pid}}" "$1")
            if [ -z "$PID" ]; then
                echo "WARN Cannot find the given container"
                return
            fi
            shift

            OPTS="--target $PID --mount --uts --ipc --net --pid"

            if [ -z "$1" ]; then
                # No command given.
                # Use su to clear all host environment variables except for TERM,
                # initialize the environment variables HOME, SHELL, USER, LOGNAME, PATH,
                # and start a login shell.
                #sudo $NSENTER "$OPTS" su - root
                sudo $NSENTER --target $PID --mount --uts --ipc --net --pid su - root
            else
                # Use env to clear all host environment variables.
                sudo $NSENTER --target $PID --mount --uts --ipc --net --pid env -i $@
            fi
        fi
    }

    --------------------------------------------
    # 执行生效  echo "[ -f ~/.bashrc_docker ] && . ~/.bashrc_docker" >> ~/.bashrc; source ~/.bashrc

    #  docker ps
    #  docker-enter  id
    #  docker-pid id




## mesos_marathon
    Mesos：Mesos采用与Linux Kernel相同的机制，只是运行在不同的抽象层次上。Mesos Kernel利用资源管理和调度的API在整个数据
    中心或云环境中运行和提供引用（例如，Hadoop、Spark、Kafaka、ElasticSearch）。

        ZooKeeper：ZooKeeper是一个分布式的，开放源码的分布式应用程序协调服务，是Google的Chubby一个开源的实现，是Hadoop
        和HBase的重要组件。它是一个为分布式应用提供一致性服务的软件，提供的功能包括：配置维护、名字服务、分布式同步、组服务等。

        Marathon：Marathon是一个Mesos框架，能够支持运行长服务，比如Web应用等。它是集群的分布式Init.d，能够原样运行任何
        Linux二进制发布版本，如Tomcat、Play等等。它也是一种私有的PaSS，实现服务的发现，为部署提供提供REST API服务，有授权
        和SSL、配置约束，通过HAProxy实现服务发现和负载平衡。
     好的，架构图看起来像这样。
    无标题1.png


    下面我们就准备开始实战部署了。首先要说明下实验环境：

    index.png


    Zookeeper伪集群部署
    在部署mesos集群之前，我们必须先部署一个可用的zookeeper集群，后面mesos会连接到zookeeper上。
    [root@linux-node1 ~]# cd /usr/local/src
    [root@linux-node1 src]# wget http://mirrors.cnnic.cn/apache ... ar.gz
    [root@linux-node1 src]# tar zxf zookeeper-3.4.6.tar.gz
    [root@linux-node1 src]# mv zookeeper-3.4.6 /usr/local/zookeeper
    [root@linux-node1 src]# ln -s /usr/local/zookeeper-3.4.6/ /usr/local/zookeeper
    [root@linux-node1 ~]# cd /usr/local/zookeeper/conf/
    [root@linux-node1 conf]# mv zoo_sample.cfg zoo.cfg


    zookeeper配置文件详解

    下面就是zoo.cfg配置文件的修改了。那么我们首先要熟悉下zookeeper配置文件。

    [root@linux-node1 ~]# cat/usr/local/zookeeper/conf/zoo.cfg

    dataDir：数据目录
    dataLogDir：日志目录
    clientPort：客户端连接端口
    tickTime：Zookeeper 服务器之间或客户端与服务器之间维持心跳的时间间隔，也就是每个 tickTime 时间就会发送一个心跳。
    initLimit：Zookeeper的Leader 接受客户端（Follower）初始化连接时最长能忍受多少个心跳时间间隔数。当已经超过
     5个心跳的时间（也就是tickTime）长度后 Zookeeper 服务器还没有收到客户端的返回信息，那么表明这个客户端连接失败。
     总的时间长度就是 5*2000=10 秒
    syncLimit：表示 Leader 与 Follower 之间发送消息时请求和应答时间长度，最长不能超过多少个tickTime 的时间长度，
    总的时间长度就是 2*2000=4 秒。
    server.A=B：C：D：
    A 是一个数字，表示这个是第几号服务器；
    B 是这个服务器的 ip 地址；
    C 表示的是这个服务器与集群中的 Leader 服务器交换信息的端口；
    D 表示的是万一集群中的 Leader 服务器挂了，需要一个端口来重新进行选举，选出一个新的 Leader，而这个端口就是用来执行
    选举时服务器相互通信的端口。

    Zookeeper配置文件修改
        如果是伪集群的配置方式，由于 B 都是一样，所以不同的 Zookeeper 实例通信端口号不能一样，所以要给它们分配不同的端口号。
    [root@linux-node1 conf]# grep '^[a-z]' zoo.cfg
    tickTime=2000
    initLimit=10
    syncLimit=5
    dataDir=/data/zk1
    clientPort=2181
    server.1=192.168.56.11:3181:4181
    server.2=192.168.56.11:3182:4182
    server.3=192.168.56.11:3183:4183
    创建三个目录用来存放zookeeper数据
    [root@linux-node1 ~]# mkdir -p /data/zk1 /data/zk2/data/zk3
    [root@linux-node1 ~]# echo "1" >/data/zk1/myid
    [root@linux-node1 ~]# echo "2" >/data/zk2/myid
    [root@linux-node1 ~]# echo "3" >/data/zk3/myid
    生成三份zookeeper配置文件
    [root@linux-node1 conf]# cp zoo.cfg zk1.cfg
    [root@linux-node1 conf]# cp zoo.cfg zk2.cfg
    [root@linux-node1 conf]# cp zoo.cfg zk3.cfg
    修改zk2和zk3的配置，使用对应的数据目录和端口。
    [root@linux-node1 conf]# sed -i 's/zk1/zk2/g'zk2.cfg
    [root@linux-node1 conf]# sed -i 's/2181/2182/g'zk2.cfg
    [root@linux-node1 conf]# sed -i 's/zk1/zk3/g'zk3.cfg
    [root@linux-node1 conf]# sed -i 's/2181/2183/g'zk3.cfg
    启动Zookeeper
    /usr/local/zookeeper/bin/zkServer.sh start /usr/local/zookeeper/conf/zk1.cfg
    /usr/local/zookeeper/bin/zkServer.sh start /usr/local/zookeeper/conf/zk2.cfg
    /usr/local/zookeeper/bin/zkServer.sh start /usr/local/zookeeper/conf/zk3.cfg
    查看Zookeeper角色
    [root@linux-node1 ~]#/usr/local/zookeeper/bin/zkServer.sh status /usr/local/zookeeper/conf/zk1.cfg
    JMX enabled by default
    Using config: /usr/local/zookeeper/conf/zk1.cfg
    Mode: follower

    [root@linux-node1 ~]#/usr/local/zookeeper/bin/zkServer.sh status /usr/local/zookeeper/conf/zk2.cfg
    JMX enabled by default
    Using config: /usr/local/zookeeper/conf/zk2.cfg
    Mode: follower

    [root@linux-node1 ~]#/usr/local/zookeeper/bin/zkServer.sh status /usr/local/zookeeper/conf/zk3.cfg
    JMX enabled by default
    Using config: /usr/local/zookeeper/conf/zk3.cfg
    Mode: leader





    连接Zookeeper
    [root@linux-node1 ~]#  /usr/local/zookeeper/bin/zkCli.sh -server192.168.56.11:2181
    通过上面的例子可以看到，目前zk3是leader,其它两个节点是follower。本文由于实验环境局限使用的是伪分布式，注意生产环境不建议使用。

    Mesos 集群部署
    Mesos集群有MesosMaster和Mesos Slave两个角色。

    安装mesosphere仓库
    需要在Mesos Master和MesosSlave节点均安装：
    # rpm -Uvh http://repos.mesosphere.com/el ... h.rpm

    Mesos Master部署
    [root@linux-node1 ~]# yum -y install mesos marathon
    安装完毕后，增加zookeeper配置
    [root@linux-node1 ~]# vim /etc/mesos/zk
    zk://192.168.56.11:2181,192.168.56.11:2182,192.168.56.11:2183/mesos
    [root@linux-node1 ~]# systemctl start mesos-master mesos-slave
    [root@linux-node1 ~]# systemctl start marathon

    Mesos Slave部署
    [root@linux-node2 ~]# yum -y install mesos marathon
    [root@linux-node2 ~]# systemctl start mesos-slave


    Mesos的Web管理界面
      Mesos安装完毕后，Mesos Master会启动一个Web服务，监听在5050端口。
    http://${HOST_IP}:5050
    这时候你将得到一个像这样的页面但可能在‘Tasks’表格没有任何的条目。

    无标题2.png


    下面我们来运行第一mesos任务，注意刷新查看Mesos的Web界面，你会在Active Tasks看到我们测试的任务。
    [root@linux-node1~]# MASTER=$(mesos-resolve `cat /etc/mesos/zk`)
    [root@linux-node1~]# mesos-execute --master=$MASTER --name="cluster-test"--command="sleep 60"

    无标题3.png


    使用Marathon调用Mesos 运行Docker容器

        配置Mesos运行Docker容器

    [root@linux-node1 ~]# yum install -y docker
    [root@linux-node1 ~]# systemctl start docker

    首先先测试下，保证手动创建Docker容器没问题。

    [root@linux-node1 ~]# docker pull nginx

    再所有mesos-slave上增加配置参数，并重启
    linux-node1:
    [root@linux-node1 ~]# echo 'docker,mesos' | tee/etc/mesos-slave/containerizers
    docker,mesos
    [root@linux-node1 ~]# systemctl restart mesos-slave

    linux-node2:
    [root@linux-node2 ~]# echo 'docker,mesos' | tee/etc/mesos-slave/containerizers
    docker,mesos
    [root@linux-node2 ~]# systemctl restart mesos-slave

      接下来，我们要使用我们marathon来创建一个nginx的Docker容器，通过Mesos进行调度。   我们上面安装mesos-master的时候，
      已经安装了marathon。默认监听在8080端口，通过使用http://{HOST}:8080/来打开marathon。如下图所示：
    无标题4.png


    我相信读者会有疑问，我们并没有对marathon做任何的配置，它是怎么知道Mesos在哪里的呢？答案是通过zookeeper,marathon启动的时候
    会读取/etc/mesos/zk配置文件，通过Zookeeper来找到Mesos Master。marathon有自己的REST API，我们通过API的方式来创建一个
    nginx的docker容器：

    首先创建如下的配置文件nginx.json：
    [root@linux-node1 ~]# cat nginx.json
    {
      "id":"nginx",
      "cpus":0.2,
      "mem":20.0,
     "instances": 1,
     "constraints": [["hostname", "UNIQUE",""]],
     "container": {
        "type":"DOCKER",
       "docker": {
         "image": "nginx",
         "network": "BRIDGE",
         "portMappings": [
            {"containerPort": 80, "hostPort": 0,"servicePort": 0, "protocol": "tcp" }
          ]
        }
      }
    }
    然后调用
    # curl -X POST http://192.168.56.11:8080/v2/apps-d @nginx.json \
    -H "Content-type: application/json"

    无标题4.png


    现在你就可以通过31984来访问到nginx了。当然了，你也可以在mesos-slave上来寻找一下这个容器：
    [root@linux-node1 ~]# docker ps -a




      如果你想创建同样的容器，可以点击上图中德Scale Application来体验一下。同样的，你也可以通过marathon的Web界面来进行容器
      的创建、扩展和销毁。

    无标题5.png

    来源： https://www.unixhot.com/article/32



## 数据持久化
```
1、    Docker Volume
Docker镜像是由多个文件系统（只读层）叠加而成。当我们启动一个容器的时候，Docker会加载只读镜像层并在其上、
添加一个读写层。如果运行中的容器修改了现有的一个已经存在的文件，那该文件将会从读写层下面的只读层复制到读写层，
该文件的只读版本仍然存在，只是已经被读写层中该文件的副本所隐藏。当删除Docker容器，并通过该镜像重新启动时，
之前的更改将会丢失。在Docker中，只读层及在顶部的读写层的组合被称为Union File System（联合文件系统）。

docker run -t -i -v /data centos:6.6 /bin/bash

数据在宿主机的位置
docker ps
docker inspect ”CONTAINER ID“

2、    提交镜像
docker ps
docker commit ”CONTAINER ID“ centos:6.6-1
docker run -t -i -v /data centos:6.6-1 /bin/bash
```



## pid定位docker
```
例如，top显示存在如下进程:
5400 nobody 20 0 73260 30620 2284 S 8.3 0.4 0:20.63 nginx
对于这样一个进程，我们如何快速定位到它是运行于哪一个docker中呢 (特别是当ecs上运行了超过10个
docker的时候)？

先通过
$ pstree -p | grep -n5 5400
找到它的最上层的父进程pid:
...
114- | |-my_init(5248)-+-nginx(5398)-+-nginx(5399)
115: | | | |-nginx(5400)
116- | | | |-nginx(5401)
...
得到父进程pid=5248, 然后遍历所有容器的init进程进行匹配:
$ docker ps | awk '{print $1}' | grep -v CONTAINER | xargs docker inspect -f '{{.State.Pid}} {{.Config.Hostname}}' |
 grep 5248

5248 bd939dc98684
利用上面输出的container id, 
$ docker ps | grep bd939dc98684
即可得到该容器的其余关键信息。
```



