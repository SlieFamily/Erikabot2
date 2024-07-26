# -*- coding: utf-8 -*-
import asyncio
import os
import re
import random
import botpy
from botpy import logging, BotAPI
from botpy.ext.command_util import Commands
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message
from botpy.types.inline import Keyboard, Button, RenderData, Action, Permission, KeyboardRow
from botpy.types.message import MarkdownPayload, KeyboardPayload

# 载入机器人配置
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))
_log = logging.get_logger()

# 初始化数据库
from db import model
model.Init()

anas_rule = "([\w\W]{1,6})语录"
rsp = ["用最爱的筷子品味最恶俗的语录才称得上健全~","知性的强J者怎能输给后辈！"]

def split_ana(text):
    name = re.findall(f"{anas_rule}[:,：]?([\s\S]*)",str(text))[0]
    ana = name[1]
    name = name[0]
    return name, ana

def build_a_demo_keyboard(name:str) -> Keyboard:
    """
    创建 button 键盘
    """
    button1 = Button(
        id="1",
        render_data=RenderData(label="我也+1", visited_label="BUTTON", style=0),
        action=Action(
            type=2,
            permission=Permission(type=2, specify_role_ids=["1"], specify_user_ids=["1"]),
            click_limit=10,
            data=f"{name}语录",
            at_bot_show_channel_list=True,
        ),
    )

    row1 = KeyboardRow(buttons=[button1])
    return Keyboard(rows=[row1])


@Commands("/add")
async def addana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        name, ana = split_ana(params)
        # by = message.author.username # 等待官方实现
        by = "Auto"
        if not ana:
            _log.info(message.attachments)
        if model.IsAdded(name,ana,by):
            await message.reply(content=random.choice(rsp))
            return True
        else:
            await message.reply(content="苦撸西，失败了失败了！")
            return False

@Commands("/del")
async def delana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        name = re.findall(f"{anas_rule}-([0-9]+)",str(params))
        if name:
            num = name[0][1]
            name = name[0][0]
            group_id = "144115218677966082"
            ana = model.GetAna(name,group,int(num))
            del_msg = model.IsDel(name,str(ana))
        if del_msg:
            await message.reply(content="这种垃圾语录没有存在的必要！")
            return True
        else:
            await message.reply(content="失败了失败了失败了……")
            return False

@Commands("/drop")
async def dropana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        name = re.findall(anas_rule, str(params))
        if name:
            name = name[0][0]
            flag = model.DropAna(name)
        if flag:
            await message.reply(content=f"果然{name}语录，就是应该狼狈退场呢~")
            return True
        else:
            await message.reply(content="嘁，让他侥幸存活了")
            return False

async def theirana(message: Message):
    name = re.findall(f" {anas_rule}[-]*([0-9]*)",str(message.content))
    _log.info(str(name))
    if name:
        num = name[0][1]
        name = name[0][0]
        group_id = "144115218677966082"
        if not num:
            my_ana = model.GetAna(name,group_id) #获取随机语录
        else:
            try:
               my_ana = model.GetAna(name,group_id,int(num)) #获取指定序号的语录
            except:
                pass
        if my_ana:
            # markdown = MarkdownPayload(content=f"{my_ana}\n>{name}语录")
            # keyboard = KeyboardPayload(content=build_a_demo_keyboard(name))
            messageResult = await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0, #2为markdown消息 
                    # msg_id=message.id,
                    content=my_ana,
                    # markdown=markdown,
                    # keyboard=keyboard,
            )

            _log.info(messageResult)
            return True

class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: Message):
        
        handlers = [
            addana,
            delana,
            dropana,
            # good_night,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return

        # 触发语录的情况
        await theirana(message=message)


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=test_config["appid"], secret=test_config["secret"])