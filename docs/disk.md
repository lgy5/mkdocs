## fdisk
```
fdisk -l 列出分区
fdisk /dev/sda
p查看    n添加    w保存    d删除    t更改分区标识

更改分区表 partprode 或者重启

测试hdparm -Tt

添加swap
1、fdisk 添加swap   mkswap /xx/xx 
2、dd if=/dev/zero of=/tmp/swap bs=大小 count=次数
        写入/etc/fstab
swapon /xx/xx  启用swap   swapoff  停用swap    swapon -s 检查
fsck 手动检查磁盘（不能操作已挂载的磁盘）

```


## parted
```
针对大于2T的磁盘
新增存储用Parted分区并建LVM卷
 
一，Parted分区
1，parted分区  www.2cto.com  
# parted /dev/sda
GNU Parted 2.1
使用 /dev/sda
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) help                               首先看看帮助熟悉下                              

(parted) mktable                                                         
新的磁盘标签类型？ gpt                     GPT就是GRUB分区表，如果是MBR，最大支持2T分区                           
(parted) p                                 打印一下信息这里的4398GB是磁盘容量                                 
Model: DELL MD32xx (scsi)
Disk /dev/sda: 4398GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
 
 
Number  Start  End  Size  File system  Name  标志
 
 
(parted) mkpart                            #新建分区                               
分区名称？  []?                            #默认                               
文件系统类型？  [ext2]?                    #默认                               
起始点？ 0G   #起点
结束点？ 4398G                             #终点                            
(parted) p                                                                
Model: DELL MD32xx (scsi)
Disk /dev/sda: 4398GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
 
 
Number  Start   End     Size    File system  Name  标志
 1      1049kB  4398GB  4398GB
 
 
(parted) toggle 1 lvm                      #标记成lvm                                   
(parted) p                                                                
Model: DELL MD32xx (scsi)
Disk /dev/sda: 4398GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
 
 
Number  Start   End     Size    File system  Name  标志
 1      1049kB  4398GB  4398GB                     lvm
 
 
(parted) quit                                                             
信息: You may need to update /etc/fstab.
2，同样的方法对sdb,sdc,sdd 分区                                  
二，创建LVM，分三大步，分别建PV,VG,LVM
1，建PV
# pvcreate /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1
  Writing physical volume data to disk "/dev/sda1"
  Physical volume "/dev/sda1" successfully created
  Writing physical volume data to disk "/dev/sdb1"
  Physical volume "/dev/sdb1" successfully created
  Writing physical volume data to disk "/dev/sdc1"
  Physical volume "/dev/sdc1" successfully created
  Writing physical volume data to disk "/dev/sdd1"
  Physical volume "/dev/sdd1" successfully created
2,建VG
# vgcreate md3200 /dev/sda1 /dev/sdb1 /dev/sdc1 /dev/sdd1
  Volume group "md3200" successfully created
# lvcreate -n md3200lv1 -L 8T md3200
  Logical volume "md3200lv1" created
You have new mail in /var/spool/mail/root
3,建LVM
#lvcreate -n md3200lv1 -L 8T md3200
  Logical volume "md3200lv1" created
#lvcreate -n md3200lv2 -L 8T md3200
 Logical volume "md3200lv2" created
三，格式化文件系统
# mkfs.ext4 /dev/md3200/md3200lv1 
mke2fs 1.41.12 (17-May-2010)
文件系统标签=
操作系统:Linux
块大小=4096 (log=2)
分块大小=4096 (log=2)
Stride=0 blocks, Stripe width=0 blocks
536870912 inodes, 2147483648 blocks
107374182 blocks (5.00%) reserved for the super user
第一个数据块=0
Maximum filesystem blocks=4294967296
65536 block groups
32768 blocks per group, 32768 fragments per group
8192 inodes per group
Superblock backups stored on blocks: 
        32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208, 
        4096000, 7962624, 11239424, 20480000, 23887872, 71663616, 78675968, 
        102400000, 214990848, 512000000, 550731776, 644972544, 1934917632
 
 
正在写入inode表: 完成                            
Creating journal (32768 blocks): 完成
Writing superblocks and filesystem accounting information: 完成
 
 
This filesystem will be automatically checked every 33 mounts or
180 days, whichever comes first.  Use tune2fs -c or -i to override.
四，设置开机自动挂载
# mkdir md3200lv1  md3200lv2
# mount /dev/md3200/md3200lv1 /md3200lv1/
# ls /md3200lv1/
lost+found
#tail -n 2 /etc/fstab
/dev/md3200/md3200lv1 /md3200lv1                ext4    defaults                1 2
/dev/md3200/md3200lv2 /md3200lv2                ext4    defaults                1 2
五，重启验证
#reboot
# df -hl
文件系统              容量  已用  可用 已用%% 挂载点
/dev/mapper/md3200-md3200lv1
                      7.9T  175M  7.5T   1% /md3200lv1
/dev/mapper/md3200-md3200lv2
                      7.9T  175M  7.5T   1% /md3200lv2
六，最后顺便测试一下存储的读写速度
# dd if=/dev/zero of=./test bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，8.83453 秒，1.2 GB/秒
# free -g
             total       used       free     shared    buffers     cached
Mem:            62         11         51          0          0          9
-/+ buffers/cache:          1         61
Swap:            7          0          7
# dd if=./test of=./test1  bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，12.3038 秒，852 MB/秒
# dd if=./test1 of=./test2  bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，19.0357 秒，551 MB/秒
# dd if=./test2 of=./test3 bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，18.641 秒，563 MB/秒
# free -g
             total       used       free     shared    buffers     cached
Mem:            62         41         21          0          0         39
-/+ buffers/cache:          2         60
Swap:            7          0          7
# dd if=./test3 of=./test4 bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，17.3797 秒，603 MB/秒
# dd if=./test4 of=./test5 bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，22.8714 秒，458 MB/秒
# dd if=./test5 of=./test6 bs=10M count=1000
记录了1000+0 的读入
记录了1000+0 的写出
10485760000字节(10 GB)已复制，100.246 秒，105 MB/秒
 
因为内存是64G，故前面测试有缓存，最后105为实际读写速度。

来源： http://www.2cto.com/os/201303/195308.html
```


## MegaCli
```
http://www.avagotech.com/docs-and-downloads/raid-controllers/raid-controllers-common-files/8-07-14_MegaCLI.zip

首先介绍下Linux系统本身查看

软件raid：查看raid级别，状态等信息

#cat /proc/mdstat

硬件raid：查看raid的厂商，型号，级别

#dmesg | grep -i raid

#cat /proc/scsi/scsi

2.硬件raid最佳的办法是通过已安装的raid厂商的管理工具来查看,下面安装MegaCLI工具查看

首先下载MegaCli，解压缩。#rpm -ivh MegaCli-1.01.24-0.i386.rpm  安装在/opt下，所以执行命令都是/opt/MegaCli 哦。

命令使用：

# /opt/MegaRAID/MegaCli/MegaCli64 -CfgForeign -Clear -a0 清除Foreign状态

#/opt/MegaCli  -LDInfo -Lall -aALL 查raid级别

#/opt/MegaCli -AdpAllInfo -aALL 查raid卡信息

#/opt/MegaCli -PDList -aALL 查看硬盘信息

#/opt/MegaCli -AdpBbuCmd -aAll 查看电池信息

#/opt/MegaCli -FwTermLog -Dsply -aALL 查看raid卡日志

#/opt/MegaCli -adpCount 【显示适配器个数】

#/opt/MegaCli -AdpGetTime –aALL 【显示适配器时间】

#/opt/MegaCli -AdpAllInfo -aAll    【显示所有适配器信息】

#/opt/MegaCli -LDInfo -LALL -aAll    【显示所有逻辑磁盘组信息】

#/opt/MegaCli -PDList -aAll    【显示所有的物理信息】

#/opt/MegaCli -AdpBbuCmd -GetBbuStatus -aALL |grep ‘Charger Status’ 【查看充电状态】

#/opt/MegaCli -AdpBbuCmd -GetBbuStatus -aALL【显示BBU状态信息】

#/opt/MegaCli -AdpBbuCmd -GetBbuCapacityInfo -aALL【显示BBU容量信息】

#/opt/MegaCli -AdpBbuCmd -GetBbuDesignInfo -aALL    【显示BBU设计参数】

#/opt/MegaCli -AdpBbuCmd -GetBbuProperties -aALL    【显示当前BBU属性】

#/opt/MegaCli -cfgdsply -aALL    【显示Raid卡型号，Raid设置，Disk相关信息】

3.磁带状态的变化，从拔盘，到插盘的过程中。

Device        |Normal|Damage|Rebuild|Normal

Virtual Drive    |Optimal|Degraded|Degraded|Optimal

Physical Drive    |Online|Failed –&gt; Unconfigured|Rebuild|Online

4.查看磁盘缓存策略

#/opt/MegaCli -LDGetProp -Cache -L0 -a0

or

#/opt/MegaCli -LDGetProp -Cache -L1 -a0

or

#/opt/MegaCli -LDGetProp -Cache -LALL -a0

ro

#/opt/MegaCli -LDGetProp -Cache -LALL -aALL

ro

#/opt/MegaCli -LDGetProp -DskCache -LALL -aALL

5.设置磁盘缓存策略

缓存策略解释：

WT    (Write through

WB    (Write back)

NORA  (No read ahead)

RA    (Read ahead)

ADRA  (Adaptive read ahead)

Cached

Direct

例子：

#/opt/MegaCli -LDSetProp WT|WB|NORA|RA|ADRA -L0 -a0

or

#/opt/MegaCli -LDSetProp -Cached|-Direct -L0 -a0

or

enable / disable disk cache

#/opt/MegaCli -LDSetProp -EnDskCache|-DisDskCache -L0 -a0

6.创建一个 raid5 阵列，由物理盘 2,3,4 构成，该阵列的热备盘是物理盘 5

#/opt/MegaCli -CfgLdAdd -r5 [1:2,1:3,1:4] WB Direct -Hsp[1:5] -a0

7.创建阵列，不指定热备

#/opt/MegaCli -CfgLdAdd -r5 [1:2,1:3,1:4] WB Direct -a0

8.删除阵列

#/opt/MegaCli -CfgLdDel -L1 -a0

9.在线添加磁盘

#/opt/MegaCli -LDRecon -Start -r5 -Add -PhysDrv[1:4] -L1 -a0

10.阵列创建完后，会有一个初始化同步块的过程，可以看看其进度。

#/opt/MegaCli -LDInit -ShowProg -LALL -aALL

或者以动态可视化文字界面显示

#/opt/MegaCli -LDInit -ProgDsply -LALL -aALL

11.查看阵列后台初始化进度

#/opt/MegaCli -LDBI -ShowProg -LALL -aALL

或者以动态可视化文字界面显示

#/opt/MegaCli -LDBI -ProgDsply -LALL -aALL

12.指定第 5 块盘作为全局热备

#/opt/MegaCli -PDHSP -Set [-EnclAffinity] [-nonRevertible] -PhysDrv[1:5] -a0

13.指定为某个阵列的专用热备

#/opt/MegaCli -PDHSP -Set [-Dedicated [-Array1]] [-EnclAffinity] [-nonRevertible] -PhysDrv[1:5] -a0

14.删除全局热备

#/opt/MegaCli -PDHSP -Rmv -PhysDrv[1:5] -a0

15.将某块物理盘下线/上线
MegaCli64 -PDList -aALL 确认    [Enclosure Device ID : Slot Number] 
                                [1  :   4]


#/opt/MegaCli -PDOffline -PhysDrv [1:4] -a0

#/opt/MegaCli -PDOnline -PhysDrv [1:4] -a0

16.查看物理磁盘重建进度

#/opt/MegaCli -PDRbld -ShowProg -PhysDrv [1:5] -a0

或者以动态可视化文字界面显示

#/opt/MegaCli -PDRbld -ProgDsply -PhysDrv [1:5] -a0

```


