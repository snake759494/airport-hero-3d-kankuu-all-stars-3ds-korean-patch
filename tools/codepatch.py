# code.bin 패치 (비압축 코드, VA = 0x100000 + 오프셋)
import keystone,struct
B=0x100000
ks=keystone.Ks(keystone.KS_ARCH_ARM,keystone.KS_MODE_ARM)
def asm(src,va):return bytes(ks.asm(src,va)[0])
FONT_PATH='rom:/image/blyt/operation_t_stageimg.bclyt'  # 쓰이지 않는 BCLIM 자리에 글꼴 저장
def font_patch(c):
    # 공유 폰트(APT GetSharedFont) 대신 RomFS의 한글 CFNT를 같은 할당자로 읽어 ResFont에 설정
    o=0x113a20-B
    assert c[o:o+4]==bytes.fromhex('94108fe2'),c[o:o+4].hex()
    # 경로로 읽은 뒤 리소스 이름을 원래 'CFontResource::SharedRead'로 되돌려 이름 검색이 계속 동작하게 함
    code=asm('add r1,pc,#0x24; bl 0x250590; ldr r0,[r4,#0x28]; add r2,pc,#0x88; mov r1,#26; mov r3,#25; bl 0x24266c;'
             'ldr r1,[r4,#0x20]; add r0,r4,#0x40; bl 0x245104; b 0x113aac',0x113a20)
    assert len(code)==0x2c
    c[o:o+len(code)]=code
    p=(FONT_PATH+chr(0)).encode('utf-16le');po=0x113a4c-B
    assert po+len(p)<=0x113aac-B
    c[po:po+len(p)]=p
def apply(code):
    c=bytearray(code);font_patch(c);return bytes(c)
