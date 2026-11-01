# 전체 한글 빌드: 번역(tr/ko) -> 각 텍스트 원천 교체 -> 컨테이너 재구성 -> 한글 .3ds
import os,sys,json,glob,re,struct,zipfile,io
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0,os.path.dirname(__file__))
import pak,sarc,sarcw,lz11,luac,tstream,lyt,ffnt,kfont,codepatch,build,extract
def ispak(d):
    if len(d)<0x20: return False
    n=struct.unpack_from('<I',d,0)[0]
    if not 0<n<5000 or 4+n*16>len(d): return False
    try:
        e=pak.read(d)
        return all(o+s<=len(d) and o>=4+n*16 and z==0 for (o,s,h),z in zip(e,[struct.unpack_from('<I',d,16+i*16)[0] for i in range(n)])) and all(e[i][0]>=e[i-1][0]+e[i-1][1] for i in range(1,n)) and e[0][0]>=4+n*16 and e[0][0]<4+n*16+0x80
    except Exception: return False
B=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
G=os.path.dirname(B)
ROM=os.path.join(G,'Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Japan).3ds')
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(G,'Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Korean).3ds')
T=os.path.join(B,'dec','tree');R=os.path.join(B,'ext','romfs')
TTF=os.path.join(G,'NanumSquareNeo-bRg.ttf');FALLBACK='C:/Windows/Fonts/malgun.ttf'
GAL=os.path.join(B,'fonts','Galmuri9.ttf')
items=json.load(open(os.path.join(B,'tr','items.json'),encoding='utf-8'))
KO={}
for f in sorted(glob.glob(os.path.join(B,'tr','ko','*.json'))):KO.update(json.load(open(f,encoding='utf-8')))
TR={x['jp']:KO[str(x['id'])] for x in items if str(x['id']) in KO}
CX=json.load(open(os.path.join(B,'tr','code_extra.json'),encoding='utf-8'))
for _j,_k in CX.items():TR.setdefault(_j,_k)
BUD={x['jp']:x['max'] for x in items}
errs=[]
isH=lambda c:0xac00<=ord(c)<=0xd7a3 or 0x3131<=ord(c)<=0x318e
# ---- SJIS 대리 한자: SJIS 원천(Lua, ATC)의 한글을 JIS 1수준 한자 코드로 표현 ----
sj_src=[x for x in items if str(x['id']) in KO and any(s.startswith(('lua:','atc')) for s in x['src'])]
# 코드 내 SJIS 문자열(일시정지 메뉴 등)
CODE_SJ={'スタート':'시작','ステージに戻る':'스테이지 복귀','リプレイに戻る':'리플레이 복귀','最初からやり直す':'처음부터 다시',
 'ステージ選択に戻る':'스테이지 선택으로','ステージ選択画面へ':'스테이지 선택 화면','メインメニューに戻る':'메인 메뉴로 돌아가기',
 'メインメニューへ':'메인 메뉴로','訓練選択画面に戻る':'훈련 선택으로','訓練選択画面へ':'훈련 선택 화면','リスタート':'재시작',
 '次へ進む':'다음으로','ゲームを終わる':'게임 종료'}
sjH=sorted({c for x in sj_src for c in KO[str(x['id'])] if isH(c)}|{c for v in CODE_SJ.values() for c in v if isH(c)}|{c for v in json.load(open(os.path.join(B,'tr','atc_seg.json'),encoding='utf-8')).values() for c in v if isH(c)})
PROXY={};ALIAS={}
def sj_codes():
    for hi in list(range(0x88,0xa0))+list(range(0xe0,0xea)):
        for lo in list(range(0x40,0x7f))+list(range(0x80,0xfd)):
            if (hi,lo)<(0x88,0x9f):continue
            try:u=bytes([hi,lo]).decode('cp932')
            except:continue
            if len(u)==1 and 0x4e00<=ord(u)<=0x9fff:yield bytes([hi,lo]),u
