import os
import re
import time
import random

from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino import R, Service, Privilege, aiorequests
from hoshino.util import FreqLimiter, DailyNumberLimiter

_max = 5
EXCEED_NOTICE = f'您今天已经冲过{_max}次了，请明早5点后再来！'
_nlmt = DailyNumberLimiter(_max)
_flmt = FreqLimiter(5)

sv = Service('pixiv', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
setu_get_url = "https://api.lolicon.app/setu/"
setu_APIKEY = '193416775ed3983f2aa954'


async def setu_api_request(r18=False):
    params = {'apikey': setu_APIKEY, 'size1200': True}
    if r18:
        params['r18'] = 1
    resp = await aiorequests.get(setu_get_url, params)
    data = await resp.json()

    if len(data['data']) == 0:
        return None

    image_data = data['data'][0]

    image_pid = image_data['pid']
    image_title = image_data['title']
    image_author = image_data['author']
    image_cqcode = '[CQ:image,timeout=10,file=%s]' % (image_data['url'])
    image_tags = ",".join(image_data['tags'])

    wrapped_message = "pid: %s\n" % image_pid + \
                      "title: %s\n" % image_title + \
                      "author: %s\n" % image_author + \
                      "%s\n" % image_cqcode + \
                      "tags: %s" % image_tags
    return wrapped_message


@sv.on_rex(re.compile(r'^(不够[涩瑟色]|[涩瑟色]图|来一?[点份张].*[涩瑟色]|再来[点份张]|看过了|铜)$'), normalize=True)
async def setu(bot: NoneBot, ctx, match):
    """随机叫一份涩图，对每个用户有冷却时间"""
    uid = ctx['user_id']
    if not _nlmt.check(uid):
        await bot.send(ctx, EXCEED_NOTICE, at_sender=True)
        return
    if not _flmt.check(uid):
        await bot.send(ctx, '您冲得太快了，请稍候再冲', at_sender=True)
        return
    _flmt.start_cd(uid)
    _nlmt.increase(uid)

    # conditions all ok, send a setu.
    if match.group().find("r18") >= 0:
        sv.logger.info("Getting an r18 picture...")
        wrapped_message = await setu_api_request(r18=True)
    else:
        sv.logger.info("Getting an picture...")
        wrapped_message = await setu_api_request()
    try:
        await bot.send(ctx, wrapped_message)
    except CQHttpError:
        sv.logger.error(f"发送图片失败")
        try:
            await bot.send(ctx, '涩图太涩，发不出去勒...')
        except:
            pass
