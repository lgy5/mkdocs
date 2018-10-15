## elk分析
```
服务端    Kibana
服务端或者独立 JDK  ElasticSearch  redis2.6（数据队列） Logstash（匹配分析数据）
客户端 JDK   Logstash(导入数据用，安装一样，分离开减轻客户端压力)
下载地址 https://www.elastic.co/downloads
https://mirrors.tuna.tsinghua.edu.cn/ELK/  国内源

ElasticSearch和Logstash依赖于JDK，所以需要安装JDK：
yum -y install java-1.8.0-openjdk java-1.8.0-openjdk-devel
java -version

redis 源码编译安装2.6以上版本 

Logstash安装
http://www.open-open.com/lib/view/open1473661753307.html
Logstash默认的对外服务的端口是9292。
rpm -ivh logstash-2.0.0-1.noarch.rpm
测试/opt/logstash/bin/logstash -e 'input{stdin{}}output{stdout{codec=>rubydebug}}'
输入hello world


vim /etc/logstash/conf.d/agent.conf

input {
   file {
     type => "ugo_nginx_access"   ##日志文件类型,自定义。好区分，类似于分组这种概念
     path => "/export1/log/access_20150407+00.log"  ##日志文件路径。
   }
   file {
     type => "nginx_access"
     path => "/usr/local/nginx/logs/python-access.log"
   }
}
output {
  #将收集到的日志存储到了redis中。
  redis {
    host => "103.41.54.16"   
    port => 6379
    data_type => "list"
    key => "logstash"
  }
}

启动 /opt/logstash/bin/logstash agent -f /usr/local/logstash/conf/agent.conf   有时候服务启动没有数据

server
grok匹配测试  http://grokdebug.herokuapp.com/

/opt/logstash/bin/logstash agent -f /usr/local/logstash/conf/fserver.conf
input {
    redis {
        host => "127.0.0.1"
        port => "6379"
        data_type => "list"
        key => "logstash"
        type => "redis-input"
    }
}

filter {
    grok {
        match => { "message" => "%{COMBINEDAPACHELOG} %{QS:x_forwarded_for}" }   nginx日志匹配
    }
    geoip {
      source => "clientip"
      target => "geoip"
      database => "/opt/logstash/GeoLiteCity.dat"
      add_field => [ "[geoip][coordinates]", "%{[geoip][longitude]}" ]
      add_field => [ "[geoip][coordinates]", "%{[geoip][latitude]}" ]
    }

    mutate {
      convert => [ "[geoip][coordinates]", "float" ]
      convert => [ "response","integer" ]
      convert => [ "bytes","integer" ]
      replace => { "type" => "nginx_access" }
      remove_field => "message"
    }

    date {
      match => [ "timestamp","dd/MMM/yyyy:HH:mm:ss Z"]

    }
    mutate {
      remove_field => "timestamp"

    }


}
output {
    elasticsearch {
        hosts => ["127.0.0.1:9200"]
        manage_template => true   可以使用模板匹配地区，geoip，
        # http://blog.csdn.net/yanggd1987/article/details/50469113
        index => "logstash-nginx-access-%{+YYYY.MM.dd}"
    }
    stdout {codec => rubydebug}
}


 ##这个命令的意义就是，删除 logstash 2015年4月的所有文件。
curl -XDELETE 'http://10.1.1.99:9200/logstash-2015.04.*

ElasticSearch 安装
ElasticSearch默认的对外服务的HTTP端口是9200，节点间交互的TCP端口是9300。
rpm -ivh elasticsearch-2.0.0.rpm
vim /etc/elasticsearch/elasticsearch.yml 添加
node.name: node-1
network.host: 0.0.0.0
path.data: /data/elasticsearch/
http.port: 9200

mkdir -pv /data/elasticsearch
chown -R elasticsearch.elasticsearch /data/elasticsearch/
/etc/init.d/elasticsearch start

测试ElasticSearch服务是否正常，预期返回200的状态码：
curl -X GET http://localhost:9200
head插件
wget https://github.com/mobz/elasticsearch-head/archive/master.zip
unzip master.zip
mv elasticsearch-head-master/ /usr/share/elasticsearch/plugins/head/
http://112.126.80.182:9200/_plugin/head/

初始化数据集，为了保证上报事件的时间戳被正常识别为日期格式
curl -XPUT http://localhost:9200/logstash-qos -d '       索引地址固定的，需要先map，在导入数据
{
 "mappings" : {
  "_default_" : {
   "properties" : {
    "timestamp":{"type":"date"}
   }
  }
 }
}';


Kibana安装
tar -zxf kibana-4.2.0-linux-x64.tar.gz
vim ./kibana/config/kibana.yml 修改
elasticsearch.url: http://192.168.1.23:9200
运行./kibana/bin/kibana

kibana 分析报错：http://elasticsearch.cn/question/232





扩展
http://www.99ya.net/archives/523.html（亿万级日志数据实时分析平台）

```



