## ant编译
```
<?xml version="1.0" encoding="UTF-8"?>
<!-- 定义一个工程，默认任务为warFile。 -->
<project name="Visit" default="warFile" basedir=".">
    
    <!-- 定义属性，打成war包的名称。 -->
    <property name="warFileName" value="CuiShou.war"></property>
    
    <!-- 定义路径，编译java文件时用到的jar包。 -->
    <path id="project.lib">
        <fileset dir="${basedir}/WebRoot/WEB-INF/lib">
            <include name="**/*.jar"/>
        </fileset>
        <fileset dir="/usr/local/tomcat_pingtai/lib">
            <include name="**/*.jar"/>
        </fileset>
    </path>
    
    <!-- 定义任务，清空任务：清空原有的class文件，创建新的build路径。 -->
    <target name="clean">
        <delete dir="${basedir}/build" />
        <mkdir dir="${basedir}/build" />
    </target>
    
    <!-- 定义任务，编译src文件夹中的java文件，编译后的class文件放到创建的文件夹下。 -->
    <target name="compile" depends="clean">
        <javac srcdir="${basedir}/src" destdir="${basedir}/build" includeantruntime="false">
            <compilerarg line="-encoding UTF-8" />
            <classpath refid="project.lib">
            </classpath>
            <compilerarg value="-XDignore.symbol.file"/>
        </javac>
        <copy todir = "${basedir}/build">
            <fileset dir="${basedir}/src" excludes="**/*.java"></fileset>   复制哪里的文件，根据实际更改
            <fileset dir="${basedir}/resources"><include name="**/**.*" /></fileset>
        </copy>
    </target>
    
    <!-- 定义默认任务，将class文件集合成jar包。 -->
    <target name="warFile" depends="compile">
        <!-- 删除原有war包。 -->
        <delete dir="${basedir}/${warFileName}" />
        <!-- 建立新war包。 -->
        <war destfile="${basedir}/${warFileName}" webxml="${basedir}/WebRoot/WEB-INF/web.xml">
            <!-- 将非jar和非class文件拷贝到war包的对应路径下。 -->
            <fileset dir="${basedir}/WebRoot">
                <include name="**/**.*" />
                <exclude name="**/*.jar"/>
                <exclude name="**/*.class"/>
            </fileset>
            <!-- 将jar和class文件拷贝到war包的对应路径下。 -->
            <lib dir="${basedir}/WebRoot/WEB-INF/lib" />
            <classes dir="${basedir}/build" />
        </war>
    </target>
    
</project>

```



