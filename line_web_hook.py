from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def MainFunction():
    return 'Hello world'

@app.route('/bot')
def Bot():
    return 'this bot'

@app.route('/bot', methods=['POST'])
def BotPost():
    content = request.json
    replyToken = content['events'][0]['replyToken']
    # print(content['events'][0]['replyToken'])

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer 5rt+ucIfGj5wGbnMWl3a6xZUg7ZDkG6hVa2M74A7P8nU1sfv/imgTu5Wo5Aaa/k4vmo5B8Oes4OweNVQvf3j7ADsdGYnVbFMDFJ7rmbFudc38PCyKrLIvivW0Z7DimqxhYw33uj/VFxzanhXl2AL8QdB04t89/1O/w1cDnyilFU=' 
    }
    data = {
        'replyToken': replyToken,
        'messages': [
            {  
                "type": "text",
                "text": "ไอสัด"
            }
        ]
    }
    dataJSON = json.dumps(data)

    r = requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, data=dataJSON)
    print(r.status_code)
    print(r.text)

    return content

if __name__ == '__main__':
    app.run()