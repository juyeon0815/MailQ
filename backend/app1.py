# # 이메일 수집 - 디버깅 강화 버전
# import os
# import msal
# import requests
# import base64
# import json
# from datetime import datetime
# from dotenv import load_dotenv 

# load_dotenv()

# # === Azure 앱 등록 정보 ===
# CLIENT_ID = os.getenv("CLIENT_ID")
# TENANT_ID = os.getenv("TENANT_ID")

# print(f"CLIENT_ID: {CLIENT_ID}")
# print(f"TENANT_ID: {TENANT_ID}")

# # === Microsoft Graph 설정 ===
# AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
# SCOPES = ["User.Read", "Mail.Read"]

# print(f"AUTHORITY: {AUTHORITY}")
# print(f"SCOPES: {SCOPES}")

# # === MSAL 앱 초기화 ===
# app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)

# # === 캐시된 계정 정리 및 로그인 ===
# accounts = app.get_accounts()
# if accounts:
#     print(f"기존 계정 {len(accounts)}개 발견, 삭제합니다.")
#     for account in accounts:
#         app.remove_account(account)

# # Device Flow 시작
# print("\n=== Device Flow 시작 ===")
# flow = app.initiate_device_flow(scopes=SCOPES)

# if "user_code" not in flow:
#     raise Exception("Device Flow 시작 실패. 앱 등록 정보를 확인하세요.")

# print("📌 아래 메시지에 따라 로그인 진행:")
# print(flow["message"])

# result = app.acquire_token_by_device_flow(flow)

# # === 토큰 결과 확인 ===
# print("\n=== 토큰 획득 결과 ===")
# if "access_token" in result:
#     print("✅ Access Token 획득 성공")
    
#     # JWT 토큰 디코딩
#     def decode_jwt(token):
#         try:
#             parts = token.split('.')
#             payload = parts[1] + '=' * (-len(parts[1]) % 4)  # padding
#             decoded_bytes = base64.urlsafe_b64decode(payload)
#             return json.loads(decoded_bytes)
#         except Exception as e:
#             print(f"JWT 디코딩 실패: {e}")
#             return None

#     token_data = decode_jwt(result['access_token'])
#     if token_data:
#         print(f"토큰 발급 시간: {datetime.fromtimestamp(token_data.get('iat', 0))}")
#         print(f"토큰 만료 시간: {datetime.fromtimestamp(token_data.get('exp', 0))}")
#         print(f"토큰 권한(scp): {token_data.get('scp')}")
#         print(f"토큰 대상(aud): {token_data.get('aud')}")
#         print(f"사용자 ID: {token_data.get('oid')}")
#         print(f"앱 ID: {token_data.get('appid')}")
    
#     # === 사용자 정보 먼저 확인 ===
#     print("\n=== 사용자 정보 확인 ===")
#     headers = {
#         "Authorization": f"Bearer {result['access_token']}",
#         "Content-Type": "application/json"
#     }
    
#     user_url = "https://graph.microsoft.com/v1.0/me"
#     user_res = requests.get(user_url, headers=headers)
    
#     print(f"사용자 정보 요청 상태코드: {user_res.status_code}")
    
#     if user_res.status_code == 200:
#         user_info = user_res.json()
#         print(f"✅ 사용자: {user_info.get('displayName')} ({user_info.get('mail')})")
#     else:
#         print(f"❌ 사용자 정보 요청 실패: {user_res.text}")
        
#     # === 메일 폴더 확인 ===
#     print("\n=== 메일 폴더 확인 ===")
#     folders_url = "https://graph.microsoft.com/v1.0/me/mailFolders"
#     folders_res = requests.get(folders_url, headers=headers)
    
#     print(f"메일 폴더 요청 상태코드: {folders_res.status_code}")
    
#     if folders_res.status_code == 200:
#         folders = folders_res.json().get("value", [])
#         print(f"✅ 메일 폴더 {len(folders)}개 발견:")
#         for folder in folders[:5]:  # 상위 5개만 출력
#             print(f"  - {folder.get('displayName')} (ID: {folder.get('id')})")
#     else:
#         print(f"❌ 메일 폴더 요청 실패: {folders_res.text}")

