## GlusterFs
```
1、部署，不适合小文件，特别是大量小文件，图片等
https://docs.gluster.org/en/latest/Quick-Start-Guide/Quickstart/

至少需要两个节点，hosts文件有ip对应

准备磁盘
mkfs.xfs -i size=512 /dev/sdb
mkdir -p /data/brick1
echo '/dev/sdb /data/brick1 xfs defaults 1 2' >> /etc/fstab
mount -a && mount
mkdir /bricks/brick1/gv0

yum install centos-release-gluster -y
yum install glusterfs-server -y
systemctl enable glusterd
systemctl start glusterd
systemctl status glusterd

server1 运行 gluster peer probe server2
server2 运行 gluster peer probe server1

复制卷，性能较低
gluster volume create gv0 replica 2 server1:/bricks/brick1/gv0 server2:/bricks/brick1/gv0
gluster volume start gv0
gluster volume info 有 Status: Started

纠删码卷，类似raid5
gluster volume create gv0 disperse 3 redundancy 1 cnd01tfilel0{1,2,3}:/bricks/brick1/gv5

还需要大量测试验证：奇数冗余删除硬盘时20s无法写入，性能变的不稳定（10M-40M）
偶数冗余删除硬盘时性能，功能无影响，读写正常

disperse：每个Dispersed Set的bricks总数，如若未指定，则volume创建命令中列出的所有bricks同属于一个Dispersed Set；
redundancy：为冗余度，决定多少brick可以interrupting，并且也决定卷的可用空间，当redundancy未指定时，默认为1；

glusterfs volume创建命令中存在disperse-data参数，为卷的创建提供了更加灵活的方式，与前两者关系为：
disperse-data =disperse - redundancy
通常，应用程序的IO块大小为2的幂次，如4k、64k、1M等，建议在进行volume 创建时，disperse-data值的配置为2的次幂，与业务的IO块大小相匹配，避免RMW操作的出现，从而提升存储系统性能。


客户端
http://gluster.readthedocs.io/en/latest/Administrator%20Guide/Setting%20Up%20Clients/

# mount -t glusterfs -o backupvolfile-server=volfile_server2,use-readdirp=no,volfile-max-fetch-attempts=2,log-level=WARNING,log-file=/var/log/gluster.log server1:/test-volume /mnt/glusterfs

如果backupvolfile-server在安装fuse客户端时添加了选项，则当第一个volfile服务器出现故障时，
backupvolfile-serveroption中指定的服务器 将用作volfile服务器来安装客户端。
在volfile-max-fetch-attempts=X选项中，指定在装入卷时尝试获取卷文件的尝试次数。
当您安装具有多个IP地址的服务器或为服务器名配置循环DNS时，此选项很有用。
如果use-readdirp设置为ON，则强制在fuse内核模块中使用readdirp模式

yum install centos-release-gluster -y
yum install glusterfs-client fio -y
mount -t glusterfs server1:/gv0 /mnt
测试 for i in `seq -w 1 100`; do cp -rp /var/log/messages /mnt/copy-test-$i; done
     ls -lA /mnt | wc -l
fio --direct=1 --rw=rw --bs=1m --size=1g --numjobs=4 --group_reporting --name=test-rw

服务端会有文件 ls -lA /bricks/brick1/gv0

2、扩容可能会影响性能,如果volume是2个备份，主机数为2的倍数
server1 运行 gluster peer probe server3
             gluster peer probe server4
gluster volume add-brick gv0  server3:/bricks/brick1/gv0 server4:/bricks/brick1/gv0

分配数据  gluster volume rebalance gv0 start    
状态     gluster volume rebalance gv0 status

3、故障处理
https://docs.gluster.org/en/latest/Administrator%20Guide/Managing%20Volumes/#replace-brick
http://blog.51cto.com/cmdschool/1908647

恢复故障brick方法

2.9.1 结束故障brick的进程

gluster volume status

Gluster process                             TCP Port  RDMA Port  Online  Pid
Brick cnd01tfilel01:/bricks/brick1/gv0      49153     0          Y       1838 
Brick cnd01tfilel02:/bricks/brick1/gv0      49153     0          Y       1719 
Brick cnd01tfilel03:/bricks/brick1/gv0      N/A       N/A        N       N/A  
Brick cnd01tfilel04:/bricks/brick1/gv0      49152     0          Y       4489 
Self-heal Daemon on localhost               N/A       N/A        Y       3718 
Self-heal Daemon on cnd01tfilel03           N/A       N/A        Y       1315 
Self-heal Daemon on cnd01tfilel04           N/A       N/A        Y       5633 
Self-heal Daemon on cnd01tfilel02           N/A       N/A        Y       2913
注：如果状态Online项为“N”的GH01存在PID号（不显示N/A）应当使用如下命令结束掉进程方可继续下面步骤。

kill -15 pid

2.9.2 创建新的数据目录
mkfs.xfs -i size=512 /dev/sdb -f
编辑fstab
vim /etc/fstab
去掉注释：
/dev/sdb /bricks/brick1 xfs defaults 1 2
mount -a

增加新的数据存放文件夹（不可以与之前目录一样）
mkdir -p /bricks/brick1/gv2

2.9.3 查询故障节点的备份节点(gh02)目录的扩展属性
正常机器 getfattr -d -m. -e hex /bricks/brick1/gv0
getfattr: Removing leading '/' from absolute path names
# file: bricks/brick1/gv0
trusted.gfid=0x00000000000000000000000000000001
trusted.glusterfs.dht=0x0000000100000000000000007ffffffe
trusted.glusterfs.volume-id=0xbe45c8bbf3a64dd9a1d735a9b9073268

2.9.4 挂载卷并触发自愈
1）将卷挂到mnt目录下
mount -t glusterfs cnd01tfilel01:/gv0 /mnt
2）新建一个卷中不存在的目录并删除
mkdir /mnt/testDir001
rmdir /mnt/testDir001
3）设置扩展属性触发自愈
setfattr -n trusted.non-existent-key -v abc /mnt
setfattr -x trusted.non-existent-key /mnt

2）检查卷的状态是否显示需要替换

In GlusterH01:
gluster volume heal gv0 info
显示如下：
Brick cnd01tfilel03:/bricks/brick1/gv0
Status: Transport endpoint is not connected
Number of entries: -
注：状态提示传输端点未连接（第2行）

2.9.6 使用强制提交完成操作
gluster volume replace-brick gv0 cnd01tfilel03:/bricks/brick1/gv0 cnd01tfilel03:/bricks/brick1/gv2 commit force
volume replace-brick: success: replace-brick commit force operation successful

brick状态 gluster volume status
自愈的进度 gluster volume heal gv0 info

注：也可以将数据恢复到另外一台服务器，详细命令如下（可选）：
gluster peer probe GH05
gluster volume replace-brick gv0 GH01:/data/brick1/gv0 GH05:/data/brick1/gv0 commit

4、主机故障，无法恢复时
找一台完全一样的机器，至少要保证硬盘数量和大小一致，安装系统，配置和故障机同样的 IP，安装 gluster 软件，
保证配置一样，在其他健康节点上执行命令 gluster peer status，查看故障服务器的 uuid

如果是主机名，保证/etc/hosts文件正常, 解析正常
[root@mystorage2 ~]# gluster peer status
Number of Peers: 3

Hostname: mystorage3
Uuid: 36e4c45c-466f-47b0-b829-dcd4a69ca2e7
State: Peer in Cluster (Connected)

Hostname: mystorage4
Uuid: c607f6c2-bdcb-4768-bc82-4bc2243b1b7a
State: Peer in Cluster (Connected)

Hostname: mystorage1
Uuid: 6e6a84af-ac7a-44eb-85c9-50f1f46acef1
State: Peer in Cluster (Disconnected)
修改新加机器的 /var/lib/glusterd/glusterd.info 和 故障机器一样

[root@mystorage1 ~]# cat /var/lib/glusterd/glusterd.info
UUID=6e6a84af-ac7a-44eb-85c9-50f1f46acef1
operating-version=40100  和其他机器一样

systemctl start glusterd 
gluster peer status 如果状态不是Peer in Cluster (Connected) ,执行 gluster peer probe gfserver03加入集群

就会自动开始同步，但在同步的时候会影响整个系统的性能。
手动同步 gluster volume heal gv2 full

可以查看状态 gluster volume heal gv2 info


5、其他常用命令
删除卷
gluster volume stop img
gluster volume delete img
将机器移出集群
gluster peer detach 172.28.26.102
只允许172.28.0.0的网络访问glusterfs
gluster volume set img auth.allow 172.28.26.*
加入新的机器并添加到卷里(由于副本数设置为2,至少要添加2（4、6、8..）台机器)
gluster peer probe 172.28.26.105
gluster peer probe 172.28.26.106
gluster volume add-brick img 172.28.26.105:/data/gluster 172.28.26.106:/data/gluster
收缩卷
# 收缩卷前gluster需要先移动数据到其他位置
gluster volume remove-brick img 172.28.26.101:/data/gluster/img 172.28.26.102:/data/gluster/img start
# 查看迁移状态
gluster volume remove-brick img 172.28.26.101:/data/gluster/img 172.28.26.102:/data/gluster/img status
# 迁移完成后提交
gluster volume remove-brick img 172.28.26.101:/data/gluster/img 172.28.26.102:/data/gluster/img commit
迁移卷
# 将172.28.26.101的数据迁移到,先将172.28.26.107加入集群
gluster peer probe 172.28.26.107
gluster volume replace-brick img 172.28.26.101:/data/gluster/img 172.28.26.107:/data/gluster/img start
# 查看迁移状态gluster volume replace-brick img 172.28.26.101:/data/gluster/img 172.28.26.107:/data/gluster/img status
#数据迁移完毕后提交gluster volume replace-brick img 172.28.26.101:/data/gluster/img 172.28.26.107:/data/gluster/img commit
# 如果机器172.28.26.101出现故障已经不能运行,执行强制提交然后要求gluster马上执行一次同步
gluster volume replace-brick img 172.28.26.101:/data/gluster/img 172.28.26.102:/data/gluster/img commit -force
gluster volume heal imgs full
```

