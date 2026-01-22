# Backlog: 이미지 생성 프롬프트 개선

## [Gemini Imagen 프롬프트 품질 향상]

### Completed Tasks

- [x] Task: 그림체별 프롬프트 상세화
- [x] Description: anime/realistic/watercolor 각 스타일의 명확한 구분
- [x] Changes:
  - anime: Pixiv 스타일, 셀셰이딩, 비주얼노벨 CG 품질 강조
  - realistic: photorealistic, Canon 85mm 렌즈, 잡지 표지 품질 강조
  - watercolor: 전통 수채화 종이 질감, 물번짐 효과 강조
  - 각 스타일에 avoid 지시 추가 (다른 스타일 특징 금지)

- [x] Task: 캐릭터 디자인 상세화
- [x] Description: 5가지 성격별 캐릭터 외모 디테일 강화
- [x] Changes:
  - 머리카락 질감, 광택 묘사 추가
  - 피부, 얼굴 특징 더 상세하게
  - 전체적으로 더 매력적인 외모 묘사

- [x] Task: 표정 묘사 개선
- [x] Description: 6가지 표정의 시각적 표현 강화
- [x] Changes:
  - 각 표정이 더 생생하고 매력적으로
  - 눈 표현, 볼 홍조 등 디테일 추가
  - excited(설렘) 표정: 놀란 느낌 -> 부끄러움+설렘 느낌으로 변경

- [x] Task: 동양인 특징 추가
- [x] Description: 캐릭터가 한국/일본인처럼 보이도록 수정
- [x] Changes:
  - gender_word에 "East Asian, Korean or Japanese" 명시
  - 캐릭터 디자인에 Asian features, K-fashion, K-drama 스타일 추가
  - 프롬프트에 CRITICAL ETHNICITY REQUIREMENT 섹션 추가
  - Western/Caucasian features 금지 명시

### Files Changed
- app/services/gemini_service.py
  - get_character_design(): 동양인 특징 포함 캐릭터 디자인
  - build_expression_prompt(): 상세한 프롬프트 생성
  - art_style_details: 그림체별 상세 설명 및 avoid 항목
  - expression_details: 표정별 상세 설명

### Expected Results
- 애니메이션 스타일: Pixiv/비주얼노벨 품질의 애니메이션 그림체
- 실사화 스타일: 실제 사람처럼 보이는 포토리얼 이미지
- 수채화 스타일: 전통 수채화 느낌의 아트워크
- 모든 스타일에서 동양인(한국/일본인) 외모