## 内网云盘
```
owncloud   https://owncloud.org/

seafile     https://www.seafile.com/home/

```

## lvm
```
lvm建立pv，vg不要格式化
建立：
pvcreate  /dev/xxx
vgcreate  vg0  /dev/xx
lvcreate  -L 512M -n lv0 vg0
mkfs.ext3 /dev/vg1/lv0
mount /dev/vg1/lv0 /data/
vim /etc/fatab
/dev/mapper/vg1-lvdata   /data                  ext3    defaults        1 2
 
查看
pvdisplay   or  pvscan
vgdisplay   or   vgscan
lvdisplay    or    lvscan
 
lvm扩容
创建一块新的分区：
fdisk  /dev/hda
 
n
 
p        #选择逻辑分区，如果没有，则首先创建扩展分区，然后再添加逻辑分区（硬盘：最多四个分区P-P-P-P或P-P-P-E）
 
1        #分区号，/dev/hda6
 
t      8e   #分区类型8e表示LVM分区
 
w        #写入分区表
 
partprobe   #重读分区表
 
partx /dev/hda #查看当前硬盘的分区表及使用情况
 
 
创建PV，扩容VG，LV
 
pvcreate /dev/hda1
 
vgdisplay #查看当前已经存在的VG信息，以存在VG：VolGroup00为例
 
vgextend VolGroup00 /dev/hda1   #扩展VolGroup00
 
lvdisplay #查看已经存在的LV信息，以存在LV：LogVol01为例
 
lvextend –L 1G /dev/VolGroup00/LogVol01 #扩展LV
 
              -l +100%FREE    全部剩余空间
 
ext3 ext4文件系统   
resize2fs /dev/VolGroup00/LogVol01 #执行该重设大小，对于当前正在使用的LogVol01有效

xfs文件系统
xfs_growfs  /dev/centos/root #执行该重设大小，对于当前正在使用的LogVol01有效
 
df –h #查看挂载情况，已经扩容
```



## samba
```
yum install samba samba-client  samba-common  samba-swat
                   服务端    客户端            通用工具          wab管理
systemctl restart smb

vim /etc/samba/smb.conf
security=share/user
若用户验证使用user，添加：
passdb backend=tdbsam
username map=/etc/samba/smbusers
vim /etc/samba/smbusers
系统用户=samba用户1[空格]samba用户2
smbpasswd -a 系统用户

/etc/samba/smb.conf  
[homes]  共享名
comment=xxxx  描述
path=/tmp/samba                     chmod o+w /tmp/samba 
public=yes  允许匿名访问
guesk ok=yes
browseable=yes  共享可见，默认yes 
writable=yes   共享可写
write list = 可写用户列表，系统用户
read only=yes  共享只读
read list=只读用户列表，系统用户   多个，分开
valid users= 允许用户列表，系统用户
invalid users = 禁止用户列表，系统用户

例：   账号认证，匿名不能访问
[work]
	comment = All
	path = /data
        #public = no
	browseable = yes
	#guest ok = yes
	writable = yes
	read only = no
        write list = ftp, work
	valid users = ftp, work




客户端
smbclient -L ip 查看共享列表
smbclient //ip/共享名 -U 用户名
mount -t cifs //ip/共享名  /mnt/abc -O username=test,passwd=

windows直接运行\\ip
```



