import glob,re,os,sys
R=re.compile(r'[　-ヿ一-鿿！-ﾟ -~\n‐-‰←-⇿■-⛿]{2,}')
J=re.compile(r'[぀-ヿ一-鿿]')
def strs(d):
    out=[]
    for al in (0,):
        s=d[al:len(d)-((len(d)-al)%2)].decode('utf-16le','replace')
        for m in R.finditer(s):
            t=m.group()
            if len(J.findall(t))>=2 and len(J.findall(t))>=len(t)*0.3: out.append((al+m.start()*2,t))
    return out
files=['ext/code.bin']+glob.glob('dec/tree/*')+glob.glob('ext/romfs/res/db/*')
res=[]
for f in files:
    d=open(f,'rb').read()
    if d[:4]==b'\x1bLua' or d[-0x28:-0x24]==b'FLIM' or d[:4] in (b'CGFX',b'FFNT',b'CTPK'):continue
    s=strs(d)
    if s: res.append((sum(len(x) for _,x in s),len(s),f,s))
res.sort(key=lambda x:-x[0])
for c,n,f,s in res: print(c,n,f[-55:],'|',' / '.join(x for _,x in s[:5])[:160].replace('\n','⏎'))
print(len(res),sum(r[0] for r in res))