## logstatsh http
```
https://www.elastic.co/blog/introducing-logstash-input-http-plugin

How do I use this plugin?

By default it will bind the webserver to all hosts ("0.0.0.0") and open the TCP port 8080 but it's
 possible configure these settings:

input {
  http {
    host => "127.0.0.1" # default: 0.0.0.0
    port => 31311 # default: 8080
  }
}
That's all you need!

What about security?
You can configure basic authentication by setting a username and password. All requests done to Logstash
will then have to set the right credentials or receive a 401 response. Only correctly authenticated requests
 will produce an event inside of Logstash. For SSL, it is necessary to specify the path to a Java Keystore 
 that contains the certificate that clients use to validate the server. Here's an example:

input {
   port => 3332
   user => myuser
   password => "$tr0ngP4ssWD!"
   ssl => on
   keystore => "/tmp/mykeystore.jks"
   keystore_password => "keystore_pass"
}


OK, now show me this plugin in action!

Step 1 - starting Logstash with http input:

bin/logstash -e "input { http { } } output { stdout { codec => rubydebug} }"
Step 2 - That's it!

To test it, let's issue two requests:

% curl -XPUT 'http://127.0.0.1:8080/twitter/tweet/1' -d 'hello'                               
% curl -H "content-type: application/json" -XPUT 'http://127.0.0.1:8080/twitter/tweet/1' -d '{
    "user" : "kimchy",
    "post_date" : "2009-11-15T14:12:12",
    "message" : "trying out Elasticsearch"
}'
Result in Logstash:

{
       "message" => "hello",
      "@version" => "1",
    "@timestamp" => "2015-05-29T14:49:00.392Z",
       "headers" => {
           "content_type" => "application/x-www-form-urlencoded",
         "request_method" => "PUT",
           "request_path" => "/twitter/tweet/1",
            "request_uri" => "/twitter/tweet/1",
           "http_version" => "HTTP/1.1",
        "http_user_agent" => "curl/7.37.1",
              "http_host" => "127.0.0.1:8080",
            "http_accept" => "*/*",
         "content_length" => "5"
    }
}
{
          "user" => "kimchy",
     "post_date" => "2009-11-15T14:12:12",
       "message" => "trying out Elasticsearch",
      "@version" => "1",
    "@timestamp" => "2015-05-29T14:49:04.105Z",
       "headers" => {
           "content_type" => "application/json",
         "request_method" => "PUT",
           "request_path" => "/twitter/tweet/1",
            "request_uri" => "/twitter/tweet/1",
           "http_version" => "HTTP/1.1",
        "http_user_agent" => "curl/7.37.1",
              "http_host" => "127.0.0.1:8080",
            "http_accept" => "*/*",
         "content_length" => "110"
    }
}
You can see that in the second request, since the content-type was application/json, the body was deserialized 
and expanded to the event root (notice the fields "user", "post_date" and "message").

Show me more concrete examples of how to use it!

Because, real world examples make everything clearer!

Elastic Watcher Integration
In this section, we’ll show you how to integrate Elastic Watcher -- the new Elasticsearch plugin for alerting
 and notification -- with Logstash. Sending notifications to Logstash via this input provides you a powerful
  toolset to further transform notifications and use Logstash’s rich collection of outputs.

Imagine that you have indices with Apache logs, and now we want to get a periodic update of how many requests
 are resulting in a 404 (Not Found) response.

The required steps for this are:

Installing Watcher
Creating a new notification on Watcher that every minute reports the number of events that have a 404 response 
status
Start Logstash with the HTTP input
Send data to Elasticsearch and watch updates on Logstash
Here we go!

1. Installing Watcher
cd elasticsearch-1.5.2
bin/plugin -i elasticsearch/watcher/latest
bin/plugin -i elasticsearch/license/latest
bin/elasticsearch # restart the server
2. Creating a watch
The Watcher plugin for elasticsearch provides an API to create and manipulate scheduled tasks, or "watches". 
A Watch will query the data in the elasticsearch cluster according to its schedule, look for certain scenarios 
(like the presence of an error event) and execute actions. Examples of actions are sending an email, writing a
 document to an index, calling an outside HTTP endpoint, and more..

For this test, I created a simple watch that:

every minute
counts number of HTTP requests that resulted in a 404
posts result to http://localhost:8080
This is the resulting JSON document I need to send to Watcher:

{
  "trigger" : {
    "schedule" : { "cron" : "0 0/1 * * * ?" }
  },
  "input" : {
    "search" : {
      "request" : {
        "indices" : [
          "logstash*"
          ],
        "body" : {
          "query" : {
            "term": { "response": 404 }
          }
        }
      }
    }
  },
  "actions" : {
    "my_webhook" : {
      "webhook" : {
        "auth" : {
          "basic" : {
            "username" : "guest",
            "password" : "guest"
          }
        },
        "method" : "POST",
        "host" : "127.0.0.1",
        "port" : 8080,
        "path": "/{{ctx.watch_id}}",
        "body" : "{{ctx.payload.hits.total}}"
      }
    }
  }
}
To install this watch you need to create it in Elasticsearch by executing a PUT request:

curl -XPUT 'http://localhost:9200/_watcher/watch/my-watch' -d @create_webhook.json
3. Logstash setup
wget http://download.elastic.co/logstash/logstash/logstash-1.5.2.tar.gz
tar -zxf logstash-1.5.2.tar.gz
cd logstash-1.5.2
bin/logstash -e "input { http { } } output { stdout { codec => rubydebug} }"
4. Results
After launching an ingestion process in another terminal, Logstash starts receiving 1 notification per 
minute in the form of a HTTP POST:

% bin/logstash -e "input { http { } } output { stdout { codec => rubydebug} }"    
Logstash startup completed
{
       "message" => "330",
      "@version" => "1",
    "@timestamp" => "2015-06-02T12:53:00.037Z",
       "headers" => {
               "content_type" => "application/x-www-form-urlencoded",
             "request_method" => "POST",
               "request_path" => "/my-watch",
                "request_uri" => "/my-watch?",
               "http_version" => "HTTP/1.1",
         "http_authorization" => "Basic Z3Vlc3Q6Z3Vlc3Q=",
        "http_accept_charset" => "UTF-8",
         "http_cache_control" => "no-cache",
                "http_pragma" => "no-cache",
            "http_user_agent" => "Java/1.8.0_20",
                  "http_host" => "127.0.0.1:8080",
                "http_accept" => "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
            "http_connection" => "keep-alive",
             "content_length" => "12"
    }
}
{
       "message" => "3103",
      "@version" => "1",
    "@timestamp" => "2015-06-02T12:54:00.030Z",
       "headers" => {
               "content_type" => "application/x-www-form-urlencoded",
             "request_method" => "POST",
               "request_path" => "/my-watch",
                "request_uri" => "/my-watch?",
               "http_version" => "HTTP/1.1",
         "http_authorization" => "Basic Z3Vlc3Q6Z3Vlc3Q=",
        "http_accept_charset" => "UTF-8",
         "http_cache_control" => "no-cache",
                "http_pragma" => "no-cache",
            "http_user_agent" => "Java/1.8.0_20",
                  "http_host" => "127.0.0.1:8080",
                "http_accept" => "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
            "http_connection" => "keep-alive",
             "content_length" => "13"
    }
}
{
       "message" => "6071",
      "@version" => "1",
    "@timestamp" => "2015-06-02T12:55:00.031Z",
       "headers" => {
               "content_type" => "application/x-www-form-urlencoded",
             "request_method" => "POST",
               "request_path" => "/my-watch",
                "request_uri" => "/my-watch?",
               "http_version" => "HTTP/1.1",
         "http_authorization" => "Basic Z3Vlc3Q6Z3Vlc3Q=",
        "http_accept_charset" => "UTF-8",
         "http_cache_control" => "no-cache",
                "http_pragma" => "no-cache",
            "http_user_agent" => "Java/1.8.0_20",
                  "http_host" => "127.0.0.1:8080",
                "http_accept" => "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
            "http_connection" => "keep-alive",
             "content_length" => "13"
    }
}

A more complex example
Now that we know how to trigger notification events from Watcher, we can leverage the plugin ecosystem in
 Logstash to escalate notifications depending in a certain criteria. This following config will:

continuously update the number of 404 requests in statsd
if the count reaches 10000 then send a message to HipChat, or
if reaches 40000, notify PagerDuty.
input {
  http { }
}
filter {
  if [headers][request_path] == "/my-watch" {
    mutate { convert => ["message", "integer" ] }
  }
}
output {
  if [headers][request_path] == "/my-watch" {
    if [message] > 40000 { # way too many, notify pagerduty
      pagerduty {
        description => "%{host} - Apache: Very high number of 404"
        details => {
          "timestamp" => "%{@timestamp}"
          "message" => "%{message}"
        }
        service_key => "apikeyforlogstashservice"
        incident_key => "logstash/apacheservice"
      }
    } else if [message] > 10000 {    # unusual amount, notify devs in hipchat
      hipchat {
         from => "logstash"
         room_id => "dev"
         token => "[api key]"
         format => "Very high number of 404 requests: %{message}"
      }
    }
    # always update count of 404 in statsd
    statsd { gauge => [ "http.status.404", "%{message}" ] }
  }
}
```



## geoip
```
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
```



## elasticsearch
```
所有索引 curl -XGET 'http://localhost:9200/_cat/indices/*?v'
删除索引 curl -XDELETE 'http://127.0.0.1:9200/winlogbeat-2016*'
        curl -XDELETE 'http://127.0.0.1:9200/winlogbeat-2017.07.20'

查看线程资源  curl http://127.0.0.1:9200/_nodes/hot_threads
集群状态      curl -XGET 'http://localhost:9200/_cluster/stats?human&pretty'
进程状态      curl -XGET http://127.0.0.1:9200/_nodes/stats/thread_pool?pretty
集群参数      curl -XGET http://127.0.0.1:9200/_cluster/settings
索引参数      curl -XGET http://127.0.0.1:9200/logstash-nginx-access-2017.10.26/_settings

集群配置
egrep -v "^#|^$" /etc/elasticsearch/elasticsearch.yml 
cluster.name: es1 #集群名字 要一致
node.name: node-1  # 节点名字，不能重复
network.host: 0.0.0.0
path.data: /data/elasticsearch/
http.port: 9200
discovery.zen.ping.multicast.enabled: false  ##关闭组播
discovery.zen.ping.unicast.hosts: ["10.51.48.109", "10.171.32.72"] # #单播发现地址 自己的和其他节点的
```



## logstash grop正则
grok匹配测试 [http://grokdebug.herokuapp.com/](http://grokdebug.herokuapp.com/)

Example

下面是日志的样子

55.3.244.1 GET /index.html 15824 0.043

正则的例子

%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration}

配置文件里是怎么写得？

input {

file {

path =&gt; “/var/log/http.log”

}

}

filter {

grok {

match =&gt; \[ "message", "%{IP:client} %{WORD:method} %{URIPATHPARAM:request} %{NUMBER:bytes} %{NUMBER:duration}" \]

}

}

解析后，是个什么样子？

client: 55.3.244.1

method: GET

request: /index.html

bytes: 15824

duration: 0.043

自定义正则

\(?&lt;field\_name&gt;the pattern here\)

\(?&lt;queue\_id&gt;\[0-9A-F\]{10,11}\)

当然你也可以把众多的正则，放在一个集中文件里面。

\# in ./patterns/postfix

POSTFIX\_QUEUEID \[0-9A-F\]{10,11}

filter {

grok {

patterns\_dir =&gt; “./patterns”

match =&gt; \[ "message", "%{SYSLOGBASE} %{POSTFIX\_QUEUEID:queue\_id}: %{GREEDYDATA:syslog\_message}" \]

}

}

