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

# Channel Access Token
line_bot_api = LineBotApi("J4ZAc6FQW2v7ZRi+LsttNSkQMqJLnfo+987q35q0c6DqrcsSbLWh/G41mw23yRl7p6Bf+9RQhESgmFNGUW/D9arAOsC+cLi/nCDSCQsUuo2wxpn6hHgNZXTgurk6gMGZ8wb+sGyC/UyLxTVxxcD4LgdB04t89/1O/w1cDnyilFU=jqeFTerwBf33iLEXJNLYiB3Ub4wboThj5RtlMM4Ank2qMqwOga7yGrvtx/hByMdENKtVNJvD/fELbO8/UCeNCpsTzXrPBjOXqaVPXlSudGWET/JmQiB9ubxT2fyD9WBVB7fj7JCb4jHysu8QE1xMXgdB04t89/1O/w1cDnyilFU=")
# Channel Secret
handler = WebhookHandler("afbedf4f7a5ca98c8866817935a74fc2")
thankString = "謝謝您的參與"
AnswererCurQuestIndex = {}
labImage = {1:"https://i.imgur.com/iufU8tU.jpg",2:"https://i.imgur.com/iufU8tU.jpg",3:"https://i.imgur.com/iufU8tU.jpg",4:"https://i.imgur.com/iufU8tU.jpg"}
labMappingTable = {1:"行動數位服務實驗室",2:"高科技產業研究實驗室",3:"人力資源管理實驗室",4:"企業分析與平價實驗室",5:"企業營運管理實驗室",6:"電子商務實驗室",7:"行銷與人工智慧實驗室",8:"口碑行銷實驗室",9:"張譯尹教授的實驗室",10:"數據分析與決策實驗室",11:"黃美慈教授的實驗室",12:"全球行銷創新實驗室",13:"行為科學管理實驗室",14:"腦科學行銷策略實驗室"}
labPro = {1:"曾盛恕 教授",2:"張順教 教授",3:"葉穎蓉 教授",4:"郭啟賢 ",5:"鄭仁偉 教授",6:"欒斌 教授",7:"吳克振 教授",8:"林孟彥 教授",9:"張譯尹 教授",10:"呂志豪 教授",11:"黃美慈 教授",12:"盛麗慧 教授",13:"謝亦泰 教授",14:"王蕙芝 教授"}
lab = {1:'1. 互相幫助及學習'+'\n'+'2. 團體合作'+'\n'+'3. 友善', 2:'1. 輕鬆愉快'+'\n'+'2. 開心'+'\n'+'3. 舒服', 
           3:'1. 融洽'+'\n'+'2. 友愛'+'\n'+'3. 互助', 4:'1. 融洽'+'\n'+'2. 輕鬆愉快'+'\n'+'3. 不拘謹'}
pro = {1:'1. 友善,會關心學生近況'+'\n'+'2. 開放'+'\n'+'3. 會針對學生不同的想法給建議', 2:'1. 開放'+'\n'+'2. 自由'+'\n'+'3. 直接直爽', 
           3:'1. 嚴謹'+'\n'+'2. 有自己的想法及原則'+'\n'+'3. 樂於分享價值觀及人生經驗談', 4:'1. 隨興放任自由'+'\n'+'2. 目標性明確'+'\n'+'3. 不會限制學生'}
suitable = {1:'1. 玩桌遊'+'\n'+'2.打籃球'+'\n'+'3.野餐', 2:'1. 紅酒'+'\n'+'2. 高爾夫'+'\n'+'3. 玩電動', 
           3:'1. 爬山'+'\n'+'2. 種樹'+'\n'+'3. 踏青', 4:'1. 辦活動'+'\n'+'2. 社交'}
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
            
def carouselColumnMaker(index):
    carouselColumnElement = CarouselColumn(
                    thumbnail_image_url=labImage[index],
                    title=labMappingTable[index],
                    text=labPro[index],
                    actions=[
                        PostbackTemplateAction(
                            label='實驗室風格',
                            text=lab[index],
                            data='notResponse'
                        ),
                        PostbackTemplateAction(
                            label='教授風格',
                            text=pro[index],
                            data='notResponse'
                        ),
                        PostbackTemplateAction(
                            label='合適人選',
                            text=suitable[index],
                            data='notResponse'
                        )
                    ]
                )
    
    return carouselColumnElement

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
    sims = model.docvecs.most_similar([inferred_vector],topn=3)
    answerId = "媒合結果為:\n"
    resultIndex = 0
    carouselMessageList = []
    for count,sim in sims:
        LabIndex = int(count)+1
        #此處判斷避免最後一個結果加上換行，造成line上面看會多一行空白
        # if(resultIndex +1 == len(sims)):
        #     answerId += labMappingTable[count]
        # else:
        #     answerId += labMappingTable[count] + "\n"
        # resultIndex +=1
        #製作回答的卡片內容
        carouselMessageList.append(carouselColumnMaker(LabIndex))
    
    #回覆卡片式的回應樣式
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=carouselMessageList
        )
    )
    
    
    #推送結果給使用者
    line_bot_api.push_message(uuid, carousel_template_message)
    

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    uuid = event.source.user_id
    # print(uuid)
    #print(type(msg))
    msg = msg.encode("utf-8")
    if event.message.text == "開始測驗":
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