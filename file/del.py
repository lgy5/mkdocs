# del unicode
import re
import sys
reload(sys)
sys.setdefaultencoding("utf8")
with open('site/search/search_index.json','r') as f:
    new = re.sub(u"[\u4e00-\u9fa5]+","",f.read().decode("utf8"))
with open('site/search/search_index.json','w') as f:
    f.write(new)