g=sj_codes()
for h in sjH:
    b,u=next(g);PROXY[h]=b;ALIAS[ord(u)]=ord(h)
def sjenc(s):
    o=bytearray()
    for c in s:
        if c in PROXY:o+=PROXY[c]
        else:
            try:o+=c.encode('cp932')
            except UnicodeEncodeError:errs.append('sjis불가 %r in %r'%(c,s));o+=b'?'
    return bytes(o)
print('SJIS 대리 한글',len(sjH))
# ---- 트리 리프 교체 목록 ----
NEW={}
def leaf(n):
    if n in NEW:return NEW[n]
    return open(os.path.join(T,n),'rb').read()
# Lua
nlua=0
for f in sorted(glob.glob(os.path.join(T,'script_*'))):
    n=os.path.basename(f);d=leaf(n)
    if d[:4]!=b'\x1bLua':continue
    h,fn=luac.parse(d);ch=0
    for p,s in list(luac.strings(fn)):
        if not any(x>=0x80 for x in s):continue
        jp=s.decode('cp932')
        if jp in TR:luac.setk(fn,p,sjenc(TR[jp]));ch+=1;nlua+=1
    if ch:NEW[n]=luac.build(h,fn)
print('lua',nlua)
# ATC 자막
ASEG=json.load(open(os.path.join(B,'tr','atc_seg.json'),encoding='utf-8'));ASEGRE=re.compile(r'@\[[^\]]*\]\[([^\]]*)\]')
NUM=re.compile(r'\d[\d,]*')
for an in ('res_bk3main_rjbb.zip@bk3main_rjbb.dat@01_2ed7d5c5@02_cc9edb3e','res_bk3main_rjbb.zip@bk3main_rjbb.dat@01_2ed7d5c5@01_cc9ed639'):   # 일본어판·영어판(영어판에도 일본어 교신 섞임)
    d=leaf(an)
    n=struct.unpack_from('<I',d,0)[0];offs=[struct.unpack_from('<I',d,4+4*i)[0] for i in range(n)]+[len(d)]
    ents=[];natc=0;miss=0
    for i in range(n):
        e=d[offs[i]:offs[i+1]];hd=e[:4];raw=e[4:].split(b'\0')[0]
        s=raw.decode('cp932');t=extract.templ(s)
        if t not in TR and all(x in ASEG for x in ASEGRE.findall(t)) and ASEGRE.findall(t):
            TR[t]=re.sub(r'(@\[[^\]]*\]\[)([^\]]*)(\])',lambda m:m.group(1)+ASEG[m.group(2)]+m.group(3),t)
        if t in TR:
            nums=NUM.findall(s);k=TR[t]
            if k.count('#')!=len(nums):errs.append('ATC # 개수 불일치 %r'%t)
            else:
                it=iter(nums);k=re.sub('#',lambda m:next(it),k);raw=sjenc(k);natc+=1
        elif extract.J.search(s):miss+=1;print('ATC미번역',repr(t))
        b=hd+raw+b'\0'
        while len(b)%4:b+=b'\0'
        ents.append(b)
    hdr=4+4*n;hdr=offs[0] if offs[0]>=hdr else hdr
    o=bytearray(d[:offs[0]]);pos=offs[0]
    for i,b in enumerate(ents):struct.pack_into('<I',o,4+4*i,len(o));o+=b
    NEW[an]=bytes(o);print('atc',an[-8:],natc,'미번역',miss)
# 타입 스트림
nts=0
for f in glob.glob(os.path.join(T,'res_bk3main_rjbb.zip@bk3main_rjbb.dat@0[02]_*@0[01]_*')):
    nm=os.path.basename(f);d=leaf(nm);p=tstream.parse(d)
    if not p:continue
    ch=0
    for fl in p:
        if fl[0]==10:
            s=tstream.sval(fl[1])
            if s in TR:fl[1]=tstream.sdata(TR[s]);ch=1;nts+=1
    if ch:NEW[nm]=tstream.build(p)
