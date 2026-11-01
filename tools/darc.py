# darc 아카이브: files(d) -> [(경로, 오프셋, 크기, 엔트리인덱스)], build(d,{인덱스:새데이터})
import struct
def _hdr(d):
    hs,ver,fs,to,ts,do=struct.unpack_from('<HIIIII',d,6);return to,ts,do
def files(d):
    to,ts,do=_hdr(d)
    n=struct.unpack_from('<III',d,to)[2];nt=to+n*12;out=[];stack=[(n,'')]
    def name(o):
        e=d.find(b'\0\0',nt+o);
        while (e-(nt+o))%2:e=d.find(b'\0\0',e+1)
        return d[nt+o:e].decode('utf-16le')
    path=['']*n;ends=[]
    for i in range(n):
        no,a,b=struct.unpack_from('<III',d,to+i*12);isdir=no>>24;nm=name(no&0xffffff)
        while ends and i>=ends[-1][0]:ends.pop()
        base=ends[-1][1] if ends else ''
        p=(base+'/'+nm) if nm else base
        if isdir:ends.append((b,p))
        else:out.append((p.lstrip('/'),a,b,i))
    return out
def build(d,new):
    to,ts,do=_hdr(d);fl=files(d);o=bytearray(d[:do]);pos=do
    order=sorted(fl,key=lambda x:x[1])
    for p,a,b,i in order:
        x=new.get(i,d[a:a+b])
        al=0x80 if a%0x80==0 else 4
        while len(o)%al:o+=b'\0'
        struct.pack_into('<II',o,to+i*12+4,len(o),len(x));o+=x
    struct.pack_into('<I',o,0xc,len(o));return bytes(o)
