## lvs_keepalived
    LAN客户端判定哪个路由器应该为其到达目标主机的下一跳网关的方式有动态及静态决策两种方式，其中，觉的动态路由发现方式有如下几种：
    1、Proxy ARP —— 客户端使用ARP协议获取其想要到达的目标，而后，由某路由以其MAC地址响应此ARP请求；
    2、Routing Protocol —— 客户端监听动态路由更新(如通过RIP或OSPF协议)并以之重建自己的路由表；
    3、ICMP IRDP (Router Discovery Protocol) 客户端 —— 客户端主机运行一个ICMP路由发现客户端程序；

    动态路由发现协议的不足之处在于它会导致在客户端引起一定的配置和处理方面的开销，并且，如果路由器故障，切换至其它路由器的过程
    会比较慢。解决此类问题的一个方案是为客户端静态配置默认路由设备，这大大简化了客户端的处理过程，但也会带来单点故障类的问题。
    默认网关故障时，LAN客户端仅能实现本地通信。

    VRRP可以通过在一组路由器(一个VRRP组)之间共享一个虚拟IP(VIP)解决静态配置的问题，此时仅需要客户端以VIP作为其默认网关即可。

    图1显示了一个基本的VLAN拓扑，其中，Router A、B、C共同组成一个VRRP组，其VIP为10.0.0.1，配置在路由器A的物理接口上，因此A为
    master路由器，B和C为backup路由器。VRRP组中，master(路由器A)负责负责转发发往VIP地址的报文，客户端1、2、3都以此VIP作为其
    默认网关。一旦master故障，backup路由器B和C中具有最高优先级的路由器将成为master并接管VIP地址，而当原来的master路由器A重新
    上线时，其将重新成为master路由器。

    VRRP是一个“选举”协议，它能够动态地将一个虚拟路由器的责任指定至同一个VRRP组中的其它路由器上，从而消除了静态路由配置的单点故障。



    VRRP术语：

    VRRP虚拟路由(VRRP router)：



    VRRP的优势：

    冗余：可以使用多个路由器设备作为LAN客户端的默认网关，大大降低了默认网关成为单点故障的可能性；
    负载共享：允许来自LAN客户端的流量由多个路由器设备所共享；
    多VRRP组：在一个路由器物理接口上可配置多达255个VRRP组；
    多IP地址：基于接口别名在同一个物理接口上配置多个IP地址，从而支持在同一个物理接口上接入多个子网；
    抢占：在master故障时允许优先级更高的backup成为master；
    通告协议：使用IANA所指定的组播地址224.0.0.18进行VRRP通告；
    VRRP追踪：基于接口状态来改变其VRRP优先级来确定最佳的VRRP路由器成为master；





    配置keepalived为实现haproxy高可用的配置文件示例：

    ! Configuration File for keepalived  

    global_defs {  
       notification_email {  
             linuxedu@foxmail.com
             mageedu@126.com  
       }  
       notification_email_from kanotify@magedu.com 
       smtp_connect_timeout 3  
       smtp_server 127.0.0.1  
       router_id LVS_DEVEL  
    }  

    vrrp_script chk_haproxy {  
        script "killall -0 haproxy"  
        interval 1  
        weight 2  
    }  

    vrrp_script chk_mantaince_down {
       script "[[ -f /etc/keepalived/down ]] && exit 1 || exit 0"
       interval 1
       weight 2
    }

    vrrp_instance VI_1 {  
        interface eth0  
        state MASTER  # BACKUP for slave routers
        priority 101  # 100 for BACKUP
        virtual_router_id 51 
        garp_master_delay 1 

        authentication {  
            auth_type PASS  
            auth_pass password  
        }  
        track_interface {  
           eth0    
        }  
        virtual_ipaddress {  
            172.16.100.1/16 dev eth0 label eth0:0 
        }  
        track_script {  
            chk_haproxy  
            chk_mantaince_down
        }  


        notify_master "/etc/keepalived/notify.sh master"  
        notify_backup "/etc/keepalived/notify.sh backup"  
        notify_fault "/etc/keepalived/notify.sh fault"  
    } 


    注意：
    1、上面的state为当前节点的起始状态，通常在master/slave的双节点模型中，其一个默认为MASTER，而别一个默认为BACKUP。
    2、priority为当关节点在当前虚拟路由器中的优先级，master的优先级应该大于slave的；


    下面是一个notify.sh脚本的简单示例：
    #!/bin/bash
    # Author: MageEdu <linuxedu@foxmail.com>
    # description: An example of notify script
    # 

    vip=172.16.100.1
    contact='root@localhost'

    Notify() {
        mailsubject="`hostname` to be $1: $vip floating"
        mailbody="`date '+%F %H:%M:%S'`: vrrp transition, `hostname` changed to be $1"
        echo $mailbody | mail -s "$mailsubject" $contact
    }

    case "$1" in
        master)
            notify master
            /etc/rc.d/init.d/haproxy start
            exit 0
        ;;
        backup)
            notify backup
            /etc/rc.d/init.d/haproxy restart
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




    配置keepalived为实现haproxy高可用的双主模型配置文件示例：

    说明：其基本实现思想为创建两个虚拟路由器，并以两个节点互为主从。

    ! Configuration File for keepalived  

    global_defs {  
       notification_email {  
             linuxedu@foxmail.com
             mageedu@126.com  
       }  
       notification_email_from kanotify@magedu.com 
       smtp_connect_timeout 3  
       smtp_server 127.0.0.1  
       router_id LVS_DEVEL  
    }  

    vrrp_script chk_haproxy {  
        script "killall -0 haproxy"  
        interval 1  
        weight 2  
    }  

    vrrp_script chk_mantaince_down {
       script "[[ -f /etc/keepalived/down ]] && exit 1 || exit 0"
       interval 1
       weight 2
    }

    vrrp_instance VI_1 {  
        interface eth0  
        state MASTER  # BACKUP for slave routers
        priority 101  # 100 for BACKUP
        virtual_router_id 51 
        garp_master_delay 1 

        authentication {  
            auth_type PASS  
            auth_pass password  
        }  
        track_interface {  
           eth0    
        }  
        virtual_ipaddress {  
            172.16.100.1/16 dev eth0 label eth0:0 
        }  
        track_script {  
            chk_haproxy  
            chk_mantaince_down
        }  


        notify_master "/etc/keepalived/notify.sh master"  
        notify_backup "/etc/keepalived/notify.sh backup"  
        notify_fault "/etc/keepalived/notify.sh fault"  
    } 

    vrrp_instance VI_2 {  
        interface eth0  
        state BACKUP  # BACKUP for slave routers
        priority 100  # 100 for BACKUP
        virtual_router_id 52
        garp_master_delay 1 

        authentication {  
            auth_type PASS  
            auth_pass password  
        }  
        track_interface {  
           eth0    
        }  
        virtual_ipaddress {  
            172.16.100.2/16 dev eth0 label eth0:1
        }  
        track_script {  
            chk_haproxy  
            chk_mantaince_down
        }    
    }


    说明：
    1、对于VI_1和VI_2来说，两个节点要互为主从关系；











    LVS + keepalived的实现：

    ! Configuration File for keepalived  

    global_defs {  
       notification_email {  
             linuxedu@foxmail.com
             mageedu@126.com  
       }  
       notification_email_from kanotify@magedu.com 
       smtp_connect_timeout 3  
       smtp_server 127.0.0.1  
       router_id LVS_DEVEL  
    }  

    vrrp_script chk_schedown {
       script "[[ -f /etc/keepalived/down ]] && exit 1 || exit 0"
       interval 2
       weight -2
    }

    vrrp_instance VI_1 {  
        interface eth0  
        state MASTER  
        priority 101
        virtual_router_id 51 
        garp_master_delay 1 

        authentication {  
            auth_type PASS  
            auth_pass password  
        }  

        track_interface {  
           eth0    
        }  

        virtual_ipaddress {  
            172.16.100.1/16 dev eth0 label eth0:0
        }  

        track_script {  
            chk_schedown
        }    
    } 


    virtual_server 172.16.100.1 80 {
        delay_loop 6
        lb_algo rr 
        lb_kind DR
        persistence_timeout 50
        protocol TCP

    #    sorry_server 192.168.200.200 1358

        real_server 172.16.100.11 80 {
            weight 1
            HTTP_GET {
                url { 
                  path /
                  status_code 200
                }
                connect_timeout 3
                nb_get_retry 3
                delay_before_retry 3
            }
        }

        real_server 172.16.100.12 80 {
            weight 1
            HTTP_GET {
                url { 
                  path /
                  status_code 200
                }
                connect_timeout 3
                nb_get_retry 3
                delay_before_retry 3
            }
        }
    }


    如果要使用TCP_CHECK检测各realserver的健康状态，那么，上面关于realserver部分的定义也可以替换为如下内容：
    virtual_server 172.16.100.1 80 {
        delay_loop 6
        lb_algo rr 
        lb_kind DR
        persistence_timeout 300
        protocol TCP

        sorry_server 127.0.0.1 80

        real_server 172.16.100.11 80 {
            weight 1
            TCP_CHECK {
                tcp_port 80
                connect_timeout 3
            }
        }

        real_server 172.16.100.12 80 {
            weight 1
            TCP_CHECK {
                connect_port 80
                connect_timeout 3
              }
        }
    }

    说明：其中的sorry_server是用于定义所有realserver均出现故障时所用的服务器。










    keepalived通知脚本进阶示例：

    下面的脚本可以接受选项，其中：
    -s, --service SERVICE,...：指定服务脚本名称，当状态切换时可自动启动、重启或关闭此服务；
    -a, --address VIP: 指定相关虚拟路由器的VIP地址；
    -m, --mode {mm|mb}：指定虚拟路由的模型，mm表示主主，mb表示主备；它们表示相对于同一种服务而方，其VIP的工作类型；
    -n, --notify {master|backup|fault}：指定通知的类型，即vrrp角色切换的目标角色；
    -h, --help：获取脚本的使用帮助；

    #!/bin/bash
    # Author: MageEdu <linuxedu@foxmail.com>
    # description: An example of notify script
    # Usage: notify.sh -m|--mode {mm|mb} -s|--service SERVICE1,... -a|--address VIP  -n|--notify {master|backup|
    falut} -h|--help 

    #contact='linuxedu@foxmail.com'
    helpflag=0
    serviceflag=0
    modeflag=0
    addressflag=0
    notifyflag=0

    contact='root@localhost'

    Usage() {
      echo "Usage: notify.sh [-m|--mode {mm|mb}] [-s|--service SERVICE1,...] <-a|--address VIP>  <-n|--notify {master|
      backup|falut}>" 
      echo "Usage: notify.sh -h|--help"
    }

    ParseOptions() {
      local I=1;
      if [ $# -gt 0 ]; then
        while [ $I -le $# ]; do
          case $1 in
          -s|--service)
            [ $# -lt 2 ] && return 3
             serviceflag=1
             services=(`echo $2|awk -F"," '{for(i=1;i<=NF;i++) print $i}'`)
            shift 2 ;;
          -h|--help)
             helpflag=1
            return 0
            shift
            ;;
          -a|--address)
            [ $# -lt 2 ] && return 3
            addressflag=1
            vip=$2
            shift 2
            ;;
          -m|--mode)
            [ $# -lt 2 ] && return 3
            mode=$2
            shift 2
            ;;
          -n|--notify)
            [ $# -lt 2 ] && return 3
            notifyflag=1
            notify=$2
            shift 2
            ;;
          *)
            echo "Wrong options..."
            Usage
            return 7
            ;;
           esac
        done
        return 0
      fi
    }

    #workspace=$(dirname $0)

    RestartService() {
      if [ ${#@} -gt 0 ]; then
        for I in $@; do
          if [ -x /etc/rc.d/init.d/$I ]; then
            /etc/rc.d/init.d/$I restart
          else
            echo "$I is not a valid service..."
          fi
        done
      fi
    }

    StopService() {
      if [ ${#@} -gt 0 ]; then
        for I in $@; do
          if [ -x /etc/rc.d/init.d/$I ]; then
            /etc/rc.d/init.d/$I stop
          else
            echo "$I is not a valid service..."
          fi
        done
      fi
    }


    Notify() {
        mailsubject="`hostname` to be $1: $vip floating"
        mailbody="`date '+%F %H:%M:%S'`, vrrp transition, `hostname` changed to be $1."
        echo $mailbody | mail -s "$mailsubject" $contact
    }


    # Main Function
    ParseOptions $@
    [ $? -ne 0 ] && Usage && exit 5

    [ $helpflag -eq 1 ] && Usage && exit 0

    if [ $addressflag -ne 1 -o $notifyflag -ne 1 ]; then
      Usage
      exit 2
    fi

    mode=${mode:-mb}

    case $notify in
    'master')
      if [ $serviceflag -eq 1 ]; then
          RestartService ${services[*]}
      fi
      Notify master
      ;;
    'backup')
      if [ $serviceflag -eq 1 ]; then
        if [ "$mode" == 'mb' ]; then
          StopService ${services[*]}
        else
          RestartService ${services[*]}
        fi
      fi
      Notify backup
      ;;
    'fault')
      Notify fault
      ;;
    *)
      Usage
      exit 4
      ;;
    esac



    在keepalived.conf配置文件中，其调用方法如下所示：
        notify_master "/etc/keepalived/notify.sh -n master -a 172.16.100.1"  
        notify_backup "/etc/keepalived/notify.sh -n backup -a 172.16.100.1"  
        notify_fault "/etc/keepalived/notify.sh -n fault -a 172.16.100.1"  