## nfs
```
一、NFS服务简介

　　NFS 是Network File System的缩写，即网络文件系统。一种使用于分散式文件系统的协定，由Sun公司开发，于1984年向外公布。
功能是通过网络让不同的机器、不同的操作系统能够彼此分享个别的数据，让应用程序在客户端通过网络访问位于服务器磁盘中的数据，
是在类Unix系统间实现磁盘文件共享的一种方法。

　　NFS 的基本原则是“容许不同的客户端及服务端通过一组RPC分享相同的文件系统”，它是独立于操作系统，容许不同硬件及操作系统的系统
共同进行文件的分享。

　　NFS在文件传送或信息传送过程中依赖于RPC协议。RPC，远程过程调用 (Remote Procedure Call) 是能使客户端执行其他系统中程序的
一种机制。NFS本身是没有提供信息传输的协议和功能的，但NFS却能让我们通过网络进行资料的分享，这是因为NFS使用了一些其它的
传输协议。而这些传输协议用到这个RPC功能的。可以说NFS本身就是使用RPC的一个程序。或者说NFS也是一个RPC SERVER。所以只要用到NFS的地方
都要启动RPC服务，不论是NFS SERVER或者NFS CLIENT。这样SERVER和CLIENT才能通过RPC来实现PROGRAM PORT的对应。可以这么理解RPC和NFS的
关系：NFS是一个文件系统，而RPC是负责负责信息的传输。

二、系统环境

系统平台：CentOS release 5.6 (Final)

NFS Server IP：192.168.1.108

防火墙已关闭/iptables: Firewall is not running.

SELINUX=disabled

三、安装NFS服务

NFS的安装是非常简单的，只需要两个软件包即可，而且在通常情况下，是作为系统的默认包安装的。

nfs-utils-* ：包括基本的NFS命令与监控程序 
portmap-* ：支持安全NFS RPC服务的连接，新的叫rpcbind
查看系统是否已安装NFS



系统默认已安装了nfs-utils portmap 两个软件包。

四、NFS系统守护进程

nfsd：它是基本的NFS守护进程，主要功能是管理客户端是否能够登录服务器；
mountd：它是RPC安装守护进程，主要功能是管理NFS的文件系统。当客户端顺利通过nfsd登录NFS服务器后，在使用NFS服务所提供的文件前，
还必须通过文件使用权限的验证。它会读取NFS的配置文件/etc/exports来对比客户端权限。
portmap：主要功能是进行端口映射工作。当客户端尝试连接并使用RPC服务器提供的服务（如NFS服务）时，portmap会将所管理的与服务
对应的端口提供给客户端，从而使客户可以通过该端口向服务器请求服务。
五、NFS服务器的配置

NFS服务器的配置相对比较简单，只需要在相应的配置文件中进行设置，然后启动NFS服务器即可。

NFS的常用目录

/etc/exports                           NFS服务的主要配置文件
/usr/sbin/exportfs                   NFS服务的管理命令
/usr/sbin/showmount              客户端的查看命令
/var/lib/nfs/etab                      记录NFS分享出来的目录的完整权限设定值
/var/lib/nfs/xtab                      记录曾经登录过的客户端信息
NFS服务的配置文件为 /etc/exports，这个文件是NFS的主要配置文件，不过系统并没有默认值，所以这个文件不一定会存在，可能要使用
vim手动建立，然后在文件里面写入配置内容。

/etc/exports文件内容格式：

<输出目录> [客户端1 选项（访问权限,用户映射,其他）] [客户端2 选项（访问权限,用户映射,其他）]
a. 输出目录：

输出目录是指NFS系统中需要共享给客户机使用的目录；

b. 客户端：

客户端是指网络中可以访问这个NFS输出目录的计算机

客户端常用的指定方式

指定ip地址的主机：192.168.0.200
指定子网中的所有主机：192.168.0.0/24 192.168.0.0/255.255.255.0
指定域名的主机：david.bsmart.cn
指定域中的所有主机：*.bsmart.cn
所有主机：*
c. 选项：

选项用来设置输出目录的访问权限、用户映射等。

NFS主要有3类选项：

访问权限选项

设置输出目录只读：ro
设置输出目录读写：rw
用户映射选项

all_squash：将远程访问的所有普通用户及所属组都映射为匿名用户或用户组（nfsnobody）；
no_all_squash：与all_squash取反（默认设置）；
root_squash：将root用户及所属组都映射为匿名用户或用户组（默认设置）；
no_root_squash：与rootsquash取反；
anonuid=xxx：将远程访问的所有用户都映射为匿名用户，并指定该用户为本地用户（UID=xxx）；
anongid=xxx：将远程访问的所有用户组都映射为匿名用户组账户，并指定该匿名用户组账户为本地用户组账户（GID=xxx）；
其它选项

secure：限制客户端只能从小于1024的tcp/ip端口连接nfs服务器（默认设置）；
insecure：允许客户端从大于1024的tcp/ip端口连接服务器；
sync：将数据同步写入内存缓冲区与磁盘中，效率低，但可以保证数据的一致性；
async：将数据先保存在内存缓冲区中，必要时才写入磁盘；
wdelay：检查是否有相关的写操作，如果有则将这些写操作一起执行，这样可以提高效率（默认设置）；
no_wdelay：若有写操作则立即执行，应与sync配合使用；
subtree：若输出目录是一个子目录，则nfs服务器将检查其父目录的权限(默认设置)；
no_subtree：即使输出目录是一个子目录，nfs服务器也不检查其父目录的权限，这样可以提高效率；
六、NFS服务器的启动与停止

在对exports文件进行了正确的配置后，就可以启动NFS服务器了。

1、启动NFS服务器

为了使NFS服务器能正常工作，需要启动portmap和nfs两个服务，并且portmap一定要先于nfs启动。

# service portmap start
# service nfs start


2、查询NFS服务器状态

# service portmap status
# service nfs status


3、停止NFS服务器

要停止NFS运行时，需要先停止nfs服务再停止portmap服务，对于系统中有其他服务(如NIS)需要使用时，不需要停止portmap服务

# service nfs stop
# service portmap stop
4、设置NFS服务器的自动启动状态

对于实际的应用系统，每次启动LINUX系统后都手工启动nfs服务器是不现实的，需要设置系统在指定的运行级别自动启动portmap和nfs服务。

# chkconfig --list portmap
# chkconfig --list nfs


设置portmap和nfs服务在系统运行级别3和5自动启动。

# chkconfig --level 35 portmap on
# chkconfig --level 35 nfs on


七、实例

1、将NFS Server 的/home/david/ 共享给192.168.1.0/24网段，权限读写。

# vi /etc/exports

/home/david 192.168.1.0/24(rw)
2、重启portmap 和nfs 服务

# service portmap restart
# service nfs restart
# exportfs


3、服务器端使用showmount命令查询NFS的共享状态

# showmount -e　　　　//默认查看自己共享的服务，前提是要DNS能解析自己，不然容易报错



# showmount -a　　　　//显示已经与客户端连接上的目录信息



4、客户端使用showmount命令查询NFS的共享状态

# showmount -e NFS服务器IP



5、客户端挂载NFS服务器中的共享目录

命令格式

# mount NFS服务器IP:共享目录 本地挂载点目录
# mount 192.168.1.108:/home/david/ /tmp/david/

# mount |grep nfs



挂载成功。

查看文件是否和服务器端一致。



6、NFS的共享权限和访问控制

现在我们在/tmp/david/ 里面建立一个文件，看看权限是什么

# touch 20130103



这里出现Permission denied，是因为NFS 服务器端共享的目录本身的写权限没有开放给其他用户，在服务器端打开该权限。

# chmod 777 -R /home/david/



再次在客户端/tmp/david/ 里面建立一个文件



我用root 用户建立的文件，变成了nfsnobody 用户。

NFS有很多默认的参数，打开/var/lib/nfs/etab 查看分享出来的/home/david/ 完整权限设定值。

# cat /var/lib/nfs/etab



默认就有sync，wdelay，hide 等等，no_root_squash 是让root保持权限，root_squash 是把root映射成nobody，no_all_squash 不让
所有用户保持在挂载目录中的权限。所以，root建立的文件所有者是nfsnobody。

下面我们使用普通用户挂载、写入文件测试。

# su - david

$ cd /tmp/david/

$ touch 2013david



普通用户写入文件时就是自己的名字，这也就保证了服务器的安全性。
　　关于权限的分析

　　1. 客户端连接时候，对普通用户的检查

　　　　a. 如果明确设定了普通用户被压缩的身份，那么此时客户端用户的身份转换为指定用户；

　　　　b. 如果NFS server上面有同名用户，那么此时客户端登录账户的身份转换为NFS server上面的同名用户；

　　　　c. 如果没有明确指定，也没有同名用户，那么此时 用户身份被压缩成nfsnobody；

　　2. 客户端连接的时候，对root的检查

　　　　a. 如果设置no_root_squash，那么此时root用户的身份被压缩为NFS server上面的root；

　　　　b. 如果设置了all_squash、anonuid、anongid，此时root 身份被压缩为指定用户；

　　　　c. 如果没有明确指定，此时root用户被压缩为nfsnobody；

　　　　d. 如果同时指定no_root_squash与all_squash 用户将被压缩为 nfsnobody，如果设置了anonuid、anongid将被压缩到所指定的
用户与组；

7、卸载已挂载的NFS共享目录

# umount /tmp/david/



八、启动自动挂载nfs文件系统

格式：

<server>:</remote/export> </local/directory> nfs < options> 0 0
# vi /etc/fstab



保存退出，重启系统。

查看/home/david 有没有自动挂载。



自动挂载成功。

九、相关命令

1、exportfs

如果我们在启动了NFS之后又修改了/etc/exports，是不是还要重新启动nfs呢？这个时候我们就可以用exportfs 命令来使改动立刻生效，
该命令格式如下：

　　# exportfs [-aruv]

　　-a 全部挂载或卸载 /etc/exports中的内容 
　　-r 重新读取/etc/exports 中的信息 ，并同步更新/etc/exports、/var/lib/nfs/xtab
　　-u 卸载单一目录（和-a一起使用为卸载所有/etc/exports文件中的目录）
　　-v 在export的时候，将详细的信息输出到屏幕上。

具体例子： 
　　# exportfs -au 卸载所有共享目录
　　# exportfs -rv 重新共享所有目录并输出详细信息

2、nfsstat

查看NFS的运行状态，对于调整NFS的运行有很大帮助。

3、rpcinfo

查看rpc执行信息，可以用于检测rpc运行情况的工具，利用rpcinfo -p 可以查看出RPC开启的端口所提供的程序有哪些。

4、showmount

　　-a 显示已经于客户端连接上的目录信息
　　-e IP或者hostname 显示此IP地址分享出来的目录

5、netstat

可以查看出nfs服务开启的端口，其中nfs 开启的是2049，portmap 开启的是111，其余则是rpc开启的。

最后注意两点，虽然通过权限设置可以让普通用户访问，但是挂载的时候默认情况下只有root可以去挂载，普通用户可以执行sudo。

NFS server 关机的时候一点要确保NFS服务关闭，没有客户端处于连接状态！通过showmount -a 可以查看，如果有的话用kill killall pkill
 来结束，（-9 强制结束）
```


