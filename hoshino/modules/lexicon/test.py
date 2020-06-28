import re
import sqlite3
from nonebot import aiocqhttp


if __name__ == "__main__":
    reg = re.compile(r'^更新词条#(.*?)#(.*)$', re.S)
    s = "更新词条#风风语录#\r[CQ:image,file={E689875E-5F86-5B70-C60C-0DB772FC5086}.mirai,url=http://gchat.qpic.cn/gchatpic_new/729147133/1109145901-2794423816-E689875E5F865B70C60C0DB772FC5086/0?term=2]"

    match = reg.search(s)

    print(match.groups())
    keyword = match.groups()[0]
    content = match.groups()[1]
    print(keyword)
    print(content)
    # print(("keyword: %s, content: %s" % (keyword, content)))


