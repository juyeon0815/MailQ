# 📬 MailQ: AI 기반 메일 요약 및 검색 도우미

**MailQ**는 Microsoft Teams와 Outlook을 연동하여, 사용자가 Teams에서 질문을 입력하면 해당 날의 메일을 요약하거나 원하는 메일을 의미 기반으로 검색해주는 AI 메일 도우미입니다.

> 수십 통의 업무 메일, 이제 직접 정리하지 마세요.  
> MailQ가 알아서 요약하고, 의미로 검색해드립니다.

---

## 🚀 주요 기능

### 1. 📌 메일 요약
- Microsoft Graph API를 통해 Outlook에서 메일을 수신
- OpenAI 기반 LLM으로 메일 내용을 분석 후, 업무용/참고용으로 자동 분류
- 요약된 제목, 내용, 해야 할 일(To-do), 메일 링크를 함께 제공

### 2. 🔍 메일 검색
- 사용자의 질문 의도 파악 → 검색 쿼리 생성
- Azure AI Search에서 의미 기반 검색 수행
- 관련 메일을 의미 정합성 기준으로 필터링
- 최종 요약 결과를 Teams 채팅으로 응답

---

## 🛠️ 기술 스택

| 항목 | 내용 |
|------|------|
| **Frontend** | Microsoft Teams (Bot Framework, Adaptive Card) |
| **Backend** | Python, Flask (Azure Web App 호스팅) |
| **Authentication** | Microsoft OAuth2 (Delegated Access) |
| **Email API** | Microsoft Graph API (Outlook 메일 연동) |
| **LLM 요약** | OpenAI GPT 모델 |
| **의미 검색** | Azure Cognitive Search |
| **파일 저장소** | Azure Blob Storage |

---

## 🔄 사용 흐름

1. **사용자 질문 입력**  
   Teams에서 `MailQ` 봇에게 질문 (예: "오늘 메일 요약해줘", "cus 오류 관련 메일 찾아줘")

2. **요청 라우팅 및 처리**
   - 요청을 Flask 서버에서 수신
   - 요약 or 검색 판단 및 각 처리 모듈로 분기

3. **요약 흐름**
   - Outlook에서 메일 가져오기 → Blob에 저장 → LLM 요약
   - 중요도에 따라 자동 분류된 요약 결과 응답

4. **검색 흐름**
   - 질문 의도 파악 → 검색 쿼리 생성 → Azure Search 검색
   - 검색 결과 검증 후 요약 응답

5. **응답 전달**  
   Adaptive Card 형식으로 Teams 채팅창에 요약 or 검색 결과 표시

---

## 📂 디렉토리 구조

```
BOT_APP/
│
├── bot/                        # Teams Bot 엔트리 포인트 및 라우팅
│   ├── main_bot.py             # 봇 초기화 및 앱 등록
│   └── teams_bot.py            # Teams 메시지 핸들러
│
├── core/                       # 핵심 기능 로직 (메일 수집, 요약, 검색 등)
│   ├── mail_fetcher.py         # Graph API 통해 Outlook 메일 수신
│   ├── mail_summarizer.py      # GPT 기반 메일 요약 처리
│   ├── mail_searcher.py        # Azure Search 연동 의미 기반 검색
│   └── mail_uploader.py        # 메일을 Blob Storage에 업로드
│
├── handler/                    # 요청별 핸들링 레이어
│   ├── summary_handler.py      # 요약 요청 처리기
│   └── search_handler.py       # 검색 요청 처리기
│
├── util/                       # 유틸리티 함수/모듈
│   ├── graph_helper.py         # Microsoft Graph API 유틸 함수
│   ├── llm_helper.py           # OpenAI LLM 호출 모듈
│   └── token_helper.py         # 사용자 access_token 저장 및 관리
│
├── .deployment                 # Azure Web App 배포 설정 파일
├── .env                        # 환경 변수 (.env 파일로 관리)
├── app.py                      # Flask 진입점 및 라우팅
├── requirements.txt            # Python 의존성 목록
├── startup.sh                  # Azure Web App 실행 스크립트
└── README.md                   # 프로젝트 설명 문서
```

---

## 🔮 향후 확장 방향

- 메일 기반 일정 자동 등록
- 메일 유형별 자동 라벨링
- 누적 데이터 기반 업무 분석 및 통계 시각화

---

## 📧 문의

궁금한 점이나 협업 제안은 [email@example.com](mailto:email@example.com) 으로 연락 주세요.