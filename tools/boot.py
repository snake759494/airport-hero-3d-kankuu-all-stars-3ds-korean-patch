# 롬을 백그라운드로 실행해 N초 후 캡처, FPS 상태 영역 출력
import sys,os,time,subprocess
sys.path.insert(0,os.path.dirname(__file__))
from emu import *
B=os.path.join(os.path.dirname(__file__),'..')
try:subprocess.run(['taskkill','/PID',open(os.path.join(B,'emu.pid')).read(),'/F'],capture_output=True)
except Exception:pass
subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'launch.py'),sys.argv[1]],capture_output=True)
time.sleep(float(sys.argv[3]) if len(sys.argv)>3 else 25)
pid=int(open(os.path.join(B,'emu.pid')).read())
h=[w for w in wins(pid) if 'Lime' in title(w)][0]
im=capture(h,sys.argv[2]);print('saved',im.crop((8,64,1288,544)).getextrema())
