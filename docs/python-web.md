## django models
```
from django.db.models import Count
from django.db import connection

select = {'day': connection.ops.date_trunc_sql('day', 'date_time')}    # 按天统计
countday = msg.objects.filter(date_time__gte=start).filter(date_time__lte=end).extra(select=select).values('day').annotate(number=Count('id'))
days = []
    for d in list(countday):
        days.append([str(d['day']),d['number']])

days 结果
[['2018-09-26', 3], ['2018-09-27', 1], ['2018-09-28', 5], ['2018-09-25', 1], ['2018-09-24', 1]]


countall = msg.objects.filter(date_time__gte=start).filter(date_time__lte=end).count()   # 统计总数
countuser = msg.objects.filter(date_time__gte=start).filter(date_time__lte=end).values_list('user_name').annotate(Count('user_name'))  # 按字段统计去重统计
userdata = list(sorted(countuser,key=lambda user: user[1],reverse=True))[:5]   # 获取前5个

userdata结果
[(u'root', 5), (u'pwm', 3), (u'test', 2), (u'lianggy', 1)]




http://www.cnblogs.com/yangmv/p/5327477.html

对数据进行增删改查
查
models.UserInfo.objects.all()
models.UserInfo.objects.all().values('user')    #只取user列
models.UserInfo.objects.all().values_list('id','user')    #取出id和user列，并生成一个列表
models.UserInfo.objects.get(id=1)
models.UserInfo.objects.get(user='yangmv')


增
models.UserInfo.objects.create(user='yangmv',pwd='123456')
或者
obj = models.UserInfo(user='yangmv',pwd='123456')
obj.save()
或者
dic = {'user':'yangmv','pwd':'123456'}
models.UserInfo.objects.create(**dic)

删
models.UserInfo.objects.filter(user='yangmv').delete()


改 
models.UserInfo.objects.filter(user='yangmv').update(pwd='520')
或者
obj = models.UserInfo.objects.get(user='yangmv')
obj.pwd = '520'
obj.save()


二、常用字段
models.DateTimeField　　日期类型 datetime
参数，
auto_now = True ：则每次更新都会更新这个时间
auto_now_add 则只是第一次创建添加，之后的更新不再改变。

class UserInfo(models.Model):
    name = models.CharField(max_length=32)
    ctime = models.DateTimeField(auto_now=True)
    uptime = models.DateTimeField(auto_now_add=True)


from web import models
def home(request):
    models.UserInfo.objects.create(name='yangmv')
    after = models.UserInfo.objects.all()
    print after[0].ctime
    return render(request, 'home/home.html')

表结构的修改
表结构修改后，原来表中已存在的数据，就会出现结构混乱，makemigrations更新表的时候就会出错
解决方法：
1、新增加的字段，设置允许为空。生成表的时候，之前数据新增加的字段就会为空。(null=True允许数据库中为空，blank=True允许admin后台中为空)
2、新增加的字段，设置一个默认值。生成表的时候，之前的数据新增加字段就会应用这个默认值



2、连表结构

一对多：models.ForeignKey(其他表)
多对多：models.ManyToManyField(其他表)
一对一：models.OneToOneField(其他表)
应用场景：

一对多：当一张表中创建一行数据时，有一个单选的下拉框（可以被重复选择）
例如：创建用户信息时候，需要选择一个用户类型【普通用户】【金牌用户】【铂金用户】等。
多对多：在某表中创建一行数据是，有一个可以多选的下拉框
例如：创建用户信息，需要为用户指定多个爱好
一对一：在某表中创建一行数据时，有一个单选的下拉框（下拉框中的内容被用过一次就消失了
例如：原有含10列数据的一张表保存相关信息，经过一段时间之后，10列无法满足需求，需要为原来的表再添加5列数据
 
 
一对多：
class Game(models.Model):
    gname = models.CharField(max_length=32)
 
class Host(models.Model):
    hostname = models.CharField(max_length=32)
    game = models.ForeignKey('Game')



```

