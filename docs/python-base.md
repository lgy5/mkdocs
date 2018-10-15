## 列表
```
列表频率排名
from collections import Counter
Counter(list).most_common

列表解析器
[a for a in range(10)] 生成一个列表
(a for a in range(10)) 生成一个生成器
{a for a in range(10)} 生成一个序列
{a:a*2 for a in range(3)} 生成一个字典

>>> {a for a in range(10) if a == 2}
set([2])


list.apped(obj) 向列表中添加一个对象 obj
a=[1,2,3]
a.append(4)  参数为字符，数字，元组，列表，字典等
a.append({‘age’:34})  返回值为 None

list.extend(seq) 把序列 seq 的内容添加到列表中
a=[1,2,3]  参数为列表或元组、字典的 key
b=[3,4,5]
a.extend(b) 返回值为 None

list.insert(n,object) 在索引为 n 的位置插入对象 obj
a=[1,2,3]  参数为索引值和字符，数字，元组，列表，字典
a.insert(0,’du’)  返回值为 None

list.pop([index]) 删除并返回指定位置的对象，默认是最后一个对象
a=[1,2,3,4,5]  参数为索引值或无
a.pop(0)  返回值为删除的值

list.reverse()  原地翻转列表
a=[1,2,3,4] 没有参数
a.reverse() 返回值为 None

list.count(obj) 返回一个对象 obj 在列表中出现的次数
a=[1,2,3,3,3,4]  参数为字符串、整数、浮点数等
a.count(1) 返回值为参数在列表的出现次数

list.index(obj,i=0,j=len(list)) 返回 list[k]==obj 的 k 值,并且 k 的范围在[i,j)
a=[1,2,3,4,5,6,2]  参数为 list 中的值和开始结束的索引（可以可无）
a.index(2) 返回值为 obj 在 list 的索引值

list.remove(value) 从列表中删除对象 obj
a=[1,2,3,4,2]  参数为 list 中的值
a.remove(2) 返回值为 None

list.sort(func=None,key=None,reverse=False) 以指定的方式排序列表中的成员，如果 func 和 key 参数指
定，则按照指定的方式比较各个元素,如果 reverse=True 则列表以反序排列
a=[1,4,2,3,5]
a.sort() a=[1,2,3,4,5]  参数为函数、key、reverse 或没有
a=[‘du’,’dumc’,’d’,’dddddd’]  返回值为 None
a.sort(key=len) a=[‘d’,’du’,’dumc’,’dddddd’] 

https://wiki.python.org/moin/HowTo/Sorting
>>> student_tuples = [
        ('john', 'A', 15),
        ('jane', 'B', 12),
        ('dave', 'B', 10),
]
>>> sorted(student_tuples, key=lambda student: student[2])   # sort by age
[('dave', 'B', 10), ('jane', 'B', 12), ('john', 'A', 15)]

a=[2,2,3,4,5]
list(set(a)    列表去重

获取两个list 的交集
#方法一:
a=[2,3,4,5]
b=[2,5,8]
tmp = [val for val in a if val in b]
print tmp
#[2, 5]

#方法二
print list(set(a).intersection(set(b)))
 
获取两个list 的并集
print list(set(a).union(set(b)))

获取两个 list 的差集
print list(set(b).difference(set(a))) # b中有而a中没有的
```



## 编码
```
UnicodeEncodeError: 'ascii' codec can’t encode characters in position 0-15: ordinal not in range(128)

# coding=utf-8 一定要是等于号

import sys
reload(sys)
sys.setdefaultencoding('utf8')
```



## 时区转换
```
# coding=utf-8
# pip install pygeoip
# wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz

import pytz
import time,os
import pygeoip
from datetime import datetime

gi = pygeoip.GeoIP('GeoLiteCity.dat',pygeoip.MEMORY_CACHE)
def ZoneTrans(ip,timedate):
 zone = gi.record_by_addr(ip)['time_zone']
 tz = pytz.timezone(zone)
 utc = pytz.timezone('Asia/Shanghai')
 dateobj = datetime.strptime(timedate, "%Y-%m-%d %H:%M:%S")
 print dateobj.replace(tzinfo=tz).astimezone(utc)
 print dateobj.replace(tzinfo=tz).astimezone(utc).strptime('%Y-%m-%d %H:%M:%S'))

ZoneTrans("50.186.14.252", "2016-10-31 04:59:35")
```



