# 에뮬레이터 창을 직접 캡처(키 입력 후): python wshot.py out.png [키|w초 ...]
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
time.sleep(0.5);capture(h,sys.argv[1]);print('saved')
