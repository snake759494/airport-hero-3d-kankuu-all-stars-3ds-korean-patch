# Lua 5.1 바이트코드(리틀엔디언, int/size_t 4바이트, number 8바이트) 파서·재구성기
import struct
class R:
    def __init__(s,d):s.d=d;s.p=0
    def u8(s):v=s.d[s.p];s.p+=1;return v
    def i32(s):v=struct.unpack_from('<i',s.d,s.p)[0];s.p+=4;return v
    def raw(s,n):v=s.d[s.p:s.p+n];s.p+=n;return v
    def str(s):
        n=s.i32()
        if n==0:return None
        return s.raw(n)[:-1]
def rfunc(r):
    f={}
    f['src']=r.str();f['hdr']=r.raw(4*2+4)  # linedefined,lastline,nups,nparams,vararg,maxstack
    n=r.i32();f['code']=r.raw(4*n);f['ncode']=n
    n=r.i32();ks=[]
    for i in range(n):
        t=r.u8()
        if t==0:ks.append((0,None))
        elif t==1:ks.append((1,r.u8()))
        elif t==3:ks.append((3,r.raw(8)))
        elif t==4:ks.append((4,r.str()))
        else:raise Exception('k type %d'%t)
    f['k']=ks
    n=r.i32();f['p']=[rfunc(r) for _ in range(n)]
    st=r.p
    n=r.i32();r.raw(4*n)
    n=r.i32()
    for i in range(n):r.str();r.i32();r.i32()
    n=r.i32()
    for i in range(n):r.str()
    f['dbg']=r.d[st:r.p]
    return f
def parse(d):
    assert d[:4]==b'\x1bLua';r=R(d);r.p=12;return d[:12],rfunc(r)
def wstr(s):
    if s is None:return struct.pack('<i',0)
    return struct.pack('<i',len(s)+1)+s+b'\0'
def wfunc(f):
    o=bytearray(wstr(f['src'])+f['hdr']+struct.pack('<i',f['ncode'])+f['code'])
    o+=struct.pack('<i',len(f['k']))
    for t,v in f['k']:
        o.append(t)
        if t==1:o.append(v)
        elif t==3:o+=v
        elif t==4:o+=wstr(v)
    o+=struct.pack('<i',len(f['p']))
    for p in f['p']:o+=wfunc(p)
    o+=f['dbg'];return bytes(o)
def build(h,f):return h+wfunc(f)
def strings(f,path=()):
    for i,(t,v) in enumerate(f['k']):
        if t==4:yield path+(i,),v
    for j,p in enumerate(f['p']):yield from strings(p,path+('p%d'%j,))
def setk(f,path,v):
    for x in path[:-1]:f=f['p'][int(x[1:])]
    t,_=f['k'][path[-1]];assert t==4;f['k'][path[-1]]=(4,v)
