## install
```
doc http://book.open-falcon.org/zh_0_2/intro/
github https://github.com/open-falcon/

一、环境准备
yum install -y redis mysql-server 
yum install -y python-virtualenv
yum install -y python-devel python-pip
yum install -y openldap-devel
yum install -y mysql-devel
yum groupinstall "Development tools"
/etc/init.d/redis start
/etc/init.d/mysqld start
chkconfig redis on
chkconfig mysqld on
二、安装后端
# 下载最新的安装包
https://github.com/open-falcon/falcon-plus/releases 

mkdir /usr/local/open-falcon/
cd /usr/local/open-falcon/
tar -zxf open-falcon-v0.2.1.tar.gz

# 修改mysql账号密码
grep -Ilr 3306  ./ | xargs -n1 -- sed -i 's/root:password/real_user:real_password/g')  
三、安装前端
# 下载代码
http://192.168.41.90:3000/lianggy/falcon-dashboard

# 确保代码放在/usr/local/open-falcon/dashboard下
mkdir /usr/local/open-falcon/dashboard
cd /usr/local/open-falcon/dashboard 
unzip falcon-dashboard-master.zip   
mv falcon-dashboard/* /usr/local/open-falcon/dashboard/

#导入表
mysql -h 127.0.0.1 -u root -p < mysql-falcon.sql

# 相关python依赖
virtualenv ./env
./env/bin/pip install -r pip_requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

---------------------
dashboard的配置文件为： 'rrd/config.py'，请根据实际情况修改

## API_ADDR 表示后端api组件的地址
API_ADDR = "http://127.0.0.1:8080/api/v1" 

## 根据实际情况，修改PORTAL_DB_*, 默认用户名为root，默认密码为""
## 根据实际情况，修改ALARM_DB_*, 默认用户名为root，默认密码为""

# 启动后端各个模块
cd /usr/local/open-falcon/
./open-falcon start

# 检查所有模块的启动状况
./open-falcon check

# 启动前端
cd /usr/local/open-falcon/dashboard 
./control start|stop


四、交换机监控
# 下载最新代码
https://github.com/gaochao1/swcollector/releases

放到/usr/local/open-falcon/switch下面
配置文件请参照cfg.example.json，修改该文件名为cfg.json
"ipRange":[            #交换机IP地址段，对该网段有效IP，先发Ping包探测，对存活IP发SNMP请求
            "192.168.56.101/32",      
            "192.168.56.102-192.168.56.120",#现在支持这样的配置方式，对区域内的ip进行ping探测，对存活ip发起snmp请求。
            "172.16.114.233" 
         ],


hosts.json  自定义host配置

{
    "hosts":
    {
        "192.168.160":"test1",
        "192.168.88.161":"test2",
        "192.168.33.2":"test3",
        "192.168.31.51":"test4"
    }
}

./control start|stop
五、邮件告警
mkdir /usr/local/open-falcon/mail/
cd /usr/local/open-falcon/mail/
mv /usr/local/open-falcon/dashboard/mailapi.py .
chmod 777 mailapi.py
pip install flask -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

vim mailapi.py
mailfrom = 'test'    发件人
mailserver = 'ip'           邮件代理服务器地址

启动
nohup python mailapi.py &
六、定时任务等
cd /usr/local/open-falcon/dashboard
mv ipmi.sh ../
mv curl_time.py ../
cd ../
chmod 777 ipmi.sh curl_time.py

vim ipmi.cfg  格式为
主机  ip



# 流量告警
* * * * * /usr/local/open-falcon/dashboard/flow_alert.py &
# ipmi监控 
*/10 * * * * /usr/local/open-falcon/ipmi.sh &
# curl时间监控
* * * * * /usr/local/open-falcon/curl_time.py &
# 备份任务
0 1 * * * /usr/local/open-falcon/dashboard/backup.sh >/dev/null 2>&1 &


打开 http://ip:8010  
user: root
pass: 123456.test

到此open-falcon安装完成。
```

## report
```
一、安装

# 确保代码放在/usr/local/open-falcon/dashboard2下
mkdir /usr/local/open-falcon/dashboard2
cd /usr/local/open-falcon/dashboard2
unzip falcon-dashboard2-master.zip             

cp -r ../dashboard/env .
cp ../dashboard/rrd/config.py ./rrd/config.py  覆盖

#启动
./control start


#下载截图用浏览器
http://phantomjs.org/download.html

放到 /usr/local/open-falcon/dashboard2/phantomjs

chmod 777 /usr/local/open-falcon/dashboard2/phantomjs

vim url.txt
格式  图片名字  图片地址
例如  Hh511      http://127.0.0.1:8011/chart/big?id=1643&start=-86400&cf=&start=-86400&graph_type=a  具体url通过监控面板确定

# 存放截图
yum install tengine
mkdir -pv /var/www/html/ && chmod 777  /var/www/html/
server {
                listen       0.0.0.0:82 default;

                location / {
                        # /usr/share/nginx/
                        root   /var/www/html/;
                        index  index.html index.htm;
                }

        }

#截图脚本
vim flow_report.sh
HTTPURL="http://10.21.30.95:82/img/$DIR"  图片存放地址
echo 内容为最终结果，根据需要修改
/usr/local/bin/sendEmail -f test  最后发送邮件，根据需要修改

#测试
chmod 777 flow_report.sh
./flow_report.sh

添加定时任务
30 7,19 * * * /usr/local/open-falcon/dashboard2/flow_report.sh >/dev/null 2>&1 &

```

