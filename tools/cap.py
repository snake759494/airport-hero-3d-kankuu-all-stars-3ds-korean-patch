# 키 입력 후 에뮬레이터 창을 캡처해 화면 영역만 저장: cap.py out.png [키...]
import sys,os,time
sys.path.insert(0,os.path.dirname(__file__))
from emu import *
B=os.path.join(os.path.dirname(__file__),'..')
pid=int(open(os.path.join(B,'emu.pid')).read())
h=[w for w in wins(pid) if 'Lime' in title(w)][0]
for s in sys.argv[2:]:
    if s.startswith('w'):time.sleep(float(s[1:]));continue
    k,_,n=s.partition('*')
    for i in range(int(n or 1)):key(h,k);time.sleep(0.35)
im=capture(h)
import numpy as np
a=np.asarray(im).astype(int);m=a.sum(2)>0
ys=np.nonzero(m[70:-40].any(1))[0];xs=np.nonzero(m[70:-40].any(0))[0]
if len(ys):im=im.crop((xs[0],70+ys[0],xs[-1]+1,70+ys[-1]+1))
im.save(sys.argv[1]);print('saved',sys.argv[1])
