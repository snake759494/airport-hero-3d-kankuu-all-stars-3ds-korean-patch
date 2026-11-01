# 모든 BFLIM/BCLIM을 PNG로 (중복 제거), view/all/<키>.png
import os,sys,glob,hashlib,json
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np, texdec as T
from PIL import Image
out='view/all';os.makedirs(out,exist_ok=True);seen={};idx={}
for p in sorted(glob.glob('dec/tree/*')):
    d=open(p,'rb').read()
    if d[-0x28:-0x24]!=b'FLIM':continue
    try:
        fmt,w,h,sz=T.bflim(d)
        hsh=hashlib.md5(d).hexdigest();k=os.path.basename(p)
        if hsh in seen: idx[k]=seen[hsh];continue
        im=T.decode(fmt,d[:sz],w,h)
        a=im[:,:,3].astype(np.float32)/255;rgb=im[:,:,:3].astype(np.float32)
        comp=(rgb*a[...,None]+np.array([100,100,100],np.float32)*(1-a[...,None])).astype(np.uint8)
        fn=hsh[:10]+'.png';Image.fromarray(comp).save(os.path.join(out,fn));seen[hsh]=fn;idx[k]=fn
    except Exception as e: print('ERR',p,e)
json.dump(idx,open('view/idx.json','w'),indent=0)
print(len(seen),len(idx))