## mailapi
```
#!/usr/bin/env python
# coding:utf-8
import os
from flask import Flask, request
import logging
import sys
reload(sys)
sys.setdefaultencoding('utf8')

mailfrom = 'test'
mailserver = '172.29.0.68'
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s', filename='mailapi.log')
app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            content = request.form.get("content")
            tos = request.form.get("tos")
            sub = request.form.get("subject").replace("["," ").replace("]"," ").split()
			ipcom = '''mysql -uroot -p123456.test falcon_portal -e 'select ip from host where hostname="%s"' | sed '1d' ''' % (sub[2])
			ip = os.popen(ipcom).read().strip()
			subject = sub[2] + '(' + ip + ')' + ' ' + sub[3] + ' ' + sub[1]
			logging.info(subject)
        except Exception,e:
            content = request.form.get("content")
            tos = request.form.get("tos")
            subject = request.form.get("subject")
        try:
            #mail = '/usr/local/bin/sendEmail -f %s -t %s -u "%s" -m "%s" -s %s -o message-charset=GB2312' % (mailfrom, tos, subject.encode("gb2312"), content.encode("gb2312"), mailserver)
            mail = '/usr/local/bin/sendEmail -f %s -t %s -u $(echo "%s" | iconv -f utf-8 -t GB2312) -m "$(echo "%s" | iconv -f utf-8 -t GB2312)"  -s %s -o message-charset=GB2312' % (mailfrom, tos, subject, content, mailserver)
            result = os.popen(mail).read()
            #logging.info(mail)
            logging.info(result)
            return result
        except Exception,e:
            return str(e)
    return "OK"


if __name__ == "__main__":
    logging.info(app.run(host='127.0.0.1', threaded=True,port=8900, debug=False))
    #app.run(host='0.0.0.0', threaded=True,port=8900, debug=True)

```

## plugin
```
#!/usr/bin/env bash
api=http://127.0.0.1:1988/v1/push
ts=$(date +%s)
endpoint=$(hostname)

curll=$(ps aux |grep curl | wc -l)
[ $curll -ge 5  ] && exit

stat=$(curl http://127.0.0.1:1988 -o /dev/null -s -w %{http_code})
if [ $stat -ne 404  ];then
    exit
fi

netdev=`sudo ifconfig -a| grep HWaddr|grep -v bond|awk '{print $1}'`
for each in $netdev
    do
    Link_detected=`sudo ethtool $each|grep detected|awk -F: '{print $2}'| tr -d " "`
    if [ "$Link_detected" = "yes" ];then
       speed=`ethtool $each|grep Speed|awk -F: '{print $2}'|awk -FM '{print $1}'`
       curl -s -X POST -d "[{\"metric\": \"net.if.speed\", \"endpoint\": \"$endpoint\", \"timestamp\": $ts,\"step\": 60,\"value\": $speed,\"counterType\": \"GAUGE\",\"tags\": \"iface=$each\"}]" $api >/dev/null
    fi
done


proce=$(ps -ef|wc -l)
curl -s -X POST -d "[{\"metric\": \"proce.num\", \"endpoint\": \"$endpoint\", \"timestamp\": $ts,\"step\": 60,\"value\": $proce,\"counterType\": \"GAUGE\",\"tags\": \"\"}]" $api >/dev/null
proce_Z=$(ps -eo stat | egrep 'z|Z'|wc -l)
curl -s -X POST -d "[{\"metric\": \"proce.num\", \"endpoint\": \"$endpoint\", \"timestamp\": $ts,\"step\": 60,\"value\": $proce_Z,\"counterType\": \"GAUGE\",\"tags\": \"type=zombie\"}]" $api  >/dev/null

user=$(w | awk /user/'{print $6}')
curl -s -X POST -d "[{\"metric\": \"login.user\", \"endpoint\": \"$endpoint\", \"timestamp\": $ts,\"step\": 60,\"value\": $user,\"counterType\": \"GAUGE\",\"tags\": \"\"}]" $api  >/dev/null

```