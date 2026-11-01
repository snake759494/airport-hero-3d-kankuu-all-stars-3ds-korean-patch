import os
B=chr(92)
p='emu/user/config/qt-config.ini';s=open(p,encoding='utf-8').read().split('\n')
w=os.path.abspath('shots').replace(B,'/')+'/'
s=[('Paths'+B+'screenshotPath='+w) if l.startswith('Paths'+B+'screenshotPath=') else l for l in s]
open(p,'w',encoding='utf-8').write('\n'.join(s))
