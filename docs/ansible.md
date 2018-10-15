## 常用模块
```
ansible-doc -l 列出所有模块
ansible-doc <模块名>   文档
ansible-doc  -s  <模块名>  简略文档
远程命令模块
ansible webservers -m command -a "free -m"
ansible webservers -m script -a "/home/test.sh 12 34"
ansible webservers -m shell -a "/home/test.sh"
copy模块
ansible webservers -m copy -a "src=/home/test.sh dest=/tmp/ owner=root group=root mode=0755"
stat模块
ansible webservers -m stat -a "path=/etc/sysctl.conf"
get_url模块
ansible webservers -m get_url -a "url=http://www.baidu.com dest=/tmp/index.html mode=0440 force=yes"
安装软件
ansible webservers -m apt -a "pkg=curl state=latest"
ansible webservers -m yum -a "name=curl state=latest"
cron模块
ansible webservers -m cron -a "name='check dirs' hour='5,2' job='ls -alh > /dev/null'"
mount模块
ansible webservers -m mount -a "name=/mnt/data src=/dev/sd0 fstype=ext3
opts=rostate=present"
service模块
ansible webservers -m service -a "name=nginx state=stopped"
ansible webservers -m service -a "name=nginx state=restarted"
ansible webservers -m service -a "name=nginx state=reloaded"
sysctl包管理模块
sysctl: name=kernel.panic value=3 sysctl_file=/etc/sysctl.conf checks=before reload=yes salt '*' pkg.upgrade
user模块
#添加用户johnd；
ansible webservers -m user -a "name=johnd comment='John Doe'"
#删除用户johnd；
ansible webservers -m user -a "name=johnd state=absent remove=yes"
```



## playbook
```
https://github.com/ansible/ansible-examples 示例 

执行  ansible-playbook  nginx.yml -f 10
-u REMOTE_USER：手工指定远程执行playbook的系统用户；   
--syntax-check：检查playbook的语法；   
--list-hosts playbooks：匹配到的主机列表； 
--step：以单任务分步骤运行，方便做每一步的确认工作

nginx.yml  yaml语法
---
- hosts: 192.168.8.22 #操作对象,之前定义的主机或主机组
  vars:    #定义变量
    worker_processes: 4
    num_cpus: 4
    max_open_file: 65506
    root: /data
  remote_user: root  #远程操作用户名，支持sudo方式运行，添加sudo:yes
  tasks:   #任务列表
  - name: Install Nginx......  #运行时会输出，默认使用action（具体的执行动作）
    yum: pkg=nginx state=latest
  - name: write the nginx config file 
    template: src=/tmp/nginx.conf dest=/etc/nginx/nginx.conf
            #参数使用key=value的格式，定义任务时也可以引用变量,/tmp/nginx.conf{{ root }}
    notify:  #触发handlers定义的程序
    - restart nginx
  - name: Nginx is running......
    service: name=nginx state=started
  handlers:   #定义的处理程序在没有通知触发时是不会执行的，触发后也只会运行一次
    - name: restart nginx
      service: name=nginx state=restarted
 
cat /tmp/nginx.conf
......
user              nginx;
worker_processes  {{ worker_processes }};
{% if num_cpus == 2 %}
worker_cpu_affinity 01 10;
{% elif num_cpus == 4 %}
worker_cpu_affinity 1000 0100 0010 0001;
{% elif num_cpus >= 8 %} 
worker_cpu_affinity 00000001 00000010 00000100 00001000 00010000 0010000001000000 10000000;
{% else %}
worker_cpu_affinity 1000 0100 0010 0001;
{% endif %}
worker_rlimit_nofile {{ max_open_file }};
......


引用其他的playbook
tasks: 
    - include: tasks/foo.yml
```



