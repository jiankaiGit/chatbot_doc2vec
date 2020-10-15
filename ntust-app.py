from flask import Flask, request, abort, send_from_directory

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, ConfirmTemplate, PostbackTemplateAction, CarouselTemplate, CarouselColumn, URITemplateAction
app = Flask(__name__)
import threading
import gensim
import os
import zipfile

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from questionList import selectedQuestion

#import sys
#import datetime
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials as SAC

# Channel Access Token
line_bot_api = LineBotApi('J4ZAc6FQW2v7ZRi+LsttNSkQMqJLnfo+987q35q0c6DqrcsSbLWh/G41mw23yRl7p6Bf+9RQhESgmFNGUW/D9arAOsC+cLi/nCDSCQsUuo2wxpn6hHgNZXTgurk6gMGZ8wb+sGyC/UyLxTVxxcD4LgdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('afbedf4f7a5ca98c8866817935a74fc2')
thankString = "謝謝您的參與"
AnswererCurQuestIndex = {}
labMappingTable = {'1':"實驗室一",'2':"實驗室二",'3':"實驗室三",'4':"實驗室四"}
f = None

#載入模型
model = Doc2Vec.load("doc2vec.model")

#創建UserAnswer資料夾
path = "UserAnswer"
if not os.path.isdir(path):
    os.mkdir(path)
    print(" create dir successful")

#壓縮指定的資料夾
def zip_dir(sPath):
    zf = zipfile.ZipFile('{}.zip'.format(path), 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(sPath):
        for file_name in files:
            zf.write(os.path.join(root, file_name))

#監聽下載動作的請求
@app.route('/download', methods=['GET'])
def download():
    zip_dir(path)
    fileName = path+ ".zip"
    dirpath = os.getcwd()
    return send_from_directory(dirpath,fileName, as_attachment=True)
    

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

def analysisMostNSim(uuid):
    answer = ""
    with open(path+"/"+uuid+".txt", 'r', encoding='utf-8') as f:
        for line in f:
            if len(line)>0:
                answer += line.strip()

    analysisText = answer.split(' ')
    #取得向量
    inferred_vector = model.infer_vector(doc_words=analysisText,alpha=0.025,steps=300)
    print("使用者: "+str(uuid)+" 回答: "+str(analysisText))
    #相似度比較 topn取出最相似的句數
    sims = model.docvecs.most_similar([inferred_vector],topn=2)
    answerId = "媒合結果為:\n"
    resultIndex = 0
    for count,sim in sims:
        count = str(int(count)+1)
        #此處判斷避免最後一個結果加上換行，造成line上面看會多一行空白
        if(resultIndex +1 == len(sims)):
            answerId += labMappingTable[count]
        else:
            answerId += labMappingTable[count] + "\n"
        resultIndex +=1
    #推送結果給使用者
    line_bot_api.push_message(uuid, TextSendMessage(text=answerId))
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    uuid = event.source.user_id
    # print(uuid)
    #print(type(msg))
    msg = msg.encode("utf-8")
    if event.message.text == "媒合推薦":
        buttons_template3 = TemplateSendMessage(
            alt_text="媒合推薦",
            template=ButtonsTemplate(
                title="歡迎使用媒合推薦系統 ~",
                text="請點選開始測驗或於文字欄中輸入開始測驗",
                thumbnail_image_url="https://i.imgur.com/iufU8tU.jpg",
                actions=[
                    MessageTemplateAction(
                        label="開始測驗",
                        text="開始測驗"
                    ),
                    MessageTemplateAction(
                        label="取消",
                        text="取消"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template3)
    elif event.message.text == "開始測驗":
        #開啟檔案，若不存在則創建新檔案
        f = open(path+"/"+uuid+".txt", 'w')
        #用使用者的UUID當 key 儲存每個使用者現在回答到第幾題
        AnswererCurQuestIndex[uuid] = 0
        #回應題目
        selectedQuestion(event,0,uuid,line_bot_api)
        #使用者目前題號+1
        AnswererCurQuestIndex[uuid] = 1
    elif event.message.text == "取消":
        if AnswererCurQuestIndex.get(uuid) != None:
            #刪除目前使用者的key
            AnswererCurQuestIndex.pop(uuid)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=thankString))
    else:
        answerQuestIndex = AnswererCurQuestIndex.get(uuid)
        if answerQuestIndex != None:
            result = selectedQuestion(event,answerQuestIndex,uuid,line_bot_api)
            AnswererCurQuestIndex[uuid] = AnswererCurQuestIndex.get(uuid) + 1
            #finish question and clear data from AnswererCurQuestIndex
            if result == "end":
                #創建一個執行續做文檔分析
                t = threading.Thread(target = analysisMostNSim, args = (uuid,))
                t.start()
                #若答題結束就將該帳號ID刪除 下次使用可以重新來過
                AnswererCurQuestIndex.pop(uuid)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入媒合推薦或點選按鈕"))

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)