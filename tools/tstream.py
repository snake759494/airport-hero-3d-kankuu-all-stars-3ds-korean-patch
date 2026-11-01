# 타입 필드 스트림: [u16 워드수(헤더 포함), u8 0, u8 타입] + 데이터. 타입 0x0a = UTF-16 문자열(NUL, 4바이트 정렬 +4)
import struct
def parse(d):
    o=0;out=[]
    while o<len(d):
        if len(d)-o<4 or not any(d[o:]):out.append([-1,d[o:]]);break
        n,z,t=struct.unpack_from('<HBB',d,o)
        if n==0 or z!=0 or o+n*4>len(d):return None
        out.append([t,d[o+4:o+n*4]]);o+=n*4
    return out
def sval(data):
    s=data.decode('utf-16le');return s[:s.index('\0')] if '\0' in s else s
def sdata(s):
    b=s.encode('utf-16le')+b'\0\0'
    b+=b'\0'*((-len(b))%4)+b'\0'*4
    return b
def build(fields):
    o=bytearray()
    for t,data in fields:
        if t<0:o+=data;continue
        o+=struct.pack('<HBB',len(data)//4+1,0,t)+data
    return bytes(o)