## 条件循环
```
变量的另一个用途是将一条命令的运行结果保存到变量中，供后面的playbook使用。
下面是一个简单的示例：
- hosts: web_servers
  tasks:
     - shell: /usr/bin/foo
       register: foo_result
       ignore_errors: True
     - shell: /usr/bin/bar
       when: foo_result.rc == 5
上述示例注册了一个foo_result变量，变量值为shell:/usr/bin/foo的运行结果，ignore_errors:True
为忽略错误。变量注册完成后，
就可以在后面playbook中使用了，当条件语句when:foo_result.rc==5成立时，shell:/usr/bin/bar
命令才会运行，其中
foo_result.rc为返回/usr/bin/foo的resultcode（返回码）。图9-8返回“rc=0”的返回码。

tasks:
  - name: "shutdown Debian flavored systems"
    command: /sbin/shutdown -t now
    when: ansible_os_family == "Debian"  结果将返回BOOL类型值,为True执行command
 - command: /bin/something
    when: result|failed
 - command: /bin/something_else
    when: result|success
  - command: /bin/still/something_else
    when: result|skipped
“when:result|success”的意思为当变量result执行结果为成功状态时，将执行/bin/something_else
命令，其他同理，其中
success为Ansible内部过滤器方法，返回Ture代表命令运行成功。

循环
- name:Install package
  yum: name={{ item }} state=installed
  with_items:
     - pkg1
     - pkg2
循环的次数为with_items的元素个数，这里有2个元素，分别为pkg1、pkg2，会分别替换{{item}}项
```



## facts
```
ansible 192.168.1.21-m setup  获取系统信息，类似于Saltstack的Grains
ansible all -m setup -a "filter=ansible_hostname"  过滤某一个值

在模板文件中这样引用Facts信息：
{{ ansible_devices.sda.model }}  ansible_devices下的sda字典下key为model的值
{{ ansible_hostname }}    ansible_hostname的值


---------------------------
自定义Facts

目标机器操作
mkdir -pv /etc/ansible/facts.d
cd /etc/ansible/facts.d
vim preferences.fact
[general]
max_memory_size=32
max_user_processes=3730
open_files=65535

执行 ansible 192.168.8.22 -m setup -a "filter=ansible_local"
.....
"ansible_facts": {
        "ansible_local": {
            "preferences": {
                "general": {
                    "max_memory_size": "32", 
                    "max_user_processes": "3730", 
                    "open_files": "65535"
                }
            }
        }
    },
........
```



## jinja2过滤器
```
使用格式：
{{变量名|过滤方法}}。

下面是实现获取一个文件路径变量过滤出文件名的一个示例：
{{ path | basename }}
获取文件所处的目录名：
{{ path | dirname }}

下面为一个完整的示例，实现从“/etc/profile”中过滤出文件名“profile”，并输出重定向到
/tmp/testshell文件中。
---- 
hosts: 192.168.1.21
  vars:    filename: /etc/profile
  tasks:    - name: "shell1"
      shell: echo {{ filename | basename }} >> /tmp/testshell
```



## 基础
```
yum install ansible -y
vim /etc/ansible/hosts  定义主机、主机组，以及主机变量
组成员主机名称支持正则描述，示例如下：
[webservers]
www[01:50].example.com  http_port=80 maxRequestsPerChild=808

[databases]
db-[a:f].example.com  http_port=303 maxRequestsPerChild=909

[databases vars]  组变量
ntp_server=ntp.atlanta.example.com
proxy=proxy.atlanta.example.com

分离主机与组特定数据
Ansible支持将/etc/ansible/hosts定义的主机名与组变量单独剥离出来存放到指定的文件中，将采用
YAML格式存放，存
放位置规定：“/etc/an-sible/group_vars/+组名”和“/etc/ansible/host_vars/+主机名”
/etc/ansible/group_vars/dbservers
/etc/ansible/group_vars/webservers
/etc/ansible/host_vars/foosball

---------------------------------------------
ansible all -m ping  测试联通性
ssh密钥认证
ssh-keygen
ssh-copy-id -i /root/.ssh/id_rsa.pub root@192.168.1.21

target目标
ip 或 one.example.com                多 个IP或主机名使用“:”号分隔
webservers    匹配目标组为webservers，多个组使用“:”号分隔
All或’*’             匹配目标所有主机
~(web|db).*\.example\.com或192.168.1.*  支持正则表达方匹配主机或IP地址
webservers:!192.168.1.22              
            匹配webservers组且排除192.168.1.22主机IP
webservers:&dbservers                            匹配webservers与dbservers两个群组的交集
webservers:!{{excluded}}:&{{required}}     支持变量匹配方式
```