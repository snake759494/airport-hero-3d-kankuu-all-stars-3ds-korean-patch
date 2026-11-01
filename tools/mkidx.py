# BFLIM 리프의 MD5 -> 리프 이름 목록 (kimg 사본 일괄 교체용)
import os,json,hashlib
B=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..');T=os.path.join(B,'dec','tree');idx={}
for n in sorted(os.listdir(T)):
    d=open(os.path.join(T,n),'rb').read()
    if len(d)>0x28 and b'FLIM' in d[-0x28:]:idx.setdefault(hashlib.md5(d).hexdigest(),[]).append(n)
json.dump(idx,open(os.path.join(B,'tr','tex_idx.json'),'w'),indent=0);print(len(idx))
