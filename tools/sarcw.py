# SARC 재구성: 헤더/SFAT/SFNT는 그대로 두고 데이터만 교체(원래 정렬 유지)
import struct
def files(d):
    hl=struct.unpack_from('<H',d,4)[0];doff=struct.unpack_from('<I',d,0xc)[0]
    n=struct.unpack_from('<H',d,hl+6)[0]
    return [(i,doff+struct.unpack_from('<I',d,hl+12+16*i+8)[0],doff+struct.unpack_from('<I',d,hl+12+16*i+12)[0]) for i in range(n)]
def build(d,new):
    """new: {index: bytes}"""
    hl=struct.unpack_from('<H',d,4)[0];doff=struct.unpack_from('<I',d,0xc)[0]
    out=bytearray(d[:doff]);fs=files(d)
    for i,s,e in fs:
        a=0x80
        while a>1 and s%a:a//=2
        b=new.get(i,d[s:e])
        while len(out)%a:out.append(0)
        st=len(out)-doff;out+=b
        struct.pack_into('<II',out,hl+12+16*i+8,st,st+len(b))
    struct.pack_into('<I',out,8,len(out))
    return bytes(out)
