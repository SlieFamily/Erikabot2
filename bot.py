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
from utils.QImage import *

# 获取Bot主目录
path = os.path.abspath(os.getcwd())

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
            for media in message.attachments:
                if media.content_type in ['image/jpeg', 'image/png', 'image/gif']:
                    _log.info('[!]所添加语录存在图片消息')
                    file_url = image_download(media.url, tag=name)
                    ana = f"[CQ:image,url=https://image.qslie.top/i/qqbot/{file_url}]"
                    break
                else:
                    return True
        if model.IsAdded(name,ana,by):
            await message.reply(content=random.choice(rsp))
        else:
            await message.reply(content="杂鱼~杂鱼~ 这种情报，绘梨花早就记录。")
    else:
        await message.reply(content="请输入所需添加的语录及其内容作为参数。\n如：/add 测试语录：内容文本")
    return True

@Commands("/del")
async def delana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        name = re.findall(f"{anas_rule}-([0-9]+)",str(params))
        if name:
            num = name[0][1]
            name = name[0][0]
            group_id = "144115218677966082"
            ana = model.GetAna(name,group_id,int(num))
            del_msg = model.IsDel(name,str(ana))
        if del_msg:
            await message.reply(content="这种垃圾语录没有存在的必要！")
        else:
            await message.reply(content="失败了失败了失败了……")
    else:
        await message.reply(content="请输入所需删除的语录及其序号作为参数。\n如：/del 测试语录-3")
    return True

@Commands("/drop")
async def dropana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        name = re.findall(anas_rule, str(params))
        if name:
            name = name[0]
            flag = model.DropAna(name)
        if flag:
            await message.reply(content=f"果然{name}语录，就是应该狼狈退场呢~")
        else:
            await message.reply(content="嘁，让他侥幸存活了")
    else:
        await message.reply(content="请输入所需销毁的语录作为参数。\n如：/drop 测试语录")
    return True

@Commands("/search")
async def searchana(api: BotAPI, message: Message, params=None):
    if params:
        _log.info(params)
        ana = str(params)
        if len(ana) < 2:
            await message.reply(content="查询字数应该大于或等于2。")
            return True

        infs = model.Inf(ana)

        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )# URL 正则表达式
        k = 0

        if infs:
            msg = f"\n发现{len(infs)}条相关语录\n\n"
            for i in range(len(infs)):
                if re.findall(url_pattern, infs[i][1]):
                    k += 1 #被拦截的url消息计数
                    continue
                msg += f'{infs[i][0]}语录-{infs[i][3]}：\n'
                msg += infs[i][1]
                msg += f'\n添加者：{infs[i][2]}'
                msg += '\n\n'
            msg += f'共计{k}条语录被隐藏'
            await message.reply(content=msg)
    else:
        await message.reply(content="请输入所需搜索的语录关键词作为参数。\n如：/search 内容")
    return True

@Commands("/list")
async def listana(api: BotAPI, message: Message, params=None):
    await message.reply(content="暂未实现。需获得markdown支持！")
    return True


async def group_theirana(message: Message):
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
            match = re.search(r'\[CQ:image,url=https://image.qslie.top/([^]]+)\]', my_ana)
            if match:
                file_url = match.group(1)
                _log.info(file_url)
                uploadMedia = await message._api.post_group_base64file(
                    group_openid=message.group_openid, 
                    file_type=1, # 1 图片，2 视频，3 语音，4 文件（暂不开放）
                    # url=file_url, # 文件Url
                    file_data=image_to_base64(file_url)
                )
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=7, # 0 文本，2 是 markdown，3 ark 消息，4 embed，7 media 富媒体
                    msg_id=message.id,
                    media=uploadMedia
                )
                return True
            # markdown = MarkdownPayload(content=f"{my_ana}\n>{name}语录")
            # keyboard = KeyboardPayload(content=build_a_demo_keyboard(name))
            else:
                await message._api.post_group_message(
                    group_openid=message.group_openid,
                    msg_type=0, #2为markdown消息 
                    msg_id=message.id,
                    content=my_ana,
                    # markdown=markdown,
                    # keyboard=keyboard,
                )
                return True

async def guild_theirana(message: Message):
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
            match = re.search(r'\[CQ:image,url=https://image.qslie.top/([^]]+)\]', my_ana)
            if match:
                file_url = match.group(1)
                await message.reply(content='',file_image="/www/wwwroot/EasyImages/"+file_url)
                return True
            await message.reply(content=my_ana)
            return True


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: Message):
        handlers = [
            addana,
            delana,
            dropana,
            searchana,
            listana,
            # xxx,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return

        # 触发语录的情况
        await group_theirana(message=message)

    async def on_at_message_create(self, message: Message):
        handlers = [
            addana,
            delana,
            dropana,
            searchana,
            listana,
            # xxx,
        ]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return

        # 触发语录的情况
        await guild_theirana(message=message)


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True, public_guild_messages=True)
    client = MyClient(intents=intents, timeout=20) # , is_sandbox=True
    client.run(appid=test_config["appid"], secret=test_config["secret"])