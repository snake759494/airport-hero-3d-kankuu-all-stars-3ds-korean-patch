# CLIM(구형 3DS 레이아웃 텍스처): decode(b)->(RGBA배열,fmt), encode(b,img)->새 바이트
import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
import texdec as T,texpatch as P
def info(b):
    im=len(b)-0x14;assert b[im:im+4]==b'imag'
    w,h,fm,sz=struct.unpack_from('<HHII',b,im+8);return T.PICA[fm],w,h,sz
def decode(b):
    fmt,w,h,sz=info(b);W,H=P._pow2(w,h,sz,fmt)
    return T.decode(fmt,b[:sz],W,H).copy(),fmt
def encode(b,img):
    fmt,w,h,sz=info(b);return P.encode(fmt,img[::-1].copy(),b[:sz])+b[sz:]
