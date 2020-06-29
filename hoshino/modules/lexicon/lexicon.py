import sqlite3
import os
import re

from nonebot import get_bot, NoneBot
from hoshino import Service, Privilege

sv = Service('lexicon', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
global_bot = get_bot()


def get_db_path(group_id):
    if group_id:
        db_name = str(group_id)
    else:
        db_name = "general"
    db_name = db_name + ".db"

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)


@sv.on_rex(re.compile(r'^更新词条#(.*?)#(.*)$', re.S), normalize=True)
async def keyword_put(bot: NoneBot, ctx, match):

    # match丢失了一些信息, 故不采用
    message_match = re.compile(r'^更新词条#(.*?)#(.*)$', re.S).match(str(ctx['message']))
    keyword = message_match.groups()[0]
    content = message_match.groups()[1]

    # 在使用mirai + CQHTTPMirai下, 对content的CQ码进行处理
    content = re.sub(r"CQ:image,file=\{.*\}.mirai,url=", "CQ:image,file=", content)

    group_id = ctx['group_id']
    db_name = get_db_path(group_id)

    sv.logger.info("db_name: " + db_name)
    sv.logger.info("keyword: " + keyword)
    sv.logger.info("content: " + content)

    try:
        conn = sqlite3.connect(db_name)
        pre_create_db(conn)
        exist_content = get_value_by_keyword(conn, keyword)

        # check if there have existed the keyword.
        if exist_content is not None:
            update_value_by_keyword(conn, keyword, content)
        else:
            put_keyword(conn, keyword, content)

        conn.commit()
        conn.close()

        sv.logger.info("Update the keyword-content pair successfully.")

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        await bot.send(ctx, '更新词条失败...', at_sender=True)

    await bot.send(ctx, '更新词条成功!', at_sender=True)


@global_bot.on_message('group')
async def keyword_trigger(context):
    group_id = context['group_id']
    keyword = str(context['message'])
    db_name = get_db_path(group_id)

    try:
        conn = sqlite3.connect(db_name)
        pre_create_db(conn)
        exist_content = get_value_by_keyword(conn, keyword)
        conn.commit()
        conn.close()

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        return

    if exist_content is not None:
        sv.logger.info("db_name: " + db_name)
        sv.logger.info("keyword: " + keyword)
        sv.logger.info("The content in database is: " + exist_content)
        await global_bot.send(context, exist_content)


@sv.on_rex(re.compile(r'^删除词条#(.*)$'), normalize=True)
async def delete_keyword_trigger(bot: NoneBot, ctx, match):
    keyword = match.groups()[0]
    group_id = ctx['group_id']
    db_name = get_db_path(group_id)

    sv.logger.info("db_name: " + db_name)
    sv.logger.info("keyword: " + keyword)

    try:
        conn = sqlite3.connect(db_name)
        pre_create_db(conn)
        exist_content = get_value_by_keyword(conn, keyword)
        if exist_content is not None:
            delete_value_by_keyword(conn, keyword)

        conn.commit()
        conn.close()

        sv.logger.info("Delete the keyword-content pair successfully.")

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        await bot.send(ctx, '删除词条失败...', at_sender=True)

    await bot.send(ctx, '删除词条成功!', at_sender=True)


def pre_create_db(conn):
    c = conn.cursor()
    create_tb_cmd = '''
        CREATE TABLE IF NOT EXISTS Dict
        (keyword TEXT,
        content TEXT NOT NULL,
        PRIMARY KEY(keyword));
    '''
    c.execute(create_tb_cmd)


def get_value_by_keyword(conn, keyword):
    c = conn.cursor()
    select_tb_cmd = '''
        SELECT content
        FROM Dict
        WHERE keyword='%s'
    ''' % keyword
    cursor = c.execute(select_tb_cmd)
    result = cursor.fetchone()

    if result is None:
        return None
    else:
        return result[0]


def update_value_by_keyword(conn, keyword, content):
    c = conn.cursor()
    update_tb_cmd = '''
        UPDATE Dict
        SET content='%s'
        WHERE keyword='%s'
    ''' % (content, keyword)
    c.execute(update_tb_cmd)


def delete_value_by_keyword(conn, keyword):
    c = conn.cursor()
    update_tb_cmd = '''
        DELETE FROM Dict
        WHERE keyword='%s'   
    ''' % keyword
    c.execute(update_tb_cmd)


def put_keyword(conn, keyword, content):
    c = conn.cursor()
    insert_tb_cmd = '''
        INSERT INTO Dict(keyword, content)
        VALUES('%s', '%s')
    ''' % (keyword, content)
    c.execute(insert_tb_cmd)
