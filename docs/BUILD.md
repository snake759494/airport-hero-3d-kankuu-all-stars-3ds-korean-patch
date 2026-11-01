# 빌드 방법

번역 대본·원문·그림 편집 명세·무비 합성 스크립트는 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 `Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Japan).3ds` (MD5 `adc02c89a841064cfb9653b4b788fd72`)
- Python 3.12+ : `pip install pillow numpy opencv-python-headless fontTools zopfli`
- .NET SDK: `tools/ocr`(Windows 일본어 OCR, 그림 글자 검출용, 선택)
- 글꼴 `NanumSquareNeo-*.ttf`, `Galmuri9.ttf`

## 폴더 구성
```
<작업 폴더>/                원본 .3ds, 글꼴
  <이 저장소>/
    tools/
    ext/                    추출물 (code.bin, exefs, romfs)
    dec/tree/               팩을 풀어 둔 리프 파일
    tr/items.json           원문 목록 {id, jp, src, max}
    tr/ko/*.json            번역 {id: 한국어}
    tr/code_extra.json      실행 코드 추가 문자열 {일본어: 한국어}
    tr/atc_seg.json         영어판 ATC 파일의 일본어 구간 번역 {일본어: 한국어}
    tr/tex_idx.json         텍스처 해시 색인 (tools/mkidx.py)
    tools/kimg.py, kimg2.py 그림 글자 편집 명세 (직접 작성)
    mov/OP_ko.moflex        한글화한 오프닝 무비 (선택)
```

## 순서
1. 추출: `python tools/ctr.py "<원본>.3ds" ext`, `python tools/codeblz.py`, `python tools/walk.py`로 zip·팩·SARC·LZ11 풀기
2. 원문 목록: `python tools/extract.py` → `tr/items.json`. 번역은 `tr/ko/*.json`에 작성
3. 그림 글자: `python tools/mkidx.py`로 해시 색인, `tools/dumptex.py`로 PNG 확인 후 `kimg.py`/`kimg2.py`에 `SPEC = {해시: [지우기·글자 그리기 명령]}` 작성. 옵션 화면 darc 안의 CLIM은 `kimg2.CSPEC = {darc 엔트리 번호: 명령}`
4. 무비(선택): 영상 스트림 프레임 디코드 → 로고·자막 영역 교체 프레임 생성 → 해당 구간 재인코딩 → `python tools/movbuild.py 원본.moflex tc.pkts mov/OP_ko.moflex`
5. 빌드: `python tools/kbuild.py` → `...(Korean).3ds`
6. 차분: `xdelta3 -e -0 -S none -A -s 원본.3ds 한글.3ds 패치.xdelta` (압축 옵션 없이)
