## shell获取ip地址
```
使用ip库可以做到。但十分不方便。(nali)
nali安装
解压
./configue && make && make install
我这里用外部url来获取相关信息。
最常见的www.ip138.com  www.ip.cn什么的都可以获取到目标IP的地区和运营商。
但适用于shell脚本的还是ip.cn舒坦。
复制内容到剪贴板
代码:
[root@localhost ~]# curl ip.cn?ip=114.114.114.114
IP：114.114.114.114 来自：江苏省南京市 信风网络
[root@localhost ~]#
用curl命令就搞定了。但想把内容拆分一下给到变量使用时确发现他万恶的用了中文符号
复制内容到剪贴板
代码:
：
。
用awk -F 倒也是可以搞定。如下：
复制内容到剪贴板
代码:
[root@localhost ~]# cat getip.sh
#!/bin/bash
Getip=$(curl -s ip.cn?ip=$1)
IParea=$(echo $Getip|awk -F "：" '{print $3}'|awk '{print $1}')
IPisp=$(echo $Getip|awk -F "：" '{print $3}'|awk '{print $2}')
if [ ! $1 ];then
IP=$(echo $Getip|awk -F "：" '{print $2}'|awk '{print $1}')
echo $IP $IParea $IPisp
else
echo $1 $IParea $IPisp
fi
[root@localhost ~]# ./getip.sh 114.114.114.114
114.114.114.114 江苏省南京市 信风网络
但还是有点不方便。于是各种百度弄了段php的代码来转换一下ip.cn的输出结果：
复制内容到剪贴板
代码:
<?php
header("Content-Type: text/html;charset=utf-8");
        $user_IP = ($_SERVER["HTTP_VIA"]) ? $_SERVER["HTTP_X_FORWARDED_FOR"] : $_SERVER["REMOTE_ADDR"];
        $user_IP = ($user_IP) ? $user_IP : $_SERVER["REMOTE_ADDR"];
        $ip = ($_GET["ip"]) ? $_GET["ip"] : $user_IP;
 
        $ch = curl_init("http://www.ip.cn?ip=$ip");
                curl_setopt($ch,CURLOPT_USERAGENT,'curl/7.31');
                curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_BINARYTRANSFER, true);
                $output = curl_exec($ch);
                        $output2 = substr($output,5);
                        $row=split(' ',$output2);
                                $cip=$row[0];
                                $carea=substr($row[1],9);
                                $cisp=$row[2];
 
        $s = ($_GET["s"]) ? $_GET["s"] : "0";
                if ($s==0)
                {
                        echo "$cip $carea $cisp";
                }
                else
                {
                        $carea1=substr($carea,0,9);
                        echo "$cip $carea1 $cisp";
                }
 
        curl_close($ch);
?>
复制内容到剪贴板
代码:
[root@localhost html]# curl localhost?ip=114.114.114.114
114.114.114.114 江苏省南京市 信风网络
[root@localhost html]#
随便找个空间一放。以后用的时候直接访问自己的页面就可以了。
```



## 初始脚本
    #!/usr/bin/env bash
    for i in `chkconfig --list | awk '{print $1}'`;do
        if [[ $i = 'atd' || $i = 'crond' || $i = 'irqbalance' || $i = 'network' || $i = 'sshd' || $i = 'rsyslog' 
        || $i = 'httpd' || $i = salt-* || $i = zabbix_* ]];then
            chkconfig --level 3 $i on
        else
            chkconfig $i off
        fi
    done
    grep -v "^#" /etc/ssh/sshd_config | grep -v "^$" | grep "^UseDNS no" > /dev/null
    if [[ $? -ne 0 ]];then
        sed -i '122a\UseDNS no' /etc/ssh/sshd_config
        /etc/init.d/sshd restart
    fi
    cat  >>/etc/profile<<EOF
    if [ $SHELL = "/bin/ksh" ]; then
         ulimit -p 16384
         ulimit -n 65536
         ulimit -c unlimited
    else
         ulimit -u 16384 -n 65536 -c unlimited
    fi
    EOF

    source /etc/profile

    ##set ulimit file
    cat >> /etc/security/limits.conf<<EOF
    *           soft    nproc   10000
    *          hard    nproc   16384
    *           soft    nofile   65536
    *           hard    nofile  65536
    EOF


    ## set sysctl
    cat >>/etc/sysctl.conf <<EOF
    fs.aio-max-nr = 1048576
    fs.file-max = 6815744
    net.ipv4.ip_local_port_range = 10000 65000
    net.ipv4.ip_conntrack_max = 10240
    net.ipv4.tcp_max_syn_backlog = 65536
    net.core.netdev_max_backlog = 32768
    net.ipv4.tcp_syncookies = 1
    net.ipv4.tcp_tw_reuse = 1
    net.ipv4.tcp_tw_recycle = 1
    net.ipv4.tcp_fin_timeout = 30
    net.core.rmem_default=262144
    net.core.wmem_default=262144
    net.core.rmem_max=4194304
    net.core.wmem_max=4194304
    net.ipv4.tcp_timestamps =0
    net.ipv4.tcp_sack =1
    net.ipv4.tcp_window_scaling =1
    EOF

    sysctl -p

    ##install

    yum install -y @base ntp gcc gcc-c++ make telnet openssl lrzsz vim openssl-devel unzip gd gd-devel libcurl-devel

    ##set clock

    ntpdate us.pool.ntp.org


    ##set ssh port
    #set -- $(sed -n '/^Port/'p /etc/ssh/sshd_config)

    #port=$2

    #if [[ "xx${port}" == "xx" ]]
    #then
     #  cat >>/etc/ssh/sshd_config<<EOF
    #Port 7522
    #EOF
    #elif [[ ${port} -eq 7522 ]]
    #then
    #        sed -i "s/7522/22/g" /etc/ssh/sshd_config
    #        echo 'ok'
    #elif [[ ${port} -eq 22 ]]
    #then
    #        sed -i "s/22/7522/g" /etc/ssh/sshd_config
    #fi

    #service sshd restart
    ##set ssh listener ip is Private IP.



## ssh端口
```
ssh-copy-id -i .ssh/id_rsa.pub '-p 27005 root@192.168.3.129'
rsync '-e ssh -p Port'  

sftp -o port=9999 dachui@210.14.133.237

 vi ~/.ssh/config
 Port 20022
 cd ~/.ssh
 chmod 600 config
或者修改全局的
vi /etc/ssh/ssh_config
Port 20022
```



## txt转csv
```
sed 's/\t/,\t/g' jigou.txt > 1.csv  数据后面加，\t

sed 's/\t/\t,/g' jigou.txt > 1.csv  数据后面加 \t ，

导出csv文件数字会自动变科学计数法的解决方法
其实这个问题跟用什么语言导出csv文件没有关系。Excel显示数字时，如果数字大于12位，它会自动转化为科学计数法；
如果数字大于15位，它不仅用于科学技术费表示，还会只保留高15位，其他位都变0。
解决这个问题：
只要把数字字段后面加上显示上看不见的字符即可，字符串前面或者结尾加上制表符"\t".
```