\#\#\#\#\#\#\#\#\#\#\#\#

logstash已经自带了不少的正则，如果想偷懒的话，可以在内置正则里借用下。

USERNAME \[a-zA-Z0-9.\_-\]+

USER %{USERNAME}

INT \(?:\[+-\]?\(?:\[0-9\]+\)\)

BASE10NUM \(?&lt;!\[0-9.+-\]\)\(?&gt;\[+-\]?\(?:\(?:\[0-9\]+\(?:.\[0-9\]+\)?\)\|\(?:.\[0-9\]+\)\)\)

NUMBER \(?:%{BASE10NUM}\)

BASE16NUM \(?&lt;!\[0-9A-Fa-f\]\)\(?:\[+-\]?\(?:0x\)?\(?:\[0-9A-Fa-f\]+\)\)

BASE16FLOAT \b\(?&lt;!\[0-9A-Fa-f.\]\)\(?:\[+-\]?\(?:0x\)?\(?:\(?:\[0-9A-Fa-f\]+\(?:.\[0-9A-Fa-f\]\*\)?\)\|\(?:.\[0-9A-Fa-f\]+\)\)\)\b

POSINT \b\(?:\[1-9\]\[0-9\]\*\)\b

NONNEGINT \b\(?:\[0-9\]+\)\b

WORD \b\w+\b

NOTSPACE \S+

SPACE \s\*

DATA .\*?

GREEDYDATA .\*

QUOTEDSTRING \(?&gt;\(?&lt;!\\)\(?&gt;”\(?&gt;\.\|\[^\"\]+\)+”\|”"\|\(?&gt;’\(?&gt;\.\|\[^\'\]+\)+’\)\|”\|\(?&gt;\(?&gt;\.\|\[^\\]+\)+\)\|\`\)\)

UUID \[A-Fa-f0-9\]{8}-\(?:\[A-Fa-f0-9\]{4}-\){3}\[A-Fa-f0-9\]{12}

\# Networking

MAC \(?:%{CISCOMAC}\|%{WINDOWSMAC}\|%{COMMONMAC}\)

CISCOMAC \(?:\(?:\[A-Fa-f0-9\]{4}.\){2}\[A-Fa-f0-9\]{4}\)

WINDOWSMAC \(?:\(?:\[A-Fa-f0-9\]{2}-\){5}\[A-Fa-f0-9\]{2}\)

COMMONMAC \(?:\(?:\[A-Fa-f0-9\]{2}:\){5}\[A-Fa-f0-9\]{2}\)

IPV6 \(\(\(\[0-9A-Fa-f\]{1,4}:\){7}\(\[0-9A-Fa-f\]{1,4}\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){6}\(:\[0-9A-Fa-f\]{1,4}\|\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){5}\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,2}\)\|:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){4}\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,3}\)\|\(\(:\[0-9A-Fa-f\]{1,4}\)?:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\)\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){3}\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,4}\)\|\(\(:\[0-9A-Fa-f\]{1,4}\){0,2}:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\)\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){2}\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,5}\)\|\(\(:\[0-9A-Fa-f\]{1,4}\){0,3}:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\)\|:\)\)\|\(\(\[0-9A-Fa-f\]{1,4}:\){1}\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,6}\)\|\(\(:\[0-9A-Fa-f\]{1,4}\){0,4}:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\)\|:\)\)\|\(:\(\(\(:\[0-9A-Fa-f\]{1,4}\){1,7}\)\|\(\(:\[0-9A-Fa-f\]{1,4}\){0,5}:\(\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\(.\(25\[0-5\]\|2\[0-4\]\d\|1\d\d\|\[1-9\]?\d\)\){3}\)\)\|:\)\)\)\(%.+\)?

IPV4 \(?&lt;!\[0-9\]\)\(?:\(?:25\[0-5\]\|2\[0-4\]\[0-9\]\|\[0-1\]?\[0-9\]{1,2}\)\[.\]\(?:25\[0-5\]\|2\[0-4\]\[0-9\]\|\[0-1\]?\[0-9\]{1,2}\)\[.\]\(?:25\[0-5\]\|2\[0-4\]\[0-9\]\|\[0-1\]?\[0-9\]{1,2}\)\[.\]\(?:25\[0-5\]\|2\[0-4\]\[0-9\]\|\[0-1\]?\[0-9\]{1,2}\)\)\(?!\[0-9\]\)

IP \(?:%{IPV6}\|%{IPV4}\)

HOSTNAME \b\(?:\[0-9A-Za-z\]\[0-9A-Za-z-\]{0,62}\)\(?:.\(?:\[0-9A-Za-z\]\[0-9A-Za-z-\]{0,62}\)\)\*\(.?\|\b\)

HOST %{HOSTNAME}

IPORHOST \(?:%{HOSTNAME}\|%{IP}\)

HOSTPORT \(?:%{IPORHOST=~/./}:%{POSINT}\)

\# paths

PATH \(?:%{UNIXPATH}\|%{WINPATH}\)

UNIXPATH \(?&gt;/\(?&gt;\[\w\_%!$@:.,-\]+\|\.\)\*\)+

TTY \(?:/dev/\(pts\|tty\(\[pq\]\)?\)\(\w+\)?/?\(?:\[0-9\]+\)\)

WINPATH \(?&gt;\[A-Za-z\]+:\|\\)\(?:\\[^\?\*\]\*\)+

URIPROTO \[A-Za-z\]+\(+\[A-Za-z+\]+\)?

URIHOST %{IPORHOST}\(?::%{POSINT:port}\)?

\# uripath comes loosely from RFC1738, but mostly from what Firefox

\# doesn’t turn into %XX