## 配置
```
yum -y install httpd 的方式安装好httpd服务。
分别在192.168.1.103和192.168.1.104上做如下操作：
[root@centos ~]# yum -y install httpd
echo 103 >/var/www/html/index.html   #（104上的要把 103字段改成 104）
[root@centos ~]# setenforce 0   #关闭SELinux
[root@centos ~]# /etc/rc.d/init.d/iptables stop   #关闭防火墙

4、开始安装LVS
下载相关软件包：
[root@centos1 ~]# mkdir download
[root@centos1 ~]# cd download/
[root@centos1 download]# wget http://www.linuxvirtualserver.org/software/kernel-2.6/ipvsadm-1.24.tar.gz  
5、安装命令
注：以下安装需要在192.168.1.101和192.168.1.104上面操作：
[root@centos1 download]# uname -r   #查看linux内核版本  
2.6.32-220.el6.x86_64  
[root@centos1 download]# ln -s /usr/src/kernels/2.6.32-220.el6.x86_64/ /usr/src/linux #不做此步骤，安装会报错 
注：此ln命令的路径要和uname -r输出内核版本一致,如果没有 /usr/src/kernels/2.6.32-220.el6.x86_64/ 需要安装 kernel-devel软件包。 
[root@centos1 download]# tar zxvf ipvsadm-1.24.tar.gz  
[root@centos1 download]# cd ipvsadm-1.24  
[root@centos1 ipvsadm-1.24]# make  
[root@centos1 ipvsadm-1.24]# make install  
[root@centos1 ipvsadm-1.24]# ipvsadm  #执行ipvsadm命令，把LVS添加到linux内核中  
IP Virtual Server version 1.2.1 (size=4096)  
Prot LocalAddress:Port Scheduler Flags  
  -> RemoteAddress:Port       Forward Weight ActiveConn InActConn  
[root@centos1 ipvsadm-1.24]# lsmod | grep ip_vs  #查看LVS是否已经添加到linux内核了，如果有如下输出表示已经成功。  
ip_vs                 108133  0   
ipv6                  322029  154 ip_vs,ip6t_REJECT,nf_conntrack_ipv6,nf_defrag_ipv6  
6配置LVS 服务端
在192.168.1.101和192.168.1.114上分别配置LVS DR模式
1）、配置LVS，建立一个脚本配置LVS
注：192.168.1.101和192.168.1.114上配置都是一样的
[root@centos1 bin]# vim lvs_dr.sh
#!/bin/bash 
. /etc/init.d/functions 
vim lvs_dr.sh 
#!/bin/bash 
GW=192.168.1.1 
# website director vip. 
SNS_VIP=192.168.1.181 
SNS_RIP1=192.168.1.103 
SNS_RIP2=192.168.1.104 
 
logger $0 called with $1 
case "$1" in 
start) 
  # set squid vip 
  /sbin/ipvsadm --set 30 5 60 
  /sbin/ifconfig eth0:0 $SNS_VIP broadcast $SNS_VIP netmask 255.255.255.255 up 
  /sbin/route add -host $SNS_VIP dev eth0:0 
  /sbin/ipvsadm -A -t $SNS_VIP:80 -s wrr -p 3 
  /sbin/ipvsadm -a -t $SNS_VIP:80 -r $SNS_RIP1:80 -g -w 1 
  /sbin/ipvsadm -a -t $SNS_VIP:80 -r $SNS_RIP2:80 -g -w 1 
  touch /var/lock/subsys/ipvsadm >/dev/null 2>&1 
  ;; 
stop) 
  /sbin/ipvsadm -C 
  /sbin/ipvsadm -Z 
  ifconfig eth0:0 down 
  ifconfig eth0:1 down 
  route del $SNS_VIP 
  route del $SS_VIP 
  rm -rf /var/lock/subsys/ipvsadm >/dev/null 2>&1 
  echo "ipvsadm stoped" 
  ;; 
status) 
  if [ ! -e /var/lock/subsys/ipvsadm ];then 
  echo "ipvsadm stoped" 
  exit 1 
  else 
  echo "ipvsadm OK" 
  fi 
  ;; 
*) 
 echo "Usage: $0 {start|stop|status}" 
 exit 1 
esac 
 exit 0 
[root@centos1 bin]# chmod +x lvs_dr.sh
[root@centos1 bin]# cp lvs_dr.sh /etc/rc.d/init.d/   #方便启动
[root@centos1 bin]# service lvs_dr.sh start   #启动lvs服务
用ipvsadm -Ln 命令查看是否有如下输出，如有证明LVS配置成功
[root@centos1 bin]# ipvsadm
IP Virtual Server version 1.2.1 (size=4096)
Prot LocalAddress:Port Scheduler Flags
  -> RemoteAddress:Port           Forward Weight ActiveConn InActConn
TCP  192.168.1.181:http wrr persistent 3
  -> 192.168.1.104:http           Route   1      0          0         
  -> 192.168.1.103:http           Route   1      0          0         
7、配置LVS RS服务器
[root@centos bin]# vim lvs_dr.sh
#!/bin/bash
. /etc/init.d/functions
SNS_VIP=192.168.1.181
 
case "$1" in
start)
      ifconfig lo:0 $SNS_VIP netmask 255.255.255.255 broadcast $SNS_VIP
      /sbin/route add -host $SNS_VIP dev lo:0
      echo "1" >/proc/sys/net/ipv4/conf/lo/arp_ignore
      echo "2" >/proc/sys/net/ipv4/conf/lo/arp_announce
      echo "1" >/proc/sys/net/ipv4/conf/all/arp_ignore
      echo "2" >/proc/sys/net/ipv4/conf/all/arp_announce
      sysctl -p >/dev/null 2>&1
      echo "RealServer Start OK"
      ;;
stop)
     ifconfig lo:0 down
      route del $SNS_VIP >/dev/null 2>&1
      echo "0" >/proc/sys/net/ipv4/conf/lo/arp_ignore
      echo "0" >/proc/sys/net/ipv4/conf/lo/arp_announce
      echo "0" >/proc/sys/net/ipv4/conf/all/arp_ignore
      echo "0" >/proc/sys/net/ipv4/conf/all/arp_announce
      echo "RealServer Stoped"
      ;;
*)
      echo "Usage: $0 {start|stop}"
      exit 1
esac
exit 0
[root@centos bin]# cp lvs_dr.sh /etc/rc.d/init.d/
[root@centos bin]# service lvs_dr.sh start  #启动lvs RS服务器
RealServer Start OK 

yum install -y keepalived
global_defs { 
   notification_email { 
         edisonchou@hotmail.com 
   } 
   notification_email_from sns-lvs@gmail.com 
   smtp_server 192.168.80.1 
   smtp_connection_timeout 30
   router_id LVS_DEVEL  # 设置lvs的id，在一个网络内应该是唯一的
} 
vrrp_instance VI_1 { 
    state MASTER   #指定Keepalived的角色，MASTER为主，BACKUP为备         
    interface eth1  #指定Keepalived的角色，MASTER为主，BACKUP为备
    virtual_router_id 51  #虚拟路由编号，主备要一致
    priority 100  #定义优先级，数字越大，优先级越高，主DR必须大于备用DR   
    advert_int 1  #检查间隔，默认为1s
    authentication { 
        auth_type PASS 
        auth_pass 1111 
    } 
    virtual_ipaddress { 
        192.168.80.200  #定义虚拟IP(VIP)为192.168.2.33，可多设，每行一个
    } 
} 
# 定义对外提供服务的LVS的VIP以及port
virtual_server 192.168.80.200 80 { 
    delay_loop 6 # 设置健康检查时间，单位是秒                   
    lb_algo wrr # 设置负载调度的算法为wlc                  
    lb_kind DR # 设置LVS实现负载的机制，有NAT、TUN、DR三个模式  
    nat_mask 255.255.255.0               
    persistence_timeout 0         
    protocol TCP                 
    real_server 192.168.80.102 80 {  # 指定real server1的IP地址
        weight 3   # 配置节点权值，数字越大权重越高             
        TCP_CHECK { 
        connect_timeout 10        
        nb_get_retry 3 
        delay_before_retry 3 
        connect_port 80 
        } 
    } 
    real_server 192.168.80.103 80 {  # 指定real server2的IP地址
        weight 3  # 配置节点权值，数字越大权重越高 
        TCP_CHECK { 
        connect_timeout 10 
        nb_get_retry 3 
        delay_before_retry 3 
        connect_port 80 
        } 
     } 
}

3.5 配置从负载服务器
 
从负载服务器与主负载服务器大致相同，只是在keepalived的配置文件中需要改以下两处：
 
（1）将state由MASTER改为BACKUP
 
（2）将priority由100改为99
 
vrrp_instance VI_1 { 
    state BACKUP # 这里改为BACKUP
    interface eth1 
    virtual_router_id 51 
    priority 99 # 这里改为99，master优先级是100
    advert_int 1 
    authentication { 
        auth_type PASS 
        auth_pass 1111 
    } 
    virtual_ipaddress { 
        192.168.80.200 
    } 
} 

```