## 数据类型
```
bisect
bisect 使用二分法在一个 "已排序 (sorted) 序列" 中查找合适的插入位置。

>>> import bisect

>>> b = [ 20, 34, 35, 65, 78 ]

>>> bisect.bisect(b, 25)  # 查找 25 在列表中的合适插入位置。
1

>>> bisect.bisect(b, 40)  # 查找 40 在列表中的合适插入位置。
3

>>> bisect.bisect_left(b, 35)  # 如果待查找元素在列表中存在，则返回左侧插入位置。
2

>>> bisect.bisect_right(b, 35)  # 如果待查找元素在列表中存在，则返回右侧插入位置。
3
还可以直接用 insort_left() 直接插入元素而非查找。

>>> bisect.insort_left(b, 25)

>>> b
[20, 25, 34, 35, 65, 78]

>>> bisect.insort_left(b, 40)

>>> b
[20, 25, 34, 35, 40, 65, 78]
用 bisect 实现一个 SortedList 非常简单。

>>> def SortedList(list, *elements):
...  for e in elements:
...   bisect.insort_right(list, e)
...
...  return list

>>> SortedList([], 3, 7, 4, 1)
[1, 3, 4, 7]

>>> o = SortedList([], 3, 7, 4, 1)

>>> o
[1, 3, 4, 7]

>>> SortedList(o, 8, 2, 6, 0)
[0, 1, 2, 3, 4, 6, 7, 8]
可以考虑用 bisect 来实现 Consistent Hashing 算法，只要找到 Key 在 Ring 上的插入位置，
其下一个有效元素就是我们的目标服务器配置。

heapq
最小堆: 完全平衡二叉树，所有节点都小于其子节点。

堆的意义：最快找到最大/最小值。在堆结构中插入或删除最小(最大)元素时进行重新构造时间复杂度为 O
(logN)，而其他方法最少为O(N)。
堆在实际开发中的更倾向于算法调度而非排序。比如优先级调度时，每次取优先级最高的；时间驱动调度
时，取时间最小或等待最长的等等。

>>> from heapq import *
>>> from random import *

>>> rand = sample(xrange(1000), 10) # 生成随机数序列。
>>> rand
[572, 758, 737, 738, 412, 755, 507, 734, 479, 374]

>>> heap = []
>>> for x in rand: heappush(heap, x) # 将随机数压入堆。
>>> heap  # 堆是树，并非排序列表。
[374, 412, 507, 572, 479, 755, 737, 758, 734, 738]

>>> while heap: print heappop(heap) # 总是弹出最小元素。
374
412
479
507
572
734
737
738
755
758
其他相关函数。

>>> d = sample(xrange(10), 10)
>>> d
[9, 7, 3, 4, 0, 2, 5, 1, 8, 6]

>>> heapify(d) # 将列表转换为堆。
>>> d
[0, 1, 2, 4, 6, 3, 5, 9, 8, 7]

>>> heappushpop(d, -1) # 先 push(item)，后 pop。弹出值肯定小于或等于 item。
-1

>>> heapreplace(d, -1) # 先 pop，后 push(item)。弹出值可能大于 item。
0

... ...

>>> a = range(1, 10, 2)
>>> b = range(2, 10, 2)
>>> [x for x in merge(a, b)]   # 合并有序序列。
[1, 2, 3, 4, 5, 6, 7, 8, 9]

... ...

>>> d = sample(range(10), 10)
>>> d
[9, 0, 3, 4, 5, 6, 1, 2, 8, 7]

>>> nlargest(5, list) # 从列表(不一定是堆)有序返回最大的 n 个元素。
[9, 8, 7, 6, 5]

>>> nsmallest(5, list) # 有序返回最小的 n 个元素。
[0, 1, 2, 3, 4]
利用元组 cmp，用数字表示对象优先级，实现优先级队列。

>>> from string import *

>>> data = map(None, sample(xrange(100), 10), sample(letters, 10))
>>> data
[(31, 'Z'),
(71, 'S'),
(94, 'r'),
(65, 's'),
(98, 'B'),
(10, 'U'),
(8, 'u'),
(25, 'p'),
(11, 'v'),
(29, 'i')]

>>> for item in data: heappush(heap, item)
>>> heap
[(8, 'u'),
(11, 'v'),
(10, 'U'),
(25, 'p'),
(29, 'i'),
(94, 'r'),
(31, 'Z'),
(71, 'S'),
(65, 's'),
(98, 'B')]

>>> while heap: print heappop(heap)
(8, 'u')
(10, 'U')
(11, 'v')
(25, 'p')
(29, 'i')
(31, 'Z')
(65, 's')
(71, 'S')
(94, 'r')
(98, 'B')
```