#     # === 메일 메시지 요청 (다양한 방법) ===
#     print("\n=== 메일 메시지 요청 ===")
    
#     # 방법 1: 직접 messages 엔드포인트
#     print("방법 1: /me/messages")
#     messages_url = "https://graph.microsoft.com/v1.0/me/messages?$top=5"
#     messages_res = requests.get(messages_url, headers=headers)
#     print(f"상태코드: {messages_res.status_code}")
    
#     if messages_res.status_code == 200:
#         messages = messages_res.json().get("value", [])
#         print(f"✅ 메시지 {len(messages)}개 발견:")
#         for msg in messages:
#             sender = msg.get("from", {}).get("emailAddress", {}).get("name", "(알 수 없음)")
#             subject = msg.get("subject", "(제목 없음)")
#             print(f"  - 보낸사람: {sender}, 제목: {subject}")
#     else:
#         print(f"❌ 메시지 요청 실패:")
#         print(f"응답 헤더: {dict(messages_res.headers)}")
#         print(f"응답 본문: {messages_res.text}")
        
#         # 에러 상세 분석
#         try:
#             error_data = messages_res.json()
#             if "error" in error_data:
#                 print(f"에러 코드: {error_data['error'].get('code')}")
#                 print(f"에러 메시지: {error_data['error'].get('message')}")
#         except:
#             pass
    
#     # 방법 2: inbox 폴더 직접 접근
#     print("\n방법 2: /me/mailFolders/inbox/messages")
#     inbox_url = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$top=5"
#     inbox_res = requests.get(inbox_url, headers=headers)
#     print(f"상태코드: {inbox_res.status_code}")
    
#     if inbox_res.status_code != 200:
#         print(f"❌ 받은편지함 접근 실패: {inbox_res.text}")
        
# else:
#     print("❌ 토큰 획득 실패:")
#     print(f"에러: {result.get('error')}")
#     print(f"에러 설명: {result.get('error_description')}")
#     print(f"전체 응답: {result}")

# # === 추가 디버깅 정보 ===
# print("\n=== 환경 확인 ===")
# print(f"Python requests 버전: {requests.__version__}")
# print(f"MSAL 버전: {msal.__version__}")

# # === 권한 확인 가이드 ===
# print("\n=== 권한 확인 가이드 ===")
# print("Azure 포털에서 다음을 확인하세요:")
# print("1. 앱 등록 > API 권한에서 'Mail.Read' 권한이 추가되어 있는지")
# print("2. 권한에 '관리자 동의 필요' 표시가 있다면 관리자 동의를 받았는지")
# print("3. 앱 등록 > 인증에서 '퍼블릭 클라이언트 플로우 허용'이 예로 설정되어 있는지")
# print("4. 사용하는 계정에 실제로 메일함이 있고 접근 권한이 있는지")

# Exchange 메일박스 상태 확인
import os
import msal
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# === Azure 앱 등록 정보 ===
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

# === MSAL 앱 초기화 및 토큰 획득 ===
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["User.Read", "Mail.Read", "MailboxSettings.Read"]

app = msal.PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)

# 기존 계정으로 silent 로그인 시도
accounts = app.get_accounts()
result = None

if accounts:
    print("기존 계정으로 silent 로그인 시도...")
    result = app.acquire_token_silent(SCOPES, account=accounts[0])

if not result:
    print("Device Flow로 새로 로그인...")
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Device Flow 시작 실패")
    
    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)

if "access_token" not in result:
    print(f"토큰 획득 실패: {result}")
    exit()

print(result['access_token'])

headers = {
    "Authorization": f"Bearer {result['access_token']}",
    "Content-Type": "application/json"
}

print("=== Exchange 메일박스 상태 진단 ===")

# 1. 사용자 기본 정보
print("\n1. 사용자 정보:")
user_res = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
if user_res.status_code == 200:
    user = user_res.json()
    print(f"   이름: {user.get('displayName')}")
    print(f"   메일: {user.get('mail')}")
    print(f"   UPN: {user.get('userPrincipalName')}")
    print(f"   계정 활성화: {user.get('accountEnabled')}")
else:
    print(f"   ❌ 사용자 정보 가져오기 실패: {user_res.status_code}")