print('ts',nts)
# UTF-16 제자리 교체
def put16(buf,o,jp,budget,tag):
    k=TR[jp]
    if budget is not None and len(k)>budget:errs.append('%s 길이초과 %d>%d %r'%(tag,len(k),budget,k));return False
    old=len(jp)
    b=k.encode('utf-16le')+b'\0\0'
    buf[o:o+len(b)]=b
    # 원래 문자열 잔여부분은 0으로
    end=o+2*max(old+1,len(k)+1)
    for z in range(o+len(b),end):buf[z]=0
    return True
nev=0
for f in glob.glob(os.path.join(T,'res_bk3main_rjbb.zip@bk3main_rjbb.dat@05_*')):
    nm=os.path.basename(f);d=bytearray(leaf(nm));ch=0
    for o,s,b in extract.u16_strings(bytes(d),need_kana=False):
        if s in TR and put16(d,o,s,b,'ev'):ch=1;nev+=1
    if ch:NEW[nm]=bytes(d)
nsc=0
for f in glob.glob(os.path.join(T,'res_scenario_rjbb.dat@*')):
    nm=os.path.basename(f);d=bytearray(leaf(nm));ch=0
    for o,s,b in extract.u16_strings(bytes(d),need_kana=False):
        if s in TR and put16(d,o,s,min(b,31),'scn'):ch=1;nsc+=1
    if ch:NEW[nm]=bytes(d)
print('ev',nev,'scn',nsc)
ROMFS={}

# 레이아웃
def lyt_set(d,t,b):
    hl=struct.unpack_from('<H',d,6)[0];n=struct.unpack_from('<H',d,0x10)[0];o=hl
    for i in range(n):
        sz=struct.unpack_from('<I',d,o+4)[0]
        if d[o:o+4]==b'txt1' and o+struct.unpack_from('<I',d,o+0x64)[0]==t:break
        o+=sz
    else:raise Exception('txt1')
    avail=o+sz-t
    if len(b)>avail:
        add=(len(b)-avail+3)//4*4;d[o+sz:o+sz]=b'\0'*add;sz+=add;avail+=add
        struct.pack_into('<I',d,o+4,sz);struct.pack_into('<I',d,0xc,len(d))
    d[t:t+avail]=b+b'\0'*(avail-len(b))
    mx=struct.unpack_from('<H',d,o+0x54)[0]
    struct.pack_into('<HH',d,o+0x54,max(mx,len(b)),len(b))
nly=0
for f in sorted(glob.glob(os.path.join(T,'*'))):
    nm=os.path.basename(f);d=leaf(nm)
    if d[:4]!=b'FLYT':continue
    d=bytearray(d);ch=0
    for t,mx,cl,txt,pn,fnt in sorted(lyt.txt1s(bytes(d)),reverse=True):   # 뒤에서부터: 섹션 확장 시 앞 오프셋 불변
        s=txt.rstrip('\0')
        if s in TR:
            k=TR[s];b=k.encode('utf-16le')+b'\0\0'
            lyt_set(d,t,b);ch=1;nly+=1
    if ch:NEW[nm]=bytes(d)
print('lyt',nly)

# 옵션 화면 darc(CLYT 레이아웃 + CLIM 텍스처)
import darc
OPT={'サウンド設定':'사운드 설정','ゲーム設定':'게임 설정','視点設定':'시점설정','データ管理':'데이터관리','バランス確認':'밸런스 확인',
 '日本語':'일본어','英語':'영어','REALモード':'REAL 모드','オート':'자동','なし':'없음','機体左側面視点':'좌측면 시점',
 '機体右側面視点':'우측면 시점','RWY18視点':'RWY18시점','RWY36視点':'RWY36시점','瀬長島視点':'세나가섬'}