## iozone
```
http://www.iozone.org

wget http://www.iozone.org/src/current/iozone3_465.tar
tar -xf iozone3_465.tar
cd iozone3_465/src/current/
make linux

 测试的时候请注意，设置的测试文件的大小一定要大过你的内存（最佳为内存的两倍大小），不然linux会给你的读写的内容进行缓存。
 会使数值非常不真实。

测试命令是 
./iozone -s 5g -i0 -i1 -i2 -Rb ioperf.xls -I    数据更真实， -I  direct io 不过读写速度结果更低
./iozone -Rab  ioperf.xls  -s 64G -i 0 -i 1 -i 2 -y 4k -q 16k  测试更大的文件更接近

常用参数解释:
-a  auto mode产生文件大小16K-512M,记录大小4K-16M的输出结果；
-e  计算时间时算上fflush，fsync的时间；
-f  指定临时测试文件 可以测试不同分区会磁盘；
-R 产生excel格式的输出（仅显示在屏幕上,不会产生excel文件）
-b 产生excel格式的文件
-s  指定测试文件大小  支持-k -m -g； 
-r  指定测试记录大小；
-g -n 指定auto模式下，最大/小测试文件大小；
-q -y 指定auto模式下，最大/小测试记录大小；
-i  指定特定的测试操作：
     (0=write/rewrite, 1=read/re-read, 2=random-read/write
3=Read-backwards, 4=Re-write-record, 5=stride-read, 6=fwrite/re-fwrite, 7=fread/Re-fread,
8=random mix, 9=pwrite/Re-pwrite, 10=pread/Re-pread, 11=pwritev/Re-pwritev, 12=preadv/Repreadv）
-I  指定direct io操作；
-p  清除cpu cache影响；
-t  并发数
-O  输出IOPS值；
-R  生成excel报告文件；
-W  读写之前锁定文件；

测试生成的ioperf1.xls是操作系统中read，write速率，以下表为例，该表是是关于write的测试结果，左侧一列是测试文件大小（Kbytes),
最上边一行是记录大小，中间数据是测试的传输速度。举例说明，比如表中的“19918”，意思是测试文件大小为64K，以记录大小为4K来进行传输，
它的传输速度为19918Kbytes/s。


-i的取值说明如下：

0=write/rewrite
1=read/re-read
2=random-read/write
3=Read-backwards
4=Re-write-record
5=stride-read
6=fwrite/re-fwrite
7=fread/Re-fread
8=random mix
9=pwrite/Re-pwrite
10=pread/Re-pread
11=pwritev/Re-pwritev
12=preadv/Re-preadv


Write:测试向一个新文件写入的性能。当一个新文件被写入时，不仅仅是那些文件中的数据需要被存储，还包括那些用于定位数据存储在存储介质的
具体位置的额外信息。这些额外信息被称作“元数据”。它包括目录信息，所分配的空间和一些与该文件有关但又并非该文件所含数据的其他数据。
拜这些额外信息所赐，Write的性能通常会比Re-write的性能低。

Re-write:测试向一个已存在的文件写入的性能。当一个已存在的文件被写入时，所需工作量较少，因为此时元数据已经存在。Re-write的性能通常
比Write的性能高。
Read: 测试读一个已存在的文件的性能。
Re-Read:测试读一个最近读过的文件的性能。Re-Read性能会高些，因为操作系统通常会缓存最近读过的文件数据。这个缓存可以被用于读以提高性能。
Random Read:测试读一个文件中的随机偏移量的性能。许多因素可能影响这种情况下的系统性能，例如：操作系统缓存的大小，磁盘数量，寻道延迟
和其他。
Random Write:测试写一个文件中的随机偏移量的性能。同样，许多因素可能影响这种情况下的系统性能，例如：操作系统缓存的大小，磁盘数量，
寻道延迟和其他。
Random Mix:测试读写一个文件中的随机偏移量的性能。同样，许多因素可能影响这种情况下的系统性能，例如：操作系统缓存的大小，磁盘数量，
寻道延迟和其他。这个测试只有在吞吐量测试模式下才能进行。每个线程/进程运行读或写测试。这种分布式读/写测试是基于roundrobin 模式的。
最好使用多于一个线程/进程执行此测试。
Backwards Read:测试使用倒序读一个文件的性能。这种读文件方法可能看起来很可笑，事实上，有些应用确实这么干。MSCNastran是一个使用
倒序读文件的应用程序的一个例子。它所读的文件都十分大（大小从G级别到T级别）。尽管许多操作系统使用一些特殊实现来优化顺序读文件的速度，
很少有操作系统注意到并增强倒序读文件的性能。
Record Rewrite:测试写与覆盖写一个文件中的特定块的性能。这个块可能会发生一些很有趣的事。如果这个块足够小（比CPU数据缓存小），
测出来的性能将会非常高。如果比CPU数据缓存大而比TLB小，测出来的是另一个阶段的性能。如果比此二者都大，但比操作系统缓存小，得到的性能
又是一个阶段。若大到超过操作系统缓存，又是另一番结果。
Strided Read:测试跳跃读一个文件的性能。举例如下：在0偏移量处读4Kbytes，然后间隔200Kbytes,读4Kbytes，再间隔200Kbytes，如此反复。
此时的模式是读4Kbytes，间隔200Kbytes并重复这个模式。这又是一个典型的应用行为，文件中使用了数据结构并且访问这个数据结构的特定区域的
应用程序常常这样做。
许多操作系统并没注意到这种行为或者针对这种类型的访问做一些优化。同样，这种访问行为也可能导致一些有趣的性能异常。一个例子是在一个
数据片化的文件系统里，应用程序的跳跃导致某一个特定的磁盘成为性能瓶颈。
Fwrite:测试调用库函数fwrite()来写文件的性能。这是一个执行缓存与阻塞写操作的库例程。缓存在用户空间之内。如果一个应用程序想要写
很小的传输块，fwrite()函数中的缓存与阻塞I/O功能能通过减少实际操作系统调用并在操作系统调用时增加传输块的大小来增强应用程序的性能。
这个测试是写一个新文件，所以元数据的写入也是要的。
Frewrite:测试调用库函数fwrite()来写文件的性能。这是一个执行缓存与阻塞写操作的库例程。缓存在用户空间之内。如果一个应用程序想要写
很小的传输块，fwrite()函数中的缓存与阻塞I/O功能能通过减少实际操作系统调用并在操作系统调用时增加传输块的大小来增强应用程序的性能。
这个测试是写入一个已存在的文件，由于无元数据操作，测试的性能会高些。
Fread:测试调用库函数fread()来读文件的性能。这是一个执行缓存与阻塞读操作的库例程。缓存在用户空间之内。如果一个应用程序想要读很小的
传输块，fwrite()函数中的缓存与阻塞I/O功能能通过减少实际操作系统调用并在操作系统调用时增加传输块的大小来增强应用程序的性能。
Freread: 这个测试与上面的fread 类似
```



## fio测试磁盘
```
注
意：不要对有数据的磁盘或者分区做测试，会破坏已存在的数据
慎用！！！

FIO安装
wget http://brick.kernel.dk/snaps/fio-2.2.5.tar.gz
yum install libaio-devel
tar -zxvf fio-2.2.5.tar.gz
cd fio-2.2.5
make
make install
二、FIO用法：
随机读：(可直接用，向磁盘写一个2G文件，10线程，随机读1分钟，给出结果)

fio -filename=/tmp/test_randread -direct=1 -iodepth 1 -thread -rw=randread -ioengine=psync -bs=16k -size=2G
-numjobs=10 -runtime=60 -group_reporting -name=mytest
说明：
filename=/dev/sdb1 测试文件名称，通常选择需要测试的盘的data目录。
direct=1 测试过程绕过机器自带的buffer。使测试结果更真实。
rw=randwrite 测试随机写的I/O
rw=randrw 测试随机写和读的I/O
bs=16k 单次io的块文件大小为16k
bsrange=512-2048 同上，提定数据块的大小范围
size=5g 本次的测试文件大小为5g，以每次4k的io进行测试。
numjobs=30 本次的测试线程为30.
runtime=1000 测试时间为1000秒，如果不写则一直将5g文件分4k每次写完为止。
ioengine=psync io引擎使用pync方式
rwmixwrite=30 在混合读写的模式下，写占30%
group_reporting 关于显示结果的，汇总每个进程的信息。

此外
lockmem=1g 只使用1g内存进行测试。
zero_buffers 用0初始化系统buffer。
nrfiles=8 每个进程生成文件的数量。

read 顺序读
write 顺序写
rw,readwrite 顺序混合读写

randwrite 随机写
randread 随机读
randrw 随机混合读写

io总的输入输出量
bw：带宽 KB/s
iops：每秒钟的IO数
runt：总运行时间
lat (msec)：延迟(毫秒)
msec： 毫秒

usec： 微秒

顺序读：

fio -filename=/dev/sdb1 -direct=1 -iodepth 1 -thread -rw=read -ioengine=psync -bs=16k -size=2G -numjobs=10
-runtime=60 -group_reporting -name=mytest
随机写：

fio -filename=/dev/sdb1 -direct=1 -iodepth 1 -thread -rw=randwrite -ioengine=psync -bs=16k -size=2G -numjobs=10
-runtime=60 -group_reporting -name=mytest
顺序写：

fio -filename=/dev/sdb1 -direct=1 -iodepth 1 -thread -rw=write -ioengine=psync -bs=16k -size=2G -numjobs=10
-runtime=60 -group_reporting -name=mytest
混合随机读写：

fio -filename=/dev/sdb1 -direct=1 -iodepth 1 -thread -rw=randrw -rwmixread=70 -ioengine=psync -bs=16k -size=2G
-numjobs=10 -runtime=60 -group_reporting -name=mytest -ioscheduler=noop
三，实际测试范例：

[root@localhost ~]# fio -filename=/dev/sdb1 -direct=1 -iodepth 1 -thread -rw=randrw -rwmixread=70 -ioengine=psync 
-bs=16k -size=200G -numjobs=30 -runtime=100 -group_reporting -name=mytest1
mytest1: (g=0): rw=randrw, bs=16K-16K/16K-16K, ioengine=psync, iodepth=1
…
mytest1: (g=0): rw=randrw, bs=16K-16K/16K-16K, ioengine=psync, iodepth=1
fio 2.0.7
Starting 30 threads
Jobs: 1 (f=1): [________________m_____________] [3.5% done] [6935K/3116K /s] [423 /190 iops] [eta 48m:20s] s]
mytest1: (groupid=0, jobs=30): err= 0: pid=23802
read : io=1853.4MB, bw=18967KB/s, iops=1185 , runt=100058msec
clat (usec): min=60 , max=871116 , avg=25227.91, stdev=31653.46
lat (usec): min=60 , max=871117 , avg=25228.08, stdev=31653.46
clat percentiles (msec):
| 1.00th=[ 3], 5.00th=[ 5], 10.00th=[ 6], 20.00th=[ 8],
| 30.00th=[ 10], 40.00th=[ 12], 50.00th=[ 15], 60.00th=[ 19],
| 70.00th=[ 26], 80.00th=[ 37], 90.00th=[ 57], 95.00th=[ 79],
| 99.00th=[ 151], 99.50th=[ 202], 99.90th=[ 338], 99.95th=[ 383],
| 99.99th=[ 523]
bw (KB/s) : min= 26, max= 1944, per=3.36%, avg=636.84, stdev=189.15
write: io=803600KB, bw=8031.4KB/s, iops=501 , runt=100058msec
clat (usec): min=52 , max=9302 , avg=146.25, stdev=299.17
lat (usec): min=52 , max=9303 , avg=147.19, stdev=299.17
clat percentiles (usec):
| 1.00th=[ 62], 5.00th=[ 65], 10.00th=[ 68], 20.00th=[ 74],
| 30.00th=[ 84], 40.00th=[ 87], 50.00th=[ 89], 60.00th=[ 90],
| 70.00th=[ 92], 80.00th=[ 97], 90.00th=[ 120], 95.00th=[ 370],
| 99.00th=[ 1688], 99.50th=[ 2128], 99.90th=[ 3088], 99.95th=[ 3696],
| 99.99th=[ 5216]
bw (KB/s) : min= 20, max= 1117, per=3.37%, avg=270.27, stdev=133.27
lat (usec) : 100=24.32%, 250=3.83%, 500=0.33%, 750=0.28%, 1000=0.27%
lat (msec) : 2=0.64%, 4=3.08%, 10=20.67%, 20=19.90%, 50=17.91%
lat (msec) : 100=6.87%, 250=1.70%, 500=0.19%, 750=0.01%, 1000=0.01%
cpu : usr=1.70%, sys=2.41%, ctx=5237835, majf=0, minf=6344162
IO depths : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
submit : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
complete : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
issued : total=r=118612/w=50225/d=0, short=r=0/w=0/d=0
Run status group 0 (all jobs):
READ: io=1853.4MB, aggrb=18966KB/s, minb=18966KB/s, maxb=18966KB/s, mint=100058msec, maxt=100058msec
WRITE: io=803600KB, aggrb=8031KB/s, minb=8031KB/s, maxb=8031KB/s, mint=100058msec, maxt=100058msec
Disk stats (read/write):
sdb: ios=118610/50224, merge=0/0, ticks=2991317/6860, in_queue=2998169, util=99.77%
主要查看以上红色字体部分的iop
```