## re正则
```
正则表达式
 正则表达式有强大并且标准化的方法来处理字符串查找、替换以及用复杂模式来解析文本。
 正则表达式的语法比程序代码更紧凑，格式更严格，比用组合调用字符串处理函数的方法更具有可读性。
 还可以在正则表达式中嵌入注释信息，这样就可以使它有自文档化的功能。


匹配符：
 ^    匹配字符串开始位置。在多行字符串模式匹配每一行的开头。
 $    匹配字符串结束位置。在多行字符串模式匹配每一行的结尾。
 .    匹配除了换行符外的任何字符，在 alternate 模式(re.DOTALL)下它甚至可以匹配换行。
 A   匹配字符串开头
 Z   匹配字符串结尾
 b   匹配一个单词边界。即 w 与 W 之间。
 B   匹配一个非单词边界；相当于类 [^b]。
 d   匹配一个数字。
 D   匹配一个任意的非数字字符。
 s   匹配任何空白字符；它相当于类  [ tnrfv]。
 S   匹配任何非空白字符；它相当于类 [^ tnrfv]。
 w   匹配任何字母数字字符；它相当于类 [a-zA-Z0-9_]。
 W   匹配任何非字母数字字符；它相当于类 [^a-zA-Z0-9_]。
 x?   匹配可选的x字符。即是0个或者1个x字符。
 x*   匹配0个或更多的x。
 x+   匹配1个或者更多x。
 x{n,m}  匹配n到m个x，至少n个，不能超过m个。
 (a|b|c) 匹配单独的任意一个a或者b或者c。
 (x)  捕获组，小括号括起来即可，它会记忆它匹配到的字符串。
   可以用 re.search() 返回的匹配对象的 groups()函数来获取到匹配的值。
 1   记忆组，它表示记住的第一个分组；如果有超过一个的记忆分组，可以使用 2 和 3 等等。
   记忆组的内容也要小括号括起来。
 (?iLmsux)    iLmsux的每个字符代表一种匹配模式
  re.I(re.IGNORECASE): 忽略大小写
  re.M(re.MULTILINE): 多行模式
  re.S(re.DOTALL):  单行
  re.L(re.LOCALE): 使预定字符类 w W b B s S 匹配本地字符，对中文支持不好
  re.U(re.UNICODE): 使预定字符类 w W b B s S d D 取决于unicode定义的字符属性
  re.X(re.VERBOSE): 忽略多余的空白字符，并可以加入注释。
 (?:表达式)   无捕获组。与捕获组表现一样，只是没有内容。
 (?P<name>表达式)   命名组。与记忆组一样，只是多了个名称。
 (?P=name)    命名组的逆向引用。
 (?#...)   “#”后面的将会作为注释而忽略掉。例如：“ab(?#comment)cd”匹配“abcd”
 (?=...)   之后的字符串需要匹配表达式才能成功匹配。不消耗字符串内容。 
 例：“a(?=d)”匹配“a12”中的“a”
 (?!...)   之后的字符串需要不匹配表达式才能成功匹配。不消耗字符串内容。 
 例：“a(?!d)”匹配“abc”中的“a”
 (?<=...)     之前的字符串需要匹配表达式才能成功匹配。不消耗字符串内容。
  例：“(?<=d)a”匹配“2a”中的“a”
 (?<!...)     之前的字符串需要不匹配表达式才能成功匹配。不消耗字符串内容。 
 例：“(?<!d)a”匹配“sa”中的“a”
 注：上面4个表达式的里面匹配的内容只能是一个字符，多个则报错。
 (?(id/name)yes-pattern|no-pattern)  如果编号为 id 或者别名为 name 的组匹配到字符串，则需要匹配yes-pattern，
 否则需要匹配no-pattern。 “|no-pattern”可以省略。如：“(d)ab(?(1)d|c)”匹配到“1ab2”和“abc”

匹配两边关键词 取中间的值
str2 = '<12345@itv.cn>'
print re.findall(r"(?<=<12).+(?=@itv.cn>)", str2)
结果： ['345']

元字符:
 "[" 和 "]"
  它们常用来匹配一个字符集。字符可以单个列出，也可以用“-”号分隔的两个给定字符来表示
  一个字符区间。
   例如，[abc] 将匹配"a", "b", 或 "c"中的任意一个字符；也可以用区间[a-c]来表示同一字符集，
   和前者效果一致。
  元字符在类别里并不起作用。例如，[a$]将匹配字符"a" 或 "$" 中的任意一个；"$" 在这里恢复成
  普通字符。
  也可以用补集来匹配不在区间范围内的字符。其做法是把"^"作为类别的首个字符；其它地方的"^"只会
  简单匹配 "^"字符本身。
   例如，[^5] 将匹配除 "5" 之外的任意字符。
  特殊字符都可以包含在一个字符类中。如，[s,.]字符类将匹配任何空白字符或","或"."。
 反斜杠 ""。
  做为 Python 中的字符串字母，反斜杠后面可以加不同的字符以表示不同特殊意义。
  它也可以用于取消所有的元字符，这样你就可以在模式中匹配它们了。
   例如，需要匹配字符 "[" 或 ""，可以在它们之前用反斜杠来取消它们的特殊意义： [ 或 。

建议使用原始字符串:
 建议在处理正则表达式的时候总是使用原始字符串。如： r'bROAD$', 而不要写成 'bROAD$'
 否则，会因为理解正则表达式而消耗大量时间(正则表达式本身就已经够让人困惑的了)。

无捕获组:
 有时你想用一个组去收集正则表达式的一部分，但又对组的内容不感兴趣。你可以用一个无捕获组“(?
 :...)”来实现这项功能。
 除了捕获匹配组的内容之外，无捕获组与捕获组表现完全一样；可以在其中放置任何字符、匹配符，可以
 在其他组(无捕获组与捕获组)中嵌套它。
 无捕获组对于修改已有组尤其有用，因为可以不用改变所有其他组号的情况下添加一个新组。
 捕获组和无捕获组在搜索效率方面也一样。

命名组:
 与用数字指定组不同的是，它可以用名字来指定。除了该组有个名字之外，命名组也同捕获组是相同的。
 (?P<name>...) 定义一个命名组，(?P=name) 则是对命名组的逆向引用。
 MatchObject 的方法处理捕获组时接受的要么是表示组号的整数，要么是包含组名的字符串。所以命名组
 可以通过数字或者名称两
 种方式来得到一个组的信息。

松散正则表达式:
 为了方便阅读和维护，可以使用松散正则表达式，它与普通紧凑的正则表达式有两点不同：
 1, 空白符被忽略。空格、制表符(tab)和回车会被忽略。如果需要匹配他们，可以在前面加一个“”来转义。
 2, 注释被忽略。注释以“#”开头直到行尾，与python代码中的一样。
 使用松散正则表达式，需要传递一个叫 re.VERBOSE的 参数。详细见下面例子。

re 有几个重要的函数：

match(): 匹配字符串开始位置。
search(): 扫描字符串，找到第一个位置。
findall(): 找到全部匹配，以列表返回。
finditer(): 找到全部匹配，以迭代器返回。
match 和 search 仅匹配一次，匹配不到返回 None。

>>> import re

>>> s = "12abc345ab"

>>> m = re.match(r"d+", s)
>>> m.group(), m.span()
('12', (0, 2))

>>> m = re.match(r"d{3,}", s)
>>> m is None
True

>>> m = re.search(r"d{3,}", s)
>>> m.group(), m.span()
('345', (5, 8))

>>> m = re.search(r"d+", s)
>>> m.group(), m.span()
('12', (0, 2))
findall 返回列表 (或空列表)，finditer 和 match、search 一样返回 MatchObject 对象。

>>> ms = re.findall(r"d+", s)
>>> ms
['12', '345']

>>> ms = re.findall(r"d{5}", s)
>>> ms
[]

>>> for m in re.finditer(r"d+", s): print m.group(), m.span()
...
12 (0, 2)
345 (5, 8)

>>> for m in re.finditer(r"d{5}", s): print m.group(), m.span() # 返回空列表
...
>>>
MatchObject

match、search、finditer 返回的对象 —— MatchObject。

group(): 返回匹配的完整字符串。
start(): 匹配的开始位置。
end(): 匹配的结束位置。
span(): 包含起始、结束位置的元组。
groups(): 返回分组信息。
groupdict(): 返回命名分组信息。
>>> m = re.match(r"(d+)(P<letter>[abc]+)", s)

>>> m.group()
'12abc'

>>> m.start()
0

>>> m.end()
5

>>> m.span()
(0, 5)

>>> m.groups()
('12', 'abc')

>>> m.groupdict()
{'letter': 'abc'}
group() 可以接收多个参数，用于返回指定序号的分组。

>>> m.group(0)
'12abc'

>>> m.group(1)
'12'

>>> m.group(2)
'abc'

>>> m.group(1,2)
('12', 'abc')

>>> m.group(0,1,2)
('12abc', '12', 'abc')
start()、end() 和 span() 同样能接收分组序号。和 group() 一样，序号 0 表示整体匹配结果。

>>> m.start(0), m.end(0)
(0, 5)

>>> m.start(1), m.end(1)
(0, 2)

>>> m.start(2), m.end(2)
(2, 5)

>>> m.span(0)
(0, 5)

>>> m.span(1)
(0, 2)

>>> m.span(2)
(2, 5)
编译标志

可以用 re.I、re.M 等参数，也可以直接在表达式中添加 "(iLmsux)" 标志。

s: 单行。"." 匹配包括换行符在内的所有字符。
i: 忽略大小写。
L: 让 "w" 能匹配当地字符，貌似对中文支持不好。
m: 多行。
x: 忽略多余的空白字符，让表达式更易阅读。
u: Unicode。
试试看。

>>> re.findall(r"[a-z]+", "%123Abc%45xyz&")
['bc', 'xyz']

>>> re.findall(r"[a-z]+", "%123Abc%45xyz&", re.I)
['Abc', 'xyz']

>>> re.findall(r"(i)[a-z]+", "%123Abc%45xyz&")
['Abc', 'xyz']
下面这么写好看多了吧？

>>> pattern = r"""
...  (d+) # number
...  ([a-z]+) # letter
... """

>>> re.findall(pattern, "%123Abcn%45xyz&", re.I | re.S | re.X)
[('123', 'Abc'), ('45', 'xyz')]
组操作

命名组：(P...)

>>> for m in re.finditer(r"(P<number>d+)(P<letter>[a-z]+)", "%123Abc%45xyz&", re.I):
...  print m.groupdict()
...
{'number': '123', 'letter': 'Abc'}
{'number': '45', 'letter': 'xyz'}
无捕获组：(:...)，作为匹配条件，但不返回。

>>> for m in re.finditer(r"(:d+)([a-z]+)", "%123Abc%45xyz&", re.I):
...  print m.groups()
...
('Abc',)
('xyz',)
反向引用： 或 (P=name)，引用前面的组。

>>> for m in re.finditer(r"<a>w+</a>", "%<a>123Abc</a>%<b>45xyz</b>&"):
...  print m.group()
...
<a>123Abc</a>

>>> for m in re.finditer(r"<(w)>w+</(1)>", "%<a>123Abc</a>%<b>45xyz</b>&"):
...  print m.group()
...
<a>123Abc</a>
<b>45xyz</b>

>>> for m in re.finditer(r"<(P<tag>w)>w+</(P=tag)>", "%<a>123Abc</a>%<b>45xyz</
b>&"):
...  print m.group()
...
<a>123Abc</a>
<b>45xyz</b>
正声明 (=...)：组内容必须出现在右侧，不返回。 负声明 (...)：组内容不能出现在右侧，不返回。 反向正声明 (<=)：
组内容必须出现在左侧，不返回。 反向负声明 (<)：组内容不能出现在左侧，不返回。

>>> for m in re.finditer(r"d+(=[ab])", "%123Abc%45xyz%780b&", re.I):
...  print m.group()
...
123
780

>>> for m in re.finditer(r"(<d)[a-z]{3,}", "%123Abc%45xyz%byse&", re.I):
... print m.group()
...
byse
更多信息请阅读官方文档或更专业的书籍。

修改

split: 用 pattern 做分隔符切割字符串。如果用 "(pattern)"，那么分隔符也会返回。

>>> re.split(r"W", "abc,123,x")
['abc', '123', 'x']

>>> re.split(r"(W)", "abc,123,x")
['abc', ',', '123', ',', 'x']
sub: 替换子串。可指定替换次数。

>>> re.sub(r"[a-z]+", "*", "abc,123,x")
'*,123,*'

>>> re.sub(r"[a-z]+", "*", "abc,123,x", 1)
'*,123,x'
subn() 和 sub() 差不多，不过返回 "(新字符串，替换次数)"。

>>> re.subn(r"[a-z]+", "*", "abc,123,x")
('*,123,*', 2)
还可以将替换字符串改成函数，以便替换成不同的结果。

>>> def repl(m):
...  print m.group()
...  return "*" * len(m.group())
...

>>> re.subn(r"[a-z]+", repl, "abc,123,x")
abc
x
('***,123,*', 2)
StringIO
提供类文件接口的字符串缓冲区，可选用性能更好的 cStringIO 版本。

>>> from contextlib import closing
>>> from cStringIO import StringIO

>>> with closing(StringIO("ab")) as f:
...  print >> f, "cd"
...  f.write("1234")
...  print f.getvalue()
abcd
1234
建议用 with 上下文确保调用 close() 方法释放所占用内存。用 getvalue() 返回字符串前，必须确保是打开状态 (closed = False)。

struct
struct 看上去有点像 format，区别是它输出的是二进制字节序列。可以通过格式化参数，指定类型、长度、字节序(大小端)、内存对齐等。

>>> from struct import *

>>> hexstr = lambda s: map(lambda c: hex(ord(c)), s)

>>> s = pack("i", 0x1234)

>>> hexstr(s)   # 4 字节整数小端排列
['0x34', '0x12', '0x0', '0x0']

>>> unpack("i", s)   # 还原。4660 = 0x1234
(4660,)

>>> s = pack(">i", 0x1234) # 大端

>>> hexstr(s)
['0x0', '0x0', '0x12', '0x34']

>>> s = pack("2i2s", 0x12, 0x34, "ab")   # 多值。注意指定字符串长度。

>>> hexstr(s)
['0x12', '0x0', '0x0', '0x0', '0x34', '0x0', '0x0', '0x0', '0x61', '0x62']

>>> unpack("2i2s", s)
(18, 52, 'ab')
还可以将结果输出到 bytearray、array、ctypes.create_str_buffer() 等缓冲对象中。

>>> fmt = "3bi2s"
>>> size = calcsize(fmt)   # 计算指定格式转换所需的字节长度。

>>> buffer = bytearray(size)

>>> pack_into(fmt, buffer, 0, 0x1, 0x2, 0x3, 0x1FFFFF, "ab")

>>> buffer
bytearray(b'x01x02x03x00xffxffx1fx00ab')

>>> unpack_from(fmt, str(buffer), 0)
(1, 2, 3, 2097151, 'ab')
```



