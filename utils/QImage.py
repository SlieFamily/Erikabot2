import re
import requests
import time
import os
import sqlite3
import base64


# 获取Bot主目录
path = os.path.abspath(os.getcwd())

def get_image_name(text:str)->str:
    '''
        匹配给定CQ文本中的图片url
    '''
    match = re.match(r'\[CQ:image,file=file:///home/erikabot/imgs/([^]]+)\]', text)
    if match:
        return match.group(1)
    else:
        return ''

def image_download(url:str, tag:str, suffix:str = ".jpg", use_timestamp:bool = True)->str:
    '''
        根据所提供的url和tag下载图片并重命名
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.36"
    }
    print("[!]访问图片url中")
    req = requests.get(url, headers = headers, timeout = 5)
    filename = ''
    dirname = '/www/wwwroot/EasyImages/i/qqbot/'
    if req.content:
        if use_timestamp:
            filename = tag+"_"+str(time.time())+suffix
        else:
            filename = tag+suffix
        with open(dirname+filename, mode = "wb") as f:
            f.write(req.content) # 下载图片
        print("[!]图片资源下载成功")
        return  filename
    return filename

def image_to_base64(image_path):
    # 读取图片文件并获取其base64编码
    with open("/www/wwwroot/EasyImages/"+image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode('utf-8')

def transf_anas_image():
    '''
    批量清理旧版本中的图片问题
    '''
    db = sqlite3.connect(path+'/db/anas.db')
    cur = db.cursor()
    cur.execute('select * from AnaList') #获取语录清单
    names = [name[0] for name in cur.fetchall()]

    for name in names: #对每一个语录进行处理
        cur.execute(f'select ana from "_{name}"')
        anas = cur.fetchall()
        print(f"======处理{name}语录=======")
        for ana in anas:
            print("-----START-------")
            ana = ana[0]
            url = get_image_name(ana)
            if url:
                print('获得图片名称：',url)
                new_ana = f"[CQ:image,url=https://image.qslie.top/i/qqbot/{url}]" 
                print('重建语录内容：',new_ana)
                cur.execute(f'update "_{name}" set ana = "{new_ana}" where ana = "{ana}"')
                db.commit()
            else:
                print('[!]当前语录无图片信息')
            print("------END-------")
        print("====================")