## vsftp
```
目录权限不能为777，否则无法登录，配置文件每行末尾不要又空格

默认兼容主动和被动模式，添加配置限制被动模式端口   FlashFXP可以看到被动模式端口
#connect_from_port_20=YES 注释这行
pasv_enable=YES
pasv_promiscuous=YES
pasv_min_port=3000
pasv_max_port=3500


从2.3.5之后，vsftpd增强了安全检查，如果用户被限定在了其主目录下，则该用户的主目录不能再具有写权限了 allow_writeable_chroot=YES 可以取消这个限制
通过如下命令行可以解决  chmod a-w /home/user
chroot_local_user=YES   限定在主目录
chroot_list_enable=YES
# (default follows)
#chroot_list_file=/etc/vsftpd/chroot_list    这些用户作为“例外”，不受限制


yum install vsftpd curlftpfs
ftp的配置文件主要有三个，位于/etc/vsftpd/目录下，分别是：
ftpusers    该文件用来指定那些用户不能访问ftp服务器。
user_list   该文件用来指示的默认账户在默认情况下也不能访问ftp.
vsftpd.conf   vsftpd的主配置文件.
ftpusers和user_list用来控制登录用户。
ftpusers文件中的内容不受任何配制项的影响，总是有效，是一个黑名单！

更新虚拟用户数据
db_load -T -t hash -f /etc/vsftpd/vftpuser.txt /etc/vsftpd/vu_list.db 
/etc/init.d/vsftpd restart


vsftpd.conf中常用的配置内容：
    1、匿名用户能否上传和写文件，一般配置为NO
    anon_upload_enable=NO
    anon_mkdir_write_enable=NO
    匿名用户能否登录，视情况而定，看是否是专有用户使用。
    anonymous_enable=NO
    2、端口设定
    port_enable=YES，即默认情况下，FTP  PORT主动模式被启用
    connect_from_port_20=YES，即默认情况下，FTP PORT主动模式进行数据传输时使用20端口(ftp-data)。YES使用，NO不使用。
    ftp_data_port=port number，设定ftp数据传输端口(ftp-data)值。默认值为20。此参数用于PORT FTP模式。
    3、通信编码模式
    默认情况下可以通过ascii模式传输。将配置改为NO后，只能通过binary形式传输。
    ascii_upload_enable=YES
    ascii_download_enable=YES



匿名
默认匿名共享目录 /var/ftp
指定匿名共享目录 anon_root=/data/3mang_apps（目录权限不能为777，否则无法登录）

vim /etc/vsftpd/vsftpd.conf
anonymous_enable=YES    允许匿名用户
local_enable=YES                允许本地用户登陆
anon_world_readable_only=YES  匿名只读
或
anon_other_write_enable=YES  匿名可写
anon_upload_enable=YES            匿名可上传
anon_mkdir_write_enable=YES    匿名可以创建目录
local_max_rate=1000000--------------1M    限制上传下载的速度

日志相关
xferlog_enable=YES
xferlog_std_format=YES
xferlog_file=/var/log/xferlog  
dual_log_enable=YES
vsftpd_log_file=/var/log/vsftpd.log

挂载
curlftpfs ftp://$IP /mnt/

用户
将配置文件中”anonymous_enable=YES “改为 “anonymous_enable=NO”
添加chroot_list_enable=YES
        chroot_list_file=/etc/vsftpd/chroot_list
useradd ftpadmin -s /sbin/nologin -d /home/ftpadmin        用户目录权限755，777会无法使用(如果是两级目录，上级需要777)
passwd ftpadmin 修改密码
/etc/vsftpd/chroot_list 添加ftpadmin   用户的登录控制还可以参照上文中user_list进行设定。


虚拟目录
比如我的ftp的默认目录是/var/ftp，我想把/mnt/soft文件夹，映射到/var/ftp/a目录中，我就如下操作
我们要先在/var/ftp目录中建一个目录
[root@localhost ~]# mkdir /var/ftp/a                               然后执行mount命令
[root@localhost ~]# mount --bind /mnt/soft /var/ftp/a    这样就OK了。
[root@localhost etc]# vi /etc/fstab
将 /mnt/soft   /home/public  auto bind 0 0                         添加到/etc/fstab文件的末尾


虚拟用户
vim /etc/vsftpd/vftpuser.txt
user
passwd
user2
passwd2

db_load -T -t hash -f /etc/vsftpd/vftpuser.txt /etc/vsftpd/vu_list.db
chmod 600 /etc/vsftpd/vu_list.db

vi /etc/pam.d/vsftp.vu  新建一个虚拟用户的PAM文件   find / -name pam_userdb.so
auth required /usr/lib64/security/pam_userdb.so db=/etc/vsftpd/vu_list
account required /usr/lib64/security/pam_userdb.so db=/etc/vsftpd/vu_list

useradd -d /home/ftpsite virtual_user 建立虚拟用户
chmod 700 /home/ftpsite

编辑/etc/vsftpd/vsftpd.conf文件，使其整个文件内容如下所示（去掉了注释内容）：
anonymous_enable=NO
local_enable=YES
local_umask=022
xferlog_enable=YES
connect_from_port_20=YES
xferlog_std_format=YES
listen=YES
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_other_write_enable=YES
anon_umask=022
one_process_model=NO
chroot_local_user=YES
allow_writeable_chroot=YES
ftpd_banner=Welcom to my FTP server.
anon_world_readable_only=NO
guest_enable=YES
guest_username=virtual_user
pam_service_name=vsftp.vu
 
上面代码中，guest_enable=YES表示启用虚拟用户；
           guest_username=virtual_user则是将虚拟用户映射为本地用户，这样虚拟用户登录后权限和virtual_user一样；
           pam_service_name=vsftp.vu 指定PAM的配置文件为 vsftp.vu


在虚拟FTP服务器中，也可以对各个用户的权限进行设置。方法是在/etc/vsftpd.conf文件中添加如下一行：
user_config_dir=/etc/vsftpd/vsftpd_user_conf  用户配置文件目录

然后在用户配置文件目录下创建相应的用户配置文件，比如为上述名为gou的用户创建一个配置文件：
#vi /etc/vsftpd/vsftpd_user_conf/gou
write_enable=NO
anono_upload_enable=NO
local_root=家目录   将权限设为virtual_user

9.添加FTP用户的步骤
      1.在vftpuser.txt中添加用户名和密码
      2.运行如下命令,将用户名和密码添加到数据库中
        db_load -T -t hash -f /etc/vsftpd/vftpuser.txt /etc/vsftpd/vu_list.db
      3 在etc/vsftpd/vsftpd_user_conf文件夹下新建和用户名相同的文件,并在其中加入
       local_root=家目录
      4 重启ftp   systemctl restart vsftpd



四、FTP 的主动与被动模式
    FTP是基于TCP的服务，在实际应用中有两个接口：一个数据接口，一个控制接口。默认情况下这两个端口是21（控制端口）和20（数据端口）。
    主动方式的FTP是：客户端从一个任意的非特权端口N（N>1024）连接到FTP服务器的命令端口，也就是21端口。然后客户端开始监听端口N+1，
    并发送FTP命令“port N+1”到FTP服务器。接着服务器会从它自己的数据端口（20）连接到客户端指定的数据端口（N+1）。
    被动方式，或者叫做PASV，当客户端通知服务器它处于被动模式时才启用。在被动方式FTP中，命令连接和数据连接都由客户端发起.
    当开启一个 FTP连接时，客户端打开两个任意的非特权本地端口（N>1024和N+1）。第一个端口连接服务器的21端口，但与主动方式的FTP不同，
    客户端不会提交PORT命令并允许服务器来回连它的数据端口，而是提交 PASV命令。这样做的结果是服务器会开启一个任意的非特权端口
    （P > 1024），并发送PORT P命令给客户端。然后客户端发起从本地端口N+1到服务器的端口P的连接用来传送数据。 
    简单的来说，可以认为两者的区别主要在于客户端和服务器端到底是由谁来确定非特权端口，也就是这一对TCP通信组合的通道。
    如果是客户端先确定非特权端口就是主动模式，服务器端先确定非特权端口就是被动模式。（但实质上通信过程是不一样的，
    这种说法只可以做简单区分用）
五、FTP相关的防火墙设定
    当Linux系统启动了防火墙后，需要相应的对防火墙进行设定，防止防火墙阻断FTP通信。
 支持主动方式FTP，防火墙设定：    
1. 任何大于1024的端口到FTP服务器的21端口。（客户端初始化的连接） 
2. FTP服务器的21端口到大于1024的端口。 （服务器响应客户端的控制端口）
3. FTP服务器的20端口到大于1024的端口。（服务器端初始化数据连接到客户端的数据端口）
 4. 大于1024端口到FTP服务器的20端口（客户端发送ACK响应到服务器的数据端口）
支持被动方式的FTP，防火墙设定:  
1. 从任何大于1024的端口到服务器的21端口（客户端初始化的连接） 
2. 服务器的21端口到任何大于1024的端口（服务器响应到客户端的控制端口的连接）
3. 从任何大于1024端口到服务器的大于1024端口（客户端初始化数据连接到服务器指定的任意端口）
4. 服务器的大于1024端口到远程的大于1024的端口（服务器发送ACK响应和数据到客户端的数据端口）
下面以被动模式的防火墙为例给出示范：
    首先vi  /etc/vsftpd/vsftpd.conf文件中配置开启pasv被动模式：
    pasv_enable=YES
    设定非特权端口的通信范围（示例只做参考）：
    最小值pasv_min_port=10020
    最大值pasv_max_port=11020
    保存后注意配置后重启vsftpd服务。
    然后vi  /etc/sysconfig/iptables，配置系统防火墙：
    -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -p icmp -j ACCEPT
    -A INPUT -i lo -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 10020:11020 -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 20 -j ACCEPT
    -A INPUT -p tcp -m state --state NEW -m tcp --dport 21 -j ACCEPT
    保存后注意重启iptables服务。

    如果FTP服务器为云服务器或者有局域网路由控制，除了单独设定路由端口映射规则并在云服务器安全规则中添加例外，还要在
    /etc/vsftpd/vsftpd.conf中声明被动模式的公网地址，以防端口映射出现问题：
    pasv_address=111.111.111.111（示例）
    pasv_addr_resolve=yes
    pasv_promiscuous=yes

注：如果连接过程中出现200 PORT command successful. Consider using PASV.这条错误信息，不要轻易按照网上建议最多的
关闭PASV模式，只采用主动模式。因为在很多情况下客户端处于VLAN等网络环境下，很难主动给出链接端口，不得不采用被动模式，
出现这个错误并不能通过关闭PASV模式解决，而应该寻找PASV各方面的位置，找到配置中存在的问题进行解决。
```



