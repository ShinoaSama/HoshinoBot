import sqlite3
import os
import re
from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino import R, Service, Privilege

sv = Service('lexicon', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
DB_NAME = "Lexicon"


@sv.on_rex(re.compile(r'^更新词条#(.*?)#(.*)$'), normalize=True)
async def keywordPut(bot: NoneBot, ctx, match):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS DICT
            (GROUPID INT,
            KEYWORD TEXT,
            CONTENT TEXT);
            '''
        c.execute(create_tb_cmd)


    except:
        sv.logger.info("Exception in handling Database.")


@sv.on_rex(re.compile(r'.*'), normalize=True)
async def keywordTrigger(bot: NoneBot, ctx, match):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS DICT
            (GROUPID INT,
            KEYWORD TEXT,
            CONTENT TEXT);
            '''
        c.execute(create_tb_cmd)
    except:
        sv.logger.info("Exception in handling Database.")
