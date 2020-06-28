import sqlite3
import os
import re
from nonebot import on_command, CommandSession, MessageSegment, NoneBot
from nonebot.exceptions import CQHttpError

from hoshino import R, Service, Privilege

sv = Service('lexicon', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
DB_NAME = "Lexicon"

@sv.on_rex(re.compile(r'.*'), normalize=True)
async def lexicon(bot: NoneBot, ctx, match):
    conn = sqlite3.connect(DB_NAME)
    create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS DICT
            (GROUPID INT,
            KEYWORD TEXT,
            CONTENT TEXT);
            '''
    conn.execute(create_tb_cmd)
    