## if判断
```
if ....; then
....
elif ....; then
....
else
....
fi

[[ $cpu_int > 600.0 ]]  小数比较不准，去掉小数点 在比较 awk -F '.' '{print $1}'

关键词匹配判断
if [[ "$CmdLine" =~ "install" ]]||[[ "$CmdLine" =~ "remove" ]]||[[ "$CmdLine" =~ "update" ]];then
        MAIL
fi

-b 文件
判断该文件是否存在，并且是否为块设备文件（是块设备文件为真）

-c文件
判断该文件是否存在，并且是否为字符设备文件（是字符设备文件为真）

-d 文件
判断该文件是否存在，并且是否为目录文件（是目录为真）

-e 文件
判断该文件是否存在（存在为真）

-f 文件
判断该文件是否存在，并且是否为普通文件（是普通文件为真）

-L 文件
判断该文件是否存在，并且是否为符号链接文件（是符号链接文件为真）

-p 文件
判断该文件是否存在，并且是否为管道文件（是管道文件为真）

-s 文件
判断该文件是否存在，并且是否为非空（非空为真）

-S 文件
判断该文件是否存在，并且是否为套接字文件（是套接字文件为真）

文件1 -nt 文件2
判断文件1的修改时间是否比文件2的新（如果新则为真）

文件1 -ot 文件2
判断文件1的修改时间是否比文件2的旧（如果旧则为真）

文件1 -ef 文件2
判断文件1是否和文件2的Inode号一致，可以理解为两个
文件是否为同一个文件。这个判断用于判断硬链接是很
好的方法

整数1 -eq 整数
判断整数1是否和整数2相等（相等为真）

整数1 -ne 整数
判断整数1是否和整数2不相等（不相等位置）

整数1 -gt 整数2
判断整数1是否大于整数2（大于为真）

整数1 -lt 整数2
判断整数1是否小于整数2（小于位置）

整数1 -ge 整数2
判断整数1是否大于等于整数2（大于等于为真）

整数1 -le 整数2
判断整数1是否小于等于整数2（小于等于为真）

-z 字符串
判断字符串是否为空（为空返回真）

-n 字符串
判断字符串是否为非空（非空返回真）

字串1 ==字串2
判断字符串1是否和字符串2相等（相等返回真）

字串1 != 字串2
判断字符串1是否和字符串2不相等（不相等返回真）

判断1 -a 判断2
逻辑与，判断1和判断2都成立，最终的结果才为真

判断1 -o 判断2
逻辑或，判断1和判断2有一个成立，最终的结果就为真

！判断
逻辑非，使原始的判断式取反
```



## 限制模式
```
bash -r


.bash_profile  添加 /bin/bash -r
.bashrc
set -o ignoreeof
alias exit="kill $(ps aux | grep logcat@pts | grep -v grep | awk '{print $2}')"

set -o option (开启)   set +o option(关闭)
set -o noclobber   该特性可防止重定向时不经意地重写了已存在的文件 
echo "kick" > tmp
-bash: tmp: Cannot overwrite existing file

set -o ignoreeof
之后，用户只能用logout或exit命令退出shell。

set -o noglob
配置noglob变量后，shell将不扩展文档名中一些特别的字符或字符串。如字符*、?、［］等将不再作为通配符

限制模式下被禁用的命令

在限制模式下运行一个脚本或部分脚本将禁用一些命令，尽管这些命令在正常模式下是可用的。这是个安全措施，可以限制脚本用户的权限，
减少运行脚本可能带来的损害。
被禁用的命令和功能：

使用 cd 来改变工作目录。
修改 $PATH, $SHELL, $BASH_ENV 或 $ENV 等环境变量
读取或修改 $SHELLOPTS，shell环境选项。
输出重定向。
调用包含 / 的命令。
调用 exec 来替代shell进程。
其他各种会造成混乱或颠覆脚本用途的命令。
在脚本中跳出限制模式。
```



## vip切换
```
#!/usr/bin/env bash
vip="192.168.1.20/24"
key="5"
stop_vip="/sbin/ifconfig em2:$key down"
start_vip="/sbin/ifconfig em2:$key $vip"
pingtest=$(fping 192.168.1.20 2> /dev/null | grep -c alive)
while true
do
 
if [ $pingtest -ne 1  ];then
    echo "redis master is down"
    $start_vip
    exit 1
else
    conne=$(/usr/local/redis-3.0.0/src/redis-cli -h 192.168.1.20 ping 2>/dev/null | grep -c PONG)
    if [ $conne -ne 1 ];then
        echo "redis master is unreachable"
        pingtest2=$(fping 192.168.1.20 2> /dev/null | grep -c alive)
        [ $pingtest2 -eq 1 ] && ssh root@192.168.1.5 $stop_vip
    $start_vip
        exit 2
    fi
fi
sleep 2
echo "======================"
done
```



## hostname主机名
```
修改/etc/sysconfig/network下的HOSTNAME   重启服务器生效
hostname +主机名  命令使其生效，重新登陆生效

可以一起修改
```



