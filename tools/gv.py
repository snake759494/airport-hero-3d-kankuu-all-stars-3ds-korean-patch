# 확대+눈금 보기: gv.py out.png scale prefix...
import sys,os,glob
from PIL import Image,ImageDraw
B=os.path.join(os.path.dirname(__file__),'..','view','up')
out,sc=sys.argv[1],int(sys.argv[2]);ims=[]
for p in sys.argv[3:]:
    f=glob.glob(os.path.join(B,p+'*.png'))[0];im=Image.open(f).convert('RGBA')
    bg=Image.new('RGBA',im.size,(255,0,255,255));bg.alpha_composite(im)
    im=bg.resize((im.width*sc,im.height*sc),Image.NEAREST);d=ImageDraw.Draw(im)
    for x in range(0,im.width,10*sc):d.line([(x,0),(x,4 if x%(50*sc) else 12)],fill=(0,255,0,255))
    for y in range(0,im.height,10*sc):d.line([(0,y),(4 if y%(50*sc) else 12,y)],fill=(0,255,0,255))
    d.text((2,2),p,fill=(255,255,0,255));ims.append(im)
W=max(i.width for i in ims);H=sum(i.height+4 for i in ims)
c=Image.new('RGBA',(W,H),(40,40,40,255));y=0
for i in ims:c.paste(i,(0,y));y+=i.height+4
c.save(out)
