#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os.path
import signal,sys

import botpy
from botpy import logging

from botpy.message import Message
from botpy.reaction import Reaction
from botpy.types.message import Embed, EmbedField
from botpy.ext.cog_yaml import read
from urllib.parse import urlparse,parse_qs

from s1forum import S1Forum
from board import Board
from bs4 import NavigableString, Tag

config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

def signal_handler(sig,frame):
    s1obj.close()
    sys.exit(0)

class S1Client(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_message_create(self, message: Message):
        _log.info(f"receive message {message.content}" )

        if message.content in [b.name for b in Board]:
            link = f"https://{s1obj.hostname}/archiver/fid-{Board[message.content].value}.html"
            post = await s1obj.fetchAndParse(link)
            await asyncio.sleep(1)

            if type(post) != NavigableString and type(post) != Tag:
                _log.info(f"Post not parsed: {post}" )
                await message.reply(content=f"Post not parsed: {post}")
                return
            embed = Embed(
                title = message.content,
                prompt = message.content + "新帖列表",
                fields = []
            )
            i = 0
            for s in post.find_all('ul')[1].find_all('a'):
                i += 1
                s = str(i)+"."+s.string
                # qqbot.logger.info(s)
                # await asyncio.sleep(0.1)
                if len(s) >= 50:
                    s = s[0:50] + "..."
                if i > 15:
                    break
                else:
                    embed["fields"].append(EmbedField(name=s, value="content")) 
            
            # 通过api发送回复消息
            await asyncio.sleep(1)
            try:
                await self.api.post_message(channel_id=message.channel_id, embed=embed)
            except:
                # send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n 帖子太长了放不下~", msg_id=message.id)
                await message.reply(content=f"<@{message.author.id}>\n 帖子太长了放不下~")

        elif message.content.startswith(f"https://{s1obj.hostname}/thread"):
            # 打印返回信息
            _log.info(f"receive message {message.content}" )
            # for i in range(5):
            # await asyncio.sleep(3)
            link = message.content
            tid = link
            urlraw = urlparse(link)
            if "&tid=" in tid:
                tid = parse_qs(urlraw.query)["tid"][0]
            else:
                tid = urlraw.path[11:-9]
            
            url = f'https://{s1obj.hostname}/archiver/tid-{tid}.html'
            
            post = await s1obj.fetchAndParse(url)

            if type(post) != NavigableString and type(post) != Tag:
                _log.info(f"Post not parsed: {post}" )
                await message.reply(content=f"Post not parsed: {post}")
                return

            # 构造消息发送请求数据对象
            embed = Embed(
                title = post.h3.string,
                prompt = post.p.string,
                fields = []
            )
            for s in post.stripped_strings:
                # qqbot.logger.info(s)
                # await asyncio.sleep(0.1)
                if len(s) >=50:
                    s = s[0:50] + "..."
                if len(embed["fields"]) > 15:
                    break
                else:
                    embed["fields"].append(EmbedField(name=s, value="content")) 

            await asyncio.sleep(1)
            # embed_post = await handle_send_embed(post)
            
            # 通过api发送回复消息
            try:
                await self.api.post_message(channel_id=message.channel_id, embed=embed)
            except:
                # send = qqbot.MessageSendRequest(content=f"<@{message.author.id}>\n 帖子太长了放不下~", msg_id=message.id)
                await message.reply(content=f"<@{message.author.id}>\n 帖子太长了放不下~")

        elif message.content.startswith(f"-post:"):
            # 打印返回信息
            _log.info(f"receive message {message.content}" )
            resptext = await s1obj.newThread(148, "Bot test 0", "Hello this is S1 bot")
            _log.info(f"return text:{resptext}" )
            # await message.reply(content=f"<@{message.author.id}>\n , return text:{resptext}")

        elif message.content.startswith(f"-reply:"):
            # 打印返回信息
            _log.info(f"receive message {message.content}" )
            # resptext = await s1obj.newThread(148, "Bot test 0", "Hello this is S1 bot")
            resptext = await s1obj.reply(148, 2092209, "Hello this is S1 bot replying")
            _log.info(f"return text:{resptext}" )
            # await message.reply(content=f"<@{message.author.id}>\n , return text:{resptext}")

    async def on_at_message_create(self, message: Message):
        # 打印返回信息
        _log.info(f"receive message {message.content}" )
        # 构造消息发送请求数据对象
        embed = Embed(
            title="embed消息",
            prompt="消息透传显示",
            fields=[
                EmbedField(name="<@!1234>hello world"),
                EmbedField(name="<@!1234>hello world"),
            ],
        )

        # embed = {
        #     "title": "embed消息",
        #     "prompt": "消息透传显示",
        #     "fields": [
        #         {"name": "<@!1234>hello world"},
        #         {"name": "<@!1234>hello world"},
        #     ],
        # }

        await self.api.post_message(channel_id=message.channel_id, embed=embed)
        # await message.reply(embed=embed) # 这样也可以

    async def on_message_reaction_add(self, reaction: Reaction):

        # 打印返回信息
        _log.info(f"receive message {reaction.emoji}" )

        # 通过api发送回复消息
        await self.api.post_message(channel_id=reaction.channel_id, content=f"<@{reaction.user_id}>\n emoji received.")

if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents.none()
    intents.guild_messages=True
    intents.guild_message_reactions=True
    intents.public_guild_messages=True
    s1obj = S1Forum("bbs.saraba1st.com/2b", config["token"]["username"], config["token"]["password"])

    client = S1Client(intents=intents)
    client.run(appid=config["token"]["appid"], token=config["token"]["token"])   

    # token = qqbot.Token(config["token"]["appid"], config["token"]["token"])
    # qqbot_message_handler = qqbot.Handler(
    #     qqbot.HandlerType.MESSAGE_EVENT_HANDLER, _message_handler
    # )
    # qqbot_at_message_handler = qqbot.Handler(
    #     qqbot.HandlerType.AT_MESSAGE_EVENT_HANDLER, _at_message_handler
    # )
    # qqbot_message_reaction_handler = qqbot.Handler(
    #     qqbot.HandlerType.MESSAGE_REACTIONS_EVENT_HANDLER, _message_reaction_handler
    # )
    # qqbot.async_listen_events(token, False, qqbot_message_handler,qqbot_at_message_handler,qqbot_message_reaction_handler)
    signal.signal(signal.SIGINT,signal_handler)
