from util.llm_helper import generate_response
import os
from dotenv import load_dotenv
import requests
import json
import urllib

load_dotenv()

ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
INEDX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")



# 1️⃣ 사용자 입력을 검색 쿼리로 리라이팅
def rewrite_user_query(user_input: str) -> str:

    print(f"🔍 사용자 입력을 검색 쿼리로 리라이팅!!: {user_input}")

    prompt = f"""
    A user has entered the following message to an email search assistant:
    "{user_input}"

    Your task is to understand the user's true intent and rewrite this message into a **concise, keyword-based Korean query** that is optimized for semantic email search.

    ✳️ Instructions:
    - Focus on extracting meaningful information such as people, dates, topics, and keywords.
    - Remove unnecessary grammar or conversational phrasing.
    - Output **only a single Korean sentence** with no extra commentary or explanation.
    - Do not translate the user’s message. Just output the refined search intent in Korean.
    """
    return generate_response(prompt, user_input).strip()


# 2️⃣ Azure AI Search 호출
def search_emails_from_index(search_text: str, user_email: str, top_k: int = 5) -> list[dict]:
    """
    Azure AI Search에서 의미 기반 이메일 검색을 수행합니다.
    """

    print(f"🔍 Azure AI Search 호출: {search_text} (top_k={top_k})")


    url = f"{ENDPOINT}/indexes/{INEDX_NAME}/docs/search?api-version=2023-07-01-Preview"

    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    body = {
        "search": search_text,
        "top": top_k,
        "queryType": "semantic",
        "semanticConfiguration": "default",
        "queryLanguage": "ko",
        "filter": f"user_email eq '{user_email}'"
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json().get("value", [])


# 3️⃣ 검색 결과를 의미 정합성 필터링
def filter_results_by_relevance(user_input: str, raw_results: list[dict]) -> list[dict]:

    print(" 3️⃣ 검색 결과를 의미 정합성 필터링")

    entries = "\n\n".join(
        [f"[{i+1}] 제목: {item.get('subject','')}\n내용: {item.get('content','')[:300]}"
         for i, item in enumerate(raw_results)]
    )

    prompt = f"""
    사용자 질문: "{user_input}"

    다음은 Azure AI Search에서 검색된 이메일 목록입니다. 각 이메일은 제목, 발신자, 수신자, 날짜, 본문 내용 등을 포함합니다.
    이 이메일들이 사용자 입력과 얼마나 관련이 있는지 평가하고,
    중요도 순으로 최대 3개까지만 반환하고, 해당 번호 리스트로 출력해주세요 (예: [1, 3])
    각 이메일의 중요도를 평가할 때는 다음 기준을 고려하세요:
    - 사용자 입력과의 관련성
    - 이메일의 발신자와 수신자
    - 날짜의 중요성 (최근 메일 우선)
    - 본문 내용의 유용성
    만약 관련성이 낮은 이메일이 있다면, 해당 이메일은 제외하고 중요도가 높은 이메일만 반환해주세요.

    {entries}

    """

    response = generate_response(prompt, json.dumps(raw_results))
    
    # ⚠️ "결과: [1, 2]" 같은 문자열일 수 있음
    try:
        indices = eval(response) if isinstance(response, str) else response
        if not isinstance(indices, list):
            indices = []
    except:
        indices = []

    return [raw_results[i - 1] for i in indices if 0 <= i - 1 < len(raw_results)]

# 4️⃣ 포맷 변환
def format_search_results_as_links(filtered_results: list[dict]) -> str:
    
    lines = []

    for item in filtered_results:
        subject = item.get("subject", "제목 없음").strip()
        message_id = item.get("id")

        if message_id:
            encoded_id = urllib.parse.quote_plus(message_id)
            link = f"https://outlook.office.com/mail/deeplink/read/{encoded_id}"
            lines.append(f"- [{subject}]({link})")
        else:
            lines.append(f"- {subject}")

    result = "\n".join(lines)

    return (
        "🔎 **다음은 검색한 결과입니다:**\n\n"
        f"{result}\n\n"
        "📮 **찾고 있던 메일이 있었나요?**\n\n"
        "_다르다면 더 자세히 알려주세요!_\n\n"
        "예: 작업 요청 관련 메일을 찾고 있어요"
    )

