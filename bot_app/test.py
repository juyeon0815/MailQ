# outlook_bot_app/test_run_all.py

# from core.mail_fetcher import fetch_today_mails
# from core.blob_uploader import save_email_to_blob
# from core.graph_client import get_user_principal_name  # access_token에서 이메일 추출
# import os

# access_token = "eyJ0eXAiOiJKV1QiLCJub25jZSI6ImlUel9rSVRWelJWRTFCbW8wUl9PckEwRFZwbUdaNHpHMnZOdXl2dFJtM2ciLCJhbGciOiJSUzI1NiIsIng1dCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSIsImtpZCI6IkNOdjBPSTNSd3FsSEZFVm5hb01Bc2hDSDJYRSJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC81NThlODdiMy1mOGI5LTRjOTItOTM5Zi03ODRkY2Q2Mjc2MGIvIiwiaWF0IjoxNzQ5OTg0NzE0LCJuYmYiOjE3NDk5ODQ3MTQsImV4cCI6MTc0OTk4OTE1MywiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsicDEiXSwiYWlvIjoiQVdRQW0vOFpBQUFBQ3VNMW5HU3NzM2lrb0V4TEIxUmVQRjBnUlpyRHRvRy9QUFVxcnhabHJOTFpTUG1Ebk43WXJLNEVMOVVRVlVSVHV2M2ppOGF2TDNnREI1UmtkVmdlMFNneVZHY3lUN05VVTRGRjJLMlhud2FvU3ZCQ1FqR0pVUFRtWFFUc3pObSsiLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcF9kaXNwbGF5bmFtZSI6Ik91dGxvb2sgTWFpbCBDb2xsZWN0b3IiLCJhcHBpZCI6ImZjZjU4NWM1LTY0Y2UtNGI5Mi05NWViLTM3NzZhOTViYmY0MCIsImFwcGlkYWNyIjoiMCIsImZhbWlseV9uYW1lIjoi6rmAIiwiZ2l2ZW5fbmFtZSI6IuyjvOyXsCIsImlkdHlwIjoidXNlciIsImlwYWRkciI6IjIxMS4yMTkuMTI0LjE1NCIsIm5hbWUiOiLquYAg7KO87JewIiwib2lkIjoiMGQ0MDEwYWYtZTY2ZS00NWRkLWE3NTEtOWYxODkxYjVkYjRmIiwicGxhdGYiOiIxNCIsInB1aWQiOiIxMDAzMjAwNEJEMzQ0QkE1IiwicmgiOiIxLkFjWUFzNGVPVmJuNGtreVRuM2hOeldKMkN3TUFBQUFBQUFBQXdBQUFBQUFBQUFEcEFBSEdBQS4iLCJzY3AiOiJNYWlsLlJlYWQgTWFpbGJveFNldHRpbmdzLlJlYWQgVXNlci5SZWFkIHByb2ZpbGUgb3BlbmlkIGVtYWlsIiwic2lkIjoiMDA1ZGI4NDktZmRkZC0xYTMzLTQwYzktYjVjYjE1OGJjM2VhIiwic2lnbmluX3N0YXRlIjpbImttc2kiXSwic3ViIjoiVElWd1A1LWpYMmFybGFwN2xnTzdINlREeUVHUk5xTVlvY1FJbGFYSXdIayIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJBUyIsInRpZCI6IjU1OGU4N2IzLWY4YjktNGM5Mi05MzlmLTc4NGRjZDYyNzYwYiIsInVuaXF1ZV9uYW1lIjoianV5ZW9uQGRldjA4MTUub25taWNyb3NvZnQuY29tIiwidXBuIjoianV5ZW9uQGRldjA4MTUub25taWNyb3NvZnQuY29tIiwidXRpIjoiTm9pUWVjUDRMa0ctR0RhNVd0b1pBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiNjJlOTAzOTQtNjlmNS00MjM3LTkxOTAtMDEyMTc3MTQ1ZTEwIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il0sInhtc19mdGQiOiJiaDRKZzNPSGZ1dDJKNG0xRGdLT2VtWXY1bkkwdm1kYVNtWUlXUV82UXh3QmFtRndZVzVsWVhOMExXUnpiWE0iLCJ4bXNfaWRyZWwiOiIxIDIiLCJ4bXNfc3QiOnsic3ViIjoiR0FRM04yS3NqNHBzR1FHOVUyVE12N2RPQW5pekMyNFhZNVY1ZndtNWZhNCJ9LCJ4bXNfdGNkdCI6MTc0OTgwMDA1MX0.MyysurNnfuQoEPKH5Dd77WB6i17bCj5HhjVNSdZbYB4iIrVgiBG9n0lOAk5_ZkH4qJ11L1mjTouoGa07pPB06sEX48ej7MNjJ28ikJAoB7pyWIwl7ao6vH4vgNMtDp7q75OyPvOMCn2mNedFPa0jk2e7g98bhFz6-OpmCvMfAl2IcB2eeCNZmD-JNTbvszSlBSBfc-aj0xhVFwPzYutjqHBfWrws5tcFbOgF8G_lM16fX91EHLNaNZTkAyndXy55k_zkzaqSAec6KIAz5oQFAa1I1ZkXsKWVdRjbJDcnW-dFxLhVz_POTgtr3UQlvlNs6Ax2GqTZHxb_bPh7FGytLg"

# # ✅ access_token에서 사용자 이메일 추출
# user_email = get_user_principal_name(access_token)

# print(user_email)

# # ✅ 오늘 받은 메일 가져오기
# mails = fetch_today_mails(access_token=access_token)

# # ✅ Blob + Chroma 저장
# for mail in mails:
#     save_email_to_blob(user_email, mail)

# print(f"{len(mails)}건 저장 완료.")

from chromadb import PersistentClient
from chromadb.config import Settings

client = PersistentClient(path="./chroma_db")  # 또는 Chroma 설정에 맞게 path 지정

# 기존 컬렉션 이름 확인
collections = client.list_collections()
print("🔎 등록된 컬렉션 목록:")
for col in collections:
    print(f"- {col.name}")

# 특정 컬렉션에서 저장된 문서 확인
collection_name = "emails"  # 저장 시 사용한 컬렉션 이름
collection = client.get_collection(name=collection_name)

# 저장된 전체 문서 조회 (최대 10건 예시)
results = collection.get(limit=10)

print(results)
print("\n📄 저장된 문서 샘플:")
for i in range(len(results["documents"])):
    print(f"{i+1}. ID: {results['ids'][i]}")
    print(f"   내용: {results['documents'][i][:100]}...")  # 너무 길면 일부만 출력