## django uwsgi
```
yum install nginx uwsgi uwsgi-plugin-python2 -y

echo '/usr/sbin/uwsgi --ini /data/admin/uwsgi.ini &' >> /etc/rc.local
chmod +x /etc/rc.local

重启 killall -9 uwsgi && /usr/sbin/uwsgi --ini /data/admin/uwsgi.ini

uwsgi.ini 内容
[uwsgi]
socket = 127.0.0.1:9090
master = true    
vhost = true    
no-site = true 
workers = 2   
reload-mercy = 10     
vacuum = true
max-requests = 1000   
limit-as = 512
buffer-size = 30000
plugins = python
pidfile = /var/run/uwsgi.pid 
daemonize = /var/log/nginx/uwsgi.log
pythonpath = /usr/lib/python2.7/site-packages/
pythonpath = /usr/lib64/python2.7/site-packages/


nginx 配置
gzip		on;
server_tokens 	off;
    location / {
            include  uwsgi_params;
            uwsgi_pass  127.0.0.1:9090;   
            uwsgi_param UWSGI_SCRIPT admin.wsgi; 
            uwsgi_param UWSGI_CHDIR /data/admin/;  
            index  index.html index.htm;
            client_max_body_size 35m;
        }
    location /static/ {
	    root /data/admin/;
        expires 10d;
	    }

```


## uwsgi+nginx
```
pip install Flask-Script uwsgi  uwsgi-tools
from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
return "Hello World!"
生产环境内，谁会用这样的代码呢，这只是Flask 的最简入门范，我的Flask项目中 app 是被做在包内的，相信很多人都是这样做的，
在包外我们采用 Flask Script 写一个 manage.py 文件 作为启动文件，这更方便于支持各种的项目，包括可以安装到 window下的 FastCGI 中。
那么我的 这个 manage.py 是这个样子的：
#!/usr/bin/env python
import os
if os.path.exists('.env'):
print('Importing environment from .env...')

for line in open('.env'):

    var = line.strip().split('=')

    if len(var) == 2:

        os.environ[var[0]] = var[1]
from app import create_app
from flask.ext.script import Manager, Shell
# 通过配置创建 app
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
def make_shell_context():
return dict(app=app)
manager.add_command("shell", Shell(make_context=make_shell_context))
@manager.command
def deploy():
"""Run deployment tasks."""

pass
if __name__ == '__main__':
manager.run()
这样做我地开发环境可以这样运行 Flask:
python manage.py runserver
uwsgi配置
vim config.ini
[uwsgi]
# uwsgi 启动时所使用的地址与端口
socket = 127.0.0.1:8001
# 指向网站目录
chdir = /var/www/html/solr/
buffer-size = 32768
post-buffering = 8192
# python 启动程序文件
wsgi-file = log_uwsgi.py
# python 程序内用以启动的 application 变量名
callable = app
# 处理器数
processes = 4
# 线程数:
threads = 2
#状态检测地址
stats = 127.0.0.1:8002
启动 uwsgi config.ini
测试 uwsgi_curl 127.0.0.1:8001
supervisor控制程序启动
yum install supervisor nginx -y  （pip install supervisor 安装新版本的）
vim /etc/supervisord.conf  底下添加
[program:my_flask]
command=/usr/bin/uwsgi /var/www/html/solr/config.ini
directory=/var/www/html/solr/
user=root
autostart=true
autorestart=true   ;程序异常退出后自动重启
loglevel=info
log_stdout=true             ; if true, log program stdout (default true)
log_stderr=true             ; if true, log program stderr (def false)
logfile_maxbytes=3MB        ; max # logfile bytes b4 rotation (default 50MB)
logfile=/var/log/upload.log
启动服务 service supervisor start
终止服务 service supervisor stop   （有可能听不掉，不行就kill -9）
vim /ect/nginx/nginx.conf
server {

listen 80;

server_name XXX.XXX.XXX; #公网地址或域名



location / {

include uwsgi_params;

uwsgi_pass 127.0.0.1:8001; # 指向uwsgi 所应用的内部地址,所有请求将转发给uwsgi 处理

# uwsgi_param UWSGI_PYHOME /home/www/my_flask/venv; # 指向虚拟环境目录

uwsgi_param UWSGI_CHDIR /home/www/my_flask; # 指向网站根目录

uwsgi_param UWSGI_SCRIPT manage:app; # 指定启动程序

}

}
```


## post请求
```
header信息
print request.headers
print request.headers.get('X-Real-Ip', request.remote_addr)
get请求信息
print request.args
print request.args.get('key')
post请求信息
print request.form
print request.form.get('key')
不管post/get使用统一的接收
from flask import request
args = request.args if request.method == 'GET' else request.form
a = args.get('a', 'default')
form 表单数据
print request.form
print request.form['name']
print request.form.get('name')
print request.form.getlist('name')
print request.form.get('nickname', default='little apple')
```