## 进制转换
```
#!/usr/bin/env python
import os,sys
# global definition
# base = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, F]
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
# bin2dec
# 二进制 to 十进制: int(str,n=10) 
def bin2dec(string_num):
 return str(int(string_num, 2))
# hex2dec
# 十六进制 to 十进制
def hex2dec(string_num):
 return str(int(string_num.upper(), 16))
# dec2bin
# 十进制 to 二进制: bin() 
def dec2bin(string_num):
 num = int(string_num)
 mid = []
 while True:
  if num == 0: break
  num,rem = divmod(num, 2)
  mid.append(base[rem])
 return ''.join([str(x) for x in mid[::-1]])
# dec2hex
# 十进制 to 八进制: oct() 
# 十进制 to 十六进制: hex() 
def dec2hex(string_num):
 num = int(string_num)
 mid = []
 while True:
  if num == 0: break
  num,rem = divmod(num, 16)
  mid.append(base[rem])
 return ''.join([str(x) for x in mid[::-1]])
# hex2tobin
# 十六进制 to 二进制: bin(int(str,16)) 
def hex2bin(string_num):
 return dec2bin(hex2dec(string_num.upper()))
# bin2hex
# 二进制 to 十六进制: hex(int(str,2)) 
def bin2hex(string_num):
 return dec2hex(bin2dec(string_num))

```