DARC='res_bk3top.zip@bk3top.dat@03_cda3533f@01_fa9eb39e';DARC_NEW={}
_dd=leaf(DARC)
for _p,_a,_b,_i in darc.files(_dd):
    if not _p.endswith('.bclyt'):continue
    x=bytearray(_dd[_a:_a+_b]);o=struct.unpack_from('<H',x,6)[0];ch=0
    for _k in range(struct.unpack_from('<I',x,0x10)[0]):
        mg=x[o:o+4];sz=struct.unpack_from('<I',x,o+4)[0]
        if mg==b'txt1':
            ml,cl=struct.unpack_from('<HH',x,o+0x4c);t=o+struct.unpack_from('<I',x,o+0x58)[0]
            jp=x[t:t+cl].decode('utf-16le').rstrip('\0')
            if jp in OPT:
                nb=OPT[jp].encode('utf-16le')+b'\0\0'
                if len(nb)>ml:errs.append('CLYT 길이초과 %r'%OPT[jp])
                else:x[t:t+ml]=nb+bytes(ml-len(nb));struct.pack_into('<H',x,o+0x4e,len(nb));ch=1
        o+=sz
    if ch:DARC_NEW[_i]=bytes(x)
for _j,_k in OPT.items():TR.setdefault('\x01opt'+_j,_k)   # 글꼴 글자 집합용
print('darc lyt',len(DARC_NEW))
# code.bin
_c0=open(os.path.join(B,'ext','code.bin'),'rb').read()
code=bytearray(_c0 if os.environ.get('NOPATCH') else codepatch.apply(_c0));nc=0
for o,s,b in extract.code_strings(bytes(code)):
    if s in TR and put16(code,o,s,b,'code@%x'%(o+0x100000)):nc+=1
for jp in CX:
    pat=jp.encode('utf-16le')+bytes(2);o=code.find(pat);n0=0
    while o>=0:
        if o%2==0 and put16(code,o,jp,len(jp),'cx'):nc+=1;n0+=1
        o=code.find(pat,o+2)
    if not n0:errs.append('cx 없음 %r'%jp)
for jp,k in CODE_SJ.items():
    b=jp.encode('cp932')+bytes(1);o=code.find(b,0x222000-0x100000)
    assert 0<o<0x223000-0x100000,jp
    z=o+len(b)
    while code[z]==0:z+=1
    nb=sjenc(k)+bytes(1)
    if len(nb)>z-o:errs.append('codeSJ 길이초과 %r'%k);continue
    code[o:z]=nb+bytes(1)*(z-o-len(nb));nc+=1
print('code',nc)
# ---- 글꼴 ----
used=set()
for k in TR.values():used|=set(k)
used.discard('\n')
def has(ttf):
    from fontTools.ttLib import TTFont
    return set(TTFont(ttf,fontNumber=0)['cmap'].getBestCmap())