# 2. 메일박스 설정 확인
print("\n2. 메일박스 설정:")
mailbox_res = requests.get("https://graph.microsoft.com/v1.0/me/mailboxSettings", headers=headers)
print(f"   상태코드: {mailbox_res.status_code}")

if mailbox_res.status_code == 200:
    mailbox = mailbox_res.json()
    print(f"   ✅ 메일박스 설정 접근 가능")
    print(f"   언어: {mailbox.get('language', {}).get('displayName')}")
    print(f"   시간대: {mailbox.get('timeZone')}")
else:
    print(f"   ❌ 메일박스 설정 접근 실패")
    print(f"   응답: {mailbox_res.text}")

# 3. Exchange Online 라이선스 확인 (조직 계정인 경우)
print("\n3. 라이선스 정보:")
try:
    # Organization 정보로 라이선스 유형 추측
    org_res = requests.get("https://graph.microsoft.com/v1.0/organization", headers=headers)
    if org_res.status_code == 200:
        orgs = org_res.json().get('value', [])
        if orgs:
            org = orgs[0]
            print(f"   조직: {org.get('displayName')}")
            print(f"   도메인: {org.get('verifiedDomains', [{}])[0].get('name', 'N/A')}")
    
    # 사용자의 할당된 라이선스 확인 (조직 계정만 가능)
    license_res = requests.get("https://graph.microsoft.com/v1.0/me/licenseDetails", headers=headers)
    if license_res.status_code == 200:
        licenses = license_res.json().get('value', [])
        print(f"   할당된 라이선스: {len(licenses)}개")
        for license in licenses:
            print(f"   - {license.get('skuPartNumber')}")
    elif license_res.status_code == 403:
        print("   개인 계정 (라이선스 정보 없음)")
    else:
        print(f"   라이선스 정보 확인 불가: {license_res.status_code}")
        
except Exception as e:
    print(f"   라이선스 확인 중 오류: {e}")

# 4. 다른 Graph API 엔드포인트 테스트
print("\n4. 다른 API 엔드포인트 테스트:")

# Outlook 카테고리 (메일박스가 있어야 접근 가능)
categories_res = requests.get("https://graph.microsoft.com/v1.0/me/outlook/categories", headers=headers)
print(f"   Outlook 카테고리: {categories_res.status_code}")

# 일정 (Exchange 기반)
calendar_res = requests.get("https://graph.microsoft.com/v1.0/me/calendar", headers=headers)
print(f"   기본 달력: {calendar_res.status_code}")

# 연락처 (Exchange 기반)
contacts_res = requests.get("https://graph.microsoft.com/v1.0/me/contacts?$top=1", headers=headers)
print(f"   연락처: {contacts_res.status_code}")

# 5. 메일 접근 시도 (상세 에러 정보)
print("\n5. 메일 접근 상세 분석:")

# 최소한의 필드만 요청
simple_mail_res = requests.get(
    "https://graph.microsoft.com/v1.0/me/messages?$select=id&$top=1", 
    headers=headers
)
print(f"   단순 메일 요청: {simple_mail_res.status_code}")

if simple_mail_res.status_code != 200:
    print(f"   에러 헤더: {dict(simple_mail_res.headers)}")
    print(f"   에러 본문: {simple_mail_res.text}")
    
    # WWW-Authenticate 헤더 확인
    www_auth = simple_mail_res.headers.get('WWW-Authenticate')
    if www_auth:
        print(f"   WWW-Authenticate: {www_auth}")

# 6. 메일 활성화 확인 방법
print("\n=== 해결 방법 ===")
print("juyeon@dev0815.onmicrosoft.com 계정의 메일박스 문제로 보입니다.")
print("\n조치 방법:")
print("1. Azure 관리센터에서 사용자에게 Exchange Online 라이선스 할당")
print("2. Microsoft 365 관리센터에서 사용자의 메일박스 활성화")
print("3. 개인 Outlook.com 계정으로 테스트해보기")
print("4. 테넌트 관리자에게 메일박스 권한 확인 요청")

print("\n온마이크로소프트 도메인 특징:")
print("- 개발/테스트용 테넌트는 기본적으로 메일박스가 비활성화될 수 있음")
print("- Exchange Online Plan이 별도로 필요할 수 있음")