## sed
    sed 'N;s/\n/ /g'  两行变一行
    sed 'N;N;s/\n/ /g'  三行变一行

    #高级编辑命令
    h: 模式空间覆盖保持空间
    H：模式空间追加保持空间
    g：保持空间取出覆盖至模式空间
    G：保持空间取出追加至模式空间
    x: 模式空间互换保持空间
    n: 读取匹配到的行的下一行至模式空间
    N：读取匹配到的行和下一行至模式空间
    d: 删除模式空间中的行
    D：删除多行模式空间中的所有行
    sed 'n;d' test.txt    #显示奇数行
    sed -n '1~2p' test.txt    #显示奇数行
    sed -n 'n;p' ip    #显示偶数行
    sed -n '2~2p' test.txt    #显示偶数行
    sed '1!G;h;$!d' test.txt    #逆序显示文件内容
    sed '$!d' fsta    #取出文件最后一行
    sed 'G' test.txt    #每行追加空白行
    sed '/^$/d;G' test.txt    #每行追加空白行，多行空白行合并一个空白行

    #普通参数
    sed '/^#\|^$/d' fstab    #删除#和空行
    sed '1,8d' fstab    #1-8行删除
    sed '/^#/d' fstab----->sed -n '/^#/p' fstab  #相反
    sed '10a\"IP"' fstab    #第10行后追加
    sed '/^tmpfs/a\"IP"' fstab    #tmpfs开头的行后增加
    sed '/^tmpfs/a\Hello\nword' fstab    #追加两行
    sed '/^tmpfs/i\hello\nword' fstab   #在行前面追加
    sed '/^tmpfs/c\hello\nword' fstab     #替换匹配到的行
    sed '/^tmpfs/w b.txt' fstab    #查找出来的行写到b.txt
    sed '/^tmpfs/!d' fstab    #除了tmpfs的行删除
    sed 's/r..t/&er/g' /etc/passwd    #所有r..t的字符串后面加er
    sed 's/^[[:space:]]\+//' /boot/grub/grub.conf    #删除每行空白字符开头的空白字符
    echo "/etc/sysconfig" | sed 's#[^/]\+$##'    #取出目录


    sed引用变量
    sed命令使用双引号的情况下，使用$var直接引用
    $ echo|sed "s/^/$RANDOM.rmvb_/g" 
    sed命令使用单引号的情况下，使用'"$var"'引用，单引号加双引号
    $ echo|sed 's/^/'"$RANDOM"'.rmvb_/g' 

    sed中执行外部命令
    sed命令使用单引号的情况下使用'`shell command`'或者'$(shell command)'引用命令执行的结果 
    $ echo|sed 's/^/'`echo $RANDOM`'.rmvb_/g' 
    $ echo|sed 's/^/'$(echo $RANDOM)'.rmvb_/g' 
    $ echo|sed 's/^/'$(date +"%Y%m%d")'.rmvb_/g' 

    sed options script file
    语法：
    sed [options] '{command}[flags]' [filename]
    -e script 将脚本中指定的命令添加到处理输入时执行的命令中  多条件，一行中要有多个操作
    -f script 将文件中指定的命令添加到处理输入时执行的命令中
    -n        抑制自动输出
    -i        编辑文件内容，会破坏软硬链接，--follow-symlinks可以保留软链接
    -i.bak    修改时同时创建.bak备份文件。
    -r        使用扩展的正则表达式
    !         取反 （跟在模式条件后与shell有所区别）
    q         退出                           w 另存
    r filename读取文件  R 读取一行
    保持前面匹配的内容    （与正则分组类似）

    sed常用内部命令
    a   在匹配后面添加
    i   在匹配前面添加
    p   打印
    d   删除
    s   查找替换
    c   更改
    y   转换   N D P 
    h H 拷贝/添加模式空间到内存缓冲区
    g G 拷贝/添加内存缓冲区到模式空间
    /s replace

    echo "this is a test" |sed 's/test/text/'
    sed 's/dog/cat'/ data1
    sed -e 's/brown/green/;s/dog/cat/' data1

    sed -n '1p' data1       #显示第一行
    sed -n '$p' data1       #显示最后一行
    sed -n '1,2p' data1     #显示第一行到第二行
    sed -n '2,$p' data1     #显示第二行到最后一行

    s/pattern/repleacement/flags

    sed '1,3y/abc/ABC/' newfile 
    y命令就是将小写转换成了大写，正则表达式元字符不能使用这个命令

    flags
    数字  表示新文本替换的模式
    g：表示用新文本替换现有文本的全部实例
    p：表示打印原始的内容
    w file:将替换的结果写入文件

    sed '2{s/fox/elephant/;s/dog/cat/}' data1
    sed '2,${s/fox/elephant/;s/dog/cat/}' data1

    sed '1,10y/abcde/ABCDE/' example.file 
    把1—10行内所有abcde转变为大写，注意，正则表达式元字符不能使用这个命令。参数y，表示把一个字符翻译为另外的字符（但是不用于正则表达式）

    modify file
    sed -i

    sed -i '/修改点/i增加内容' filename
    sed -i '/修改点/d'  filename

    修改点可以是行号
    可是字符串【唯一字符串】
    增
    sed -i '4iabc' data3  在第四行之前插入abc
    sed -i '4aabc' data3  在第三行之后插入abc
    sed -i '/abc/c789' data3 将abc改为789

    删
    sed -i '4d' data3
    sed -i '/number 2/d' data3

    改
    将This is line number 2.改为 this is a test line number 2.
    sed -i '/line number 2/cthis is test line number 2' data3


    sed -n "$=" test  统计test有多少行

    sed 在指定位置插入一行

    正则表达式

    元字符集^
    锚定行的开始如：/^sed/匹配所有以sed开头的行。
    $
    锚定行的结束如：/sed$/匹配所有以sed结尾的行。
    .
    匹配一个非换行符的字符如：/s.d/匹配s后接一个任意字符，然后是d。
    *
    匹配零或多个字符如：/*sed/匹配所有模板是一个或多个空格后紧跟sed的行。
    []
    匹配一个指定范围内的字符，如/[Ss]ed/匹配sed和Sed。
    [^]
    匹配一个不在指定范围内的字符，如：/[^A-RT-Z]ed/匹配不包含A-R和T-Z的一个字母开头，紧跟ed的行。
    \(..\)
    保存匹配的字符，如s/\(love\)able/\1rs，loveable被替换成lovers。
    &
    保存搜索字符用来替换其他字符，如s/love/**&**/，love这成**love**。
    \<
    锚定单词的开始，如:/\<love/匹配包含以love开头的单词的行。
    \>
    锚定单词的结束，如/love\>/匹配包含以love结尾的单词的行。
    x\{m\}
    重复字符x，m次，如：/0\{5\}/匹配包含5个o的行。
    x\{m,\}
    重复字符x,至少m次，如：/o\{5,\}/匹配至少有5个o的行。
    x\{m,n\}
    重复字符x，至少m次，不多于n次，如：/o\{5,10\}/匹配5--10个o的行。