HN=has(TTF);HM=has(FALLBACK)
main=set(range(0x20,0x7f))|{ord(c) for c in used}|set(range(0xff01,0xff5f))|{0x3000,0x30fb,0x30fc,0xff5e,0x2026,0x300c,0x300d,0x300e,0x300f,0x3010,0x3011}
main0=set(main);main={c for c in main if c in HN or c in HM}
gN=kfont.render_ttf(TTF,22,sorted(c for c in main if c in HN),24,30,25,yadj=-3,hang_adv=24)
gM=kfont.render_ttf(FALLBACK,20,sorted(c for c in main if c not in HN and c in HM),24,30,25,yadj=-2,hang_adv=24)
gN.update(gM)
JPF='C:/Windows/Fonts/msgothic.ttc'
gJ=kfont.render_ttf(JPF,22,sorted(c for c in main0 if c not in gN and c in has(JPF)),24,30,25,yadj=-3,hang_adv=24)
gN.update(gJ)
miss=sorted({c for c in used if ord(c) not in gN});print('주글꼴 누락',''.join(miss))
cf,_=kfont.build(b'CFNT',gN,24,30,25,30,256,512,alias=ALIAS,height=30,width=24,ascent=25)
ROMFS[codepatch.FONT_PATH[5:]]=cf;print('CFNT',len(cf))
def small_font(orig,size,need):
    f=ffnt.read(orig);cw,chh=f['cw'],f['ch']
    im=ffnt.images(f)[0];cols=f['cols']
    def cell(i):r,c=divmod(i,cols);return im[r*(chh+1):r*(chh+1)+chh,c*(cw+1):c*(cw+1)+cw].copy()
    gl={}
    for c,i in f['cmap'].items():
        if 0x3040<=c<=0x30ff or 0x4e00<=c<=0x9fff:continue   # 일본어 글리프 제거
        gl[c]=(cell(i),f['widths'].get(i,f['dw']))
    hs=sorted({ord(c) for c in need if isH(c)})
    gg=kfont.render_ttf(GAL,size,hs,cw,chh,f['bl'],yadj=chh-9,mono=True,hang_adv=cw)
    gg={c:(im_,(l,min(w,cw-1),a_)) for c,(im_,(l,w,a_)) in gg.items()}  # 셀 오른쪽 경계 번짐 방지
    gl.update(gg)
    for c in [ord(x) for x in '・…「」『』【】⇒♪～']:
        if c not in gl and c in f['cmap']:gl[c]=(cell(f['cmap'][c]),f['widths'].get(f['cmap'][c],f['dw']))
    codes=sorted(gl);sw=f['sw']
    while True:
        cols2=sw//(cw+1);rows2=f['sh']//(chh+1)
        if cols2*rows2>=len(codes):break
        sw*=2
    out,_=kfont.build(b'FFNT',gl,cw,chh,f['bl'],f['lf'],sw,f['sh'],alias=ALIAS,ffnt_ver=struct.unpack_from('<I',orig,8)[0],height=f['h'],width=f['w'],ascent=f['asc'],dw=f['dw'],v4=True)
    return out
def S(pred):
    o=set()
    for x in items:
        k=KO.get(str(x['id']))
        if k and any(pred(src,x['id']) for src in x['src']):o|=set(k)
    return o
ALLC=set(''.join(TR.values()))
NEED={h:ALLC for h in ('9fc4e27e','01c534d6','374564f2','1ed49181')}
FF={}
for nm in glob.glob(os.path.join(T,'*')):
    b=os.path.basename(nm)
    h=b.rsplit('@',1)[-1]
    if h in ('9fc4e27e','01c534d6','374564f2','1ed49181') and h not in os.environ.get('SKIPFF',''):
        if h not in FF:FF[h]=small_font(leaf(b),10,NEED[h])
        NEW[b]=FF[h]
print('FFNT',{k:len(v) for k,v in FF.items()})
# ---- 컨테이너 재구성 ----
import kimg
KI={} if os.environ.get('NOKIMG') else kimg.make(T,leaf);NEW.update(KI);print('텍스처',len(KI))
import kimg2,clim
for _p,_a,_b,_i in darc.files(_dd):
    if _i in kimg2.CSPEC:
        x=_dd[_a:_a+_b];DARC_NEW[_i]=clim.encode(x,kimg.render(x,kimg2.CSPEC[_i],clim.decode(x)[0]))
if DARC_NEW:NEW[DARC]=darc.build(_dd,DARC_NEW);print('darc',len(DARC_NEW))
if os.environ.get('NEWF'):
    _f=os.environ['NEWF'].split(',');NEW={k:v for k,v in NEW.items() if any(s in k for s in _f)}