## vsftpd-mysql结合
```
一、安装所需要程序

1、事先安装好开发环境和mysql数据库;

# yum -y install mysql-server mysql-devel
# yum -y groupinstall "Development Tools" "Development Libraries"

2.安装pam_mysql-0.7RC1

# tar zxvf  pam_mysql-0.7RC1.tar.gz
# cd  pam_mysql-0.7RC1
# ./configure --with-mysql=/usr --with-openssl
# make
# make install

3.安装vsftpd

# yum -y install vsftpd


二、创建虚拟用户账号

1.准备数据库及相关表

首先请确保mysql服务已经正常启动。而后，按需要建立存储虚拟用户的数据库即可，这里将其创建为vsftpd数据库。

mysql> create database vsftpd;

mysql> grant select on vsftpd.* to vsftpd@localhost identified by 'www.magedu.com';
mysql> grant select on vsftpd.* to vsftpd@127.0.0.1 identified by 'www.magedu.com';
mysql> flush privileges;

mysql> use vsftpd;
mysql> create table users (
    -> id int AUTO_INCREMENT NOT NULL,
    -> name char(20) binary NOT NULL,
    -> password char(48) binary NOT NULL,
    -> primary key(id)
    -> );

2、添加测试的虚拟用户

根据需要添加所需要的用户，需要说明的是，这里将其密码采用明文格式存储，原因是pam_mysql的password()函数与MySQL的password()函数
可能会有所不同。

mysql> insert into users(name,password) values('tom','magedu');
mysql> insert into users(name,password) values('jerry','magedu');


三、配置vsftpd

1.建立pam认证所需文件

#vi /etc/pam.d/vsftpd.mysql
添加如下两行
auth required /lib/security/pam_mysql.so user=vsftpd passwd=www.magedu.com host=localhost db=vsftpd table=users 
接上行 usercolumn=name passwdcolumn=password crypt=0
account required /lib/security/pam_mysql.so user=vsftpd passwd=www.magedu.com host=localhost db=vsftpd table=users 
接上行 usercolumn=name passwdcolumn=password crypt=0

2.修改vsftpd的配置文件，使其适应mysql认证

建立虚拟用户映射的系统用户及对应的目录
#useradd -s /sbin/nologin -d /var/ftproot vuser
#chmod go+rx /var/ftproot

请确保/etc/vsftpd.conf中已经启用了以下选项
anonymous_enable=YES
local_enable=YES
write_enable=YES
anon_upload_enable=NO
anon_mkdir_write_enable=NO
chroot_local_user=YES

而后添加以下选项
guest_enable=YES
guest_username=vuser

并确保pam_service_name选项的值如下所示
pam_service_name=vsftpd.mysql


四、启动vsftpd服务

# service vsftpd start
# chkconfig vsftpd on

查看端口开启情况

# netstat -tnlp |grep :21
tcp        0      0 0.0.0.0:21              0.0.0.0:*               LISTEN      23286/vsftpd 

使用虚拟用户登录,验正配置结果，以下为本机的命令方式测试，你也可以在其它Win Box上用IE或者FTP客户端工具登录验正
# ftp localhost



五、配置虚拟用户具有不同的访问权限

vsftpd可以在配置文件目录中为每个用户提供单独的配置文件以定义其ftp服务访问权限，每个虚拟用户的配置文件名同虚拟用户的用户名。
配置文件目录可以是任意未使用目录，只需要在vsftpd.conf指定其路径及名称即可。

1、配置vsftpd为虚拟用户使用配置文件目录

# vim vsftpd.conf
添加如下选项
user_config_dir=/etc/vsftpd/vusers_dir 

2、创建所需要目录，并为虚拟用户提供配置文件

# mkdir /etc/vsftpd/vusers_dir/
# cd /etc/vsftpd/vusers_dir/
# touch tom jerry

3、配置虚拟用户的访问权限

虚拟用户对vsftpd服务的访问权限是通过匿名用户的相关指令进行的。比如，如果需要让tom用户具有上传文件的权限，可以修改
/etc/vsftpd/vusers/tom文件，在里面添加如下选项即可。
anon_upload_enable=YES
```



