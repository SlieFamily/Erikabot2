import re

anas_rule = "([\w\W]{1,6})语录"

def split_ana(text):
    name = re.findall(anas_rule,str(text))
    if name:
    	return name

name = split_ana("我要爆点语")
print(name)