print('NEW',[k for k in NEW if 'bk3top' in k])
def rebuild(d,path):
    """원본 바이트 d(경로 path)를 하위 교체 반영하여 재구성. 변경 없으면 None"""
    if d[:4]==b'PK\x03\x04':
        z=zipfile.ZipFile(io.BytesIO(d));ch=False;outs=[]
        for inf in z.infolist():
            x=z.read(inf.filename);y=rebuild(x,path+'@'+inf.filename.replace('/','_'))
            if y is not None:ch=True;x=y
            outs.append((inf,x))
        if not ch:return None
        bio=io.BytesIO();zo=zipfile.ZipFile(bio,'w',zipfile.ZIP_DEFLATED)
        for inf,x in outs:
            ni=zipfile.ZipInfo(inf.filename,inf.date_time);ni.compress_type=zipfile.ZIP_DEFLATED;ni.external_attr=inf.external_attr
            zo.writestr(ni,x)
        zo.close();r=bio.getvalue()
        if len(r)>len(d):   # 게임이 압축본 크기 한도를 가짐 → 원본보다 커지면 zopfli로 재압축
            import zipw;r=zipw.build(d,{inf.filename:x for inf,x in outs});print('zopfli',path,len(r),len(d))
            if len(r)>len(d):r=zipw.build(d,{inf.filename:x for inf,x in outs},it=30);print(' zopfli x30',len(r))
            if len(r)>len(d):errs.append('zip 크기 초과 %s %d>%d'%(path,len(r),len(d)))
        return r
    if d[:4]==b'SARC':
        new={}
        for i,((nm,s,e),(_,s2,e2)) in enumerate(zip(sarc.parse(d),sarcw.files(d))):
            y=rebuild(d[s:e],path+'@'+nm.replace('/','_'))
            if y is not None:new[i]=y
        return sarcw.build(d,new) if new else None
    if d[:1]==b'\x11' and path.endswith('_LZ.bin'):
        y=rebuild(lz11.dec(d),path+'@lz');return lz11.enc_raw(y) if y is not None else None
    if ispak(d):
        its=pak.unpack(d);ch=False;out=[]
        for i,(h,b) in enumerate(its):
            y=rebuild(b,path+'@%02d_%08x'%(i,h))
            if y is not None:ch=True;b=y
            out.append((h,b))
        return pak.pack(out,d) if ch else None
    return NEW.get(path)
for dp,dn,fs in os.walk(R):
    for f in fs:
        p=os.path.relpath(os.path.join(dp,f),R).replace(os.sep,'/')
        if p.startswith(('voice/','movie/','sound/')) or p in ROMFS:continue
        y=rebuild(open(os.path.join(R,p),'rb').read(),p.replace('/','_'))
        if y is not None:ROMFS[p]=y
print('romfs 교체',sorted(ROMFS))
if errs:
    print('오류',len(errs));print('\n'.join(errs))
    if '--force' not in sys.argv:sys.exit(1)
MV=os.path.join(B,'mov','OP_ko.moflex')
if os.path.exists(MV):ROMFS['movie/OP.moflex']=open(MV,'rb').read();print('movie OP')
if os.environ.get('DUMP'):
    import pickle;pickle.dump((ROMFS,bytes(code),NEW),open(os.path.join(B,'romfs.pkl'),'wb'))
# HOME 메뉴 제목(SMDH: exefs icon, romfs banner.icn)
def smdh(d):
    d=bytearray(d)
    for i in (0,1,7):
        o=8+0x200*i
        for a,n,t in ((0,0x80,'나는 항공관제관 칸쿠 ALL STARS'),(0x80,0x100,'나는 항공관제관 에어포트\n히어로3D 칸쿠 ALL STARS'),(0x180,0x80,'Sonic Powered')):
            b=t.encode('utf-16le');d[o+a:o+a+n]=b+bytes(n-len(b))
    return bytes(d)
ROMFS['banner.icn']=smdh(open(os.path.join(R,'banner.icn'),'rb').read())
ICON=smdh(open(os.path.join(B,'ext','exefs','icon'),'rb').read())
build.build(ROM,OUT,ROMFS,bytes(code),newicon=ICON)
print('완료',OUT)
