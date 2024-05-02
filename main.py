from fastapi import FastAPI
from mangum import Mangum
import gspread
from pydantic import BaseModel

class KakaoRequest(BaseModel):
    intent: dict
    userRequest: dict
    bot: dict
    action: dict

class KaKaoResponse(BaseModel):
    version: str
    template: dict
    data: dict | None
    context: dict | None


app = FastAPI()
spreadsheet_url = ""


@app.post("/read-sheet")
def read_sheet(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    data = worksheet.get_all_records()

    data_string = ""
    for row in data:
        data_string += f"📌{row['user']}\n{row['title']}\n\n"

    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [ { "simpleText": {"text": data_string.strip()} }]
        },
        data=None,
        context=None
    )
    return kakao_response


@app.post("/write-sheet")
def write_sheet(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    
    user = request.action['params']['user']
    title = request.action['params']['title']
    id = len(worksheet.get_all_records())
    new_row = [id, user, title]
    worksheet.append_row(new_row)
    
    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [ { "simpleText": {"text": f"기도제목 추가 완료!\n📌{user}\n{title}" } }]
            },
        context=None
    )
    return kakao_response

@app.post("/read-sheet-one")
def read_sheet(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    data = worksheet.get_all_records()

    targetUser = request.action['params']['target_user']
    
    data_string = ""
    for row in data:
        if row['user'] == targetUser:
            data_string = f"📌{targetUser}\n{row['title']}\n\n"

    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [
                {
                    "basicCard": {
                        "title": targetUser,
                        "description": data_string,
                        "thumbnail": {
                            "imageUrl": "https://t1.kakaocdn.net/openbuilder/sample/lj3JUcmrzC53YIjNDkqbWK.jpg"
          },
          "buttons": [
            {
              "action": "message",
              "label": "열어보기",
              "messageText": "짜잔! 우리가 찾던 보물입니다"
            },
            {
              "action":  "webLink",
              "label": "구경하기",
              "webLinkUrl": "https://e.kakao.com/t/hello-ryan"
            }
          ]
        }
      }
    ]
  },
        data={
            "name":targetUser,
            "title":data_string,
        },
        context=None
    )
    return kakao_response
    

handler = Mangum(app)