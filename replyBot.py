#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os.path
import signal,sys

import qqbot
from qqbot.core.util.yaml_util import YamlUtil
from urllib.parse import urlparse,parse_qs

from s1forum import S1Forum
from board import Board

config = YamlUtil.read(os.path.join(os.path.dirname(__file__), "config.yaml"))

def signal_handler(sig,frame):
    s1obj.close()
    sys.exit(0)

async def _message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理

    :param event: 事件类型
    :param message: 事件对象(如监听消息是Message对象)
    """
    if message.content in [b.name for b in Board]:
        msg_api = qqbot.AsyncMessageAPI(token, False)
        qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
        link = f"https://{s1obj.hostname}/archiver/fid-{Board[message.content].value}.html"
        embed_post = await s1obj.getlist(link,message.content)
        await asyncio.sleep(1)
        send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n oops", embed=embed_post, msg_id=message.id)
        # 通过api发送回复消息
        await asyncio.sleep(1)
        try:
            msgresp = await msg_api.post_message(message.channel_id, send)
        except qqbot.core.exception.error.ServerError:
            send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n 帖子太长了放不下~", msg_id=message.id)
            await msg_api.post_message(message.channel_id, send)

    elif message.content.startswith(f"https://{s1obj.hostname}/thread"):
        msg_api = qqbot.AsyncMessageAPI(token, False)
        # 打印返回信息
        qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
        # for i in range(5):
        # await asyncio.sleep(3)
        link = message.content
        embed_post = await s1obj.getpost(link)
        await asyncio.sleep(1)
        # embed_post = await handle_send_embed(post)
        
        # 构造消息发送请求数据对象
        send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n oops", embed=embed_post, msg_id=message.id)
        # 通过api发送回复消息
        await asyncio.sleep(1)

        try:
            msgresp = await msg_api.post_message(message.channel_id, send)
            # qqbot.logger.info(str(msgresp.content))
            # if msgresp.content != f"<@{message.author.id}>\n o_O":
            #     await handle_exceed_limit()
        except qqbot.core.exception.error.ServerError:
            send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n 帖子太长了放不下~", msg_id=message.id)
            await msg_api.post_message(message.channel_id, send)

async def _at_message_handler(event, message: qqbot.Message):
    """
    定义事件回调的处理

    :param event: 事件类型
    :param message: 事件对象(如监听消息是Message对象)
    """
    msg_api = qqbot.MessageAPI(token, False)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % message.content)
    # 构造消息发送请求数据对象
    send = qqbot.MessageSendRequest("收到你的消息: %s" % message.content, message.id)
    # 通过api发送回复消息
    msg_api.post_message(message.channel_id, send)

async def _message_reaction_handler(event, reaction: qqbot.Reaction):
    """
    定义事件回调的处理

    :param event: 事件类型
    :param message: 事件对象(如监听消息是Message对象)
    """
    msg_api = qqbot.MessageAPI(token, False)
    # 打印返回信息
    qqbot.logger.info("event %s" % event + ",receive message %s" % reaction.content)
    # 构造消息发送请求数据对象
    send = qqbot.MessageSendRequest("收到你的消息: %s" % reaction.content, reaction.id)
    # 通过api发送回复消息
    msg_api.post_message(reaction.channel_id, send)

if __name__ == "__main__":
    # async的异步接口的使用示例
    token = qqbot.Token(config["token"]["appid"], config["token"]["token"])
    s1obj = S1Forum("bbs.saraba1st.com/2b", config["token"]["username"], config["token"]["password"])
    qqbot_message_handler = qqbot.Handler(
        qqbot.HandlerType.MESSAGE_EVENT_HANDLER, _message_handler
    )
    qqbot_at_message_handler = qqbot.Handler(
        qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _at_message_handler
    )
    qqbot_message_reaction_handler = qqbot.Handler(
        qqbot.HandlerType.MESSAGE_REACTIONS_EVENT_HANDLER, _message_reaction_handler
    )
    qqbot.async_listen_events(token, False, qqbot_message_handler,qqbot_at_message_handler,qqbot_message_reaction_handler)
    signal.signal(signal.SIGINT,signal_handler)