## lambda reduce map filter zip
```
匿名函数lambda
lambda语句中，冒号前是参数，可以有多个，用逗号隔开，冒号右边是返回值。
def f(x,y):
 return x+y
print f(2,3)
# 5
g = lambda x,y:x+y
print g(2,3)
# 5

reduce 逐次操作列表的每一项，接受的参数为两个，最后返回一个结果 
def add(x,y):
 return x+y
print reduce(add,xrange(1,10))
# 45
print reduce(lambda x,y:x+y,xrange(1,10))
# 45

map函数
map函数会根据提供的函数对指定序列做映射。
print map(lambda x: x ** 2, xrange(1,6)) 对一个序列中的每个元素进行平方运算
# [1, 4, 9, 16, 25]
print map(lambda x, y: x + y, [1, 3, 5, 7, 9], [2, 4, 6, 8, 10])
# [3, 7, 11, 15, 19]
print map(None,[1, 3, 5, 7, 9], [2, 4, 6, 8, 10])   当函数为None时，操作和zip相似
# [(1, 2), (3, 4), (5, 6), (7, 8), (9, 10)]

filter函数
filter函数会对序列参数sequence中的每个元素调用function函数，最后返回的结果包含调用结果为True的元素。
def is_even(x):
 if x%2==0:
  return True
 return False
print filter(is_even,xrange(1,11))  #返回偶数
# [2, 4, 6, 8, 10]
print filter(lambda x:x%2,xrange(1,11))  #返回奇数
# [1, 3, 5, 7, 9]
如果function参数为None，返回结果和sequence参数相同。

zip函数
取出每一个数组的元素，然后组合
x = [1, 2, 3]
y = [4, 5, 6]
z = [7, 8, 9]
xyz = zip(x, y, z)
print xyz
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
print zip(*xyz)   # 解zip函数
# [(1, 2, 3), (4, 5, 6), (7, 8, 9)]


```



## 多线程
```
多线程
Python里，多个cpu考虑使用多线程，io（磁盘，网络通讯）多线程

线程执行是无序的，线程是不安全的，共同操作数据时没有检查机制，所有要加锁
默认情况下主线程结束子线程不结束，除非设置setDaemon(True)

import threading
def worker(a_tid,a_account):
  print a_tid,a_account

for i in range(20):  
 th = threading.Thread(name='name',target=worker,args=(‘key’,), kwargs={'a_tid':'a', 'a_account':2} ) 
产生一个线程对象
#参数name线程名字，可以不写,参数 target 是要执行的函数, args 里面的是参数列表(一个参数需要加个逗号，代表是，列表),
kwargs是字典式的参数列表
 th.start()  启动这个线程

# 多线程+队列版本： 
   
import socket 
import threading 
from Queue import Queue 
def scan(port): 
  s = socket.socket() 
  s.settimeout(0.1) 
  if s.connect_ex(('localhost', port)) == 0: 
 print port, 'open' 
  s.close() 
 
def worker(): 
  while not q.empty(): 
 port = q.get()  获取数据队列分配的值 
 try: 
   scan(port) 
 finally: 
   q.task_done() 
 
if __name__ == '__main__': 
  q = Queue() 
  map(q.put,xrange(1,65535))  数据放入队列
  threads = [threading.Thread(target=worker) for i in xrange(500)]  定义500个线程
  map(lambda x:x.start(),threads)   启动线程
  # q.join() 开启会慢
 
 

threading.Thread类的使用：
 1，在自己的线程类的 __init__ 里调用 threading.Thread.__init__(self, name = threadname) # threadname 为线程的名字
 2， run()，通常需要重写，编写代码实现做需要的功能。
 3，getName()，获得线程对象名称
 4，setName()，设置线程对象名称
 5，start()，启动线程
 6，join(timeout=None)，等待另一线程结束后再运行。如果给出timeout，则最多阻塞timeout秒
 7，setDaemon(bool)，设置子线程是否随主线程一起结束，必须在start()之前调用。默认为 False
 8，isDaemon()，判断线程是否随主线程一起结束
 9，isAlive()，检查线程是否在运行中。
    此外threading模块本身也提供了很多方法和其他的类，可以帮助我们更好的使用和管理线程。
    可以参看https://docs.python.org/2/library/threading.html?highlight=threading#module-threading。

线程锁
import threading
lock = threading.Lock()  产生一个锁对象
share = [0,1]
num = 2
def AddNum():
 global num
 lock.acquire()  获得锁
 share.append(num)
 print 'share add:', num
 print 'now:', share
 num += 1
 lock.release()  释放锁 
Condition(锁上锁)
•对于消费者，在消费前检查队列是否为空。
•如果为空，调用condition实例的wait()方法。
•消费者进入wait()，同时释放所持有的lock（隐形释放，处于wait状态就会释放）。
•除非被notify，否则它不会运行。
• 生产者可以acquire这个lock，因为它已经被消费者release。
•当调用了condition的notify()方法后，消费者被唤醒，但唤醒不意味着它可以开始运行。
•notify()并不释放lock，调用notify()后，lock依然被生产者所持有。
•生产者通过condition.release()显式释放lock。
•消费者再次开始运行，同时申请锁，现在它可以得到队列中的数据而不会出现IndexError异常。

from threading import Condition, Thread
import time
import random


queue = []
condition = Condition()

class ConsumerThread(Thread):
 def run(self):
  global queue
  while True:
   condition.acquire()
   if not queue:
    print "Nothing in queue, consumer is waiting"
    condition.wait()  如果queue为空，进入wait,同时释放锁，唤醒时同时获得锁
    print "Producer added something to queue and notified the consumer"
   num = queue.pop(0)
   print "Consumed", num
   condition.release()
   time.sleep(random.random())

class ProducerThread(Thread):
 def run(self):
  nums = range(5)
  global queue
  while True:
   condition.acquire()  获得锁
   num = random.choice(nums)
   queue.append(num)
   print "Produced", num
   condition.notify()  唤醒wait
   condition.release()  释放锁
   time.sleep(random.random())

ProducerThread().start()
ConsumerThread().start()

队列（Queue）
队列是线程安全
•在原来使用list的位置，改为使用Queue实例（下称队列）。
•这个队列有一个condition，它有自己的lock。如果你使用Queue，你不需要为condition和lock而烦恼。
•生生产者调用队列的put方法来插入数据。
•put(—) 在插入数据前有一个获取lock的逻辑。
•同时，put()也会检查队列是否已满。如果已满，它会在内部调用wait()，生产者开始等待。
• 消费者使用get方法。
•get()从队列中移出数据前会获取lock。
•get()会检查队列是否为空，如果为空，消费者进入等待状态。
•get()和put()都有适当的notify()。现在就去看Queue的源码吧。
from threading import Thread
import time
import random
from Queue import Queue

queue = Queue(10)

class ProducerThread(Thread):
 def run(self):
  nums = range(5)
  global queue
  while True:
   num = random.choice(nums)
   queue.put(num)
   print "Produced", num
   time.sleep(random.random())

class ConsumerThread(Thread):
 def run(self):
  global queue
  while True:
   num = queue.get()
   #queue.task_done()
   print "Consumed", num
   time.sleep(random.random())

ProducerThread().start()
ConsumerThread().start()
```



