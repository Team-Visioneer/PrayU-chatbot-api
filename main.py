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
    
    id = request.userRequest['user']['id']
    church = request.action['params']['church']
    user = request.action['params']['user']
    title = request.action['params']['title']

    new_row = [id, church, user, title]
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

    imageUrl_arr = ["https://postfiles.pstatic.net/MjAyNDA1MDRfODgg/MDAxNzE0ODIyODQ5NjE5.HvRK76jtWQuCfZlMGypdZ7hcVEghh1LZuVORhvoSTdAg.IMYM74C7JhQuRNd2fz801-EsKDOY-bC1DauWjxAb3DQg.PNG/be93d279a99d4cde9da35a75e3381a1e222.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfNTIg/MDAxNzE0ODIyODQ5Njc4.ag1SFox4UZMozvI3LEqVDRvIwaEbCLJ7P6dp3bNSFB8g.ufNaYblfwYkwnhVeA1d2H5S7tAkwkoq2ovs1gEMGQmog.PNG/%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfOCAg/MDAxNzE0ODIzMjg1OTcy.f32ter3yUbDZGdc2o_vmeoonZwokjScAkq1pWg5IxQQg.MWe2VE1Cx1m9SjxT5iF_VLoh2d0YjKX1YJoz761BFtgg.PNG/92e65a180ed04aefb7d9e1984010f4c9.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfMTgz/MDAxNzE0ODIzMjg1OTY3.bogLffAt0F1i9dXlfNXwxUTdg9cS54WgAN_jbZBjOVwg.9buM5Aq9D_qeQaqF5wSkqoqeDqs7DfU5HPxwND7X-i0g.PNG/5a2cb2f347d94917b4eb7060583b8581.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfNTkg/MDAxNzE0ODIzMjg1OTk0.k7nCOhwTsEC1dOixCGHJjzvWPBplYfo7k6R5J7iyUKIg.WWvF_BYPhdT6L5w19_luKe4DCZBUPmGCJHV7eta7efEg.PNG/15f4756fe2eb4d97a0cb18822e9c891a.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfMjQy/MDAxNzE0ODIzMjg1OTY4.LhCC5HvasbcQvAbOQpnSJQcDS0bxvIG55p9ISiv6oi0g.ZsvOKQh_Vf5M_7U9ZrIj7Bw-cVzV0yf8lPtn5KxWLY4g.PNG/ad4f23e099704f5784a1320e26a3d160.png?type=w966",
                    "https://postfiles.pstatic.net/MjAyNDA1MDRfMTA3/MDAxNzE0ODIzMjg1OTk2.MHgFEPaMHVpN9y_dlagf-ses6AdKi26zJBevlH5Bav4g.Az1qnpNfrShSSVr_GNBoNho9qGmDRUuy-5IRzHH3Jkgg.PNG/5504113b48ef4c91a7083d9928e8e866.png?type=w966"]
    
    imageUrl = imageUrl_arr[random.randint(0, len(imageUrl_arr))]
    targetUser = request.action['clientExtra']['target_user']
    
    data_string = ""
    for row in data:
        if row['user'] == targetUser:
            data_string = f"{row['title']}\n\n"
    
    kakao_response = KaKaoResponse(
        version="2.0",
        template={
            "outputs": [
                {
                    "basicCard": {
                        "title": f"{targetUser}님의 기도제목",
                        "description": data_string,
                        "thumbnail": {
                            "imageUrl": imageUrl
                            },
                        "buttons": [
                            {
                            "action": "block",
                            "label": "처음으로",
                            "blockId": "663090f9f46daf295c7b3e40",
                            },
                        ]
                        }
                    }
                ],
            
            },
        data={
            "name":targetUser,
            "title":data_string,
            },
        
        context=None
    )
    return kakao_response
    

handler = Mangum(app)