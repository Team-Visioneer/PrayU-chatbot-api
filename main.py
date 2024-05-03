from fastapi import FastAPI
from mangum import Mangum
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import gspread
import random


class Config(BaseSettings):
    spreadsheet_url: str

    model_config = SettingsConfigDict(env_file=".env")


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


config = Config() # type: ignore
app = FastAPI()

@app.post("/read-sheet")
def read_sheet(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(config.spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    data = worksheet.get_all_records()

    church_list = worksheet.col_values(2)
    user_list = worksheet.col_values(3)
    user = request.action['params']['user']
    church = request.action['params']['church']

    if church not in church_list:
        kakao_response = KaKaoResponse(
            version="2.0",
            template={
                "outputs": [ { "simpleText": {"text": f"해당 교회는 등록되어 있지 않습니다.\n{church}" } }]
            },
            data=None,
            context=None
        )
        return kakao_response


    if user not in user_list:
        kakao_response = KaKaoResponse(
            version="2.0",
            template={
                "outputs": [ { "simpleText": {"text": "친구들의 기도제목을 보기 위해서는 기도제목 쓰기를 완료해야됩니다!" } }]
            },
            data=None,
            context=None
        )
        return kakao_response

        
    
    church_users = [ row['user'] for row in data if row['church'] == church ]
    random.shuffle(church_users)
    random_church_users = [ church_users.pop() for _ in range(min(3, len(church_users))) ]
    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [
                {
                    "textCard": {
                        "title": f"{church} 친구들 기도제목 보기",
                        "description": f"기도제목을 올려준 {church} 친구들 중 랜덤으로 3명을 보여드려요. 기도제목이 궁금한 친구를 선택해주세요!",
                        "buttons": [
                                {
                                    "label": f"{r_user} 기도제목 보기",
                                    "action": "block",
                                    "blockId": "66337723eb1acd7e513d9d1d",
                                    "extra": {
                                        "target_user": r_user
                                    }
                                }
                                for r_user in random_church_users
                                
                            ]
                               
                    }
                }
            ]
        },
        data=None,
        context=None
    )
    return kakao_response


@app.post("/write-sheet")
def write_sheet(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(config.spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    
    user = request.action['params']['user']
    title = request.action['params']['title']
    id = len(worksheet.get_all_records())+1
    new_row = [id, user, title]
    worksheet.append_row(new_row)
    
    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [ { "simpleText": {"text": f"기도제목 추가 완료!\n📌{user}\n{title}" } }]
            },
            data=None,
        context=None
    )
    return kakao_response


@app.post("/read-sheet-one")
def read_sheet_one(request: KakaoRequest) -> KaKaoResponse:
    gc = gspread.service_account("secrets.json")
    doc = gc.open_by_url(config.spreadsheet_url)
    worksheet = doc.worksheet("PrayU_DB")
    data = worksheet.get_all_records()

    targetUser = request.action['clientExtra']['target_user']
    
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