## awk函数
    awk 认为文件中的每一行是一条记录 记录与记录的分隔符为换行符
                    每一列是一个字段 字段与字段的分隔符默认为空格
    awk
    awk options program file

    获取指定时间端的日志 awk '$4>="[31/Jan/2018:16:00:00" && $4<="[31/Jan/2018:16:30:00"' log
    或  awk '{split($4,array,"[");if(array[2]>="31/Jan/2018:17:00:00" && array[2]<="31/Jan/2018:17:30:00"){print $0}}' log

    统计日志uv  awk '{a[$1]++} END{for(i in a)print i,a[i]}' localhost_access_log.2016-10-12.txt | wc -l
    pv                 wc -l  localhost_access_log.2016-10-12.txt

    列转行
    awk '{for(i=0;++i<=NF;)a[i]=a[i]?a[i] FS $i:$i}END{for(i=0;i++<NF;)print a[i]}' 1.txt
    name age                     alice 21         ====>       ryan 30


    行加求和  awk '{
                      sum=0 
                       for(n=1;n<5;n++)
                        (sum+=$n)
                        print sum}' t2
    列加求和  awk '{sum +=$1}END{print sum}' t2

    -F fs 指定描绘一行中数据字段的文件分隔符  默认为空格
    -f file 指定读取程序的文件名
    -v var=value 定义awk程序中使用的变量和默认值
    -mf N 指定数据文件中要处理的字段的最大数目
    -mr N 指定数据文件中的最大记录大小
    -w keyword 指定awk的兼容模式或警告级别

    awk 程序脚本由左大括号和右大括号定义。脚本命令必须放置在两个大括号之间。由于awk命令行假定脚本是单文本字符串，
    所以必须将脚本包括在单引号内。

    $0 表示整行文本
    $1 表示文本行中的第一个数据字段
    $2 表示文本行中的第二个数据字段
    $N                    N 
    $NF  


    通过awk进行输出排列
    将/etc/passwd文件中的 描述：UID：GID：shell按顺序输出【$5 $3 $4 $7】 

    输出格式如：
    　username: root UID: 0 GID: 0 SHELL: /bin/bash


    echo "my name is rich" | awk '{$4="dave";print $0}'

    从文件中读取程序

    [root@VFAST ~]# vim script2
    {
    print $5 "'s userid is " $1
    }

    [root@VFAST ~]# awk -F: -f script2 /etc/passwd


    在处理数据之前运行脚本 【插入文件头】
    [root@VFAST ~]# awk 'BEGIN {print "hello world!"}'
    hello world!


    高级awk command

    awk 支持两种不同类型的变量
    内置变量
    用户自定义变量


    内置变量
    1.字段和记录分隔符变量

    数据字段变量
    允许使用美元符和数据字段在记录中的数字位置引用数据记录中的单个数据字段   $1 $2 $n
    数据字段由字段分隔符号描述  默认为空格

    FS内置变量属于一组内置变量，他们用于控制awk在输入数据和输出数据中处理字段和记录的方式


    awk数据字段和记录变量

    变量                 描述
    FIELDWIDTHS          以空格分隔的数字列表，用空格定义每个数据字段的精确宽度
    FS                   输入字段分隔符号
    RS                   输入记录分隔符
    OFS                  输出字段分隔符号
    ORS                  输出记录分隔符号


    cat /etc/passwd
    [root@VFAST ~]# awk -F: '{print $1,$2,$3}' /etc/passwd
            等价
    [root@VFAST ~]# awk 'BEGIN {FS=":"} {print $1,$2,$3} ' /etc/passwd


    [root@VFAST ~]# awk 'BEGIN {FS=":";OFS="-"} {print $1,$2,$3} ' /etc/passwd


    FIELDWIDTHS 变量允许不使用字段分隔符读取记录，在某些应用程序中，数据不使用字段分隔符号，而是被放置的特定列中，
    在这种情况下必须使用FIELDWIDTHS变量以匹配记录中的数据布局

    vim data3

    1005.324759.37
    115-2.349194.00
    05b10.1298100.1

    [root@VFAST ~]# awk 'BEGIN{FIELDWIDTHS="3 5 2 5"}''{print $1,$2,$3,$4}' data3
    100 5.324 75 9.37
    115 -2.34 91 94.00
    05b 10.12 98 100.1

    RS ORS变量定义awk程序处理数据流中记录的方式，默认情况是换行符
    RS默认变量值表示输入数据流中文本的每个新行为一条新纪录
      有时数据字段分布在数据流的多行上，典型的例子是包含地址和电话号码的数据，他们分别在单独的行上

    [root@VFAST ~]# cat data7
    Riley Mullen
    123 Main Street
    Chicago,IL 60602
    (312)555-1234

    [root@VFAST ~]# awk 'BEGIN{FS="\n";RS=""} {print $1,$4}' data7
    Riley Mullen (312)555-1234

    将RS变量设置问空字符串，然后再数据流中的数据记录之间保留一个空行，awk会将每个空行解析为记录的分隔符
    [root@VFAST ~]# cat data7 |awk 'BEGIN{FS="\n";RS=""}{print $1,$2,$3,$4}'
    Riley Mullen 123 Main Street Chicago,IL 60602 (312)555-1234

    [root@VFAST ~]# awk 'BEGIN{FS="\n";OFS="-"} {print $1,$2,$3,$4}' data7
    Riley Mullen---
    123 Main Street---
    Chicago,IL 60602---
    (312)555-1234---


    vim vfast
    123
    456 789
    123456
    789


    awk 'BEGIN{RS="\n";ORS="***"}{print $0}' vfast



    用户自定义的变量
    在脚本中附值变量
    [root@VFAST ~]# awk 'BEGIN{
    > testing="this is a test"
    > print testing
    > testing=45
    > print testing
    > }'
    this is a test
    45


    数学计算

    [root@VFAST ~]# awk 'BEGIN{x=4;x=x*2+3;print x}'
    11

    在命令行中附值变量

    vim script0
    BEGIN{FS=":"}
    {print $n}
    [root@VFAST ~]# awk -f script0 n=1 /etc/passwd
    将$n变量附值为1


    使用数组
    awk 使用关联数组，其不同于数字数组，他的索引值可以是任何文本字符串，不需要使用使用一系列的数字来标识数组中包含的数组元素。
    关联数组由引用各个值的混杂的字符串构成。每个索引必须唯一。且唯一标识分配给它的数据元素

    定义数组变量
    var[index]=element
    var是变量名称，index是关联数组的索引值，而element是数据元素值
    EXAMPLES:
    var[1]=1
    var[2]=2

    [root@VFAST ~]# awk 'BEGIN{
    > var[1]=1
    > var[2]=2
    > total=var[1]+var[2]
    > print total
    > }'

    通过计算结果为3
    3


    awk 'NR==1{print $2}' /proc/meminfo  取/proc/memeinfo文件的第一列的第一行
    NR 指定行号


    打印第一行 第二行数值 

    awk 'NR==1{t=$2}NR==2{f=$2;print f/t*100}' /proc/meminfo


    vim aa
    1
    2
    3
    4

    awk '{ sum += $1 } END { print sum}' aa




    awk 'END{print NR}' test  统计test有多少行
    awk 'END{print $0}' test  打印最后一行


    awk 'END{print NF}' test  统计列数



    2.3.     条件操作符:


        <、<=、==、!=、>=、~ 匹配正则表达式、!~不匹配正则表达式


    匹配字符串
    == 精确匹配
    !=取反

    awk -F: '$1=="root"{print $0}' /etc/passwd
    awk -F: '$1!="root"{print $0}' /etc/passwd

    ~
    !~ 模糊匹配

    awk -F: '$1 ~ "ro"{print $0}' /etc/passwd

    awk -F: '$1 !~ "ro"{print $0}' /etc/passwd


    数字匹配

    > < >= <=   ==

    vim file
    1
    2
    3
    4

    awk '$1>2{print $0}' file
    awk '$1>=2{print $0}' file
    awk '$1<2{print $0}' file
    awk '$1<=2{print $0}' file
    awk '$1==2{print $0}' file


        匹配:awk '{if ($4~/ASIMA/) print $0}' temp 表示如果第四个域包含ASIMA，就打印整条

        精确匹配:awk '$3=="48" {print $0}' temp    只打印第3域等于"48"的记录

        不匹配:  awk '$0 !~ /ASIMA/' temp      打印整条不包含ASIMA的记录

        不等于:  awk '$1 != "asima"' temp

        小于:    awk '{if ($1<$2) print $1 "is smaller"}' temp

        设置大小写: awk '/[Gg]reen/' temp      打印整条包含Green，或者green的记录

        任意字符: awk '$1 ~/^...a/' temp    打印第1域中第四个字符是a的记录，符号’^’代表行首，符合’.’代表任意字符

        或关系匹配: awk '$0~/(abc)|(efg)/' temp   使用|时，语句需要括起来

        AND与关系:  awk '{if ( $1=="a" && $2=="b" ) print $0}' temp
        OR或关系:   awk '{if ($1=="a" || $1=="b") print $0}' temp


    awk 函数

    awk '{ if ( $1 > 9) print $1}'
    10


    awk `{if ($1 > 9) print $1 * 2} data`

    20

    or

    awk '{
    if ($1 > 9)
    {
    x=$1 * 2
    print x
    }}' data



    else

    awk '{ if ( $1 > 9 ) print $1 * 2;else print $1/2 }' data


    or

    awk '{if ($1>9)
    {
       x=$1 * 2
    print x
    }
    else
      {
        y=$1 / 2
    }}' data







    while语句

    while (condition)
    {
      satements
    }



    cat data1
    1 2 3
    4 5 6
    7 8 9

    awk '{
    total = 0
    i = 1
    while ( i < 4 )
    {
     total += $i
     i++
    }
    print total
    }' data1




    total +=$i
    i++
    的意思是将data1中的1 到3 个字段累加




    break continue


    awk '{
    total = 0
    i = 1
    while ( i < 4 )
    {
     total += $i
      if (i == 2)
        break
     i++
    }
    print total
    }' data1


    输出结果$1 + $2

    awk '{
    total = 0
    for (i=1;i<4;i++)
    {
    total += $i
    }
    print total
    }' data1


    输出结果
    $1+$2+$3的和


    do-while
    在检查之前执行语句
    do
    {
    statements
    }while (condition)


    awk '{
    total = 0
    i = 1
    do
    {
    total += $i
    i++
    }while (total < 150)
    print total}' data1


    判断total的值是否大于150  如果不大于150和后一个字段累加 如果大于150则输出该字段  如果累加大于150则不在往后累加



    关于while例子

    awk '{
    a=0
    i=1
    do
    {
    a+=$i
    i++
    }
    while (a>150)
    print a
    }' data
    10
    7
    3
    [root@instructor tmp]# awk '{
    a=0
    i=1
    do
    {
    a+=$i
    i++
    }
    while (a<150)
    print a
    }' data
    263
    187
    287

    错误死循环

    [root@instructor tmp]# awk '{
    a=0
    i=1
    do
    {
    a+=$i
    i++
    }
    while (a>150)
    print a
    }' data



    [root@instructor tmp]# cat data1
    100 110 20 
    160 150 140
    130 10 20



    当第二行$1是160  符合while条件为真，则继续累加$2  依然大于150  继续累加$3依然大于150  条件永远为真  自然不会跳出循环

    system函数
    在awk中调用系统shell命令

    awk 'BEGIN{system("echo hello")}'
    hello


    or
    [root@baism 桌面]# awk 'BEGIN{system("date")}'
    2014年 04月 30日 星期三 11:06:23 CST

    注意 一定要把system("") 中的命令用双引号引起来




    cat a.txt
    192.168.1
    192.168.2
    192.168.3
    172.16.3
    192.16.1
    192.16.2
    192.16.3
    10.0.4
    期望输出
    192.168.1-192.168.3
    172.16.3
    192.16.3-192.16.1
    10.0.4

    [root@instructor ~]# awk 'BEGIN{RS="";FS="\n";OFS="\n"}{print $1 "-" $3,$4,$7 "-" $4,$8}' aa.txt 
    192.168.1-192.168.3
    172.16.3
    192.16.3-172.16.3
    10.0.4

    zhangsan
    Beijing.China
    san@163.com
    010-12345678

    wangwu
    Tianjin.China
    wu@163.com
    010-23456789

    awk 'BEGIN{RS="";FS="\n"}{print "~~~~~~~~~~~~~~~~~~~~~~~~"}{print $1,$2 "\n" $3,$4}' data