## gitlab安装
```
gitlab
https://about.gitlab.com/downloads/#centos6

yum install curl openssh-server postfix cronie
service postfix start
chkconfig postfix on
lokkit -s http -s ssh
wget https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el6/gitlab-ce-8.9.8-ce.0.el6.x86_64.rpm
rpm -i gitlab-ce-XXX.rpm
gitlab-ctl reconfigure


默认账号
Username: root
Password: 5iveL!fe


gitlab + ldap

在/etc/gitlab/gitlab.rb 追加ldap配置 
# For omnibus packages
gitlab_rails['ldap_enabled'] = true
gitlab_rails['ldap_servers'] = YAML.load <<-EOS # remember to close this block with 'EOS' below
main: # 'main' is the GitLab 'provider ID' of this LDAP server
  label: 'LDAP'
  host: 'ldap_server_IP'
  port: 389
  uid: 'uid'
  method: 'plain' # "tls" or "ssl" or "plain"
  allow_username_or_email_login: true
  bind_dn: 'cn=xxx,dc=xxx,dc=com'
  password: 'PASSWPRD'
  active_directory: false
  base: 'ou=xxx,dc=xxx,dc=com'
  user_filter: ''
EOS
使配置生效

#gitlab-ctl reconfigure
至此gitlab 安装集成ldap完成


ldap登陆报错日志位置 /var/log/gitlab/gitlab-rails/production.log

gitlab服务启动关闭及重启

gitlab-ctl start|stop|restart
需要注意的是修改过/etc/gitlab/gitlab.rb 后 需要执行 

#gitlab-ctl reconfigure
ps 这个命令会执行chef将/etc/gitlab/gitlab.rb添加的参数加入 /var/opt/gitlab/gitlab-rails/etc/gitlab.yml

---------------------------

Gitlab 汉化及维护

由于服务对象是广大师生，为了降低新手上手的难度，所有进行汉化也是非常有必要的。好在国内有人已经进行了这方面的工作，我们
只需要共享其成果即可（欢迎向原项目提交高质量翻译）。

首先确认版本：

sudo cat /opt/gitlab/embedded/service/gitlab-rails/VERSION
并确认当前汉化版本的 VERSION 是否相同，当前最新的汉化版本为 8.6 。
如果安装版本小于当前汉化版本，请先升级。如果安装版本大于当前汉化版本，请在本项目中提交新的 issue。
如果版本相同，首先在本地 clone 仓库。

# GitLab.com 仓库
git clone https://gitlab.com/larryli/gitlab.git

# 或 Coding.net 镜像
git clone https://git.coding.net/larryli/gitlab.git
根据我的测试， Coding.net 的镜像不完整，clone 之后无法 checkout
然后比较汉化分支和原分支，导出 patch 用的 diff 文件。

# 8.1 版本的汉化补丁
git diff origin/8-6-stable..8-6-zh > ../8.6.diff
然后上传 8.6.diff 文件到服务器。

# 停止 gitlab
sudo gitlab-ctl stop
sudo patch -d /opt/gitlab/embedded/service/gitlab-rails -p1 < 8.6.diff
确定没有 .rej 文件，重启 GitLab 即可。

sudo gitlab-ctl start
如果汉化中出现问题，请重新安装 GitLab（注意备份数据）。

Gitlab 运维

管理
sudo gitlab-ctl start   # 启动所有 gitlab 组件
sudo gitlab-ctl stop   # 停止所有 gitlab 组件
sudo gitlab-ctl restart  # 重启所有 gitlab 组件
备份

备份GitLab repositories and GitLab metadata
在 crontab 中加入如下命令：

0 2 * * * /usr/bin/gitlab-rake gitlab:backup:create
恢复

首先进入备份 gitlab 的目录，这个目录是配置文件中的gitlab_rails['backup_path']，默认为/var/opt/gitlab/backups。

然后停止 unicorn 和 sidekiq ，保证数据库没有新的连接，不会有写数据情况。

sudo gitlab-ctl stop unicorn
# ok: down: unicorn: 0s, normally up
sudo gitlab-ctl stop sidekiq
# ok: down: sidekiq: 0s, normally up
然后恢复数据，1406691018为备份文件的时间戳

gitlab-rake gitlab:backup:restore BACKUP=1406691018
修改数据存储地址

默认情况下，gitlab 将数据存储在/var/opt/gitlab/git-data目录下，受限于分区情况&方便管理，我们需要将数据迁移到别的目录下。

无需数据迁移
如果还没有投入使用，则可以直接在配置文件中添加：

git_data_dir "/path/to/git-data"
然后执行：

sudo gitlab-ctl reconfigure
就可以生效了。

进行数据迁移
如果已经有数据了，则需要进行迁移。

首先需要暂停服务，避免用户在迁移期间读写数据：

sudo gitlab-ctl stop
然后使用rsync数据进行迁移：

注意前一个地址不需要/，后一个地址需要/，且只需要迁移repositories目录即可
sudo rsync -av /var/opt/gitlab/git-data/repositories /path/to/git-data/
然后运行配置工具以更新并重启服务：

官网文档是先更新配置再启动服务，但我在使用中发现先更新配置会提示无法连接上服务器，出现这种问题时可以先启动服务再更新配置。
sudo gitlab-ctl reconfigure
sudo gitlab-ctl start
最后不要忘了在网页端确认数据的地址是否正确。

关于权限问题
在使用中，我一开始创建了一个gitlabhq用户并创建了一个文件夹，然后修改地址，服务正常启动后提示500。
后来使用root账户在/home下直接创建文件夹解决了这个问题。
如果有遇到类似问题的，可以尝试用root创建目录。
监听IPv6

教育网拥有得天独厚的IPv6资源，所以为我们的gitlab服务添加IPv6支持很有必要。

修改/etc/gitlab/gitlab.rb文件中的：

# nginx['listen_addresses'] = ['*']
为

nginx['listen_addresses'] = ['*', '[::]']
然后执行

sudo gitlab-ctl reconfigure
然后就可以通过IPv6访问了。
```



