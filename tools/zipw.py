# 원본보다 작게 압축하기 위해 zopfli raw deflate로 zip 작성 (게임이 압축본 크기 한도를 가짐)
import struct,zlib,zipfile,io
import zopfli.zlib
def build(orig_zip,files,it=1):
    z=zipfile.ZipFile(io.BytesIO(orig_zip));out=bytearray();cd=bytearray()
    for inf in z.infolist():
        d=files[inf.filename];raw=zopfli.zlib.compress(d,numiterations=it)[2:-4]
        crc=zlib.crc32(d)&0xffffffff;nm=inf.filename.encode();t,dt=_dos(inf.date_time)
        off=len(out)
        out+=struct.pack('<IHHHHHIIIHH',0x04034b50,20,0,8,t,dt,crc,len(raw),len(d),len(nm),0)+nm+raw
        cd+=struct.pack('<IHHHHHHIIIHHHHHII',0x02014b50,20,20,0,8,t,dt,crc,len(raw),len(d),len(nm),0,0,0,0,inf.external_attr,off)+nm
    n=len(z.infolist());co=len(out);out+=cd
    out+=struct.pack('<IHHHHIIH',0x06054b50,0,0,n,n,len(cd),co,0)
    return bytes(out)
def _dos(dt):
    y,m,d,H,M,S=dt;return (H<<11)|(M<<5)|(S//2),((y-1980)<<9)|(m<<5)|d