## 实时同步lsyncd
```
1.1 inotify + rsync
最近一直在寻求生产服务服务器上的同步替代方案，原先使用的是inotify + rsync，但随着文件数量的增大到100W+，目录下的文件列表就达20M，
在网络状况不佳或者限速的情况下，变更的文件可能10来个才几M，却因此要发送的文件列表就达20M，严重减低的带宽的使用效率以及同步效率；
更为要紧的是，加入inotifywait在5s内监控到10个小文件发生变化，便会触发10个rsync同步操作，结果就是真正需要传输的才2-3M的文件，
比对的文件列表就达200M。使用这两个组合的好处在于，它们都是最基本的软件，可以通过不同选项做到很精确的控制，比如排除同步的目录，
同步多个模块或同步到多个主机。

搭建过程参考 Linux下同步工具inotify+rsync使用详解 或这里。

1.2 sersync
后来听同事说 sersync 这么个工具可以提高同步的性能，也解决了同步大文件时出现异常的问题，所以就尝试了一下。sersync是国内的一个
开发者开源出来的，使用c++编写，采用多线程的方式进行同步，失败后还有重传机制，对临时文件过滤，自带crontab定时同步功能。网上看到
有人说性能还不错，说一下我的观点：

国产开源，文档不是很全，在2011年之后就没更新了（googlecode都要快关闭了，其实可以转交其他人维护），网上关于它的使用和讨论都止于
10年了采用xml配置文件的方式，可读性比较好，但是有些原生的有些功能没有实现就没法使用了
无法实现多目录同步，只能通过多个配置文件启动多个进程
文件排除功能太弱。这个要看需求，不是每个人都需要排除子目录。而对于我的环境中，这个功能很重要，而且排除的规则较多
虽然提供插件的功能，但很鸡肋，因为软件本身没有持续更新，也没有看到贡献有其它插件出现（可能是我知识面不够，
还用不到里面的refreshCDN plugin）。
虽然不懂c++，但大致看了下源码 FileSynchronize，拼接rsync命令大概在273行左右，最后一个函数就是排除选项，
简单一点可以将--exclude=改成--eclude-from来灵活控制。有机会再改吧。

另外，在作者的文章 Sersync服务器同步程序 项目简介与设计框架 评论中，说能解决上面 rsync + inotify中所描述的问题。
阅读了下源码，这个应该是没有解决，因为在拼接rsync命令时，后面的目的地址始终是针对module的，只要执行rsync命令，
就会对整个目录进行遍历，发送要比对的文件列表，然后再发送变化的文件。sersync只是减少了监听的事件，减少了rsync
的次数——这已经是很大的改进，但每次rsync没办法改变。（如有其它看法可与我讨论）

其实我们也不能要求每一个软件功能都十分健全，关键是看能否满足我们当下的特定的需求。所谓好的架构不是设计出来的，而是进化来的。
目前使用sersync2没什么问题，而且看了它的设计思路应该是比较科学的，特别是过滤队列的设计。双向同步看起来也是可以实现。

1.3 lsyncd
废话说这么多，本文就是介绍它了。有些博客说lsyncd是谷歌开源的，实际不是了，只是托管在了googlecode上而已，
幸运的是已经迁移到github了：https://github.com/axkibe/lsyncd 。

Lysncd 实际上是lua语言封装了 inotify 和 rsync 工具，采用了 Linux 内核（2.6.13 及以后）里的 inotify 触发机制，
然后通过rsync去差异同步，达到实时的效果。我认为它最令人称道的特性是，完美解决了 inotify + rsync海量文件同步带来的
文件频繁发送文件列表的问题 —— 通过时间延迟或累计触发事件次数实现。另外，它的配置方式很简单，lua本身就是一种配置语言，
可读性非常强。lsyncd也有多种工作模式可以选择，本地目录cp，本地目录rsync，远程目录rsyncssh。

实现简单高效的本地目录同步备份（网络存储挂载也当作本地目录），一个命令搞定。

2. 使用 lsyncd 本地目录实时备份
这一节实现的功能是，本地目录source实时同步到另一个目录target，而在source下有大量的文件，并且有部分目录和临时文件不需要同步。

2.1 安装lsyncd
安装lsyncd极为简单，已经收录在ubuntu的官方镜像源里，直接通过apt-get install lsyncd就可以。
在Redhat系（我的环境是CentOS 6.2 x86_64 ），可以手动去下载 lsyncd-2.1.5-6.fc21.x86_64.rpm，但首先你得安装两个依赖
yum install lua lua-devel。也可以通过在线安装，需要epel-release扩展包：

# rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm# yum install lsyncd
源码编译安装
从源码编译安装可以使用最新版的lsyncd程序，但必须要相应的依赖库文件和编译工具：yum install lua lua-devel asciidoc cmake。

从 googlecode lsyncd 上下载的lsyncd-2.1.5.tar.gz，直接./configure、make && make install就可以了。

从github上下载lsyncd-master.zip 的2.1.5版本使用的是 cmake 编译工具，无法./configure：

# uzip lsyncd-master.zip# cd lsyncd-master# cmake -DCMAKE_INSTALL_PREFIX=/usr/local/lsyncd-2.1.5# make && make install
我这个版本编译时有个小bug，如果按照INSTALL在build目录中make，会提示：

[100%] Generating doc/lsyncd.1Updating the manpage
a2x: failed: source file not found: doc/lsyncd.1.txt
make[2]: *** [doc/lsyncd.1] Error 1make[1]: *** [CMakeFiles/manpage.dir/all] Error 2make: *** [all] Error 2
解决办法是要么直接在解压目录下cmake，不要mkdir build，要么在CMakeList.txt中搜索doc字符串，在前面加上${PROJECT_SOURCE_DIR}。

2.2 lsyncd.conf
下面都是在编译安装的情况下操作。

echo 8192000 > /proc/sys/fs/inotify/max_user_watches  执行并写入rc.local

2.2.1 lsyncd同步配置
# cd /usr/local/lsyncd-2.1.5# mkdir etc var# vi etc/lsyncd.confsettings {
    logfile      ="/usr/local/lsyncd-2.1.5/var/lsyncd.log",
    statusFile   ="/usr/local/lsyncd-2.1.5/var/lsyncd.status",
    inotifyMode  = "CloseWrite",
    maxProcesses = 7,
    -- nodaemon =true,
    }

sync {    default.rsync,
    source    = "/tmp/src",
    target    = "/tmp/dest",
    -- excludeFrom = "/etc/rsyncd.d/rsync_exclude.lst",
    rsync     = {
        binary    = "/usr/bin/rsync",
        archive   = true,
        compress  = true,
        verbose   = true
        }
    }
到这启动 lsycnd 就可以完成实时同步了，默认的许多参数可以满足绝大部分需求，非常简单。

2.2.2 lsyncd.conf配置选项说明
settings
里面是全局设置，--开头表示注释，下面是几个常用选项说明：

logfile 定义日志文件
stausFile 定义状态文件
nodaemon=true 表示不启用守护模式，默认
statusInterval 将lsyncd的状态写入上面的statusFile的间隔，默认10秒
inotifyMode 指定inotify监控的事件，默认是CloseWrite，还可以是Modify或CloseWrite or Modify
maxProcesses 同步进程的最大个数。假如同时有20个文件需要同步，而maxProcesses = 8，则最大能看到有8个rysnc进程
maxDelays 累计到多少所监控的事件激活一次同步，即使后面的delay延迟时间还未到
sync
里面是定义同步参数，可以继续使用maxDelays来重写settings的全局变量。一般第一个参数指定lsyncd以什么模式运行：rsync、
rsyncssh、direct三种模式：

default.rsync ：本地目录间同步，使用rsync，也可以达到使用ssh形式的远程rsync效果，或daemon方式连接远程rsyncd进程；
default.direct ：本地目录间同步，使用cp、rm等命令完成差异文件备份；
default.rsyncssh ：同步到远程主机目录，rsync的ssh模式，需要使用key来认证
source 同步的源目录，使用绝对路径。
target 定义目的地址.对应不同的模式有几种写法：
/tmp/dest ：本地目录同步，可用于direct和rsync模式
172.29.88.223:/tmp/dest ：同步到远程服务器目录，可用于rsync和rsyncssh模式，拼接的命令类似于/usr/bin/rsync -ltsd --delete 
--include-from=- --exclude=* SOURCE TARGET，剩下的就是rsync的内容了，比如指定username，免密码同步
172.29.88.223::module ：同步到远程服务器目录，用于rsync模式
三种模式的示例会在后面给出。
init 这是一个优化选项，当init = false，只同步进程启动以后发生改动事件的文件，原有的目录即使有差异也不会同步。默认是true
delay 累计事件，等待rsync同步延时时间，默认15秒（最大累计到1000个不可合并的事件）。也就是15s内监控目录下发生的改动，会累积到一次
rsync同步，避免过于频繁的同步。（可合并的意思是，15s内两次修改了同一文件，最后只同步最新的文件）
excludeFrom 排除选项，后面指定排除的列表文件，如excludeFrom = "/etc/lsyncd.exclude"，如果是简单的排除，可以使用exclude = LIST。
这里的排除规则写法与原生rsync有点不同，更为简单：
监控路径里的任何部分匹配到一个文本，都会被排除，例如/bin/foo/bar可以匹配规则foo
如果规则以斜线/开头，则从头开始要匹配全部
如果规则以/结尾，则要匹配监控路径的末尾
?匹配任何字符，但不包括/
*匹配0或多个字符，但不包括/
**匹配0或多个字符，可以是/
delete 为了保持target与souce完全同步,双向同步时改为false，Lsyncd默认会delete = true来允许同步删除。它除了false，还有startup
、running值，请参考 Lsyncd 2.1.x ‖ Layer 4 Config ‖ Default Behavior。
rsync
（提示一下，delete和exclude本来都是rsync的选项，上面是配置在sync中的，我想这样做的原因是为了减少rsync的开销）

bwlimit 限速，单位kb/s，与rsync相同（这么重要的选项在文档里竟然没有标出）
compress 压缩传输默认为true。在带宽与cpu负载之间权衡，本地目录同步可以考虑把它设为false
perms 默认保留文件权限。
其它rsync的选项
其它还有rsyncssh模式独有的配置项，如host、targetdir、rsync_path、password_file，见后文示例。rsyncOps={"-avz","--delete"}
这样的写法在2.1.*版本已经不支持。

lsyncd.conf可以有多个sync，各自的source，各自的target，各自的模式，互不影响。

2.3 启动lsyncd
使用命令加载配置文件，启动守护进程，自动同步目录操作。

lsyncd -log Exec /usr/local/lsyncd-2.1.5/etc/lsyncd.conf
2.4 lsyncd.conf其它模式示例
以下配置本人都已经过验证可行，必须根据实际需要裁剪配置：

settings {
    logfile ="/usr/local/lsyncd-2.1.5/var/lsyncd.log",
    statusFile ="/usr/local/lsyncd-2.1.5/var/lsyncd.status",
    inotifyMode = "CloseWrite",
    maxProcesses = 8,
    }


-- I. 本地目录同步，direct：cp/rm/mv。 适用：500+万文件，变动不大
sync {    default.direct,
    source    = "/tmp/src",
    target    = "/tmp/dest",
    delay = 1
    maxProcesses = 1
    }

-- II. 本地目录同步，rsync模式：rsync
sync {    default.rsync,
    source    = "/tmp/src",
    target    = "/tmp/dest1",
    excludeFrom = "/etc/rsyncd.d/rsync_exclude.lst",
    rsync     = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        bwlimit   = 2000
        } 
    }

-- III. 远程目录同步，rsync模式 + rsyncd daemon
sync {    default.rsync,
    source    = "/tmp/src",
    target    = "syncuser@172.29.88.223::module1",    delete="running",
    exclude = { ".*", ".tmp" },
    delay = 30,
    init = false,
    rsync     = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        verbose   = true,
        password_file = "/etc/rsyncd.d/rsync.pwd",
        _extra    = {"--bwlimit=200"}
        }
    }

-- IV. 远程目录同步，rsync模式 + ssh shell
sync {    default.rsync,
    source    = "/tmp/src",
    target    = "172.29.88.223:/tmp/dest",
    -- target    = "root@172.29.88.223:/remote/dest",
    -- 上面target，注意如果是普通用户，必须拥有写权限
    maxDelays = 5,
    delay = 30,
    -- init = true,
    rsync     = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        bwlimit   = 2000
        -- rsh = "/usr/bin/ssh -p 22 -o StrictHostKeyChecking=no"
        -- 如果要指定其它端口，请用上面的rsh
        }
    }

-- V. 远程目录同步，rsync模式 + rsyncssh，效果与上面相同
sync {    default.rsyncssh,
    source    = "/tmp/src2",
    host      = "172.29.88.223",
    targetdir = "/remote/dir",
    excludeFrom = "/etc/rsyncd.d/rsync_exclude.lst",
    -- maxDelays = 5,
    delay = 0,
    -- init = false,
    rsync    = {
        binary = "/usr/bin/rsync",
        archive = true,
        compress = true,
        verbose   = true,
        _extra = {"--bwlimit=2000"},
        },
    ssh      = {
        port  =  1234
        }
    }
上面的内容几乎涵盖了所有同步的模式，其中第III个要求像rsync一样配置rsyncd服务端，见本文开头。第IV、V配置ssh方式同步，达到的效果
相同，但实际同步时你会发现每次同步都会提示输入ssh的密码，可以通过以下方法解决：

在远端被同步的服务器上开启ssh无密码登录，请注意用户身份：

user$ ssh-keygen -t rsa
一路回车...
user$ cd ~/.ssh
user$ cat id_rsa.pub >> authorized_keys
把id_rsa私钥拷贝到执行lsyncd的机器上

user$ chmod 600 ~/.ssh/id_rsa
测试能否无密码登录
user$ ssh user@172.29.88.223
3. lsyncd的其它功能
lsyncd的功能不仅仅是同步，官方手册 Lsyncd 2.1.x ‖ Layer 2 Config ‖ Advanced onAction 高级功能提到，还可以监控某个目录下的
文件，根据触发的事件自己定义要执行的命令，example是监控某个某个目录，只要是有jpg、gif、png格式的文件参数，就把它们转成pdf，
然后同步到另一个目录。正好在我运维的一个项目中有这个需求，现在都是在java代码里转换，还容易出现异常，通过lsyncd可以代替这样的
功能。但，门槛在于要会一点点lua语言（根据官方example还是可以写出来）。

另外偶然想到个问题，同时设置了maxDelays和delay，当监控目录一直没有文件变化了，也会发生同步操作，虽然没有可rsync的文件。

TO-DO：

其它同步工具：csync2，clsync，btsync，drdb 。
lsyncd双向同步：GlusterFS
```