## 异常处理
```
异常处理
出现异常也可以继续执行
try:
 s = input('Enter something --> ') # Python 2 的输入是 raw_input()
except EOFError as e:  捕获EOFError异常，e代表异常的详细信息
 print('nWhy did you do an EOF on me?')
except:    捕获所有异常
 print('nWhy did you do an Exception on me?')
else:   没有捕捉到异常时执行
 print('No exception was raised.')
finally:   # 不管是否有异常,最后都会执行
 print('finally .....')

常见异常(可避免的):
  使用不存在的字典关键字 将引发 KeyError 异常。
  搜索列表中不存在的值 将引发 ValueError 异常。
  调用不存在的方法 将引发 AttributeError 异常。
  引用不存在的变量 将引发 NameError 异常。
  未强制转换就混用数据类型 将引发 TypeError 异常。
  导入一个并不存在的模块将引发一个 ImportError 异常。
raise 语句
 可以使用 raise 语句引发异常(抛出异常)。你还得指明错误/异常的名称和伴随异常触发的异常对象。
 可以引发 Error 或 Exception 类的直接或间接导出类。
 
 在Python 3里，抛出自定义异常的语法有细微的变化。
  Python 2          Python 3
 ① raise MyException        MyException
 ② raise MyException, 'error message'      raise MyException('error message')
 ③ raise MyException, 'error message', a_traceback  raise MyException('error message').with_traceback(a_traceback)
 ④ raise 'error message'       unsupported(不支持)
 说明:
 ① 抛出不带自定义错误信息的异常，这种最简单的形式下，语法没有改变。
 ② 抛出带自定义错误信息的异常时:Python 2用一个逗号来分隔异常类和错误信息；Python 3把错误信息作为参数传递给异常类。
 ③ 抛出一个带用户自定义回溯(stack trace,堆栈追踪)的异常。在Python 2和3里这语法完全不同。
 ④ 在Python 2里，可以仅仅抛出一个异常信息。在Python 3里，这种形式不再被支持。2to3将会警告你它不能自动修复这种语法。
 
 例：
 raise RuntimeError("有异常发生")   #抛出异常后脚本退出执行
```



## 函数
```
函数
def func(参数):
   ““”func的描述“”“
   print(func)         #函数体
   return           #函数内执行到return代表结束，可有返回值，也可以没有返回值，是函数执行的结果
   print(‘func’)      #永远看不到这一行

”“”以上只是函数的定义“”“

func()         # 代表调用函数，返回函数的执行结果
func            #代表函数对象，是引用函数

在函数内return的返回值可以进行赋值操作


定义函数是在内存中开辟一块空间来存放代码，函数名指向这块内存空间，但是没有执行，加上()后执行该代码，
return的内容为函数的执行的结果，没有return，结果为None，函数执行结果和print没有关系，print 只代表打印。
def func(first,second):
return first+second

a1 = func(4,5)
print a1
a2 = func
print func
print a2
print a2(3,4) 
执行结果：
9
<function func at 0x7f38bca44c80>
<function func at 0x7f38bca44c80>
7





可变量参数
参数可以有多个，也可以没有

def func(arg1,*args,**kw):  #参数名称前加*，代表元组；加**代表字典
 print('arg1:%s' % arg1)
 print args
 print kw
func('A','B','C',D=1,E=2)

结果：
arg1:A
('B', 'C')
{'E': 2, 'D': 1}


def func(name,age=10):     #参数的默认值  
 pass 
匿名函数
Lambda是一个匿名函数，没有函数名，可以使代码更精简，但是具有局限性。


lambda语句中，冒号前是参数，可以有多个，用逗号隔开，冒号右边是返回值。

Reduce


Reduce为逐次操作列表的每一项，接受的参数为两个，最后返回一个结果。

闭包closures
函数套函数
import time
def hl(func):
 def wrap():
  begin = int(time.time())
  print begin
  func()
  end = int(time.time())
  print end
  print "cost:",end - begin
  return end - begin
 return wrap
def t():
 time.sleep(1)
hl(t)()
装饰器
函数执行前扩展一些函数、执行后扩展一些函数
import time
def hl(func):
 def wrap():
  begin = int(time.time())
  print begin
  func()
  end = int(time.time())
  print end
  print "cost:",end - begin
  return end - begin
 return wrap
@hl
def t():
 time.sleep(1)
t()

##############################
def mb(func):
def wrap():
return '<b>' + func() + '</b>'
return wrap
def mi(func):
def wrap():
return '<i>' + func() + '</i>'
return wrap
@mb
@mi
def hello():
return('hello')
print(hello())
```