## gitlab邮件
```
配置SMTP发送邮件配置，使用163邮箱。

$ sudo vi /etc/gitlab/gitlab.rb                           
# Change the external_url to the address your users will type in their browserexternal_url 'http://xxhost.com'
#Sending application email via SMTP
gitlab_rails['smtp_enable'] = true
gitlab_rails['smtp_address'] = "smtp.163.com"
gitlab_rails['smtp_port'] = 25
gitlab_rails['smtp_user_name'] = "xxuser@163.com"
gitlab_rails['smtp_password'] = "xxpassword"
gitlab_rails['smtp_domain'] = "163.com"
gitlab_rails['smtp_authentication'] = :login
gitlab_rails['smtp_enable_starttls_auto'] = true
##修改gitlab配置的发信人
gitlab_rails['gitlab_email_from'] = "xxuser@163.com"
user["git_user_email"] = "xxuser@163.com"
（网易服务器smtp机器要求身份验证帐号和发信帐号必须一致，如果用户在发送邮件时，身份验证帐号和发件人帐号是不同的，因此拒绝发送。）

gitlab-ctl reconfigure  配置生效
gitlab-ctl tail  查看相关日志
```



## git
```
http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000

git config
git config --global user.name name
git config --global user.email email

获取远程仓库并合并
git pull https://github.com/XX-net/XX-Net.git master
git add .
git commit -m 'net'
git push -u origin master(第一次上传)
git push(之后上传)

.gitignore文件不起作用时清理cache
git rm -r --cached .
git add .
git commit -m 'update .gitignore'


yum install curl-devel expat-devel gettext-devel openssl-devel zlib-devel #依赖

yum install git

创建版本库
mkdir learngit
cd learngit
git init
git add readme.txt #把文件添加到仓库
git commit -m "wrote a readme file" #把文件提交到仓库


git status        #仓库当前的状态
git diff filename #就是查看difference，显示的格式正是Unix通用的diff格式

版本回退
git log
git reset --hard commit开头 #版本号没必要写全，前几位就可以了

git reflog
54edaa9 HEAD@{2}: commit: 3
967d2cd HEAD@{3}: commit: m
git reset --hard 54edaa9

git checkout其实是用版本库里的版本替换工作区的版本，无论工作区是修改还是删除，都可以“一键还原”

分支
git branch dev   #创建dev分支
git checkout dev #切换dev分支
git branch       #查看当前分支
git checkout -b <name>  创建+切换分支

git checkout master 切换回master分支
git merge dev 把dev分支的工作成果合并到master分支

git branch -d dev 删除dev分支


搭建Git服务器
安装git
useradd git
收集所有客户端的公钥，~/.ssh/id_rsa.pub文件，把所有公钥导入到/home/git/.ssh/authorized_keys文件里，一行一个。
cd /srv
git init --bare sample.git
git init
chown -R git:git sample.git
修改/etc/passwd git:x:1001:1001:,,,:/home/git:/usr/bin/git-shell

git clone git@server:/srv/sample.git #克隆git库
git pull #更新git库
```

## git clean
```
清除历史记录 并创建新项目

1、rm -rf .git

2、
git init
git add .
git commit -m "Initial commit"

3、
git remote add origin <github-uri>
git push -u --force origin master

```

## jenkins
```
http://pkg.jenkins-ci.org/redhat/

wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat/jenkins.repo
rpm --import http://pkg.jenkins-ci.org/redhat/jenkins-ci.org.key
yum install java jenkins

jenkins的邮件报警发件人要和管理邮箱一样

构建后脚本（例子）

#!/bin/bash

[ ! -d ../package ] && mkdir ../package
tar -zcf ../package/$JOB_NAME-$tag.tar.gz .
```

