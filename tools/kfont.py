# 한글 글꼴 생성: CFNT(v3, 공유 폰트 대체) / FFNT(게임 내장 소형 폰트 재구성)
import struct,os,sys,numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from tex import tile4
from PIL import Image,ImageDraw,ImageFont
def al(x,a):return (x+a-1)//a*a
def render_ttf(ttf,size,chars,cw,ch,base,yadj=0,hang_adv=None,thr=None,mono=False):
    """chars -> {code:(img[ch,cw] uint8, (left,glyphW,charW))}; base = 기준선 y"""
    f=ImageFont.truetype(ttf,size);out={}
    asc,_=f.getmetrics()
    for c in chars:
        s=chr(c)
        if s==' ' or s=='　':
            w=(cw if s=='　' else max(2,size*3//10));out[c]=(np.zeros((ch,cw),np.uint8),(0,0,w));continue
        bb=f.getbbox(s)
        if bb[2]<=bb[0]:continue
        S=4 if not mono else 1
        g=Image.new('L',(cw*S,ch*S));d=ImageDraw.Draw(g)
        if S>1:
            fb=ImageFont.truetype(ttf,size*S);bbb=fb.getbbox(s)
        hang=0xac00<=c<=0xd7a3 or 0x3131<=c<=0x318e
        gw=bb[2]-bb[0]
        if hang and hang_adv:
            adv=hang_adv;ox=max(-bb[0],(adv-gw)//2-bb[0])
        else:
            ox=1-bb[0];adv=gw+2
            if c>=0x3000:adv=max(adv,cw)  # 전각 기호
            if c>=0x3000:ox=(adv-gw)//2-bb[0]
        oy=base-asc+yadj
        if S>1:
            d.text((ox*S,oy*S),s,font=fb,fill=255)
            a=np.array(g.resize((cw,ch),Image.LANCZOS))
        else:
            d.text((ox,oy),s,font=f,fill=255);a=np.array(g)
            a=np.where(a>(thr or 100),255,0).astype(np.uint8)
        out[c]=(a,(0,min(cw,max(adv,1)),min(cw,adv)))
    return out
def sheets_from(glyphs,codes,cw,ch,sw,sh):
    cols=sw//(cw+1);rows=sh//(ch+1);per=cols*rows
    ns=(len(codes)+per-1)//per;sheets=[]
    for s in range(ns):
        img=np.zeros((sh,sw),np.uint8)
        for k,c in enumerate(codes[s*per:(s+1)*per]):
            r,cc=divmod(k,cols);g=glyphs[c][0]
            img[r*(ch+1):r*(ch+1)+ch,cc*(cw+1):cc*(cw+1)+cw]=g[:ch,:cw]
        sheets.append(img)
    return sheets,cols,rows
def cwdh_cmap(codes,glyphs,start_off,alias):
    """alias: {extra_code: target_code} 같은 글리프를 공유하는 추가 코드"""
    idx={c:i for i,c in enumerate(codes)}
    cwdh=bytearray(b'CWDH'+b'\0'*4+struct.pack('<HHI',0,len(codes)-1,0))
    for c in codes:cwdh+=struct.pack('<bBB',*glyphs[c][1])
    while len(cwdh)%4:cwdh+=b'\0'
    struct.pack_into('<I',cwdh,4,len(cwdh))
    m=dict(idx)
    for a,t in alias.items():
        if t in idx and a not in m:m[a]=idx[t]
    ks=sorted(m)
    cmap_off=start_off+len(cwdh)
    cmap=bytearray(b'CMAP'+b'\0'*4+struct.pack('<HHHHI',ks[0],ks[-1],2,0,0)+struct.pack('<H',len(ks)))
    for c in ks:cmap+=struct.pack('<HH',c,m[c])
    while len(cmap)%4:cmap+=b'\0'
    struct.pack_into('<I',cmap,4,len(cmap))
    return bytes(cwdh),bytes(cmap),cmap_off
def build(magic,glyphs,cw,ch,base,linefeed,sw,sh,alias={},ffnt_ver=0x03000000,height=None,width=None,ascent=None,altchar=None,fmt=11,dw=None,v4=False):
    codes=sorted(glyphs)
    sheets,cols,rows=sheets_from(glyphs,codes,cw,ch,sw,sh)
    tiles=[tile4(s) for s in sheets];ss=len(tiles[0])
    maxw=max(g[1][2] for g in glyphs.values())
    hs=0x14
    if magic==b'CFNT':finf_len=0x20
    else:finf_len=0x20
    tg=hs+finf_len
    tglp_hdr=0x20
    so=al(tg+tglp_hdr,0x2000 if v4 else 0x80)
    sheetdata=b''.join(tiles)
    cw_off=so+len(sheetdata)
    cwdh,cmap,cm_off=cwdh_cmap(codes,glyphs,cw_off,alias)
    total=cm_off+len(cmap)
    o=bytearray()
    o+=magic+b'\xff\xfe'+struct.pack('<HIIH',hs,ffnt_ver,total,4)+b'\0\0'
    assert len(o)==hs
    if altchar is None:altchar=ord('?')
    alti=codes.index(altchar) if altchar in codes else 0
    dw=dw or (0,cw,cw)
    if magic==b'CFNT':
        finf=b'FINF'+struct.pack('<IBBH',finf_len,1,linefeed,alti)+struct.pack('<bBBB',dw[0],dw[1],dw[2],1)
        finf+=struct.pack('<III',tg+8,cw_off+8,cm_off+8)+struct.pack('<BBBB',height or ch,width or cw,ascent or base,0)
    else:
        # FFNT v3/v4 FINF: type,height,width,ascent,linefeed(u16),alt(u16),dw(3),enc,tglp,cwdh,cmap
        finf=b'FINF'+struct.pack('<IBBBBHH',finf_len,1,height or ch,width or cw,ascent or base,linefeed,alti)+struct.pack('<bBBB',dw[0],dw[1],dw[2],1)
        finf+=struct.pack('<III',tg+8,cw_off+8,cm_off+8)
    assert len(finf)==finf_len,len(finf)
    o+=finf
    if v4:tglp=b'TGLP'+struct.pack('<IBBBBIHHHHHHI',so-tg+len(sheetdata),cw,ch,len(tiles),maxw,ss,base,fmt,cols,rows,sw,sh,so)
    else:tglp=b'TGLP'+struct.pack('<IBBBBIHHHHHHI',so-tg+len(sheetdata),cw,ch,base,maxw,ss,len(tiles),fmt,cols,rows,sw,sh,so)
    o+=tglp;o+=b'\0'*(so-len(o));o+=sheetdata+cwdh+cmap
    assert len(o)==total
    return bytes(o),sheets