## 字典
```
dict.clear() 删除字典中所有元素
a=dict(x=1,y=2)  参数无
a.clear()  返回值为 None

dict.get(key) 对字典 dict 中的键 key,返回它对应的值 value， 如果字典中不存在此键，
则返回 None
a=dict(x=1,y=2)
a.get(‘x’) 参数为字符、整数等，返回值为 values 或 None

dict.keys() 返回一个包含字典中键的列表
a=dict(x=1,y=2)  参数无
a.keys()  返回值为 key 组成的列表

dict.values() 返回一个包含字典中所有值的列表
a={‘x’:1,’y’:2}  参数无
a.values() 返回值为 value 组成的列表

dict.items() 返回一个包含字典中(键, 值)的列表
a={‘x’:1,’y’:2}  参数无
a.items() [('y', 2), ('x', 1)]  返回值为（key，value）组成的列表

dict.copy() 返回字典（浅复制）的一个副本 
a={‘x’:1,’y’:2}  参数无
b=a.copy() 返回值为字典

dict.has_key(key) 测试 dict 中是否有 key
a.has_key(‘x’) 参数为字符、整数等（可以为 key，也可以不是）
return boole  返回值为布尔值（True or False）

dict.iteritems() 返回（key,value）的迭代器，由于 for 循环
a = {'a':1,'b':2}
for k,v in a.iteritems(): for 循环调用
... print k,v
...
a 1
b 2
s= a.iteritems()
>>> s.next() next 方法调用
('a', 1)
>>> s.next()
('b', 2)

dict.iterkeys() 返回 key 的迭代器
dict.itervalues() 返回 value 的迭代器

dict.pop(key[,default]) 如果字典中 key 键存在，删除并返回 dict[key]，如果 key 键不存在，
且没有给出 default 的值，引发 KeyError 异常
a={‘x’:1,’y’:2,’z’:3} 
a.pop(‘x’) 1  参数为 key
a.pop(‘abc’,’sky’) sky 返回值为 value

dict.popitem() 删除第一个键值对
a={‘x’:1,’y’:2,’z’:3}
a.popitem() 参数无
(‘x’,1)  返回值为删除的（key，value）

dict.setdefault(key, default=None) 如果字典中不存在 key 键，由 dict[key]=default 为它赋值。
a={‘x’:1}
a.setdefalut(‘y’)  参数为 key
a.setdefault(‘z’,3)  返回值为 value 或 None
{'x': 1, 'y': None, 'z': 3}

dict.update(dict2) 将字典 dict2 的键-值对添加到字典 dict
a = {'a':1}  b = {'b':2}
a.update(b) 参数为字典
>>> a  返回值为 None
{'a': 1, 'b': 2}

dict.fromkeys(seq, val=None) 创建并返回一个新字典， 以 seq 中的元素做该字典的键， val 做
该字典中所有键对应的初始值(如果不提供此值，则默认为 None)
a.fromkeys(‘d’,3)  参数为 key 和 value（可以可无），并不修改原字典
{'d': 3}  返回一个字典
a={'a': 1, 'b': 2}
>>> a.viewitems()
dict_items([('a', 1), ('b', 2)])
>>> a.viewkeys()
dict_keys(['a', 'b'])
>>> a.viewvalues()
dict_values([1, 2])

排序
sorted(dic1.iteritems(),key=lambda key:key[0],reverse=True)  按照key排序，reverse=True反转，从大到小
sorted(dic1.iteritems(),key=lambda key:key[1],reverse=True)  按照value排序
```



## 类与对象
```
类与对象class（oop）
web flask
运维 salt zabbix cobbler
大数据 hadoop
 
类的属性  类里面的变量，实例化后可以修改
类的方法  类里面的函数
 
类的构造器，解构器
   def __init__(self):
       在实例初始化是隐藏调用
   def __del__(self):
       在实例消亡时隐藏调用实例化  f1 = Friut('app',33)
self表示实例化的名字
 
基类  包含   子类 包含   对象
类和函数都是可调用的
实现一个计数器，统计多少的实例
class Friut(object):            定义类
count = 0                   类的一个属性
def __init__(self,name,weight):       初始类的实例的属性
self.name = name
self.weight = weight
Friut.count += 1
def info(self):                 类包含的一个的对象或方法
print self.name,self.weight,Friut.count
 
类的方法
   @staticmethod
   def func_name()
       他的调用只能通过类名.func_name()
   @classmethod
   def func_name(self)
       调用方式类名.func_name() 或者 实例名.func_name()
 
通过dir(类名)查看
__doc__定义类时的描述
__name__类的名字
__module__ 模块的名称  __main__
__base__类的基类
__dict__所有类的方法和属性
 
类的继承、封装
class Parent(object):  # define parent class
def myMethod(self):
print 'Calling parent method'
def setAttr(self, attr):
Parent.parentAttr = attr
 
class Child(Parent): # define child class  继承Parent
def myMethod (self):
print 'Calling child method'      覆盖父类的myMethod方法
 
隐藏类的方法
class JustCounter(object):
__secretCount = 0
def count(self):
self.__secretCount += 1
print self.__secretCount
counter = JustCounter()
counter.count()
print counter.__secretCount
实例化后无法直接调用，只能由class调用
 
super
class A(object):   
def __init__(self):
print "enter A"
class B(A):  #
def __init__(self):
print "enter B"
super(B, self).__init__()
print "leave B"
 
变量范围
B 内建build in：没有定义过，拿来就能用的
G 全局 global
E 闭包
L 本地变量 local


 
模块
import 模块或者py文件
在以下位置寻找
import sys
print sys.path
```



## 迭代器
```
迭代器
节省内存空间
1.for-in 语句在底层都是对一个 Iterator(迭代器) 对象进行操作的
2.使用了 yield 关键字的函数就是一个 Generator(生成器) 函数，被调用的时候生成一个可以控制自己运行的迭代器
3.调用使用了 yield 关键字的函数,最好用 for-in 语句
迭代器是一个对象，它实现了迭代器协议，一般需要实现如下两个方法
1. next 方法(返回容器的下一个元素)  2. __iter__ 方法（返回迭代器自身）
type(iter(range(10)))
Out[5]: listiterator
 
对一个对象调用 iter() 就可以得到它的迭代器。它的语法如下:
iter(obj)
如果传递一个参数给 iter() ，它会检查你传递的是不是一个序列，如果是，那么很简单:
根据索引从 0 一直迭代到序列结束。另一个创建迭代器的方法是使用类，一个实现了 __iter__() 和 next() 方法的类可以作为迭代器使用.
iter(func，sentinel)
如果是传递两个参数给 iter() ，它会重复地调用 func ，直到迭代器的下个值等于sentinel。
it = iter([1, 2, 3, 4, 5])
while True:
 try:
  x = next(it) 获得下一个值
 except StopIteration: 遇到StopIteration就退出循环（已经没有数据了）
  break
```



