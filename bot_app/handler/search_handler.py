from core.mail_searcher import rewrite_user_query, search_emails_from_index, filter_results_by_relevance, format_search_results_as_links


def handle_search_request(turn_context, user_email: str, user_input: str):
    
    # 1️⃣ 사용자 입력을 검색 쿼리로 리라이팅
    rewritten_query = rewrite_user_query(user_input)

    # 2️⃣ Azure AI Search 호출
    search_results = search_emails_from_index(rewritten_query, user_email)

    # 3️⃣ 의미 정합성 필터링 (GPT)
    filtered_results = filter_results_by_relevance(user_input, search_results)

    # 4️⃣ 포맷 변환
    response_text = format_search_results_as_links(filtered_results)

    # ✅ 최종 결과 반환 (Teams Bot에 전달)
    return turn_context.send_activity(response_text)