## upload api
```
#!/usr/bin/env python
#coding:utf-8
import os
import commands
from flask import Flask, request, redirect,render_template
import urllib
import logging
import re
logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s', filename='/var/log/upload.log')
UPLOAD_FOLDER = '/var/www/html/logfile/now'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #ALL_DATA = eval(request.get_data())
        ALL_DATA = request.get_data()
        ALL_DATA = urllib.unquote(ALL_DATA)
        try:
            meetingid = re.findall(r'meetingid=[0-9]+',ALL_DATA)[0].split('=')[1]
            fileName = re.findall(r'(?<=fileName=).*\d+\.(?:error|log)',ALL_DATA)[0].replace('error','error.log')
        except:
            print ALL_DATA
            return "bad"
            #print ALL_DATA
        PATH = os.path.join(app.config['UPLOAD_FOLDER'],meetingid)
        if not os.path.isdir(PATH):
            os.mkdir(PATH)
        try:
            with open(os.path.join(PATH,fileName),'a') as f:
                f.write(ALL_DATA)
        except IOError:
            os._exit(1)
    return "OK!" 
@app.route("/crossdomain.xml", methods=['GET', 'POST'])
def cross():
    return '''<?xml version="1.0"?>
<cross-domain-policy>
	<allow-access-from domain="*" />
	<allow-access-from domain="www.3mang.com" />
</cross-domain-policy>'''
@app.route("/download",methods=['GET','POST'])
def download():
    if request.method == 'POST':
        os.environ['url']=request.form['url']
        result=commands.getoutput('/usr/local/solr/1.sh $url')
        if re.match(r'.*.zip',result):
            return render_template('download.html',result=result)
        else:
            return render_template('download.html',message=result)
    return render_template('download.html')
@app.route("/todayid",methods=['GET','POST'])
def todayid():
    if request.method == 'POST':
        os.environ['classid']=request.form['classid']
        result=commands.getoutput('/usr/local/solr/2.sh $classid')
        if re.match(r'.*.zip',result):
            return render_template('todayid.html',result=result)
        else:
            return render_template('todayid.html',message=result)
    return render_template('todayid.html')
if __name__ == "__main__":
    logging.info(app.run(host='0.0.0.0', threaded=True,port=13966, debug=False))
```



## 上下文
```
上下文
上下文译自context，文字解释起来比较费劲
针对你的问题，可以简单地理解为一个应用运行过程中/一次请求中的所有数据
对于应用，上下文包括但不限于：
应用的启动脚本是哪个文件，启动时指定了哪些参数

加载了哪些配置文件，导入了哪些配置

连了哪个数据库

有哪些public的工具类、常量

应用跑再哪个机器上，IP多少，内存多大...
对于一次请求，就是
请求的方法、地址、参数、post上来的数据、带上来的cookie...

当前的session

处理这个请求时创建出来的变量、对象..

http://www.cnblogs.com/hazir/p/what_is_web_framework.html


http://blog.jobbole.com/84870/


https://www.zhihu.com/question/34873227

```



## 基础
```
from flask import Flask,render_template,session,request,abort, redirect, url_for
app = Flask(__name__)    创建了这个类的实例
 
@app.route('/', methods=['GET', 'POST'])               
def hello_world():
    return redirect(url_for('login'))   重定向到/login，url_for函数
 
@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404   自定义404错误页面

@app.route('/user/<username>')   变量名
def show_user_profile(username):
    # show the user profile for that user
    return 'User %s' % username    传入变量

登录
@app.route('/')
def index():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''
 
@app.route('/logout')
def logout():
    # 如果会话中有用户名就删除它。
    session.pop('username', None)
    return redirect(url_for('index'))
 
# 设置密钥，复杂一点：
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
 
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,)
```



## 渲染模板


```
from flask import Flask, render_template, request

app = Flask(__name__)
 
@app.route('/', methods=['GET', 'POST'])
def index():
    user = request.form.get('user', 'Flask')
    return render_template('index.html', user=user)
@app.route('/hello/<name>')
    def hello(name=None):
    return render_template('hello.html',name=name)
  
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

vim templates/index.html
<html>
<title>Flask - Vfast</title>

<body>
    <h1>Hello, {{ user|title }}!</h1></br>
    <form method='POST'>
        <input type='text', name='user'>
        <input type='submit', name='submit'>
    </form>
</body>
</html>
vim templates/hello.html
<!doctype html>
<title>Hello from Flask</title>
{% if name %}
  <h1>Hello {{ name }}!</h1>
{% else %}
  <h1>Hello World!</h1>
{% endif %}

```