## awk分析例子
```
Linux Web服务器网站故障分析常用的命令

系统连接状态篇：
1.查看TCP连接状态
netstat -nat |awk '{print $6}'|sort|uniq -c|sort -rn
netstat -n | awk '/^tcp/ {++S[$NF]};END {for(a in S) print a, S[a]}' 或
netstat -n | awk '/^tcp/ {++state[$NF]}; END {for(key in state) print key,"\t",state[key]}'
netstat -n | awk '/^tcp/ {++arr[$NF]};END {for(k in arr) print k,"t",arr[k]}'
netstat -n |awk '/^tcp/ {print $NF}' |sort|uniq -c|sort -rn
netstat -ant | awk '{print $NF}' | grep -v '[a-z]' | sort | uniq -c

2.查找请求数请20个IP（常用于查找攻来源）：
netstat -anlp|grep 80|grep tcp|awk '{print $5}'|awk -F: '{print $1}'|sort|uniq -c|sort -nr|head -n20
netstat -ant |awk '/:80/{split($5,ip,":");++A[ip[1]]}END{for(i in A) print A[i],i}' |sort -rn|head -n20

3.用tcpdump嗅探80端口的访问看看谁最高
tcpdump -i eth0 -tnn dst port 80 -c 1000 | awk -F"." '{print $1"."$2"."$3"."$4}’ | sort | uniq -c | sort -nr |head -20

4.查找较多time_wait连接
netstat -n|grep TIME_WAIT|awk '{print $5}'|sort|uniq -c|sort -rn|head -n20

5.找查较多的SYN连接
netstat -an | grep SYN | awk '{print $5}' | awk -F: '{print $1}’ | sort | uniq -c | sort -nr | more

6.根据端口列进程
netstat -ntlp | grep 80 | awk '{print $7}' | cut -d/ -f1



网站日志分析篇1（Apache）：
1.获得访问前10位的ip地址
cat access.log|awk '{print $1}’|sort|uniq -c|sort -nr|head -10
cat access.log|awk '{counts[$(11)]+=1}; END {for(url in counts) print counts[url], url}’

2.访问次数最多的文件或页面,取前20
cat access.log|awk '{print $11}’|sort|uniq -c|sort -nr|head -20

3.列出传输最大的几个exe文件（分析下载站的时候常用）
cat access.log |awk '($7~/.exe/){print $10 " " $1 " " $4 " " $7}’|sort -nr|head -20

4.列出输出大于200000byte(约200kb)的exe文件以及对应文件发生次数
cat access.log |awk '($10 > 200000 && $7~/.exe/){print $7}’|sort -n|uniq -c|sort -nr|head -100

5.如果日志最后一列记录的是页面文件传输时间，则有列出到客户端最耗时的页面
cat access.log |awk '($7~/.php/){print $NF " " $1 " " $4 " " $7}’|sort -nr|head -100

6.列出最最耗时的页面(超过60秒的)的以及对应页面发生次数
cat access.log |awk '($NF > 60 && $7~/.php/){print $7}’|sort -n|uniq -c|sort -nr|head -100

7.列出传输时间超过 30 秒的文件
cat access.log |awk '($NF > 30){print $7}’|sort -n|uniq -c|sort -nr|head -20

8.统计网站流量（G)
cat access.log |awk '{sum+=$10} END {print sum/1024/1024/1024}’

9.统计404的连接
awk '($9 ~/404/)’ access.log | awk '{print $9,$7}’ | sort

10. 统计http status
cat access.log |awk '{counts[$(9)]+=1}; END {for(code in counts) print code, counts[code]}'
cat access.log |awk '{print $9}'|sort|uniq -c|sort -rn

10.蜘蛛分析，查看是哪些蜘蛛在抓取内容。
/usr/sbin/tcpdump -i eth0 -l -s 0 -w - dst port 80 | strings | grep -i user-agent | grep -i -E 
'bot|crawler|slurp|spider'

网站日分析2(Squid篇）按域统计流量
zcat squid_access.log.tar.gz| awk '{print $10,$7}' |awk 'BEGIN{FS="[ /]"}{trfc[$4]+=$1}END
{for(domain in trfc){printf "%st%dn",domain,trfc[domain]}}'

数据库篇
1.查看数据库执行的sql
/usr/sbin/tcpdump -i eth0 -s 0 -l -w - dst port 3306 | strings | egrep -i 'SELECT|UPDATE|DELETE
|INSERT|SET|COMMIT|ROLLBACK|CREATE|DROP|ALTER|CALL'

系统Debug分析篇
1.调试命令
strace -p pid
2.跟踪指定进程的PID
gdb -p pid
```



