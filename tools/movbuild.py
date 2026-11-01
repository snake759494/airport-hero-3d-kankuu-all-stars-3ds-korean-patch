# tc.pkts(재인코딩 프레임)를 원본 moflex에 다시 묶음: movbuild.py src.moflex tc.pkts out.moflex
import sys,os,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from moflex import parse
from mux import groups,mux
from apply import readtc
src,tc,dst=sys.argv[1:4]
rep=readtc(tc);gs=groups(parse(open(src,'rb').read()));vi=0
for g in gs:
    for f in g['frames']:
        if f[0]==1:
            if vi in rep:f[2]=rep[vi]
            vi+=1
m,sp=mux(gs);open(dst,'wb').write(m);print('movie',vi,len(rep),len(m))
