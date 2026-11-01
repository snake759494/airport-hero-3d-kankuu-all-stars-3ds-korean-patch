import glob,re,os,sys,collections
def jp(s): return sum(1 for c in s if '぀'<=c<='ヿ' or '一'<=c<='鿿')
res=collections.defaultdict(lambda:[0,0,0])
files=['ext/code.bin']+glob.glob('dec/tree/*')+glob.glob('ext/romfs/res/db/*')
for f in files:
    d=open(f,'rb').read()
    if d[:4]==b'\x1bLua':
        continue
    # utf16
    for m in re.finditer(rb'(?:(?:[\x00-\xff][\x30\x4e-\x9f\xff\x20]|[\x20-\x7e]\x00)){2,}',d):
        if m.start()%2: continue
        s=m.group().decode('utf-16le','ignore')
        if jp(s)>=1: r=res[f];r[0]+=1;r[1]+=len(s)
    for m in re.finditer(rb'(?:[\x81-\x9f\xe0-\xef][\x40-\xfc]|[\x20-\x7e]){3,}',d):
        try: s=m.group().decode('shift_jis')
        except: continue
        if jp(s)>=2: res[f][2]+=1
for f,v in sorted(res.items(),key=lambda x:-x[1][1]): print(v,f)
