import re

def get_image_name(text:str)->str:
    '''
        匹配给定CQ文本中的图片url
    '''
    match = re.search(r'\[CQ:image,file=file:///home/erikabot/imgs/([^]]+)\]', text)
    if match:
        return match.group(1)
    else:
        return ''

url = "123[CQ:image,file=file:///home/erikabot/imgs/爆点_1704803727.889104.jpg]123"
match = get_image_name(url)
new_ana = f"[CQ:image,url=https://image.qslie.top/i/qqbot/{match}]"

print(new_ana)