## 模式
```
LVS 简介
         LVS 是 Linux  Virtual Server ，Linux 虚拟服务器；是一个虚拟的服务器集群【多台机器 LB IP】。LVS 集群分为三层结构:
·负载调度器(load balancer)：它是整个LVS 集群对外的前端机器，负责将client请求发送到一组服务器[多台LB IP]上执行，而client端
认为是返回来一个同一个IP【通常把这个IP 称为虚拟IP/VIP】
·服务器池(server pool)：一组真正执行client 请求的服务器，一般是我们的web服务器；除了web，还有FTP，MAIL，DNS
·共享存储(shared stored)：它为 server pool 提供了一个共享的存储区，很容易让服务器池拥有相同的内容，提供相同的服务[不是很理解]
LVS 有4中常用的模式，分别讲一下4中模式的区别：
LVS  DR 模式
1.   DR(Direct  Routing)模式的网络结构：

        2.  工作的基本原理：
        (1). client 发送一个pv请求给VIP；VIP 收到这请求后会跟LVS设置的LB算法选择一个LB 比较合理的realserver，然后把此请求的
        package 的MAC地址修改为realserver的MAC地址；下面是我们通信的package的基本格式：


在这个通信的Package 有六个主要的字段：src mac 、 dst mac 、 src ip 、 src prot 、  dst ip 、 dst ip ；  现在这个包里面的 
dst mac 是LVS VIP的网卡MAC [在TCP 三次握手完成时就只知道dsp ip 和dsp mac了]
· DR 模式会把packet 里面的dst mac  改成 realserver的MAC 地址；然后VIP会把这个包广播到当前的这个LAN里面；所以，要提前保证VIP
 和 所有的realserver 在同一个网段，也就是在用过LAN里面。
同一个网段：用子网掩码来实现的，我们知道我们的网络中有局域网，一个局域网有很多台机器，这些LAN里面的所有机器都公用一个外网IP；我
们是怎样界定这个LAN的呢？用的就是网段号；IP只是是32位二进制数表示，这32位分为：网络位 + 主机位；表现在子网掩码是就是：网络位是1，
主机位是0；这样网络位 = IP  按位 与  子网掩码；所以，我们在把realserver 挂到LVS上前，需要确认DR模式，且IP 在同一个网段内。
·ARP协议会把这个包发送给真正的realserver【根据MAC 找到机器】
·把这个src ip----->realserver 的mac 地址建立一个hash表；这此次连接未断开前，同一个client发送的请求通过查询hash表，在次发送到
这台realserver上面；
·realserver 收到这个pachet后，首先判断dst ip 是否是自己的IP地址；如果不是就丢掉包；如果是就处理这个包。所以，DR模式还要在所有
的realserver 的机器上面绑定VIP的ip地址：
[html] view plain copy
1.  /sbin/ifconfig lo:0 inet VIP netmask 255.255.255.255   -----> 这个要注意！  
· 这样realserver 发现package 的dst 自己能识别【绑定了2个IP】，会处理这个包，处理完后把package的src  mac  dst mac  src ip 
  dst ip 都修改后再通过ARP 发送给VIP，通过VIP 发送给client。   realserver 发送给 VIP的package的格式：

· realserver 处理这个包后，会跟dst 为client ip 直接发送给 client ip；不经过lvs ；这样虽然效率比较高，但是有安全漏洞。 

                  LVS DR 工作的基本原理package 的详细信息：http://os.51cto.com/art/201105/264303.htm
         3.  LVS DR模式的注意情况：
·  LVS 的VIP 和 realserver 必须在同一个网段，不然广播后所有的包都会丢掉： 提前确认LVS/硬件LB 是什么模式，是否需要在同一个网段
·  所有的realserver 都必须绑定VIP的IP地址，否则realserver 收到package后发现dst 不是自己的I怕，所有包都会丢掉。
·  realserver·处理完包后直接把package 通过dst IP 发送给 client ，不通过LVS/迎接IP 了这样的LVS /VIP 效率会更高一点。
【通过把realserver的ip暴漏给外界，不是很安全】
LVS  NAT 模式
1.    LVS NAT 模式的网络结构：

            2.   NAT 模式的基本原理：
·   NAT 模式工作原理的模拟图：

·   client：202.100.1.2 
    VIP:     202.103.106.5    
                  realserver : 172.16.0.2  172.16.0.3  分别提供http 和ftp服务
        (1). 首先client 发送请求[package] 给VIP；
[html] view plain copy
1.  #client 发送给VIP的package：  
2.SOURCE 202.100.1.2:3478  EDST   202.103.106.5:80  
        (2). VIP 收到package后，会根据LVS设置的LB算法选择一个合适的realserver，然后把package 的DST IP 修改为realserver：   
[html] view plain copy
1.  # VIP 发送给realserver的package：  
2. SOURCE   202.100.1.2:3478  EDST   172.16.0.3：8000  
        (3). realserver 收到这个package后判断dst ip 是自己，就处理这个package ，处理完后把这个包发送给LVS VIP：
[html] view plain copy
1.  # realserver 处理完成后发送给VIP的package：  
2.   SOURCE   172.16.0.3：8000  EDST     202.100.1.2:3478    # lvs 收到这个package 后发现dst ip 不是自己的会不会
丢掉？感觉有错误  
       (4). LVS 收到这个package 后把sorce ip改成VIP的IP，dst ip改成 client ip然后发送给client：
[html] view plain copy
1.  #VIP收到package 后修改sourceip 发送给client的包：  
2.  SOURCE   202.103.106.5.80：80  EDST   202.100.1.2:3478  
           3. NAT 模式的注意事项：
· NAT 模式修改的是dst IP，直接走 switch 或pub 不需要修改MAC 所以，不需要VIP 和realserver 同在一个网段内。
· NAT 模式 package in  和package out 都需要经过LVS ；因此LVS 的可能会成为一个系统瓶颈问题。
LVS  FULL NAT 模式
1.     FULL NATT的基本原理：
              FULL NAT  在client请求VIP 时，不仅替换了package 的dst ip，还替换了package的 src ip；但VIP 返回给
              client时也替换了src ip；还是通过上面NAT 模式的工作原因的图进行分析 FULL NAT 的工作原理：
         (1). 首先client 发送请求[package] 给VIP；
[html] view plain copy
1.  #client 发送给VIP的package：  
2.SOURCE 202.100.1.2:3478  EDST   202.103.106.5:80  
        (2). VIP 收到package后，会根据LVS设置的LB算法选择一个合适的realserver，然后把package 的DST IP 修改为
        realserver；把sorce ip 改成 lvs 集群的LB IP   
[html] view plain copy
1.  # VIP 发送给realserver的package：  
2. SOURCE   172.24.101.135[lb ip]  EDST   172.16.0.3：8000  
        (3). realserver 收到这个package后判断dst ip 是自己，就处理这个package ，处理完后把这个包发送给LVS VIP：
[html] view plain copy
1.  # realserver 处理完成后发送给VIP的package：  
2.   SOURCE   172.16.0.3：8000  EDST     172.24.101.135[这个ip是 LVS VIP 集群的一太机器]     
       (4). LVS 收到这个package 后把sorce ip改成VIP的IP，dst ip改成 client ip然后发送给client：
[html] view plain copy
1.  #VIP收到package 后修改sourceip 发送给client的包：  
2.SOURCE   202.103.106.5.80：80  EDST   202.100.1.2:3478  
      2. FULL NAT 模式的注意事项：
·FULL NAT 模式也不需要 LBIP 和realserver ip 在同一个网段；
·full nat 跟nat 相比的优点是：保证RS回包一定能够回到LVS；因为源地址就是LVS--> 不确定
·full nat  因为要更新sorce ip 所以性能正常比nat 模式下降 10%
LVS  IP TUNNEL 模式
1.IP TUNNEL 模式的网络结构图：


       2. IP TUNNEL 模式的基本原理：
还是按NAT 模式的基本框架来说明TUNNEL 模式的基本原理：
        (1). 首先client 发送请求[package] 给VIP；
[html] view plain copy
1.  #client 发送给VIP的package：  
2.SOURCE 202.100.1.2:3478  DST   202.103.106.5:80  
        (2). VIP 收到package后，会根据LVS设置的LB算法选择一个合适的realserver；并把client发送的package 包装到一个
        新的IP包里面；新的IP包的dst是realserver的IP
[html] view plain copy
1.  # VIP 发送给realserver的package：  
2. client 发送的包  <strong>DST   172.16.0.3：8000</strong>  
        (3). realserver 收到这个package后判断dst ip 是自己，然后解析出来的package的dst是VIP；会检测我们的网卡上是否
        帮了VIP的ip地址；如果帮了就会处理这个包，如果没有直接丢掉。 我们一般在realserver上面 lo:0 绑定了VIP的ip地址，
        就可以处理
[html] view plain copy
1.  # realserver 处理完成后直接发送给client响应包：  
2. SOURCE   172.16.0.3：8000  DST      202.100.1.2:3478  【client ip】  
      3. IP TUNNEL 模式的注意：
·TUNNEL 模式必须在所有的realserver 机器上面绑定VIP的IP地址
·TUNNEL 模式的vip ------>realserver 的包通信通过TUNNEL 模式，不管是内网和外网都能通信，所以不需要lvs vip跟realserver 
在同一个网段内
·TUNNEL 模式 realserver会把packet 直接发给client 不会给lvs了
·TUNNEL 模式走的隧道模式，所以运维起来比较难，所以一般不用

  LVS  DR、NAT、FULL NAT、IP TUNNEL 模式的区别：
1.    是否需要lvs vip跟realserver 在同一个网段：
             DR 模式因为只修改 package的 MAC地址通过ARP广播的形势找到realserver，所以 要求LVS 的VIP 和realserver的IP
              必须在同一个网段内，也就是在挂载VIP 时先确认LVS的工作模式，如果是DR模式需要先确认这个IP 只是否能挂在这个LVS下面。
其他模式因为都会修改DST ip 为 realserver的IP 地址，所以不需要在同一个网段内
        2.   是否需要在realserver 绑定LVS vip 的IP 地址：
              realserver 收到package后会判断dst ip 是否是自己的ip，如果不是就直接丢掉包；因为DR模式dst 没有修改还是LVS
              的VIP；所以需要在realserver上面绑定VIP；IP TUNNEL 模式只是对package 重新包装一层，realserver解析后的IP包
              的DST  仍然是 LVS的VIP ；也需要在realserver上面绑定VIP；其他的都不需要
        3.   四种模式的性能比较：
因为DR模式   TP TUNELL 模式都是在package in 时经过LVS ；在package out是直接返回给client；所以二者的性能比NAT 模式高；
但IP TUNNEL 因为是TUNNEL 模式比较复杂，其性能不如DR模式；FULL NAT 模式因为不仅要更换 DST IP 还更换 SOURCE IP  所以性能比
NAT 下降10%
所以，4中模式的性能如下：DR  --> IP TUNNEL  --->NAT ----->FULL NAT
 LVS 实践中的积累
1. lvs 不会主动断开连接
比如 client 通过LVS VIP 采用长链接方式访问server，即使我们把LVS下面的realserver的status.html文件删除了；本来通过LVS 跟
这台realserver 链接的请求也不会被LVS
强制断开；要等到client自己断开连接；【在client主动断开期间；client可以跟这台realserver 正常通信】；这样有个好处时在网络
抖动时；LVS不会频繁的流量截断，到不同的RS上面
```