## inotify_sync
```
当web文件越来越多(百万级数量html,jpg等小 文件)，同步就越来越慢，根本做不到实时，按照网上的调优方法都尝试过，问题根本没有解决。
经过我一翻细致研究，终于把慢的核心问题研究明白，先总结一句 inotifywait响应不会有延迟，rsync也很快。大家同样有慢的烦恼，
那是因为网上的inotify+rsync的教程都是坑。下面我们来分 析。
inotifywait 单独分析

1
/usr/local/bin/inotifywait -mrq --format '%Xe %w%f' -e modify,create,delete,attrib /data/
执行上面命令，是让inotifywait监听/data/目录，当监听到有发生modify,create,delete,attrib等事件发生时，按%Xe %w%f的格式输出。
在/data/目录touch几个文件

1
touch /data/{1..5}
观看inotify输出


ATTRIB /data/1           -- 表示发生了ATTRIB事件 路径为/data/1
ATTRIB /data/2
ATTRIB /data/3
ATTRIB /data/4
ATTRIB /data/5
知道上面的输出效果之后 我们应该想得到，可以用rsync获取inotifywait监控到的文件列表来做指定的文件同步，而不是每次都由rsync
做全目录扫描来判断文件是否存在差异。
网上的inotify+rsync分析
我们来看网上的教程，我加了注释。(网上所有的教程基本都一模一样，尽管写法不一样，致命点都是一样的)


#!/bin/bash 
/usr/bin/inotifywait -mrq --format '%w%f'-e create,close_write,delete /backup |while read file
#把发生更改的文件列表都接收到file 然后循环，但有什么鬼用呢？下面的命令都没有引用这个$file 下面做的是全量rsync
do 
    cd /backup && rsync -az --delete /backup/ rsync_backup@192.168.24.101::backup/--password-file=/etc/rsync.password 
done
#注意看 这里的rsync 每次都是全量的同步(这就坑爹了)，而且 file列表是循环形式触发rsync ，等于有10个文件发生更改，就触发10次
rsync全量同步(简直就是噩梦)，那还不如直接写个死循环的rsync全量同步得了。
#有很多人会说 日志输出那里明明只有差异文件的同步记录。其实这是rsync的功能，他本来就只会输出有差异需要同步的文件信息。
不信你直接拿这句rsync来跑试试。
#这种在需要同步的源目录文件量很大的情况下，简直是不堪重负。不仅耗CPU还耗时，根本不可以做到实时同步。
改良方法
要做到实时，就必须要减少rsync对目录的递归扫描判断，尽可能的做到只同步inotify监控到已发生更改的文件。结合rsync的特性，
所以这里要分开判断来实现一个目录的增删改查对应的操作。
脚本如下


#!/bin/bash
src=/data/                          # 需要同步的源路径
des=data                             # 目标服务器上 rsync --daemon 发布的名称，rsync --daemon这里就不做介绍了，
网上搜一下，比较简单。
rsync_passwd_file=/etc/rsyncd.passwd            # rsync验证的密码文件
ip1=192.168.0.18                     # 目标服务器1
ip2=192.168.0.19                     # 目标服务器2
user=root                            # rsync --daemon定义的验证用户名
cd ${src}                            # 此方法中，由于rsync同步的特性，这里必须要先cd到源目录，inotify再监听 ./ 
才能rsync同步后目录结构一致，有兴趣的同学可以进行各种尝试观看其效果
/usr/local/bin/inotifywait -mrq --format '%Xe %w%f' -e modify,create,delete,attrib ./ | while read file         
# 把监控到有发生更改的"文件路径列表"循环
do

INO_EVENT=$(echo $file | awk '{print $1}') # 把inotify输出切割 把事件类型赋值给INO_EVENT

INO_FILE=$(echo $file | awk '{print $2}') # 把inotify输出切割 把文件路径赋值给INO_FILE

echo '------------------------------------'

echo $file

#增加、修改事件

#增、改放在同一个判断，因为他们都肯定是针对文件的操作，即使是新建目录，要同步的也只是一个空目录，不会影响速度。
if [[ $INO_EVENT =~ 'CREATE' ]] || [[ $INO_EVENT =~ 'MODIFY' ]] # 判断事件类型
then
echo 'CREATE or MODIFY'
rsync -avzR --password-file=/etc/rsync- client.pass ${INO_FILE} ${user}@${ip1}::${des} &&# INO_FILE 变量代表路径哦
rsync -avzR --password-file=/etc/rsync-client.pass ${INO_FILE} ${user}@${ip2}::${des}
#仔细看 上面的rsync同步命令 源是用了${INO_FILE}变量 即每次只针对性的同步发生改变的文件 然后用-R参数把源的目录结构递归到目标
后面 保证目录结构一致性

fi

#删除事件

if [[ $INO_EVENT =~ 'DELETE' ]]

then

echo 'DELETE'

rsync -avzR --delete --password-file=/etc/rsync-client.pass $(dirname ${INO_FILE}) ${user}@${ip1}::${des} &&

rsync -avzR --delete --password-file=/etc/rsync-client.pass $(dirname ${INO_FILE}) ${user}@${ip2}::${des}

#看rsync命令 如果直接同步已删除的路径${INO_FILE}会报no such or directory错误 所以这里同步的源是被删文件或目录的上一级路径，
并加上--delete来删除目标上有而源中没有的文件，这里不能做到指定文件删除，如果删除的路径越靠 近根，则同步的目录月多，同步删除的
操作就越花时间。这里有更好方法的同学，欢迎交流。

fi

#修改属性事件 指 touch chgrp chmod chown等操作

if [[ $INO_EVENT =~ 'ATTRIB' ]]

then

echo 'ATTRIB'

if [ ! -d "$INO_FILE" ] # 如果修改属性的是目录 则不同步，因为同步目录会发生递归扫描，等此目录下的文件发生同步时，rsync会
顺带更新此目录。

then

rsync -avzR --password-file=/etc/rsync-client.pass ${INO_FILE} ${user}@${ip1}::${des} &&

rsync -avzR --password-file=/etc/rsync-client.pass ${INO_FILE} ${user}@${ip2}::${des}

fi

fi
done
每两小时做1次全量同步
因为inotify只在启动时会监控目录，他没有启动期间的文件发生更改，他是不知道的，所以这里每2个小时做1次全量同步，防止各种意外遗漏
，保证目录一致。

1
2
crontab -e
* */2 * * * rsync -avz --password-file=/etc/rsync-client.pass /data/ root@192.168.0.18::data && rsync -avz 
--password-file=/etc/rsync-client.pass /data/ root@192.168.0.19::data
改良后我们公司这种百万级小文件也能做到实施同步了。
下面附上inotify的参数说明
inotify介绍-- 是一种强大的、细颗粒的、异步的文件系统监控机制，*&####&*_0_*&####&*内核从2.6.13起，加入Inotify可以监控
文件系统中添加、删除、修改移动等各种事件，利用这个内核接口，就可以监控文件系统下文件的各种变化情况。
inotifywait 参数说明
参数名称    参数说明
-m,–monitor    始终保持事件监听状态
-r,–recursive    递归查询目录
-q,–quiet    只打印监控事件的信息
–excludei    排除文件或目录时，不区分大小写
-t,–timeout    超时时间
–timefmt    指定时间输出格式
–format    指定时间输出格式
-e,–event    后面指定删、增、改等事件
inotifywait events事件说明
事件名称    事件说明
access    读取文件或目录内容
modify    修改文件或目录内容
attrib    文件或目录的属性改变
close_write    修改真实文件内容
close_nowrite    
close    
open    文件或目录被打开
moved_to    文件或目录移动到
moved_from    文件或目录从移动
move    移动文件或目录移动到监视目录
create    在监视目录下创建文件或目录
delete    删除监视目录下的文件或目录
delete_self    
unmount    卸载文件系统
优化 Inotify
# 在/proc/sys/fs/inotify目录下有三个文件，对inotify机制有一定的限制


[root@web ~]# ll /proc/sys/fs/inotify/
总用量0
-rw-r--r--1 root root 09月923:36 max_queued_events
-rw-r--r--1 root root 09月923:36 max_user_instances
-rw-r--r--1 root root 09月923:36 max_user_watches
-----------------------------
max_user_watches #设置inotifywait或inotifywatch命令可以监视的文件数量(单进程)
max_user_instances #设置每个用户可以运行的inotifywait或inotifywatch命令的进程数
max_queued_events #设置inotify实例事件(event)队列可容纳的事件数量
----------------------------

[root@web ~]# echo 50000000>/proc/sys/fs/inotify/max_user_watches -- 把他加入/etc/rc.local就可以实现每次重启都生效
[root@web ~]# echo 50000000>/proc/sys/fs/inotify/max_queued_events
```