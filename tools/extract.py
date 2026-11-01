# 모든 텍스트 원천에서 일본어 문자열을 모아 tr/items.json 생성 (원문 -> 정보)
import os,sys,glob,re,json,struct,collections
sys.path.insert(0,os.path.dirname(__file__))
import luac,tstream,lyt
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
T=os.path.join(B,'dec','tree')
J=re.compile('[぀-ヿ一-鿿]')
KANA=re.compile(r'[ぁ-ー、。！？]')
items=collections.OrderedDict()
def add(jp,src,budget=None):
    it=items.setdefault(jp,{'src':[],'max':None})
    if src not in it['src']:it['src'].append(src)
    if budget is not None:it['max']=budget if it['max'] is None else min(it['max'],budget)
NUM=re.compile(r'\d[\d,]*')
def templ(s):return NUM.sub('#',s)
# --- UTF-16 제자리 문자열 (NUL 종료, 뒤 0 영역까지 사용 가능) ---
def u16_strings(d,start=0,end=None,need_kana=True,cap=None):
    end=end or len(d);n=(end-start)//2
    arr=struct.unpack_from('<%dH'%n,d,start);out=[];s0=0
    for k,c in enumerate(arr):
        if c==0:
            if k>s0:
                s=''.join(map(chr,arr[s0:k]))
                if ok16(s) and (KANA.search(s) if need_kana else J.search(s)):
                    z=k
                    while z<n and arr[z]==0:z+=1
                    budget=z-s0-1
                    if cap:budget=min(budget,cap)
                    out.append((start+s0*2,s,budget))
            s0=k+1
    return out
def ok16(s):
    return all(c=='\n' or 0x20<=ord(c)<0x7f or 0x3000<=ord(c)<=0x30ff or 0x4e00<=ord(c)<=0x9fff or 0xff00<=ord(c)<=0xffef or 0x2010<=ord(c)<=0x266f or c in '×÷°' for c in s)
def junk(c):
    o=ord(c);return (0x3400<=o<=0x9fff and 0x20<=(o&255)<0x7f and 0x20<=(o>>8)<0x7f) or o<0x80
def clean(o,s,b):
    i=0
    while i<len(s) and junk(s[i]):i+=1
    if i and i<len(s) and any(ord(c)<0x80 for c in s[:i]) and any(ord(c)>=0x3400 for c in s[:i]):return o+2*i,s[i:],b-i
    return o,s,b
def code_strings(code):
    out=[]
    for o,s,b in u16_strings(code):
        o,s,b=clean(o,s,b)
        real=[c for c in s if (0x3040<=ord(c)<=0x9fff) and not junk(c)]
        if len(real)<2 or 'rom:' in s or sum(junk(c) for c in s if ord(c)>=0x3400)*2>len(s):continue
        out.append((o,s,b))
    good=set(''.join(s for _,s,_ in out))
    for o,s,b in u16_strings(code,need_kana=False):
        if not KANA.search(s) and len(s)>=2 and all(c in good for c in s) and all(0x4e00<=ord(c)<=0x9fff for c in s):out.append((o,s,b))
    # 코드 영역 오검출 제거: 실제 문자열은 rodata(0x1fe5b4 이후) 또는 짝수 정렬 연속 구간
    return sorted(out)
def main():
    code=open(os.path.join(B,'ext','code.bin'),'rb').read()
    cs=code_strings(code)
    for o,s,b in cs:add(s,'code@%x'%(o+0x100000),min(b,len(s)+ (b-len(s))))
    # Lua
    for f in sorted(glob.glob(os.path.join(T,'script_*'))):
        d=open(f,'rb').read()
        if d[:4]!=b'\x1bLua':continue
        h,fn=luac.parse(d)
        for p,s in luac.strings(fn):
            if any(x>=0x80 for x in s):add(s.decode('cp932'),'lua:'+os.path.basename(f))
    # ATC 자막(SJIS)
    for nm,lang in (('01_cc9ed639','en'),('02_cc9edb3e','ja')):
        if lang!='ja':continue
        d=open(os.path.join(T,'res_bk3main_rjbb.zip@bk3main_rjbb.dat@01_2ed7d5c5@'+nm),'rb').read()
        n=struct.unpack_from('<I',d,0)[0];offs=[struct.unpack_from('<I',d,4+4*i)[0] for i in range(n)]+[len(d)]
        for i in range(n):
            s=d[offs[i]+4:offs[i+1]].split(b'\0')[0].decode('cp932')
            if J.search(s):add(templ(s),'atc')
    # 타입 스트림(공항명, 카메라 위치)
    for f in glob.glob(os.path.join(T,'res_bk3main_rjbb.zip@bk3main_rjbb.dat@0[02]_*@0[01]_*')):
        d=open(f,'rb').read();p=tstream.parse(d)
        if not p:continue
        for t,x in p:
            if t==10:
                s=tstream.sval(x)
                if J.search(s):add(s,'ts:'+os.path.basename(f))
    # 이벤트 메시지(고정 버퍼)
    for f in glob.glob(os.path.join(T,'res_bk3main_rjbb.zip@bk3main_rjbb.dat@05_*')):
        d=open(f,'rb').read()
        for o,s,b in u16_strings(d,need_kana=False):add(s,'ev',b)
    # 시나리오 제목
    for f in glob.glob(os.path.join(T,'res_scenario_rjbb.dat@*')):
        d=open(f,'rb').read()
        for o,s,b in u16_strings(d,need_kana=False):add(s,'scn',min(b,31))
    # 갤러리
    # 레이아웃 기본 문자열
    for f in sorted(glob.glob(os.path.join(T,'*'))):
        d=open(f,'rb').read()
        if d[:4]!=b'FLYT':continue
        for t,mx,cl,txt,pn,fnt in lyt.txt1s(d):
            txt=txt.rstrip('\0')
            if J.search(txt):add(txt,'lyt:'+fnt,mx//2-1)
    out=[{'id':i,'jp':k,**v} for i,(k,v) in enumerate(items.items())]
    os.makedirs(os.path.join(B,'tr'),exist_ok=True)
    json.dump(out,open(os.path.join(B,'tr','items.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
    c=collections.Counter(x['src'][0].split(':')[0].split('@')[0] for x in out)
    print(len(out),sum(len(x['jp']) for x in out),c)
if __name__=='__main__':main()