URIPATH \(?:/\[A-Za-z0-9$.+!\*'\(\){},~:;=@\#%\_-\]\*\)+

\#URIPARAM \?\(?:\[A-Za-z0-9\]+\(?:=\(?:\[^&\]\*\)\)?\(?:&\(?:\[A-Za-z0-9\]+\(?:=\(?:\[^&\]\*\)\)?\)?\)\*\)?

URIPARAM \?\[A-Za-z0-9$.+!\*’\|\(\){},~@\#%&/=:;\_?-\\[\\]\]\*

URIPATHPARAM %{URIPATH}\(?:%{URIPARAM}\)?

URI %{URIPROTO}://\(?:%{USER}\(?::\[^@\]\*\)?@\)?\(?:%{URIHOST}\)?\(?:%{URIPATHPARAM}\)?

\# Months: January, Feb, 3, 03, 12, December

MONTH \b\(?:Jan\(?:uary\)?\|Feb\(?:ruary\)?\|Mar\(?:ch\)?\|Apr\(?:il\)?\|May\|Jun\(?:e\)?\|Jul\(?:y\)?\|Aug\(?:ust\)?\|Sep\(?:tember\)?\|Oct\(?:ober\)?\|Nov\(?:ember\)?\|Dec\(?:ember\)?\)\b

MONTHNUM \(?:0?\[1-9\]\|1\[0-2\]\)

MONTHDAY \(?:\(?:0\[1-9\]\)\|\(?:\[12\]\[0-9\]\)\|\(?:3\[01\]\)\|\[1-9\]\)

\# Days: Monday, Tue, Thu, etc…

DAY \(?:Mon\(?:day\)?\|Tue\(?:sday\)?\|Wed\(?:nesday\)?\|Thu\(?:rsday\)?\|Fri\(?:day\)?\|Sat\(?:urday\)?\|Sun\(?:day\)?\)

\# Years?

YEAR \(?&gt;\d\d\){1,2}

HOUR \(?:2\[0123\]\|\[01\]?\[0-9\]\)

MINUTE \(?:\[0-5\]\[0-9\]\)

\# ’60′ is a leap second in most time standards and thus is valid.

SECOND \(?:\(?:\[0-5\]\[0-9\]\|60\)\(?:\[:.,\]\[0-9\]+\)?\)

TIME \(?!&lt;\[0-9\]\)%{HOUR}:%{MINUTE}\(?::%{SECOND}\)\(?!\[0-9\]\)

\# datestamp is YYYY/MM/DD-HH:MM:SS.UUUU \(or something like it\)

DATE\_US %{MONTHNUM}\[/-\]%{MONTHDAY}\[/-\]%{YEAR}

DATE\_EU %{MONTHDAY}\[./-\]%{MONTHNUM}\[./-\]%{YEAR}

ISO8601\_TIMEZONE \(?:Z\|\[+-\]%{HOUR}\(?::?%{MINUTE}\)\)

ISO8601\_SECOND \(?:%{SECOND}\|60\)

TIMESTAMP\_ISO8601 %{YEAR}-%{MONTHNUM}-%{MONTHDAY}\[T \]%{HOUR}:?%{MINUTE}\(?::?%{SECOND}\)?%{ISO8601\_TIMEZONE}?

DATE %{DATE\_US}\|%{DATE\_EU}

DATESTAMP %{DATE}\[- \]%{TIME}

TZ \(?:\[PMCE\]\[SD\]T\|UTC\)

DATESTAMP\_RFC822 %{DAY} %{MONTH} %{MONTHDAY} %{YEAR} %{TIME} %{TZ}

DATESTAMP\_OTHER %{DAY} %{MONTH} %{MONTHDAY} %{TIME} %{TZ} %{YEAR}

\# Syslog Dates: Month Day HH:MM:SS

SYSLOGTIMESTAMP %{MONTH} +%{MONTHDAY} %{TIME}

PROG \(?:\[\w.\_/%-\]+\)

SYSLOGPROG %{PROG:program}\(?:\\[%{POSINT:pid}\\]\)?

SYSLOGHOST %{IPORHOST}

SYSLOGFACILITY &lt;%{NONNEGINT:facility}.%{NONNEGINT:priority}&gt;

HTTPDATE %{MONTHDAY}/%{MONTH}/%{YEAR}:%{TIME} %{INT}

\# Shortcuts

QS %{QUOTEDSTRING}

\# Log formats

SYSLOGBASE %{SYSLOGTIMESTAMP:timestamp} \(?:%{SYSLOGFACILITY} \)?%{SYSLOGHOST:logsource} %{SYSLOGPROG}:

COMMONAPACHELOG %{IPORHOST:clientip} %{USER:ident} %{USER:auth} \\[%{HTTPDATE:timestamp}\\] “\(?:%{WORD:verb} %{NOTSPACE:request}\(?: HTTP/%{NUMBER:httpversion}\)?\|%{DATA:rawrequest}\)” %{NUMBER:response} \(?:%{NUMBER:bytes}\|-\)

COMBINEDAPACHELOG %{COMMONAPACHELOG} %{QS:referrer} %{QS:agent}

\# Log Levels

LOGLEVEL \(\[A-a\]lert\|ALERT\|\[T\|t\]race\|TRACE\|\[D\|d\]ebug\|DEBUG\|\[N\|n\]otice\|NOTICE\|\[I\|i\]nfo\|INFO\|\[W\|w\]arn?\(?:ing\)?\|WARN?\(?:ING\)?\|\[E\|e\]rr?\(?:or\)?\|ERR?\(?:OR\)?\|\[C\|c\]rit?\(?:ical\)?\|CRIT?\(?:ICAL\)?\|\[F\|f\]atal\|FATAL\|\[S\|s\]evere\|SEVERE\|EMERG\(?:ENCY\)?\|\[Ee\]merg\(?:ency\)?\)

## awstats
```
http://blog.csdn.net/wanglipo/article/details/18080819
wget https://prdownloads.sourceforge.net/awstats/awstats-7.5.tar.gz
tar -zxf awstats-7.5.tar.gz 
mv awstats-7.5 /usr/local/awstats
cd /usr/local/awstats/tools/
mkdir -pv /var/lib/awstats
chmod 777 /var/lib/awstats
perl awstats_configure.pl
----- AWStats awstats_configure 1.0 (build 1.9) (c) Laurent Destailleur -----
This tool will help you to configure AWStats to analyze statistics for
one web server. You can try to use it to let it do all that is possible
in AWStats setup, however following the step by step manual setup
documentation (docs/index.html) is often a better idea. Above all if:
- You are not an administrator user,
- You want to analyze downloaded log files without web server,
- You want to analyze mail or ftp log files instead of web log files,
- You need to analyze load balanced servers log files,
- You want to 'understand' all possible ways to use AWStats...
Read the AWStats documentation (docs/index.html).

-----> Running OS detected: Linux, BSD or Unix

-----> Check for web server install

Enter full config file path of your Web server.
Example: /etc/httpd/httpd.conf
Example: /usr/local/apache2/conf/httpd.conf
Example:c:\Programfiles\apachegroup\apache\conf\httpd.conf
Config file path ('none' to skip web server setup):
>/etc/httpd/conf/httpd.conf  根据自己的httpd服务安装的具体路径填写
-----> Check and complete web server config file
'/etc/httpd/conf/httpd.conf'
 Add 'Alias /awstatsclasses "/usr/local/awstats/wwwroot/classes/"'
 Add 'Alias /awstatscss
"/usr/local/awstats/wwwroot/css/"'
 Add 'Alias /awstatsicons
"/usr/local/awstats/wwwroot/icon/"'
 Add 'ScriptAlias /awstats/ "/usr/local/awstats/wwwroot/cgi-bin/"'
 Add '<Directory>' directive
 AWStats directives added to Apache config file.

-----> Update model config file '/usr/local/awstats/wwwroot/cgi-bin/awstats.model.conf'
 File awstats.model.conf updated.

-----> Need to create a new config file ?
Do you want me to build a new AWStats config/profile
file (required if first install) [y/N] ?y

-----> Define config file name to create
What is the name of your web site or profile analysis ?
Example: www.mysite.com
Example: demo
Your web site, virtual server or profile name:
>lingling 可以是任意的名字，也可以是完整的域名格式，只是为了区分你要分析的那份日志的来源的网站，自己注意不要混淆就好。

-----> Define config file path
In which directory do you plan to store your config file(s) ?
Default: /etc/awstats
Directory path to store config file(s) (Enter for default):
>
默认的awstats生成的配置文件目录，根据喜好可以更改。
-----> Create config file '/etc/awstats/awstats.lingling.conf'
 Config file /etc/awstats/awstats.lingling.conf created.

-----> Restart Web server with '/sbin/service httpd restart'
Stopping httpd:                                     [OK]
Starting httpd:                                       [OK]

-----> Add update process inside a scheduler
Sorry, configure.pl does not support automatic add to cron yet.
You can do it manually by adding the following command to your cron:
/usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=lingling
Or if you have several config files and prefer having only one command:
/usr/local/awstats/tools/awstats_updateall.pl now
Press ENTER to continue...

A SIMPLE config file has been created: /etc/awstats/awstats.lingling.conf
You should have a look inside to check and change manually main parameters.
You can then manually update your statistics for 'lingling' with command:
> perl awstats.pl -update -config=lingling
You can also read your statistics for 'lingling' with URL:
> http://localhost/awstats/awstats.pl?config=lingling

Press ENTER to finish...


1、由于httpd的log文件默认是/var/log/httpd/access.log，
所以要修改/etc/awstats/awstats.lingling.conf文件里的LogFile：
把LogFile="/var/log/httpd/mylog.log"改为LogFile="/var/log/httpd/access_log"
或者LogFile="var/log/access_log.%YYYY-0%MM-0%DD-0.log"
2、然后，手动更新一下：
# cd /usr/local/awstats/wwwroot/cgi-bin/
# perl awstats.pl –update –config=lingling
3、打开浏览器，用awstats分析日志：
http://10.100.10.11/awstats/awstats.pl?config=lingling

4、可以将更新的命令作为执行计划，使其每天执行一次，方便分析前一天的日。
# crontab –e
10 1 * * * /usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=lingling > /dev/null 2&>1

三、用awstats分析tomcat的访问日志
1、要分析tomcat的日志，就要首先了解其日志格式。
并比较与httpd的访问日志格式有什么不同之处，然后就可以参照awstats分析httpd日志的格式来定义awstats分析tomcat的日志。
我的tomcat服务器上定义的访问日志格式如下：
<Valve className="org.apache.catalina.valves.
AccessLogValve" directory="logs"
prefix="localhost_access_log." suffix=".txt"
       pattern="%h %l %u %t &quot;%r&quot; %s %b" />
%...a: 远程IP地址  
%...A: 本地IP地址  
%...B: 已发送的字节数，不包含HTTP头  
%...b: CLF格式的已发送字节数量，不包含HTTP头。  
例如当没有发送数据时，写入‘-’而不是0。  
%e: 环境变量FOOBAR的内容  
%...f: 文件名字  
%...h: 远程主机  
%...H 请求的协议  
%i: Foobar的内容，发送给服务器的请求的标头行。  
%...l: 远程登录名字（来自identd，如提供的话）  
%...m 请求的方法  
%n: 来自另外一个模块的注解“Foobar”的内容  
%o: Foobar的内容，应答的标头行  
%...p: 服务器响应请求时使用的端口  
%...P: 响应请求的子进程ID。  
%...q 查询字符串（如果存在查询字符串，则包含“?”后面的  
部分；否则，它是一个空字符串。）  
%...r: 请求的第一行  
%...s: 状态。对于进行内部重定向的请求，这是指*原来*请求  
的状态。如果用%...>s，则是指后来的请求。  
%...t: 以公共日志时间格式表示的时间（或称为标准英文格式）  
%t: 以指定格式format表示的时间  
%...T: 为响应请求而耗费的时间，以秒计  
%...u: 远程用户（来自auth；如果返回状态（%s）是401则可能是伪造的）  
%...U: 用户所请求的URL路径  
%...v: 响应请求的服务器的ServerName  
%...V: 依照UseCanonicalName设置得到的服务器名字  
最后的tomcat的访问日志内容如下：
203.156.200.162 - - [29/Aug/2012:11:16:58 +0800] "GET /front/magazine/getContent.htm?contentId=124504 HTTP/1.1" 
200 20001
2、由于我的tomcat服务器是在其他机器上，所以我将tomcat的服务日志copy到本机的/var/log/httpd/下即可。
如copy的文件是：localhost_access_log.2012-08-29.txt
3、配置awstats分析此日志(tomcat 的域名并不是httpd的虚拟主机，所以没有写进httpd.conf文件里面)
# cd /usr/local/awstats/tools
# perl awstats_configure.pl
----- AWStats awstats_configure 1.0 (build 1.9) (c) Laurent Destailleur -----
This tool will help you to configure AWStats to analyze statistics for
one web server. You can try to use it to let it do all that is possible
in AWStats setup, however following the step by step manual setup
documentation (docs/index.html) is often a better idea. Above all if:
- You are not an administrator user,
- You want to analyze downloaded log files without web server,
- You want to analyze mail or ftp log files instead of web log files,
- You need to analyze load balanced servers log files,
- You want to 'understand' all possible ways to use AWStats...
Read the AWStats documentation (docs/index.html).

-----> Running OS detected: Linux, BSD or Unix

-----> Check for web server install

Enter full config file path of your Web server.
Example: /etc/httpd/httpd.conf
Example: /usr/local/apache2/conf/httpd.conf
Example: c:\Program files\apache group\apache\conf\httpd.conf
Config file path ('none' to skip web server setup):
>none
Your web server config file(s) could not be found.
You will need to setup your web server manually to declare AWStats
script as a CGI, if you want to build reports dynamically.
See AWStats setup documentation (file docs/index.html)

-----> Update model config file '/usr/local/awstats/wwwroot/cgi-bin/awstats.model.conf'
 File awstats.model.conf updated.

-----> Need to create a new config file ?
Do you want me to build a new AWStats config/profile
file (required if first install) [y/N] ? y

-----> Define config file name to create
What is the name of your web site or profile analysis ?
Example: www.mysite.com
Example: demo
Your web site, virtual server or profile name:
>buoqu.com
-----> Define config file path
In which directory do you plan to store your config file(s) ?
Default: /etc/awstats
Directory path to store config file(s) (Enter for default):
>

-----> Create config file '/etc/awstats/awstats.buoqu.com.conf'
 Config file /etc/awstats/awstats.buoqu.com.conf created.

-----> Add update process inside a scheduler
Sorry, configure.pl does not support automatic add to cron yet.
You can do it manually by adding the following command to your cron:
/usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=buoqu.com
Or if you have several config files and prefer having only one command:
/usr/local/awstats/tools/awstats_updateall.pl now
Press ENTER to continue...


A SIMPLE config file has been created: /etc/awstats/awstats.buoqu.com.conf
You should have a look inside to check and change manually main parameters.
You can then manually update your statistics for 'buoqu.com' with command:
> perl awstats.pl -update -config=buoqu.com
You can also build static report pages for 'buoqu.com' with command:
> perl awstats.pl -output=pagetype -config=buoqu.com

Press ENTER to finish...
4、修改要分析日志文件
# vim /etc/awstats/awstats.buoqu.com.conf
将LogFile="/var/log/httpd/mylog.log"
改为
LogFile="/usr/local/awstats/tools/logresolvemerge.pl /usr/local/awstats/flashlog/china/localhost_access_log.%
YYYY-24-%MM-24-%DD-24.txt /usr/local/awstats/flashlog/usa/localhost_access_log.%YYYY-24-%MM-24-%DD-24.txt |"
5、重启httpd服务，并分析日志
# service httpd restart
# cd /usr/local/awstats/wwwroot/cgi-bin
# perl awstats.pl -update -config=buoqu.com

Setup ('/etc/awstats/awstats.buoqu.com.conf' file, web server or permissions) may be wrong.
Check config file, permissions and AWStats documentation (in 'docs' directory).
出错：日志格式不匹配。
解决：这个时候，就知道我为什么要先了解怎么定义tomcat的日志格式了。
修改文件/etc/awstats/awstats.buoqu.com.conf
# vim /etc/awstats/awstats.buoqu.com.conf
LogFormat = 1
LogFormat ="%host %other %logname %time1 %methodurl %code %bytesd"   自定义格式

# perl awstats.pl -update -config=buoqu.com
6、打开网址查看分析结果：

http://10.100.10.11/awstats/awstats.pl?config=buoqu.com


7、手动执行命令可写入crontab。
①、如果，想在分析页面上直接刷新，可以开启AllowToUpdateStatsFromBrowser=1，默认情况下是关闭的。
②、若是想每个页面上都直接有“立即更新”的按钮，而不想每次都手动的修改配置文件的话，可以再awstats的基本配置文件里修改。
# cd /usr/local/awstats/wwwroot/cgi-bin
# vim awstats.model.conf
将AllowToUpdateStatsFromBrowser=0改为AllowToUpdateStatsFromBrowser=1即可。
这样，以后的网页都可以直接点击刷新的。
注意：每次修改配置文件后要重启httpd服务
③、若是要在浏览器上直接刷新，那么apache用户就要有对数据文件操作的权限
# chown apache.apache –R /var/lib/awstats
# chmod 755 /var/log/httpd
效果如图：

四、添加一些插件，使awstats看起来更人性化和直观化。
IP显示地区
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
gunzip GeoIP.dat.gz
gunzip GeoLiteCity.dat.gz
mv *.dat /opt/
yum install GeoIP perl-Geo-IP
perl -MCPAN -e "install Geo::IP::PurePerl"

vim /etc/awstats/awstats.www.test.com.conf
将以下语句的#注释去掉：
#LoadPlugin="tooltips"      在html报告中增加一些提示信息
#LoadPlugin="decodeutfkeys" 处理搜索引擎UTF8编码的关键字

#LoadPlugin="geoip GEOIP_STANDARD /pathto/GeoIP.dat" #1429行
#LoadPlugin="geoip_city_maxmind GEOIP_STANDARD /pathto/GeoIPCity.dat" #1438行
修改为：
LoadPlugin="geoip GEOIP_STANDARD /var/geoip/GeoIP.dat"
LoadPlugin="geoip_city_maxmind GEOIP_STANDARD /var/geoip/GeoLiteCity.dat"

 使用QQ纯真版IP
(1) 在awstats的wwwroot下的plugin目录里下载
cd /usr/local/awstats/wwwroot/cgi-bin/plugins
# yum安装时目录为：/usr/share/awstats/wwwroot/cgi-bin/plugins ，没有则建立
wget http://www.haiyun.me/download/qqwry.pl
wget http://www.haiyun.me/download/qqhostinfo.pm
获取最新的IP信息的方式为：到update.cz88.net中下在windows安装版，之后在安装目录里有qqwry.dat，既是最新的数据。
(2)上传qqwry到awstats的wwwroot下的plugin目录里.
(3) 修改插件配置
#修改qqwry.pl内IP数据目录：
my $ipfile="${DIR}/plugins/qqwry.dat";
(4) 添加插件到awstats
#修改awstats配置加载扩展：
LoadPlugin="qqhostinfo"
删除旧的统计数据库  rm -rf /var/lib/awstats/*
重新生成一下数据库     /usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=
www.test.com

-------------------------------------------------
#!/usr/bin/env bash
rsync -avz /var/lib/awstats/ /usr/local/awstats/var-lib-awstats
find /usr/local/awstats/flashlog/ -mtime +1 -exec rm -f {} \;

Date=$(date +%Y-%m-%d -d "1 day ago")
#101.200.131.163 flash china
rsync -avz '-e ssh -p 27554' 10.44.28.154:/usr/local/tomcat/logs/localhost_access_log.$Date.txt
 /usr/local/awstats/flashlog/china/
rsync -avz '-e ssh -p 27554' 47.88.7.159:/usr/local/tomcat/logs/localhost_access_log.$Date.txt 
 /usr/local/awstats/flashlog/usa/

/usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=flash
# http://monitor.3mang.com/awstats/awstats.pl?config=flash

-----------------------------------------------------------
#awstats log   定时任务
0 1 * * * /bin/bash /usr/local/awstats/scplog.sh > /usr/local/awstats/scplog.log 2&>1

awstats分析多个日志
分析单个日志：
LogFile="/usr/local/nginx/logs/host.access.log"
分析多个日志：
1）分开写
LogFile="/usr/local/awstats/tools/logresolvemerge.pl /usr/local/nginx/logs/231.pcstars_access.log 
/usr/local/nginx/logs/232.pcstars_access.log /usr/local/nginx/logs/233.pcstars_access.log
 /usr/local/nginx/logs/234.pcstars_access.log /usr/local/nginx/logs/mg.pcstars_access.log|"
2)以匹配模式:
LogFile="/usr/local/awstats/tools/logresolvemerge.pl /usr/local/nginx/logs/*.pcstars_access.log|"
说明：使用 awstats 内建的工具logresolvemerge.pl 来合并日志，记的后面加一个"|"，表示匹配你要一起合并分析的日志
完成awstats配置文件的设置之后，需要更新记录：
 /usr/local/awstats/tools/awstats_updateall.pl now
 或
 /usr/local/awstats/wwwroot/cgi-bin/awstats.pl -update -config=www.nginx.log -configdir="/etc/awstats"
```



## 访问分析
```
PIWIK
https://piwik.org/


Google Analytics
https://developers.google.com/analytics/?hl=zh-cn
```



## es_date
elasticsearch原生支持date类型，结合该类型和Kibana可以做出漂亮有用的图表。这里简单记录下使用的方法。

使用date类型可以用如下两种方式：

使用毫秒的时间戳，直接将毫秒值传入即可。

传入格式化的字符串，默认是ISO 8601标准，例如2015-02-27T00:07Z\(零时区\)、2015-02-27T08:07+08:00\(东八区\),这两个时间实际是同一个，只是时区不同，关于时间戳，可以参见我之前的文章。另外还可以自定义时间格式，参见es的文档。但个人不建议使用自定义格式，设置不当容易遇到时区问题。在php中获取ISO 8601标准的时间很简单，date\('c',time\(\)）即可。

elasticsearch默认会自动识别date类型，如果想关闭该功能，修改mapping的设置'date\_detection' =&gt; false即可 。





elasticsearch原生支持date类型，json格式通过字符来表示date类型。所以在用json提交日期至elasticsearch的时候，es会隐式转换，把es认为是date类型的字符串直接转为date类型。至于什么样的字符串es会认为可以转换成date类型，参考elasticsearch官网介绍https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-date-format.html。



　　date类型是包含时区信息的，如果我们没有在json代表日期的字符串中显式指定时区，对es来说没什么问题，但是如果通过kibana显示es里的数据时，就会出现问题，数据的时间会晚8个小时。因为kibana从es里读取的date类型数据，没有时区信息，kibana会默认当作0时区来解析，但是kibana在通过浏览器展示的时候，会通过js获取当前客户端机器所在的时区，也就是东八区，所以kibana会把从es得到的日期数据减去8小时。这里就会导致kibana经常遇到的“数据时间延迟8小时”的问题。



　　所以最佳实践方案就是：我们在往es提交日期数据的时候，直接提交带有时区信息的日期字符串，如：“2016-07-15T12:58:17.136+0800”。

## logstash区分数据
```
场景，logstash采集2个数据源A和B，A数据源的入kafka，B数据源的都入es。

语法

Input{ 
  file { path => a  type => A }
  file { path => b  type => B }
}

output {
  if [type] == "A" {
    kafka {...}
  }
  if [type] == "B" {
    es {...}
  }
}
我的实现的场景：

bin/logstash -e 'input{
   file{
    type => "normal"
    path => "/data/log/test/abc*.log"
    start_position => beginning
    exclude => "*abc*.log"
  }

  file{
    type => "error"
    path => "/data/log/test/*error*.log"
    start_position => beginning
  }
}
output{
if [type] == "error" {
    kafka{
       bootstrap_servers => "127.0.0.1:9092,127.0.0.1:9092"
       topic_id => "loga"
      }
}
    stdout{codec=>rubydebug}
}'
```



## winlogbeat
配置 winlogbeat.yml   配置ignore\_older，否则会导入系统里很久之前的数据

```
winlogbeat.event_logs:
    - name: Application
      ignore_older: 48h
      provider:
          - Application Error
          - Application Hang
          - Windows Error Reporting
          - EMET
    - name: Security
      level: critical, error, warning
      event_id: 4624, 4625, 4700-4800, -4735
      ignore_older: 48h
    - name: System
      level: critical, error, warning
      ignore_older: 48h
    - name: Microsoft-Windows-Windows Defender/Operational
      include_xml: true
      ignore_older: 48h
```

**导入es模板** scripts\import\_dashboards.exe -es [http://192.168.33.60:9200](http://192.168.33.60:9200)

**安装服务**

powershell管理员运行 .\install-service-winlogbeat.ps1

执行报错scripts is disabled on this system 需要先执行  Set-ExecutionPolicy RemoteSigned解除限制

net start/stop winlogbeat

**命令行运行**  .\winlogbeat.exe -c .\winlogbeat.yml

## filebeat例子
https://www.elastic.co/guide/en/logstash/current/logstash-config-for-filebeat-modules.html\#parsing-system

Apache 2 Logs

MySQL Logs

Nginx Logs

System Logs

Apache 2 Access Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/apache2/access.log\*

* /var/log/apache2/other\_vhosts\_access.log\*

exclude\_files: \[".gz$"\]

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{IPORHOST:\[apache2\]\[access\]\[remote\_ip\]} - %{DATA:\[apache2\]\[access\]\[user\_name\]} \\[%{HTTPDATE:\[apache2\]\[access\]\[time\]}\\] \"%{WORD:\[apache2\]\[access\]\[method\]} %{DATA:\[apache2\]\[access\]\[url\]} HTTP/%{NUMBER:\[apache2\]\[access\]\[http\_version\]}\" %{NUMBER:\[apache2\]\[access\]\[response\_code\]} %{NUMBER:\[apache2\]\[access\]\[body\_sent\]\[bytes\]}\( \"%{DATA:\[apache2\]\[access\]\[referrer\]}\"\)?\( \"%{DATA:\[apache2\]\[access\]\[agent\]}\"\)?",

"%{IPORHOST:\[apache2\]\[access\]\[remote\_ip\]} - %{DATA:\[apache2\]\[access\]\[user\_name\]} \\[%{HTTPDATE:\[apache2\]\[access\]\[time\]}\\] \"-\" %{NUMBER:\[apache2\]\[access\]\[response\_code\]} -" \] }

remove\_field =&gt; "message"

}

mutate {

add\_field =&gt; { "read\_timestamp" =&gt; "%{@timestamp}" }

}

date {

match =&gt; \[ "\[apache2\]\[access\]\[time\]", "dd/MMM/YYYY:H:m:s Z" \]

remove\_field =&gt; "\[apache2\]\[access\]\[time\]"

}

useragent {

source =&gt; "\[apache2\]\[access\]\[agent\]"

target =&gt; "\[apache2\]\[access\]\[user\_agent\]"

remove\_field =&gt; "\[apache2\]\[access\]\[agent\]"

}

geoip {

source =&gt; "\[apache2\]\[access\]\[remote\_ip\]"

target =&gt; "\[apache2\]\[access\]\[geoip\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

Apache 2 Error Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/apache2/error.log\*

exclude\_files: \[".gz$"\]

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["\\[%{APACHE\_TIME:\[apache2\]\[error\]\[timestamp\]}\\] \\[%{LOGLEVEL:\[apache2\]\[error\]\[level\]}\\]\( \\[client %{IPORHOST:\[apache2\]\[error\]\[client\]}\\]\)? %{GREEDYDATA:\[apache2\]\[error\]\[message\]}",

"\\[%{APACHE\_TIME:\[apache2\]\[error\]\[timestamp\]}\\] \\[%{DATA:\[apache2\]\[error\]\[module\]}:%{LOGLEVEL:\[apache2\]\[error\]\[level\]}\\] \\[pid %{NUMBER:\[apache2\]\[error\]\[pid\]}\(:tid %{NUMBER:\[apache2\]\[error\]\[tid\]}\)?\\]\( \\[client %{IPORHOST:\[apache2\]\[error\]\[client\]}\\]\)? %{GREEDYDATA:\[apache2\]\[error\]\[message1\]}" \] }

pattern\_definitions =&gt; {

"APACHE\_TIME" =&gt; "%{DAY} %{MONTH} %{MONTHDAY} %{TIME} %{YEAR}"

}

remove\_field =&gt; "message"

}

mutate {

rename =&gt; { "\[apache2\]\[error\]\[message1\]" =&gt; "\[apache2\]\[error\]\[message\]" }

}

date {

match =&gt; \[ "\[apache2\]\[error\]\[timestamp\]", "EEE MMM dd H:m:s YYYY", "EEE MMM dd H:m:s.SSSSSS YYYY" \]

remove\_field =&gt; "\[apache2\]\[error\]\[timestamp\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

MySQL Logsedit

Here are some configuration examples for shipping and parsing MySQL error and slowlog logs.

MySQL Error Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/mysql/error.log\*

* /var/log/mysqld.log\*

exclude\_files: \[".gz$"\]

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{LOCALDATETIME:\[mysql\]\[error\]\[timestamp\]} \(\\[%{DATA:\[mysql\]\[error\]\[level\]}\\] \)?%{GREEDYDATA:\[mysql\]\[error\]\[message\]}",

"%{TIMESTAMP\_ISO8601:\[mysql\]\[error\]\[timestamp\]} %{NUMBER:\[mysql\]\[error\]\[thread\_id\]} \\[%{DATA:\[mysql\]\[error\]\[level\]}\\] %{GREEDYDATA:\[mysql\]\[error\]\[message1\]}",

"%{GREEDYDATA:\[mysql\]\[error\]\[message2\]}"\] }

