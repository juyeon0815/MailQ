from openai import AzureOpenAI
import os
from dotenv import load_dotenv      

load_dotenv() 

def generate_response(prompt: str, content: str) -> str:

    api_key = os.getenv("OPENAI_API_KEY")
    api_version = os.getenv("OPENAI_API_VERSION")
    api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
    model = os.getenv("OPENAI_MODEL")

    # prompt가 비어있으면 기본 메시지로 설정
    if not prompt:
        prompt = """
            당신은 이메일 어시스턴트 챗봇의 사용자 입력을 보고 의도를 분류하는 시스템입니다.

            사용자의 입력 문장을 보고 다음 중 하나로 분류하세요:

            - summary: 오늘 받은 메일 요약을 요청하는 경우
            - search: 특정 메일이나 내용을 찾으려는 의도인 경우 (예: 이슈, 일정, 요청, 부서, 사람, 시스템 이름 등)
            - other: 일상적인 인사, 잡담, 비업무적인 대화 등 업무와 관련 없는 경우

            ⚠️ 불완전하거나 키워드 위주의 짧은 문장(예: "cus 연동오류", "일정 공유")이라도 **업무 관련 메일을 찾으려는 의도**로 판단되면 `search`로 분류하세요.
            ⚠️ 단, 입력이 너무 모호하거나 문맥상 판단이 어려운 경우에는 **"other"**이라고만 답하세요.
            
            예시:
            - "오늘 메일 뭐 왔어?" → summary
            - "받은 메일 정리해줘" → summary
            - "cus 연동오류" → search
            - "SR 일정 공유된 거 있어?" → search
            - "메일에서 일정 찾아줘" → search
            - "오늘 점심 뭐 먹지?" → other
            - "안녕?" → other

            아래 문장의 의도를 판단해 **summary**, **search**, **other** 중 하나만 출력하세요:

            "{user_input}"
        """

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_endpoint
    )
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        temperature=0.3,
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content.strip()