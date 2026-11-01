# 키를 일정 시간 누르고 있기: hold.py 키 초
import sys,os,time
sys.path.insert(0,os.path.dirname(__file__))
from emu import *
B=os.path.join(os.path.dirname(__file__),'..')
pid=int(open(os.path.join(B,'emu.pid')).read())
h=[w for w in wins(pid) if 'Lime' in title(w)][0]
key(h,sys.argv[1],float(sys.argv[2]))