## 上传文件
```
from flask import Flask, render_template, request

app = Flask(__name__)
 
@app.route('/', methods=['GET', 'POST'])
def index():
    user = request.form.get('user', 'Flask')
    return render_template('index.html', user=user)
@app.route('/hello/<name>')
    def hello(name=None):
    return render_template('hello.html',name=name)
  
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

vim templates/index.html
<html>
<title>Flask - Vfast</title>

<body>
    <h1>Hello, {{ user|title }}!</h1></br>
    <form method='POST'>
        <input type='text', name='user'>
        <input type='submit', name='submit'>
    </form>
</body>
</html>
vim templates/hello.html
<!doctype html>
<title>Hello from Flask</title>
{% if name %}
  <h1>Hello {{ name }}!</h1>
{% else %}
  <h1>Hello World!</h1>
{% endif %}

```



## falcon邮件网关
使用 curl http://127.0.0.1:8900 -d "tos=lianggy@163.cn&subject=dd&content=aa"

```
#!/usr/bin/env python
#coding:utf-8
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
        content = request.form.get("content")
        tos = request.form.get("tos")
        subject = request.form.get("subject")
        try:
            mail = '/usr/local/bin/sendEmail -f %s -t %s -u "%s" -m "%s" -s %s' % 
                                                    (mailfrom, tos, subject, content, mailserver)
            result = os.popen(mail).read()
            logging.info(result)
            return result
        except Exception,e:
            return str(e)
    return "OK"


if __name__ == "__main__":
    logging.info(app.run(host='127.0.0.1', threaded=True,port=8900, debug=False))
    #app.run(host='0.0.0.0', threaded=True,port=8900, debug=True)
```



## table分页
```
<table class="table table-condensed table-bordered">
    <caption>title</caption>
        <thead>
            <tr>
              <th>主机</th>
              <th>监控项</th>
              <th>备注</th>
              <th>时间</th></tr>
          </thead>
         <tbody id="table_result">
            <tr>
               <td>1</td>
               <td>2</td>
               <td>3</td>
               <td>4</td>
            </tr>
          </tbody>
        </table>
        <ul id="barcon" class="pagination pull-right"></ul>  //空的用来放分页后的表格

js：------------------------------------------

goPage(1,6);
    function goPage(pno, psize) {
        var itable = document.getElementById("table_result");//通过ID找到表格
        var num = itable.rows.length;//表格所有行数(所有记录数)
        var totalPage = 0;//总页数
        var pageSize = psize;//每页显示行数
        //总共分几页
        if (num / pageSize > parseInt(num / pageSize)) {
            totalPage = parseInt(num / pageSize) + 1;
        } else {
            totalPage = parseInt(num / pageSize);
        }
        var currentPage = pno;//当前页数
        var startRow = (currentPage - 1) * pageSize + 1;//开始显示的行  1
        var endRow = currentPage * pageSize;//结束显示的行  6
        endRow = (endRow > num) ? num : endRow;
        //遍历显示数据实现分页
        for (var i = 1; i < (num + 1); i++) {
            var irow = itable.rows[i - 1];
            if (i >= startRow && i <= endRow) {
                irow.style.display = "table-row"; //当前页的数据
            } else {
                irow.style.display = "none"; //非当前页的数据
            }
        }
        var tempStr = "";
        if (currentPage > 1) {
            tempStr += "<li><a href=\"#\" onClick=\"goPage(" + (currentPage - 1) + "," + psize + ")\">&laquo;</a></li>"
            for (var j = 1; j <= totalPage; j++) {
                tempStr += "<li><a href=\"#\" onClick=\"goPage(" + j + "," + psize + ")\">" + j + "</a></li>"
            }
        } else {
            tempStr += "<li><a href=\"#\">&laquo;</a></li>";
            for (var j = 1; j <= totalPage; j++) {
                tempStr += "<li><a href=\"#\" onClick=\"goPage(" + j + "," + psize + ")\">" + j + "</a></li>"
            }
        }
        if (currentPage < totalPage) {
            tempStr += "<li><a href=\"#\" onClick=\"goPage(" + (currentPage + 1) + "," + psize + ")\">&raquo;</a></li>";
            for (var j = 1; j <= totalPage; j++) {
            }
        } else {
            tempStr += "<li><a href=\"#\">&raquo;</a></li>";
            for (var j = 1; j <= totalPage; j++) {
            }
        }
        document.getElementById("barcon").innerHTML = tempStr;
    }
```



