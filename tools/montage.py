import glob,os,sys
from PIL import Image,ImageDraw
fs=sorted(glob.glob('view/all/*.png'),key=lambda f:-Image.open(f).size[0]*Image.open(f).size[1])
os.makedirs('view/m',exist_ok=True)
W=1600;page=0;x=y=0;rowh=0;img=Image.new('RGB',(W,1200),(40,40,40));d=ImageDraw.Draw(img)
def flush():
    global img,d,page
    img.save('view/m/p%02d.png'%page);page+=1;img=Image.new('RGB',(W,1200),(40,40,40));d=ImageDraw.Draw(img)
for f in fs:
    im=Image.open(f);w,h=im.size;s=min(1,380/max(w,h));im=im.resize((max(1,int(w*s)),max(1,int(h*s))))
    if x+im.size[0]>W: x=0;y+=rowh+12;rowh=0
    if y+im.size[1]+12>1200: flush();x=y=rowh=0
    img.paste(im,(x,y+10));d.text((x,y),os.path.basename(f)[:6],fill=(255,255,0));x+=im.size[0]+4;rowh=max(rowh,im.size[1])
flush();print(page)