## 找隐藏文件
```
ls -AF |grep '^\.'  只显示隐藏文件
find -name '.?*'
```



## expect密钥
```
生成密钥文件  ssh-keygen -q -t rsa -N "" -f /root/.ssh/id_rsa
yum install expect

expect "*"   匹配所有，空行等等。

#!/usr/bin/expect
set ip [lindex $argv 0]
set pass [lindex $argv 1]
spawn  ssh-copy-id -i /root/.ssh/id_rsa.pub $ip
expect {
    "(yes/no)?" {
        send "yes\n"
           expect "password:" {
            send "$pass\n"
           }
    }
 
    "password:" {
        send "$pass\n"
    }
}
expect eof

chmod expect_l1.sh
./expect_l1.sh ip pass
注意，不是bash脚本，不能sh except_l1.sh
-----------------------------------
sudo 
#!/usr/bin/expect
set timeout 10
spawn sudo -i
expect "*password*"
send "Tm121#^gnaM\n"
interact   #执行完成后保持交互状态，把控制权交给控制台

命令行 expect -c "spawn sudo -i;expect "*password*";send "Tm121#^gnaM"\n;interact"
```



## select交互
```
#!/bin/sh
PS3="make your choice in (1-4): "
select i in www groad net exit
do
    case $i in
         www) echo "1-www";;
         groad) echo "2-groad";;
         net) echo "3-net";;
         exit) exit;;
    esac
done
```



## 命令重定向
```
| 管道符接收标准输出，arping -h 2>&1 | tail -n 1  ,这样就可以接受标准错误输出（标准错误输出（stderr）默认也是输出到屏幕）

1，标准输入的控制
语法：命令< 文件将文件做为命令的输入。
例如：   mail -s “mail test” test@ahlinux.com < file1
将文件file1 当做信件的内容，主题名称为mail test，送给收信人。

2，标准输出的控制
语法：命令> 文件将命令的执行结果送至指定的文件中。
例如：    ls -l > list
将执行“ls -l” 命令的结果写入文件list 中。

语法：命令>! 文件将命令的执行结果送至指定的文件中，若文件已经存在，则覆盖。
例如：    ls -lg >! list 
将执行“ls - lg” 命令的结果覆盖写入文件list 中。

语法：命令>& 文件将命令执行时屏幕上所产生的任何信息写入指定的文件中。
例如：cc file1.c >& error
将编译file1.c 文件时所产生的任何信息写入文件error 中。

语法：命令 >> 文件将命令执行的结果附加到指定的文件中。
例如： ls - lag >> list
将执行“ls - lag” 命令的结果附加到文件list 中。

语法：命令 >>& 文件将命令执行时屏幕上所产生的任何信息附加到指定的文件中。
例如： cc file2.c >>& error
将编译file2.c 文件时屏幕所产生的任何信息附加到文件error 中。

关于输入、输出和错误输出

在字符终端环境中，标准输入/标准输出的概念很好理解。输入即指对一个应用程序或命令的输入，无论是从键盘输入还是从别的文件输入；
输出即指应用程序或命令产生的一些信息；与 Windows 系统下不同的是，Linux 系统下还有一个标准错误输出的概念，这个概念主要是
为程序调试和系统维护目的而设置的，错误输出于标准输出分开可以让一些高级的错误信息不干扰正常的输出信息，从而方便一般用户的使用。

在 Linux 系统中：标准输入（stdin）默认为键盘输入；标准输出（stdout）默认为屏幕输出；标准错误输出（stderr）默认也是输出到
屏幕（上面的 std 表示 standard）。在 BASH 中使用这些概念时一般将标准输出表示为 1，将标准错误输出表示为 2。下面我们举例来
说明如何使用他们，特别是标准输出和标准错误输出。

输入、输出及标准错误输出主要用于 I/O 的重定向，就是说需要改变他们的默认设置。
先看这个例子：
$ ls > ls_result
$ ls -l >> ls_result
上面这两个命令分别将 ls 命令的结果输出重定向到 ls_result 文件中和追加到 ls_result 文件中，而不是输出到屏幕上。">"就是
输出（标准输出和标准错误输出）重定向的代表符号，连续两个 ">" 符号，即 ">>" 则表示不清除原来的而追加输出。
再来看一个稍微复杂的例子：


$ find /home -name lost* 2> err_result
这个命令在 ">" 符号之前多了一个 "2"，"2>" 表示将标准错误输出重定向。由于 /home 目录下有些目录由于权限限制不能访问，因此
会产生一些标准错误输出被存放在 err_result 文件中。大家可以设想一下 find /home -name lost* 2》err_result 命令会产生什么结果？

如果直接执行 find /home -name lost* > all_result ，其结果是只有标准输出被存入 all_result 文件中，要想让标准错误输出和
标准输入一样都被存入到文件中，那该怎么办呢？看下面这个例子：


$ find /home -name lost* > all_result 2>& 1
上面这个例子中将首先将标准错误输出也重定向到标准输出中，再将标准输出重定向到 all_result 这个文件中。这样我们就可以将所有的
输出都存储到文件中了。为实现上述功能，还有一种简便的写法如下：


$ find /home -name lost* >& all_result
如果那些出错信息并不重要，下面这个命令可以让你避开众多无用出错信息的干扰：


$ find /home -name lost* 2> /dev/null
有兴趣的朋友，可以试验下如下的几种重定向方式，看看结果是什么？


$ find /home -name lost* > all_result 1>& 2
$ find /home -name lost* 2> all_result 1>& 2
$ find /home -name lost* 2>& 1 > all_result
另外一个非常有用的重定向操作符是 "-"，请看下面这个例子：


$ （cd /source/directory && tar cf - . ） | （cd /dest/directory && tar xvfp -）
该命令表示把 /source/directory 目录下的所有文件通过压缩和解压，快速的全部移动到 /dest/directory 目录下去，这个命令在 
/source/directory 和 /dest/directory 不处在同一个文件系统下时将显示出特别的优势。

另外，几种不常见的用法：
n<&- 表示将 n 号输入关闭
<&- 表示关闭标准输入（键盘）
n>&- 表示将 n 号输出关闭
>&- 表示将标准输出关闭
```



## while read
```
1、准备数据文件
$cat a.txt
200:2
300:3
400:4
500:5
 
2、用while循环从文件中读取数据
#!/bin/ksh
while read line
do
    echo $line
done < a.txt
```



## 高效不常见的命令
```
1. mv xxxx{,.bak}等同于mv xxxx xxxx.bak
2. esc + . 能填充之前命令的最后一个字段
3. diff <(ssh host1 cat file1) <(ssh host2 cat file2) diff两个远程文件
4. ctrl + r然后输入xxx，搜索之前包含xxx的命令
5. Python -m SimpleHTTPServer，启动一个HTTP服务器，可以用来下载文件
6. vim编辑文件后发现需要root权限， :w !sudo tee % 。(w：表示vim的修改操作，这个命令的输出更改后的文件到“标准输出”
！sudo tee % ：执行 一个 shell 命令， % 表示当前打开的这个文件的名字。
整个命令就是 将w的输出传给 tee，tee 在root 权限下 把更改的内容存在文件当中。)
7. ctrl+z可以把当前程序丢后台，fg命令可以恢复。
8. 退出su，退出ssh，可以用ctrl+d(真有人不知道这个，手敲exit, logout)。
9. sudo !!用sudo执行上条命令。
10. 如果在前台运行了一个程序，但是你需要退出终端，保持程序继续在后台运行，你可以这样：ctrl+z，把程序放在后台；
让程序继续运行；disown -h %1（%n是你jobs命令返回的那个，没有其它后台程序的话，一般是%1）。
```



