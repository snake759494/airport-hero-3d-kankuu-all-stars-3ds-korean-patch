# 백그라운드 에뮬레이터 조작+캡처: python s.py out.png [키[*n]|w초 ...]
# 창을 활성화하지 않고 스레드 입력만 연결해 렌더 위젯에 포커스를 준 뒤 키 전송, Ctrl+P(내장 스크린샷)로 캡처
import sys,os,time,glob,shutil,ctypes
sys.path.insert(0,os.path.dirname(__file__))
from emu import *
from ctrlkey import ctrl_key
k=ctypes.windll.kernel32
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
pid=int(open(os.path.join(B,'emu.pid')).read())
h=[w for w in wins(pid) if 'Lime' in title(w)][0]
r=[c for c in children(h) if 'OwnDC' in cls(c)][0]
def focus():
    tid=u.GetWindowThreadProcessId(h,None);me=k.GetCurrentThreadId()
    u.AttachThreadInput(me,tid,True);u.SetFocus(r);u.AttachThreadInput(me,tid,False)
focus()
for s in sys.argv[2:]:
    if s.startswith('w'):time.sleep(float(s[1:]));continue
    kk,_,n=s.partition('*')
    for i in range(int(n or 1)):key(h,kk,0.12);time.sleep(0.4)
SD=os.path.join(B,'shots');old=set(glob.glob(os.path.join(SD,'*.png')))
focus();ctrl_key(h,ord('P'))
for i in range(40):
    time.sleep(0.25);new=set(glob.glob(os.path.join(SD,'*.png')))-old
    if new:break
time.sleep(0.3);shutil.move(list(new)[0],sys.argv[1]);print('saved',sys.argv[1])