## 字符串
```
空格，特殊的符号 处理
str.rstrip() 删除 str 字符串末尾的空格
str.lstrip() 删除 str 字符串开始的空格
str.strip()  在 str 上执行 lstrip()和 rstrip()
参数均为无，返回值均为修改后的字符串，原字符串无变化

str.center(width)  返回一个原字符串居中,并使用空格填充至长度 width 的新字符串
str.ljust(width) 返回一个原字符串左对齐,并使用空格填充至长度 width 的新字符串
str.rjust(width) 返回一个原字符串右对齐,并使用空格填充至长度 width 的新字符串
string.zfill(width)  返回长度为 width 的字符串，原字符串 string 右对齐，前面填充 0
str.expandtabs(tabsize=8)  把字符串 str 中的 tab 符号转为空格，默认的空格数是 8
参数为整数  返回值为修改后的字符串
a=‘t123abc23t’
a.strip() ‘123abc123’
a.srtip(‘123’) ‘t123abc23t’
a.rstrip() ‘t123abc23’
a.lsrtip(‘123’) ‘t123abc23t’
s.expandtabs(4)  ' 123abc23 '
s='hello'
s.center(20)  ' hello
'

字符串的大小写转换
string.title()  返回"标题化"的 string,就是说所有单词都是以大写开始， 其余字母均为小写
str.lower() 转换 string 中所有大写字符为小写
str.upper() 转换 string 中所有小写字符为大写
str.swapcase()  翻转 string 中的大小写
str.capitalize()  把字符串的第一个字符大写
参数均为无，返回值均为修改后的字符串，原字符串无变化

字符串的判断
参数均为无，返回值均为布尔值
str.isalnum() 
如果 str 至少有一个字符并且所有字符都是字母或数字则返回 True,否则返回 False
str.isalpha()
如果 str 至少有一个字符并且所有字符都是字母则返回 True,否则返回 False
str.isdigit()
如果 str 只包含数字则返回 True 否则返回 False
str.isdecimal()
如果 string 只包含十进制数字则返回 True 否则返回 False
str.isspace()
如果 str 中只包含空格，则返回 True，否则返回 False
str.istitle()
如果 str 是标题化的(见 title())则返回 True，否则返回 False
str.isupper()  如果 str 中包含至少一个区分大小写的字符，并且所有这些(区分大小写的)字符
都是大写，则返回 True，否则返回 False
str.islower()  如果 str 中包含至少一个区分大小写的字符，并且所有这些(区分大小写的)字符
都是小写，则返回 True，否则返回 False
#################################################
参数为字符串或元组，返回值为布尔值（True or False）
str.startswith(obj, beg=0,end=len(string))  检查字符串是否是以 obj 开头，是则返回 True，否则返回
False。如果 beg 和 end 指定值，则在指定范围内检查
str.endswith(obj, beg=0,end=len(string))  检查字符串是否以 obj 结束，如果 beg 或者 end 指定则
检查指定的范围内是否以 obj 结束，如果是，返回 True,否则返回 False
字符串的分割，组合，查找，替换
str.join(sqp) 以 string 作为分隔符，将 seq 中所有的元素(字符串表示)合并为一个
新的字符串
l=['I', 'am', 'tom']  参数为元组、列表、字典，且内容为字符串
'--'.join(l) 'I--am--tom'  返回值为元组、列表、字典的 key 和 str 的合并的新字符串
str.split(str="", num=string.count(str))
以 str 为分隔符切片 string，如果 num 有指定值，则仅分隔 num 个子字符串
astr=‘I | am | tom!’  参数为分隔符和分割次数（可有可无）
astr.split(‘|’) ['I ', ' am ', ' tom!']  返回值为分割后的列表
string.find(str, beg=0, end=len(string)) 检测 str 是否包含在 string 中， 如果 beg 和 end 指定范围，
则检查是否包含在指定范围内，如果是返回开始的索引值，否则返回-1
string.index(str, beg=0, end=len(string)) 
跟 find()方法一样，只不过如果 str 不在 string 中会报一个 ValueError 异常.
string.rfind(str, beg=0,end=len(string) )  类似于 find()函数，不过是从右边开始查找.
string.rindex( str, beg=0,end=len(string))  类似于 index()，不过是从右边开始
a=‘i am a student’  参数为字符串和开始结束的索引（可以可无）
a.find(‘am’) 2  返回值为开始的索引值或-1
str.replace(str1, str2, num=string.count(str1))
把 str 中的 str1 替换成 str2,如果 num 指定，则替换不超过 num 次
a=‘du,hello,du bye’  参数为原字符串和新字符串，替换次数（可以可无）
a.replace(‘du’,’minchao’,1) 'minchao,hello,du bye'  返回值为替换后的字符串，原来的不变
string.count(str, beg=0, end=len(string)) 返回 str 在 string 里面出现的次数，如果 beg 或者
end 指定则返回指定范围内 str 出现的次数
a=‘du,hello,du bye’  参数为字符串和开始结束的索引（可有可无）
a.count(‘du’,3) return 1 返回值为 str 出现的次数
string.partition(str)
有点像 find()和 split()的结合体,从 str 出现的第一个位置起,把 字 符 串 string 分 成 一 个 3 元 素
的 元 组 (string_pre_str,str,string_post_str),如果 string 中不包含 str 则 string_pre_str == string.
s='a b c d e'  参数为字符串，返回值为分割后组成的元组
s.partition('c') >> ('a b ', 'c', ' d e')
s.partition('f') >> ('a b c d e', '', '')
string.rpartition(str)  类似于 partition()函数,不过是从右边开始查找.
string.splitlines(num=string.count('n'))
按照行分隔，返回一个包含各行作为元素的列表，如果 num 指定则仅切片 num 个行.
s = '''332 参数为整数，返回值为字符各行组成的列表
2432
4343'''
s.splitlines()  ['332', '2432', '4343']

字符串 编码
string.decode(encoding='UTF-8', errors='strict')
以 encoding 指定的编码格式解码 string，如果出错默认报一个 ValueError 的 异 常 ， 除 非 errors
指 定 的 是 'ignore' 或 者'replace'
s = '你好'
>>> s
'xc4xe3xbaxc3'
s.decode(encoding='GBK')
u'u4f60u597d'
string.encode(encoding='UTF-8', errors='strict')
以 encoding 指定的编码格式编码 string，如果出错默认报一个 ValueError 的异常，除非 errors 指定
的是'ignore'或者'replace'
```



## 元组
```
tuple.index(obj,i=0,j=len(list)) 返回 tuple[k]==obj 的 k 值,并且 k 的范围在[i,j)
a=(1,2,3,4,5,6,2)  参数为 tuple 中的值和开始结束的索引（可以可无）
a.index(2) 返回值为 obj 在 tuple 的索引值

tuple.count(obj) 返回一个对象 obj 在 tuple 中出现的次数
a=(1,2,3,3,3,4)  参数为字符串、整数、浮点数等
a.count(1) 返回值为参数在 tuple 的出现次数
```



## eval
```

功能：将字符串str当成有效的表达式来求值并返回计算结果。

语法： eval(source[, globals[, locals]])

参数：

source：一个Python表达式或函数compile()返回的代码对象

globals：可选。必须是dictionary

locals：可选。任意map对象

可以把list,tuple,dict和string相互转化。 
eval可以执行命令，如果只是格式转换， ast模块的 ast.literal_eval() 更加安全

字符串转换成列表

a = "[[1,2], [3,4], [5,6], [7,8], [9,0]]"

type(a)

type 'str'

b = eval(a)

print b

[[1, 2], [3, 4], [5, 6], [7, 8], [9, 0]]

type(b)

type 'list'

字符串转换成字典

a = "{1: 'a', 2: 'b'}"

type(a)

type 'str'

b = eval(a)

print b

{1: 'a', 2: 'b'}

type(b)

type 'dict'

```