## ceph
```
http://docs.ceph.com/docs/master/

ceph清理, 慎用!!
# ceph-deploy purge node1 node2 ...
# ceph-deploy purgedata node1 node2 ...

cat /etc/yum.repos.d/ceph.repo
[Ceph]
name=Ceph packages for $basearch
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/$basearch
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

[Ceph-noarch]
name=Ceph noarch packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/noarch
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

[ceph-source]
name=Ceph source packages
baseurl=http://mirrors.aliyun.com/ceph/rpm-mimic/el7/SRPMS
enabled=1
gpgcheck=1
type=rpm-md
gpgkey=https://mirrors.aliyun.com/ceph/keys/release.asc
priority=1

部署节点
yum install ceph-deploy -y
ssh-keygen
ssh-copy-id hostname
所有节点
yum -y install ceph ceph-radosgw

部署节点
ceph-deploy new ceph-node1 ceph-node2 ceph-node3
ceph-deploy install ceph-node1 ceph-node2 ceph-node3

ceph-deploy mon create-initial
当成功执行上面命令的时候，在本地目录下会生成如下文件：
ceph.client.admin.keyring
ceph.bootstrap-osd.keyring
ceph.bootstrap-mds.keyring

ceph-deploy admin ceph-node1 ceph-node2 ceph-node3
ceph-deploy mgr create node1  高于luminous12.x 的版本添加

ceph-deploy osd create --data /dev/vdb node1
ceph-deploy osd create --data /dev/vdb node2
ceph-deploy osd create --data /dev/vdb node3

查看状态
ceph health detail
ceph -s

创建一个metadata服务器
ceph-deploy mds create ceph-node1
官方建议目前即使在生产环境中只是用一台metadata服务器也是可以的
但并不是不可以使用多台metadata服务器，只不过是那种情况下将缺少商业支持。

http://docs.ceph.org.cn/cephfs/createfs/   pg_num=100
$ ceph osd pool create cephfs_data <pg_num>
$ ceph osd pool create cephfs_metadata <pg_num>
$ ceph fs new cephfs cephfs_metadata cephfs_data

/etc/ceph/ceph.client.admin.keyring 认证信息
yum install ceph-fuse
mount -t ceph 192.168.41.31:6789:/ /mnt -o name=admin,secret=passwd 内核空间挂载
或者 ceph-fuse -m {ip-address-of-monitor}:6789 /mnt/ceph    用户空间挂载
```

## MooseFS
```
https://moosefs.com

1、安装
Add the key:
# curl "https://ppa.moosefs.com/RPM-GPG-KEY-MooseFS" > /etc/pki/rpm-gpg/RPM-GPG-KEY-MooseFS

Add an appropriate repository entry:
# curl "http://ppa.moosefs.com/MooseFS-3-el7.repo" > /etc/yum.repos.d/MooseFS.repo
then install appropriate MooseFS components:

For Master Servers:
# yum install moosefs-master moosefs-cgi moosefs-cgiserv moosefs-cli
systemctl start moosefs-master

For Metaloggers:
# yum install moosefs-metalogger
vim /etc/mfs/mfsmetalogger.cfg
MASTER_HOST = 192.168.41.31
systemctl start moosefs-metalogger

For Chunkservers:
# yum install moosefs-chunkserver
vim /etc/mfs/mfschunkserver.cfg
MASTER_HOST = 192.168.41.31
vim /etc/mfs/mfshdd.cfg
/bricks/brick1/
chown mfs.mfs /bricks/brick1/
systemctl start moosefs-chunkserver

For Clients:
# yum install moosefs-client
mkdir /mfsdata
mfsmount /mfsdata -H 192.168.41.31

```