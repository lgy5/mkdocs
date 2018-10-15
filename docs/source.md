## gem国内源
```
https://ruby.taobao.org/(不维护了)
http://gems.ruby-china.org/

$ gem sources --add http://gems.ruby-china.org/ --remove http://rubygems.org/
$ gem sources -l
*** CURRENT SOURCES ***
 
https://ruby.taobao.org
# 请确保只有 ruby.taobao.org
$ gem install rails
```


## cpan
```
cpan安装模块手工确认解决方法

方法一
在命令行执行如下命令：
cpan
o conf prerequisites_policy follow
o conf commit
exit

方法二
设置如下的环境变量
PERL_MM_USE_DEFAULT=1

更换国内源
vim /usr/share/perl5/CPAN/Config.pm  修改
'urllist' => [q[http://mirrors.163.com/cpan/]]
```

## rpmforge源
```
官网  http://pkgs.repoforge.org/rpmforge-release/（直接安装对应的rpm包）

国内 
http://mirror.bjtu.edu.cn/repoforge/

cat /etc/yum.repo.d/rpmforge.repo
### Name: RPMforge RPM Repository for RHEL 6 - dag
### URL: http://rpmforge.net/
[rpmforge]
name = RHEL $releasever - RPMforge.net - dag
baseurl = http://mirror.bjtu.edu.cn/repoforge/redhat/el6/en/$basearch/rpmforge
mirrorlist = http://mirror.bjtu.edu.cn/repoforge/redhat/el6/en/mirrors-rpmforge
#mirrorlist = file:///etc/yum.repos.d/mirrors-rpmforge
enabled = 1
protect = 0
gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-rpmforge-dag
gpgcheck = 0 
```


## yum仓库
```
企业yum仓库搭建实战

上面只是将自己制作的rpm包，放入yum源。但还有一种企业需求，说的更具体一点，平时学生上课yum安装软件都是从公网下载的，占用带宽，
因此在学校里搭建一个内网yum服务器，但又考虑到学生回家也要使用yum安装软件，如果yum软件的数据库文件repodata不一样，就会有问题。
因此我想到的解决方法就是直接使用公网yum源的repodata。



镜像同步公网yum源上游yum源必须要支持rsync协议，否则不能使用rsync进行同步。http://mirrors.ustc.edu.cn/status/

CentOS官方标准源：rsync://mirrors.ustc.edu.cn/centos/

epel源：rsync://mirrors.ustc.edu.cn/epel/

同步命令：

# 使用rsync同步yum源，为了节省带宽、磁盘和下载时间，我只同步了CentOS6的rpm包，这样所有的rpm包只占用了21G，全部同步需要300G左右。

# 同步base源，小技巧，我们安装系统的光盘镜像含有部分rpm包，大概3G，这些就不用重新下载。

/usr/bin/rsync -av
rsync://mirrors.ustc.edu.cn/centos/6/os/x86_64/
/data/yum_data/centos/6/os/x86_64/

/usr/bin/rsync -av
rsync://mirrors.ustc.edu.cn/centos/6/extras/x86_64/
/data/yum_data/centos/6/extras/x86_64/

/usr/bin/rsync -av rsync://mirrors.ustc.edu.cn/centos/6/updates/x86_64/
/data/yum_data/centos/6/updates/x86_64/

# epel源

/usr/bin/rsync -av –exclude=debug
rsync://mirrors.ustc.edu.cn/epel/6/x86_64/ /data/yum_data/epel/6/x86_64/

学生使用内网yum源方法

# 可以自建一个内网dns，如果没有，可使用hosts解析。

echo
‘192.168.0.200 mirrors.aliyun.com’ >>/etc/hosts
```