pattern\_definitions =&gt; {

"LOCALDATETIME" =&gt; "\[0-9\]+ %{TIME}"

}

remove\_field =&gt; "message"

}

mutate {

rename =&gt; { "\[mysql\]\[error\]\[message1\]" =&gt; "\[mysql\]\[error\]\[message\]" }

}

mutate {

rename =&gt; { "\[mysql\]\[error\]\[message2\]" =&gt; "\[mysql\]\[error\]\[message\]" }

}

date {

match =&gt; \[ "\[mysql\]\[error\]\[timestamp\]", "ISO8601", "YYMMdd H:m:s" \]

remove\_field =&gt; "\[apache2\]\[access\]\[time\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

MySQL Slowlogedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/mysql/mysql-slow.log\*

* /var/lib/mysql/hostname-slow.log

exclude\_files: \[".gz$"\]

multiline:

pattern: "^\# User@Host: "

negate: true

match: after

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["^\# User@Host: %{USER:\[mysql\]\[slowlog\]\[user\]}\(\\[\[^\\]\]+\\]\)? @ %{HOSTNAME:\[mysql\]\[slowlog\]\[host\]} \\[\(IP:\[mysql\]\[slowlog\]\[ip\]\)?\\]\(\s\*Id:\s\* %{NUMBER:\[mysql\]\[slowlog\]\[id\]}\)?\n\# Query\_time: %{NUMBER:\[mysql\]\[slowlog\]\[query\_time\]\[sec\]}\s\* Lock\_time: %{NUMBER:\[mysql\]\[slowlog\]\[lock\_time\]\[sec\]}\s\* Rows\_sent: %{NUMBER:\[mysql\]\[slowlog\]\[rows\_sent\]}\s\* Rows\_examined: %{NUMBER:\[mysql\]\[slowlog\]\[rows\_examined\]}\n\(SET timestamp=%{NUMBER:\[mysql\]\[slowlog\]\[timestamp\]};\n\)?%{GREEDYMULTILINE:\[mysql\]\[slowlog\]\[query\]}"\] }