## echo read
```
echo -e 解释转义字符  "\t" tab键      "\n"  回车
         -n  不换行
echo $?  上条命令状态码
echo $#   参数个数
echo $*    返回所有参数
$@基本上与上面相同。只不过是“$*”返回的是一个字符串，字符串中存在多外空格。“$@”返回多个字符串
echo $n  位置参数变量

B=$RANDOM  随机数
     $((RANDOM %10))  10以内的随机数

read  -p  打印信息
         -t   限定时间
         -s  不回显
         -n  输入字符个数
```



## 脚本控制
```
脚本控制


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
查看信号
kill -l 



crtl+C   SIGINT
ctrl+Z   SIGTSTP  暂停进程
程序退出   EXIT


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

信号捕获
trap 命令格式
trap commands signals      例如 trap "echo hehe" SIGINT  当收到ctrl-c时输出 hehe,多个信号 空格隔开


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
移除捕获
使用  “-” 移除捕获

trap - SIGINT  移除忽略ctrl-c信号


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
count=1
trap "echo hello" SIGINT   
while [ $count -lt 50 ]
  do
    echo "#loop $count"
             sleep 3
        count=$[$count + 1 ]
              if [ $count -eq 5 ]
                      then
                         trap - SIGINT
                         echo "I just remove the trap"
               fi
 done

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

trap "echo hello" SIGINT  捕获ctrl-c信号 如果在$count等于1-5的时候执行ctrl-c这忽略信号

if [ $count -eq 5 ]
                      then
                         trap - SIGINT
                         echo "I just remove the trap"
fi

在$count=5后 移除捕获
则受到ctrl-c之后中断



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


以后台模式运行脚本

nohup scripts &       and   &               jobs       kill %ID



演示的时候给脚本755 权限  执行不能使用sh

/script &  ## 1111

and

nohup /script & ##2222

注销用户 登陆在查看进程是否在     1111不在  2222在


运行多个后台程序     &

每运行一个后台程序 都会有一个后台作业号

./test1 &
./test2 &


此类后台运行当注销该账户的时候所有后台程序也退出



不使用控制台的情况下运行脚本   nohup scripts &




ctrl-z   bg  fg

ctrl-z  停止当前运行程序

fg 后台到前台

bg  启动后台停止程序




nice指定程序运行的优先级    -19   ----  20  值越小  优先级越大


nice -n -10 ./test &



renice  更改正在运行程序的优先级

renice 10 -p 1234       -p  pid



~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

任务定制

at   batch  cron


at  atq  atrm 




batch  让脚本在计算机负载比较低的情况下运行  

batch -f filename time     如果你定义的该时间服务器负载高 会延迟执行


cron    
定制cron任务表格

crontab -e



anacron 程序

cron只能在linux运行的时候执行  当linux关闭后就不会再运行了   anacron能够在机器关闭运行后检查程序使用的时间戳确定
程序是否在关闭服务器的时候错过了运行，如果错过了会安排程序尽快运行



anacron程序使用自己的表格 （/etc/anacron）指定作业

表格格式
period delay identifier command



period  定义作业应该间隔多久运行一次  以天为单位
delay   指定在anacron程序确定应该运行一个命令之后需要多长时间才会实际运行该命令，该选项可以为不同的命令设置不同的
执行延迟，避免在开机时大量程序执行

identifier 是一个唯一的非空字符串 可以唯一的标识日志消息和错误电子邮件中的作用
```



## cut sort
```
cut -c 指定字符   -c 1-5 1-5个字符  -c 5  第5个字符
    -d 列于列之间分隔符
    -f 指定列  -f1-3 1-3列 -f 4 第四列
    -b  byte  


sort  -r  倒序
        -n  按数字排序
        -k2  排序第2列
        -t:   指定：为分割符
```



## shell颜色
```
linux shell脚本的颜色

脚本中echo显示内容带颜色显示,echo显示带颜色，需要使用参数-e
　　格式如下：
　　echo -e "\033[字背景颜色；文字颜色m字符串\033[0m"
　　例如：
　　echo -e "\033[41;36m something here \033[0m"
　　其中41的位置代表底色， 36的位置是代表字的颜色
　　注： ?www.2cto.com ?
　　1、字背景颜色和文字颜色之间是英文的""
　　2、文字颜色后面有个m
　　3、字符串前后可以没有空格，如果有的话，输出也是同样有空格
　　下面是相应的字和背景颜色，可以自己来尝试找出不同颜色搭配

　　例
　　echo -e “\033[31m 红色字 \033[0m”
　　echo -e “\033[34m 黄色字 \033[0m”
　　echo -e “\033[41;33m 红底黄字 \033[0m”
　　echo -e “\033[41;37m 红底白字 \033[0m”
　　字颜色：30—–37
　　echo -e “\033[30m 黑色字 \033[0m”
　　echo -e “\033[31m 红色字 \033[0m”
　　echo -e “\033[32m 绿色字 \033[0m”
　　echo -e “\033[33m 黄色字 \033[0m”
　　echo -e “\033[34m 蓝色字 \033[0m”
　　echo -e “\033[35m 紫色字 \033[0m”
　　echo -e “\033[36m 天蓝字 \033[0m”
　　echo -e “\033[37m 白色字 \033[0m”

　　字背景颜色范围：40—–47
　　echo -e “\033[40;37m 黑底白字 \033[0m”
　　echo -e “\033[41;37m 红底白字 \033[0m”
　　echo -e “\033[42;37m 绿底白字 \033[0m”
　　echo -e “\033[43;37m 黄底白字 \033[0m”
　　echo -e “\033[44;37m 蓝底白字 \033[0m”
　　echo -e “\033[45;37m 紫底白字 \033[0m”
　　echo -e “\033[46;37m 天蓝底白字 \033[0m”
　　echo -e “\033[47;30m 白底黑字 \033[0m”
　　最后面控制选项说明 ?www.2cto.com ?
　　\33[0m 关闭所有属性
　　\33[1m 设置高亮度
　　\33[4m 下划线
　　\33[5m 闪烁
　　\33[7m 反显
　　\33[8m 消隐
?
　　\33[30m — \33[37m 设置前景色
　　\33[40m — \33[47m 设置背景色
　　\33[nA 光标上移n行
　　\33[nB 光标下移n行
　　\33[nC 光标右移n行
　　\33[nD 光标左移n行
　　\33[y;xH设置光标位置
　　\33[2J 清屏
　　\33[K 清除从光标到行尾的内容
　　\33[s 保存光标位置
　　\33[u 恢复光标位置
　　\33[?25l 隐藏光标
　　\33[?25h 显示光标
```



