# 게임 자체 아카이브: u32 개수 + [u32 오프셋, u32 크기, u32 이름해시, u32 0] (헤더는 4바이트 뒤부터 16바이트 단위)
import struct,sys,os
def read(d):
    n=struct.unpack_from('<I',d,0)[0];out=[]
    for i in range(n):
        o,s,h,z=struct.unpack_from('<4I',d,4+i*16);out.append((o,s,h))
    return out
def unpack(d):
    return [(h,d[o:o+s]) for o,s,h in read(d)]
def pack(items,orig=None):
    n=len(items);hdr=(4+n*16+0x7f)&~0x7f
    if orig is not None: hdr=read(orig)[0][0]
    body=bytearray();ents=[];pos=hdr
    for h,b in items:
        ents.append((pos,len(b),h));body+=b;pad=(-len(b))&0x7f;body+=b'\0'*pad;pos+=len(b)+pad
    head=bytearray(hdr);struct.pack_into('<I',head,0,n)
    for i,(o,s,h) in enumerate(ents): struct.pack_into('<4I',head,4+i*16,o,s,h,0)
    return bytes(head+body)
if __name__=='__main__':
    d=open(sys.argv[1],'rb').read()
    for i,(o,s,h) in enumerate(read(d)): print(i,hex(o),hex(s),hex(h),d[o:o+8])
