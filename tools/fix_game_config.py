import re
p='game_config.json'
s=open(p,'r',encoding='utf-8').read()
# merge adjacent options entries for the same key
s2=re.sub(r'("options":\s*\[[^\]]*\])\s*("options":\s*\[[^\]]*\])', lambda m: '"options": [' + m.group(1).split('[',1)[1].rsplit(']',1)[0] + ', ' + m.group(2).split('[',1)[1].rsplit(']',1)[0] + ']', s, count=1)
if s!=s2:
    open(p,'w',encoding='utf-8').write(s2)
    print('fixed')
else:
    print('nochange')
