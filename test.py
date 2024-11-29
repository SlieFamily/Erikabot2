import re
anas_rule = "([\w\W]{1,6})语录"
def split_ana(text):
    name = re.findall(f"{anas_rule}[:,：]?([\s\S]*)",str(text))[0]
    ana = name[1]
    name = name[0]
    return name, ana

print(split_ana("爆点语录"))