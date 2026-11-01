# romfs.pkl 중 일부만 반영한 테스트 롬: python bis.py out.3ds key1,key2 [code]
import sys,os,pickle
sys.path.insert(0,os.path.dirname(__file__));import build
R,c,*_=pickle.load(open('romfs.pkl','rb'))
ks=[k for k in R if any(s in k for s in sys.argv[2].split(','))] if sys.argv[2]!='-' else []
print(ks)
build.build('../Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Japan).3ds',sys.argv[1],{k:R[k] for k in ks},c if 'code' in sys.argv[3:] else None)