pattern\_definitions =&gt; {

"GREEDYMULTILINE" =&gt; "\(.\|\n\)\*"

}

remove\_field =&gt; "message"

}

date {

match =&gt; \[ "\[mysql\]\[slowlog\]\[timestamp\]", "UNIX" \]

}

mutate {

gsub =&gt; \["\[mysql\]\[slowlog\]\[query\]", "\n\# Time: \[0-9\]+ \[0-9\]\[0-9\]:\[0-9\]\[0-9\]:\[0-9\]\[0-9\]\(\.\[0-9\]+\)?$", ""\]

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

Nginx Logsedit

Here are some configuration examples for shipping and parsing Nginx access and error logs.

Nginx Access Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/nginx/access.log\*

exclude\_files: \[".gz$"\]

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{IPORHOST:\[nginx\]\[access\]\[remote\_ip\]} - %{DATA:\[nginx\]\[access\]\[user\_name\]} \\[%{HTTPDATE:\[nginx\]\[access\]\[time\]}\\] \"%{WORD:\[nginx\]\[access\]\[method\]} %{DATA:\[nginx\]\[access\]\[url\]} HTTP/%{NUMBER:\[nginx\]\[access\]\[http\_version\]}\" %{NUMBER:\[nginx\]\[access\]\[response\_code\]} %{NUMBER:\[nginx\]\[access\]\[body\_sent\]\[bytes\]} \"%{DATA:\[nginx\]\[access\]\[referrer\]}\" \"%{DATA:\[nginx\]\[access\]\[agent\]}\""\] }

