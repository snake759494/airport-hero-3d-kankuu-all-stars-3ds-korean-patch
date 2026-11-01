# 기술 문서

## 롬 구조
- 복호화된 CCI → NCCH → ExeFS(`.code`, BLZ 압축, `icon`) + RomFS. `tools/ctr.py`, `tools/codeblz.py`, `tools/build.py`가 추출·재조립을 맡습니다.
- 대부분의 데이터는 RomFS `res/*.zip`(내부 `.dat` 팩) 안에 있고, 팩은 다시 SARC·LZ11 압축·darc·BFLIM/CLIM 텍스처·BCLYT/CLYT 레이아웃으로 이루어집니다(`tools/pak.py`, `sarc.py`, `sarcw.py`, `lz11.py`, `darc.py`, `lyt.py`, `walk.py`).
- 게임은 `res/*.zip` 크기가 원본보다 커지면 무한 로딩에 빠집니다. 재압축 결과가 원본보다 크면 zopfli로 원본 이하가 되도록 다시 압축합니다(`zipw.py`).

## 텍스트 원천
| 원천 | 형식 | 처리 |
| --- | --- | --- |
| 관제 교신(ATC, 일본어판·영어판 파일) | Shift-JIS | 한글은 SJIS 1수준 한자 코드를 대리 글자로 쓰고 폰트 별칭(alias)으로 한글 글리프에 연결. 영어판 파일에 섞인 일본어 교신은 구간 단위로 번역 |
| 실행 코드(code.bin) | UTF-16LE / Shift-JIS | 원래 길이 안에서 제자리 교체(`codepatch.py`, `extract.py`) |
| 레이아웃(BFLYT) | UTF-16LE | `lyt.py`로 텍스트 박스 교체(길이 확장 가능) |
| 옵션 화면 레이아웃(darc 안 CLYT) | UTF-16LE | 텍스트 박스 최대 길이 안에서 교체 |
| 이벤트·시나리오·타입 스트림 | UTF-16LE 고정 버퍼/전용 형식 | `tstream.py` 등 |
| HOME 메뉴 제목 | SMDH | ExeFS `icon`과 RomFS `banner.icn`의 제목 교체 |

## 글꼴
- 본문은 게임이 읽는 CFNT를 새로 만들어 RomFS에 넣고, 실행 코드를 고쳐 이 폰트를 불러오게 합니다(`kfont.py`, `codepatch.py`).
- 작은 FFNT 4종은 일본어 글리프를 지우고 필요한 한글만 Galmuri9로 채웁니다.

## 그림 글자
- BFLIM/CLIM(주로 ETC1A4/RGBA) 텍스처를 풀어 원본 글자를 지우고(투명 비우기·행 단위 배경 복원·inpaint) 한글을 렌더링한 뒤 다시 인코딩합니다(`texpatch.py`, `clim.py`, `etc1enc.py`, `koimg.py`).
- 같은 그림이 여러 팩에 사본으로 들어 있어 해시 색인으로 모든 사본을 함께 바꿉니다.
- 타이틀 로고는 카타카나 글자 영역을 로고 바탕색으로 채운 뒤 한글 로고 글자를 얹었습니다.

## 오프닝 무비
- `movie/OP.moflex`(MobiClip, 400×240)의 영상 스트림을 프레임 단위로 풀어, 타이틀 로고는 기준 프레임에서 만든 차이를 프레임별 불투명도에 맞춰 더하고, 「羽田空港」 자막은 프레임마다 지운 뒤(inpaint) 한글을 같은 불투명도로 합성했습니다. 해당 구간(0~620프레임)만 재인코딩해 다시 묶습니다(`moflex.py`, `mux.py`, `movbuild.py`). 디코더·인코더는 별도 MobiClip 도구를 씁니다(미포함).