## svn
```
. 1.  安装  SVN （3 3  台主机上都执行 ） 【默认端口： 3690 】
yum -y install subversion
. 2.  创建目录并初始化
mkdir -pv /tmp/svn
svnadmin create /tmp/svn #初始化SVN的仓库，用于存放代码
. 3.  准备代码
mkdir -pv /tmp/www/{trunk,branches,tags} #创建主干、分支、里程碑目录
echo csn > /tmp/www/trunk/a.html
. 4.  导入代码
svn import /tmp/www/ file:///tmp/svn/www -m 'project D'
#将/tmp/www目录的代码导入到/tmp/svn/www 里，并标识为project D
. 5.  修改启动配置文件
vim /etc/init.d/svnserve
. 6.  启动服务
service svnserve start
. 7.  开启上传权限（# # 默认任何人都可以下载，但无上传权限 ）
vim /tmp/svn/conf/svnserve.conf （ 配置文件必须顶到行首 ）
#取消以上四行的注释
. 8.  添加上传用户身份
vim /tmp/svn/conf/passwd
dev = client #添加用户格式：用户名 = 密码
. 9.  代码同步
#客户端下载代码
cd /var/www/html #代码下载目录
svn checkout svn://192.168.38.1/www
#客户端上传代码
echo upload_test > /var/www/html/www/trunk/b.html
svn add /var/www/html/www/trunk/b.html
cd /var/www/html/www/ #代码同步到本地的根目录（工作副本）
svn commit -m ‘version2’
#需进入同步目录中（工作副本），提交上传，并标识version2
10. 版本更新
svn update
结合  Apache
. 1.  安装 e Apache  模块
yum -y install mod_dav_svn
. 2.  修改配置文件（ 末行添加，根据仓库所在路径编辑 ）
vim /etc/httpd/conf.d/subversion.conf
<Location />
DAV svn
SVNPath  /tmp/svn # # 初始化目录（仓库）
</Location>
. 3.  启动 d httpd  服务
service httpd restart
. 4.  浏览器下载代码
N SVN  备份
svnadmin hotcopy /tmp/svn/ /tmp/bak
N SVN  的钩子联动
. 1.  复制钩子模板
cp /tmp/svn/hooks/post-commit.tmpl /tmp/svn/hooks/post-commit
. 2.  编辑模板， 注释掉最后一行 ，并加入以下命令，达到更新联动的效果
vim /tmp/svn/hooks/post-commit
ssh root@192.168.38.2 -C “cd /var/www/html/www/ && svn update”
或
echo “$REPOS=“$1”;$REV"=“$2””| mutt -s 'update code'
abc@163.com;ssh 192.168.38.2 “cd /var/www/html/www/ && svn update”
. 3.  为钩子模板添加可执行权限
chmod +x /tmp/svn/hooks/post-commit
# # 查看 x selinux  状态
sestatus
```



## svn http访问
```
https://docs.bitnami.com/virtual-machine/components/subversion/

yum install mod_dav_svn
# svnadmin create stuff  
# chown -R apache.apache stuff/

修改/etc/httpd/conf.d/subversion.conf
<Location /repos>  
   DAV svn  
   SVNParentPath /var/www/svn  
      AuthType Basic # 使用基本认证方式，即用户名、密码认证  
      AuthName "Authorization Realm" # 在认证对话框中出现的提示信息  
      AuthUserFile /etc/svn/svnusers.conf # 指定存放用户名信息的文件路径  
      Require valid-user # 限定只有用户输入正确的用户名和密码后才能访问该标签所指向的路径  
</Location> 

# mkdir -p /etc/svn/  
# htpasswd -c /etc/svn/svnusers.conf admin 

/etc/init.d/httpd restart  

```



## svn备份
```
直接复制svn目录
svnadmin recover /path/to/repos  将版本库数据库恢复到稳定状态

===================
svnlook youngest sinacuishou/    查看到目前为止最新的版本号

svnadmin dump sinacuishou/ > sinacuishou_svn.dumpfile 导出
 
svnadmin load sinacuishou/ < sinacuishou_svn.dumpfile  倒入

svnadmin dump myrepos –r 23 >rev-23.dumpfile           //将version23导出
svnadmin dump myrepos –r 100:200 >rev-100-200.dumpfile  //将version100~200导出
对比较大的库可以分解成几个文件导出，便于备份
-r 指定版本
```