remove\_field =&gt; "message"

}

mutate {

rename =&gt; { "@timestamp" =&gt; "read\_timestamp" }

}

date {

match =&gt; \[ "\[nginx\]\[access\]\[time\]", "dd/MMM/YYYY:H:m:s Z" \]

remove\_field =&gt; "\[nginx\]\[access\]\[time\]"

}

useragent {

source =&gt; "\[nginx\]\[access\]\[agent\]"

target =&gt; "\[nginx\]\[access\]\[user\_agent\]"

remove\_field =&gt; "\[nginx\]\[access\]\[agent\]"

}

geoip {

source =&gt; "\[nginx\]\[access\]\[remote\_ip\]"

target =&gt; "\[nginx\]\[access\]\[geoip\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

Nginx Error Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/nginx/error.log\*

exclude\_files: \[".gz$"\]

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{DATA:\[nginx\]\[error\]\[time\]} \\[%{DATA:\[nginx\]\[error\]\[level\]}\\] %{NUMBER:\[nginx\]\[error\]\[pid\]}\#%{NUMBER:\[nginx\]\[error\]\[tid\]}: \(\\*%{NUMBER:\[nginx\]\[error\]\[connection\_id\]} \)?%{GREEDYDATA:\[nginx\]\[error\]\[message\]}"\] }

remove\_field =&gt; "message"

}

mutate {

rename =&gt; { "@timestamp" =&gt; "read\_timestamp" }

}

