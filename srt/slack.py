import config
import requests

errorText = "오류 발생"
successText = "정상 동작"



def post_message(token, channel, text):
    '''slack 메시지 전송 함수'''
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )
    return response