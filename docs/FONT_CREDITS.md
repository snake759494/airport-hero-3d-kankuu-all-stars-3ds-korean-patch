# 글꼴

| 용도 | 글꼴 | 비고 |
| --- | --- | --- |
| 게임 본문 폰트(CFNT, 24×30 칸) | 나눔스퀘어네오 Bold, 22px | 원본 고딕과 가장 비슷함 |
| 작은 비트맵 폰트 4종(관제 표·정보창·썸네일·QR) | Galmuri9 | 아주 작은 글자용 |
| 그림 글자(로고·메뉴·UI)·무비 | 나눔스퀘어네오 Heavy / ExtraBold / Bold | 원본 색·외곽선에 맞춰 렌더링 |

- 나눔스퀘어네오: 네이버 — 나눔글꼴 라이선스
- Galmuri: quiple — SIL Open Font License 1.1

글꼴 파일은 저장소에 포함하지 않습니다. 빌드하려면 저장소 상위 작업 폴더에 `NanumSquareNeo-*.ttf`를 두고, Galmuri9.ttf 경로를 `tools/kbuild.py`의 `GAL`에 지정하세요.
