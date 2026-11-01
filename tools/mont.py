# 해시 목록 텍스처 몽타주: mont.py out.png h1 h2 ... (2배 확대, 라벨)
import sys,os
from PIL import Image,ImageDraw
ims=[]
for h in sys.argv[2:]:
    im=Image.open('view/tex/%s.png'%h[:8]);s=2 if im.width<=256 else 1
    im=im.resize((im.width*s,im.height*s),Image.NEAREST)
    c=Image.new('RGB',(max(im.width,90),im.height+14),(20,20,20));c.paste(im,(0,14))
    d=ImageDraw.Draw(c);d.text((2,1),'%s %dx%d'%(h[:8],im.width//s,im.height//s),fill=(255,255,0));ims.append(c)
W=1200;x=y=rh=0;pos=[]
for i in ims:
    if x+i.width>W:x=0;y+=rh+4;rh=0
    pos.append((x,y));x+=i.width+4;rh=max(rh,i.height)
o=Image.new('RGB',(W,y+rh),(50,50,50))
for i,p in zip(ims,pos):o.paste(i,p)
o.save(sys.argv[1])
