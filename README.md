# 나는 항공관제관 에어포트 히어로 3D 칸쿠 ALL STARS (3DS) 비공식 한글패치

닌텐도 3DS 일본판 **ぼくは航空管制官 エアポートヒーロー3D 関空 ALL STARS** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 릴리즈 파일
| 파일 | 용도 |
| --- | --- |
| `AirportHero3D_KankuuAllStars_3DS_KO_v1.0.xdelta` | 본편 패치 — 복호화된 카트리지 덤프(`.cci`/`.3ds`)용 |

## 적용 방법 (에뮬레이터)
1. 아래 해시와 일치하는 **원본 덤프**(복호화된 카트리지 덤프, 256MB)를 준비합니다. CIA나 암호화된 덤프에는 적용할 수 없습니다.
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.$J'`
2. xdeltaUI 등으로 원본에 xdelta를 적용합니다.
   - 명령줄: `xdelta3 -d -s "Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Japan).3ds" AirportHero3D_KankuuAllStars_3DS_KO_v1.0.xdelta "Boku wa Koukuu Kanseikan - Airport Hero 3D - Kankuu All Stars (Korean).3ds"`
3. 만들어진 `.3ds`를 Azahar 등 3DS 에뮬레이터에서 실행합니다.

> 3DS 실기에서는 확인하지 않았습니다.

## 해시
| 항목 | 값 |
| --- | --- |
| 원본 크기 | 268,435,456 바이트 |
| 원본 MD5 | `adc02c89a841064cfb9653b4b788fd72` |
| 원본 SHA-256 | `33d07f7c58938e07478b7cbe66092b63d6dd38e3e518afbaf7e36ad50d4cb219` |
| 결과 3DS 크기 / SHA-256 | 144,146,432 바이트 / `7aa1c14d91a19b2419a058357dc4d2ae412b637a7f7984929643fc421ad88ec3` |

릴리즈 첨부 파일의 SHA-256은 [release_manifest.json](release_manifest.json)에 있습니다.

## 한글화 내용
- 관제 무선 교신(ATC, 일본어·영어 설정 모두), 튜토리얼, 메뉴·옵션·시스템 메시지, 카드·가챠·스테이지 정보, 이벤트 메시지 등 텍스트 약 1,000종과 실행 코드 속 문자열
- 오프닝 무비: 타이틀 로고(「나는 항공관제관 / 에어포트 히어로 / 하네다」)와 「羽田空港」 자막을 한글로 교체(해당 구간 재인코딩)
- 그림 글자: 타이틀 로고(「나는 항공관제관 / 에어포트 히어로 / 칸쿠」, 3D·ALL STARS는 원본 유지), 메인 메뉴·버튼, 관제 명령 버튼, 옵션 화면, 카드·코인·가챠 화면, 결과 화면, 위치 이름표 등
- HOME 메뉴 제목(SMDH)
- 글꼴: 본문 폰트(나눔스퀘어네오 Bold), 작은 비트맵 폰트 4종(Galmuri9)

## 그대로 둔 것
- 엔딩 무비(제작진 크레딧)
- 공항 코드·항공 용어 등 영어 표기(RUNWAY, ILS, 경로 이름 등)
- 게임 중 나오지 않는 디버그·개발용 데이터

## 검증 범위
Azahar 계열 에뮬레이터에서 부팅, 타이틀·메인 메뉴, 옵션 화면(사운드·게임·시점 설정)을 확인했고, 오프닝 무비는 재인코딩 프레임을 디코드해 확인했습니다. 전체 플레이 검증은 하지 않았습니다. 문제를 발견하면 Issues에 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
