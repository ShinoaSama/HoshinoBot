import sqlite3
import os, random
import re

from nonebot import get_bot, NoneBot
from hoshino import Service, Privilege

sv = Service('randomsaying', manage_priv=Privilege.SUPERUSER, enable_on_default=True, visible=False)
global_bot = get_bot()


def get_db_path(group_id):
    if group_id:
        db_name = str(group_id)
    else:
        db_name = "general"
    db_name = db_name + ".db"

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), db_name)


@sv.on_rex(re.compile(r'^更新随机词条#(.*?)#(.*)$', re.S), normalize=True)
async def keyword_put(bot: NoneBot, ctx, match):
    # match丢失了一些信息, 故不采用
    message_match = re.compile(r'^更新随机词条#(.*?)#(.*)$', re.S).match(str(ctx['message']))
    keyword = message_match.groups()[0]
    content = message_match.groups()[1]
    content = content.strip()

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
        put_keyword(conn, keyword, content)
        conn.commit()
        conn.close()

        sv.logger.info("Update the keyword-content pair successfully.")

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        await bot.send(ctx, '更新随机词条失败...', at_sender=True)

    await bot.send(ctx, '更新随机词条成功!', at_sender=True)


@global_bot.on_message('group')
async def keyword_trigger(context):
    group_id = context['group_id']
    keyword_match = re.compile(r'^随机(.*)$', re.S).match(str(context['message']))
    if keyword_match is None:
        return

    keyword = keyword_match.groups()[0]
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

    # select randomly
    num = len(exist_content)
    if num == 0:
        return

    selected_index = random.randint(0, num - 1)
    await global_bot.send(context, exist_content[selected_index][0])


@sv.on_rex(re.compile(r'^清空随机词条#(.*)$'), normalize=True)
async def clear_keyword_trigger(bot: NoneBot, ctx, match):

    if ctx['user_id'] != 729147133:
        await bot.send(ctx, '权限不足!', at_sender=True)
        return

    keyword = match.groups()[0]
    group_id = ctx['group_id']
    db_name = get_db_path(group_id)

    try:
        conn = sqlite3.connect(db_name)
        pre_create_db(conn)
        clear_key_value_pairs(conn, keyword)
        conn.commit()
        conn.close()
        sv.logger.info("clear the keyword-content pairs successfully.")

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        await bot.send(ctx, '清空随机词条失败...', at_sender=True)

    await bot.send(ctx, '清空随机词条成功!', at_sender=True)


@sv.on_rex(re.compile(r'^删除随机词条#(.*?)#(.*)$'), normalize=True)
async def delete_keyword_trigger(bot: NoneBot, ctx, match):
    message_match = re.compile(r'^删除随机词条#(.*?)#(.*)$', re.S).match(str(ctx['message']))
    keyword = message_match.groups()[0]
    content = message_match.groups()[1]
    content = content.strip()

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
        delete_key_value_pair(conn, keyword, content)
        conn.commit()
        conn.close()
        sv.logger.info("Delete the keyword-content pair successfully.")

    except Exception as e:
        sv.logger.info("Exception in handling Database: " + str(e))
        await bot.send(ctx, '删除随机词条失败...', at_sender=True)

    await bot.send(ctx, '删除随机词条成功!', at_sender=True)


def pre_create_db(conn):
    c = conn.cursor()
    create_tb_cmd = '''
        CREATE TABLE IF NOT EXISTS Dict
        (keyword TEXT NOT NULL,
        content TEXT NOT NULL,
        PRIMARY KEY(keyword, content));
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
    result = cursor.fetchall()
    return result


def delete_key_value_pair(conn, keyword, content):
    c = conn.cursor()
    delete_cmd = '''
        DELETE FROM Dict
        WHERE keyword='%s' AND content='%s' 
    ''' % (keyword, content)
    c.execute(delete_cmd)


def clear_key_value_pairs(conn, keyword):
    c = conn.cursor()
    delete_cmd = '''
        DELETE FROM Dict
        WHERE keyword='%s'
    ''' % keyword
    c.execute(delete_cmd)


def put_keyword(conn, keyword, content):
    c = conn.cursor()
    pre_search_cmd = '''
        SELECT *
        FROM Dict
        WHERE keyword='%s' AND content='%s'
    ''' % (keyword, content)
    cursor = c.execute(pre_search_cmd)
    result = cursor.fetchone()

    # check if there exists a same key-value pair.
    # if not exist, put a new key-value pair.
    if result is None:
        insert_tb_cmd = '''
            INSERT INTO Dict(keyword, content)
            VALUES('%s', '%s')
        ''' % (keyword, content)
        c.execute(insert_tb_cmd)
