# 모든 컨테이너를 재귀적으로 풀어 dec/tree 에 리프를 저장
import os,sys,struct,zipfile,io
sys.path.insert(0,os.path.dirname(__file__))
import pak,sarc,lz11
OUT='dec/tree'
def ispak(d):
    if len(d)<0x20: return False
    n=struct.unpack_from('<I',d,0)[0]
    if not 0<n<5000 or 4+n*16>len(d): return False
    try:
        e=pak.read(d)
        return all(o+s<=len(d) and o>=4+n*16 and z==0 for (o,s,h),z in zip(e,[struct.unpack_from('<I',d,16+i*16)[0] for i in range(n)])) and all(e[i][0]>=e[i-1][0]+e[i-1][1] for i in range(1,n)) and e[0][0]>=4+n*16 and e[0][0]<4+n*16+0x80
    except Exception: return False
def walk(d,path,log):
    if d[:4]==b'PK\x03\x04':
        z=zipfile.ZipFile(io.BytesIO(d))
        for n in z.namelist(): walk(z.read(n),path+'@'+n.replace('/','_'),log)
        return
    if d[:4]==b'SARC':
        for nm,s,e in sarc.parse(d): walk(d[s:e],path+'@'+nm.replace('/','_'),log)
        return
    if d[:1]==b'\x11' and path.endswith('_LZ.bin'):
        walk(lz11.dec(d),path+'@lz',log);return
    if ispak(d):
        for i,(h,b) in enumerate(pak.unpack(d)): walk(b,path+'@%02d_%08x'%(i,h),log)
        return
    fn=os.path.join(OUT,path);os.makedirs(os.path.dirname(fn),exist_ok=True);open(fn,'wb').write(d)
    log.append((path,len(d),d[:4]))
log=[]
R='ext/romfs'
for dp,dn,fs in os.walk(R):
    for f in fs:
        p=os.path.relpath(os.path.join(dp,f),R).replace(os.sep,'/')
        if p.startswith(('voice/','movie/','sound/')): continue
        walk(open(os.path.join(dp,f),'rb').read(),p.replace('/','_'),log)
import collections
c=collections.Counter(m for _,_,m in log)
print(len(log),c.most_common(40))
open('dec/tree.txt','w',encoding='utf-8').write('\n'.join('%s\t%d\t%r'%x for x in log))