date {

match =&gt; \[ "\[nginx\]\[error\]\[time\]", "YYYY/MM/dd H:m:s" \]

remove\_field =&gt; "\[nginx\]\[error\]\[time\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

System Logsedit

Here are some configuration examples for shipping and parsing system logs.

System Authorization Logsedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/auth.log\*

* /var/log/secure\*

exclude\_files: \[".gz$"\]

multiline:

pattern: "^\s"

match: after

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} sshd\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: %{DATA:\[system\]\[auth\]\[ssh\]\[event\]} %{DATA:\[system\]\[auth\]\[ssh\]\[method\]} for \(invalid user \)?%{DATA:\[system\]\[auth\]\[user\]} from %{IPORHOST:\[system\]\[auth\]\[ssh\]\[ip\]} port %{NUMBER:\[system\]\[auth\]\[ssh\]\[port\]} ssh2\(: %{GREEDYDATA:\[system\]\[auth\]\[ssh\]\[signature\]}\)?",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} sshd\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: %{DATA:\[system\]\[auth\]\[ssh\]\[event\]} user %{DATA:\[system\]\[auth\]\[user\]} from %{IPORHOST:\[system\]\[auth\]\[ssh\]\[ip\]}",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} sshd\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: Did not receive identification string from %{IPORHOST:\[system\]\[auth\]\[ssh\]\[dropped\_ip\]}",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} sudo\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: \s\*%{DATA:\[system\]\[auth\]\[user\]} :\( %{DATA:\[system\]\[auth\]\[sudo\]\[error\]} ;\)? TTY=%{DATA:\[system\]\[auth\]\[sudo\]\[tty\]} ; PWD=%{DATA:\[system\]\[auth\]\[sudo\]\[pwd\]} ; USER=%{DATA:\[system\]\[auth\]\[sudo\]\[user\]} ; COMMAND=%{GREEDYDATA:\[system\]\[auth\]\[sudo\]\[command\]}",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} groupadd\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: new group: name=%{DATA:system.auth.groupadd.name}, GID=%{NUMBER:system.auth.groupadd.gid}",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} useradd\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: new user: name=%{DATA:\[system\]\[auth\]\[user\]\[add\]\[name\]}, UID=%{NUMBER:\[system\]\[auth\]\[user\]\[add\]\[uid\]}, GID=%{NUMBER:\[system\]\[auth\]\[user\]\[add\]\[gid\]}, home=%{DATA:\[system\]\[auth\]\[user\]\[add\]\[home\]}, shell=%{DATA:\[system\]\[auth\]\[user\]\[add\]\[shell\]}$",

"%{SYSLOGTIMESTAMP:\[system\]\[auth\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[auth\]\[hostname\]} %{DATA:\[system\]\[auth\]\[program\]}\(?:\\[%{POSINT:\[system\]\[auth\]\[pid\]}\\]\)?: %{GREEDYMULTILINE:\[system\]\[auth\]\[message\]}"\] }

pattern\_definitions =&gt; {

"GREEDYMULTILINE"=&gt; "\(.\|\n\)\*"

}

remove\_field =&gt; "message"

}

date {

match =&gt; \[ "\[system\]\[auth\]\[timestamp\]", "MMM d HH:mm:ss", "MMM dd HH:mm:ss" \]

}

geoip {

source =&gt; "\[system\]\[auth\]\[ssh\]\[ip\]"

target =&gt; "\[system\]\[auth\]\[ssh\]\[geoip\]"

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

Syslogedit

Example Filebeat config:

filebeat.prospectors:

* input\_type: log

paths:

* /var/log/messages\*

* /var/log/syslog\*

exclude\_files: \[".gz$"\]

multiline:

pattern: "^\s"

match: after

output.logstash:

hosts: \["localhost:5044"\]

Example Logstash pipeline config:

input {

beats {

\# The port to listen on for filebeat connections.

port =&gt; 5044

\# The IP address to listen for filebeat connections.

host =&gt; "0.0.0.0"

}

}

filter {

grok {

match =&gt; { "message" =&gt; \["%{SYSLOGTIMESTAMP:\[system\]\[syslog\]\[timestamp\]} %{SYSLOGHOST:\[system\]\[syslog\]\[hostname\]} %{DATA:\[system\]\[syslog\]\[program\]}\(?:\\[%{POSINT:\[system\]\[syslog\]\[pid\]}\\]\)?: %{GREEDYMULTILINE:\[system\]\[syslog\]\[message\]}"\] }

pattern\_definitions =&gt; { "GREEDYMULTILINE" =&gt; "\(.\|\n\)\*" }

remove\_field =&gt; "message"

}

date {

match =&gt; \[ "\[system\]\[syslog\]\[timestamp\]", "MMM d HH:mm:ss", "MMM dd HH:mm:ss" \]

}

}

output {

elasticsearch {

hosts =&gt; localhost

manage\_template =&gt; false

index =&gt; "%{\[@metadata\]\[beat\]}-%{+YYYY.MM.dd}"

document\_type =&gt; "%{\[@metadata\]\[type\]}"

}

}

## elk优化
```
refresh_interval for indexing
Elasticsearch 是一个近实时搜索引擎。它实际上是每 1 秒钟刷新一次数据。对于日志分析应用，我们用不着这么实时，
所以 logstash 自带的模板修改成了 5 秒钟。你还可以根据需要继续放大这个刷新间隔以提高数据写入性能。
修改 refresh_interval ，那么只需要新写一个tmpl.json：
{
  "order" : 1,
  "template" : "logstash-*",
  "settings" : {
    "index.refresh_interval" : "30s",
    "index.number_of_replicas" : 0     #关闭副本
  }
}
然后运行 curl -XPUT http://localhost:9200/_template/template_newid -d '@/root/tmpl.json' 即可。
logstash 默认的模板， order 是 0，id 是 logstash，通过 logstash/outputs/elasticsearch 的配置选项 template_name 修改。
新模板要比order大
```



## logstash5 root启动
vim  /etc/logstash/startup.options 

LS\_USER=root



/usr/share/logstash/bin/system-install 重新生成启动脚本

重启logstash

## es集群重启
```
elasticsearch集群，有时候可能需要修改配置，增加硬盘，扩展内存等操作，需要对节点进行维护升级。但是业务不能停，
如果直接kill掉节点，可能导致数据丢失。而且集群会认为该节点挂掉了，就开始转移数据，当重启之后，它又会恢复数据，
如果你当前的数据量已经很大了，这是很耗费机器和网络资源的。

官方提供的安全重启集群节点的方法：

第一步：先暂停集群的shard自动均衡。

curl -XPUT http://127.0.0.1:9200/_cluster/settings -d'
{
"transient" : {
"cluster.routing.allocation.enable" : "none"
}
}'
第二步：shutdown你要升级的节点

curl -XPOST http://127.0.0.1:9200/_cluster/nodes/_local/_shutdown
elasticsearch 在 2.0版本之后移除了shutdown接口，所以用pid直接停止即可。

第三步：升级重启该节点，并确认该节点重新加入到了集群中

第四步：重复2-3步，升级重启其它要升级的节点。

第五步：重启启动集群的shard均衡

curl -XPUT http://127.0.0.1:9200/_cluster/settings -d'
{
"transient" : {
"cluster.routing.allocation.enable" : "all"
}
}'
到此整个集群安全升级并且重启结束。
```

## logio
```
yum install npm -y
npm install -g log.io  安装

cd /root/.log.io
cat log_server.conf  模板文件  web_server.conf（当前目录下）
exports.config = {
  host: '0.0.0.0',
  port: 28777,
  auth: {
    user: "admin",
    pass: "xxxx"
  }
}

cat harvester.conf
exports.config = {
  nodeName: "application_server",
  logStreams: {
    tomcat_pingtai: [
      "/usr/local/tomcat_pingtai/logs/catalina.out",
    ],
    tomcat_pingtaitest: [
      "/usr/local/tomcat_pingtaitest/logs/catalina.out",
    ],
    tomcat_cuishou: [
      "/usr/local/tomcat_cuishou/logs/catalina.out",
    ],
    tomcat_cuishoutest: [
      "/usr/local/tomcat_cuishoutest/logs/catalina.out",
    ],
    tomcat_blacklist: [
      "/usr/local/tomcat_blacklist/logs/catalina.out",
    ]
  },
  server: {
    host: '0.0.0.0',
    port: 28777
  }
}


nohup log.io-server  & Launch server
nohup log.io-harvester  & Start log harvester 

浏览器打开 http://localhost:28778

nginx 代理
/etc/nginx/conf.d/default.conf 
location /logio {
        proxy_pass http://192.168.1.2:28778/;
        auth_basic "secret";
        auth_basic_user_file /etc/nginx/passwd.db;
    }
    location /socket.io {
        proxy_pass http://192.168.1.2:28778/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

htpasswd -c /etc/nginx/passwd.db admin
chmod 400 /etc/nginx/passwd.db
chown nginx.nginx /etc/nginx/passwd.db

/etc/init.d/nginx reload
```