## 常用正则
```
一、校验数字的表达式
数字：^[0-9]*$
n位的数字：^\d{n}$
至少n位的数字：^\d{n,}$
m-n位的数字：^\d{m,n}$
零和非零开头的数字：^(0|[1-9][0-9]*)$
非零开头的最多带两位小数的数字：^([1-9][0-9]*)+(.[0-9]{1,2})?$
带1-2位小数的正数或负数：^(\-)?\d+(\.\d{1,2})?$
正数、负数、和小数：^(\-|\+)?\d+(\.\d+)?$
有两位小数的正实数：^[0-9]+(.[0-9]{2})?$
有1~3位小数的正实数：^[0-9]+(.[0-9]{1,3})?$
非零的正整数：^[1-9]\d*$ 或 ^([1-9][0-9]*){1,3}$ 或 ^\+?[1-9][0-9]*$
非零的负整数：^\-[1-9][]0-9″*$ 或 ^-[1-9]\d*$
非负整数：^\d+$ 或 ^[1-9]\d*|0$
非正整数：^-[1-9]\d*|0$ 或 ^((-\d+)|(0+))$
非负浮点数：^\d+(\.\d+)?$ 或 ^[1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0$
非正浮点数：^((-\d+(\.\d+)?)|(0+(\.0+)?))$ 或 ^(-([1-9]\d*\.\d*|0\.\d*[1-9]\d*))|0?\.0+|0$
正浮点数：^[1-9]\d*\.\d*|0\.\d*[1-9]\d*$ 或 ^(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|
([0-9]*[1-9][0-9]*))$
负浮点数：^-([1-9]\d*\.\d*|0\.\d*[1-9]\d*)$ 或 ^(-(([0-9]+\.[0-9]*[1-9][0-9]*)|([0-9]*[1-9][0-9]*\.[0-9]+)|
([0-9]*[1-9][0-9]*)))$
浮点数：^(-?\d+)(\.\d+)?$ 或 ^-?([1-9]\d*\.\d*|0\.\d*[1-9]\d*|0?\.0+|0)$

二、校验字符的表达式
汉字：^[\u4e00-\u9fa5]{0,}$
英文和数字：^[A-Za-z0-9]+$ 或 ^[A-Za-z0-9]{4,40}$
长度为3-20的所有字符：^.{3,20}$
由26个英文字母组成的字符串：^[A-Za-z]+$
由26个大写英文字母组成的字符串：^[A-Z]+$
由26个小写英文字母组成的字符串：^[a-z]+$
由数字和26个英文字母组成的字符串：^[A-Za-z0-9]+$
由数字、26个英文字母或者下划线组成的字符串：^\w+$ 或 ^\w{3,20}$
中文、英文、数字包括下划线：^[\u4E00-\u9FA5A-Za-z0-9_]+$
中文、英文、数字但不包括下划线等符号：^[\u4E00-\u9FA5A-Za-z0-9]+$ 或 ^[\u4E00-\u9FA5A-Za-z0-9]{2,20}$
可以输入含有^%&’,;=?$\”等字符：[^%&',;=?$\x22]+
禁止输入含有~的字符：[^~\x22]+

三、特殊需求表达式
Email地址：^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$
域名：[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(/.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+/.?
InternetURL：[a-zA-z]+://[^\s]* 或 ^http://([\w-]+\.)+[\w-]+(/[\w-./?%&=]*)?$
手机号码：^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$
电话号码(“XXX-XXXXXXX”、”XXXX-XXXXXXXX”、”XXX-XXXXXXX”、”XXX-XXXXXXXX”、”XXXXXXX”和”XXXXXXXX)：^($$\d{3,4}-)|
\d{3.4}-)?\d{7,8}$
国内电话号码(0511-4405222、021-87888822)：\d{3}-\d{8}|\d{4}-\d{7}
身份证号(15位、18位数字)：^\d{15}|\d{18}$
短身份证号码(数字、字母x结尾)：^([0-9]){7,18}(x|X)?$ 或 ^\d{8,18}|[0-9x]{8,18}|[0-9X]{8,18}?$
帐号是否合法(字母开头，允许5-16字节，允许字母数字下划线)：^[a-zA-Z][a-zA-Z0-9_]{4,15}$
密码(以字母开头，长度在6~18之间，只能包含字母、数字和下划线)：^[a-zA-Z]\w{5,17}$
强密码(必须包含大小写字母和数字的组合，不能使用特殊字符，长度在8-10之间)：^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}$
日期格式：^\d{4}-\d{1,2}-\d{1,2}
一年的12个月(01～09和1～12)：^(0?[1-9]|1[0-2])$
一个月的31天(01～09和1～31)：^((0?[1-9])|((1|2)[0-9])|30|31)$
钱的输入格式：
有四种钱的表示形式我们可以接受:”10000.00″ 和 “10,000.00″, 和没有 “分” 的 “10000″ 和 “10,000″：^[1-9][0-9]*$
这表示任意一个不以0开头的数字，但是，这也意味着一个字符”0″不通过，所以我们采用下面的形式：^(0|[1-9][0-9]*)$
一个0或者一个不以0开头的数字.我们还可以允许开头有一个负号：^(0|-?[1-9][0-9]*)$
这表示一个0或者一个可能为负的开头不为0的数字.让用户以0开头好了.把负号的也去掉，因为钱总不能是负的吧.下面我们要加的是说明
可能的小数部分：^[0-9]+(.[0-9]+)?$
必须说明的是，小数点后面至少应该有1位数，所以”10.”是不通过的，但是 “10″ 和 “10.2″ 是通过的：^[0-9]+(.[0-9]{2})?$
这样我们规定小数点后面必须有两位，如果你认为太苛刻了，可以这样：^[0-9]+(.[0-9]{1,2})?$
这样就允许用户只写一位小数。下面我们该考虑数字中的逗号了，我们可以这样：^[0-9]{1,3}(,[0-9]{3})*(.[0-9]{1,2})?$
1到3个数字，后面跟着任意个 逗号+3个数字，逗号成为可选，而不是必须：^([0-9]+|[0-9]{1,3}(,[0-9]{3})*)(.[0-9]{1,2})?$
备注：这就是最终结果了，别忘了”+”可以用”*”替代。如果你觉得空字符串也可以接受的话(奇怪，为什么?)最后，别忘了在用函数时去掉
去掉那个反斜杠，一般的错误都在这里
xml文件：^([a-zA-Z]+-?)+[a-zA-Z0-9]+\\.[x|X][m|M][l|L]$
中文字符的正则表达式：[\u4e00-\u9fa5]
双字节字符：[^\x00-\xff] (包括汉字在内，可以用来计算字符串的长度(一个双字节字符长度计2，ASCII字符计1))
空白行的正则表达式：\n\s*\r (可以用来删除空白行)
HTML标记的正则表达式：<(\S*?)[^>]*>.*?</\1>|<.*? /> (网上流传的版本太糟糕，上面这个也仅仅能部分，对于复杂的嵌套标记依旧无能为力)
首尾空白字符的正则表达式：^\s*|\s*$或(^\s*)|(\s*$) (可以用来删除行首行尾的空白字符(包括空格、制表符、换页符等等)，
非常有用的表达式)
腾讯QQ号：[1-9][0-9]{4,} (腾讯QQ号从10000开始)
中国邮政编码：[1-9]\d{5}(?!\d) (中国邮政编码为6位数字)
IP地址：\d+\.\d+\.\d+\.\d+ (提取IP地址时有用)
IP地址：((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))
```
