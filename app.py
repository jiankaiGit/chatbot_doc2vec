from flask import Flask, request, abort

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
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

# Channel Access Token
line_bot_api = LineBotApi("jqeFTerwBf33iLEXJNLYiB3Ub4wboThj5RtlMM4Ank2qMqwOga7yGrvtx/hByMdENKtVNJvD/fELbO8/UCeNCpsTzXrPBjOXqaVPXlSudGWET/JmQiB9ubxT2fyD9WBVB7fj7JCb4jHysu8QE1xMXgdB04t89/1O/w1cDnyilFU=")
# Channel Secret
handler = WebhookHandler("994675102d50dfee59c7edfc417ecbc0")
thankString = "謝謝您的參與"
AnswererCurQuestIndex = {}
userTokenDict = {}
labMappingTable = {'1':"實驗室一",'2':"實驗室二"}
f = None

#載入模型
model = Doc2Vec.load("doc2vec.model")

import os
path = "UserAnswer"
if not os.path.isdir(path):
    os.mkdir(path)
    print(" create dir successful")

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
        questionList(event,0,uuid)
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
            #---原本期望用for迴圈做問卷一問一答，但似乎LineBot本身設定就無法進行，永遠僅會出現第一題---
            # q_list = ["1. 您的姓名：", "2. 您的性別：", "3. 您有興趣加入的實驗室或指導教授：","我們已收到您的資料，謝謝您的耐心填答!"]

            # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=q_list[answerQuestIndex]))

            result = questionList(event,answerQuestIndex,uuid)
            AnswererCurQuestIndex[uuid] = AnswererCurQuestIndex.get(uuid) + 1
            #finish question and clear data from AnswererCurQuestIndex
            if result == "end":
                #若答題結束就將該帳號ID刪除 下次使用可以重新來過
                AnswererCurQuestIndex.pop(uuid)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入媒合推薦或點選按鈕"))

def getResult(uuid):
    #測試語句
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
    answerId = ""
    for count,sim in sims:
        answerId += labMappingTable[count] + "\n"

    line_bot_api.push_message(uuid, TextSendMessage(text=answerId))


def questionList(event, index,uuid):
    #從1開始才是第1題的答案
    if index !=0:
        f = open(path+"/"+uuid+".txt", 'a')
        #把答案寫進檔案裡
        f.write(event.message.text + "\n")

    if index == 0:
        text = "您的姓名:"

    elif index == 1:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您的性別:",
                actions=[
                    MessageTemplateAction(
                        label="男",
                        text="男"
                    ),
                    MessageTemplateAction(
                        label="女",
                        text="女"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 2:
        text = "您有興趣加入的實驗室或指導教授:"
        
    elif index == 3:
        text = "您擁有哪些專長/專業:"   
    elif index == 4:
        text = "我們已收到您的資料，謝謝您的耐心填答，請稍等媒合結果"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
        t = threading.Thread(target = getResult, args = (uuid,))
        t.start()
        #回傳結束符號
        return "end"
        
    else:
       text = "您好"     
    '''
    elif index == 4:
        text = "您有哪些興趣/嗜好:"

    elif index == 5:
        text = "您的人格特質/個性:"  

    elif index == 6:
        text = "您有考取過哪些專業證照:"

    elif index == 7:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                thumbnail_image_url="https://i.imgur.com/Ip2MMln.png",
                title=" ",
                text=str(index+1)+". 您最近一次考過的英語檢定成績為第幾級:",
                actions=[
                    MessageTemplateAction(
                        label="第一級",
                        text="第一級"
                    ),
                    MessageTemplateAction(
                        label="第二級",
                        text="第二級"
                    ),
                    MessageTemplateAction(
                        label="第三級",
                        text="第三級"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 8:
        text = "您預計的論文領域級研究方向/內容:"

    elif index == 9:
        message = TemplateSendMessage(
            alt_text="Carousel template",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        title=str(index+1)+". 您期望與指導教授開會的方式:",
                        text="【個人】",
                        actions=[
                            MessageTemplateAction(
                                label="個人 - 每週一次",
                                text="個人 - 每週一次"
                            ),
                            MessageTemplateAction(
                                label=" 個人 - 兩週一次",
                                text="個人 - 兩週一次"
                            ),
                            MessageTemplateAction(
                                label="個人 - 無固定",
                                text="個人 - 無固定"
                            )
                        ]
                    ),
                    CarouselColumn(
                        title=str(index+1)+". 您期望與指導教授開會的方式:",
                        text="【分組】",
                        actions=[
                            MessageTemplateAction(
                                label="分組 - 每週一次",
                                text="分組 - 每週一次"
                            ),
                            MessageTemplateAction(
                                label="分組 - 兩週一次",
                                text="分組 - 兩週一次"
                            ),
                            MessageTemplateAction(
                                label="分組 - 無固定",
                                text="分組 - 無固定"
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
        return "continue"
    elif index == 10:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您預計的論文時程:",
                actions=[
                    MessageTemplateAction(
                        label="碩一上開始、碩二上結束",
                        text="碩一上開始、碩二上結束"
                    ),
                    MessageTemplateAction(
                        label="碩一上開始、碩二下結束",
                        text="碩一上開始、碩二下結束"
                    ),
                    MessageTemplateAction(
                        label="碩一下開始、碩二下結束",
                        text="碩一下開始、碩二下結束"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 11:
        text = "您所期望指導教授的領導風格:"

    elif index == 12:
        text = "您所期望實驗室的氣氛/氛圍:"  

    elif index == 13:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您所期望實驗室的人數:",
                actions=[
                    MessageTemplateAction(
                        label="1-5人",
                        text="1-5人"
                    ),
                    MessageTemplateAction(
                        label="6-10人",
                        text="6-10人"
                    ),
                    MessageTemplateAction(
                        label="11-15人",
                        text="11-15人"
                    ),
                    MessageTemplateAction(
                        label="16人以上",
                        text="16人以上",
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 14:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您是否期望有固定座位:",
                actions=[
                    MessageTemplateAction(
                        label="是",
                        text="是"
                    ),
                    MessageTemplateAction(
                        label="否",
                        text="否"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
        
    elif index == 15:
        text = "您期望實驗室有哪些設備:"

    elif index == 16:
        text = "您期望實驗室有哪些聚餐或活動(例如:桌遊、期末聚餐等):"       

    elif index == 17:
        text = "您參與過的專題、計劃或競賽領域及內容方向:"

    elif index == 18:
        text = "您曾經或現在工作、實習或打工的產業、領域及職務類別有哪些:"  

    elif index == 19:
        text = "在就讀研究所這段期間，有哪些其他規劃(例如:交換、雙聯、實習、提畢等):"

    elif index == 20:
        text = "您所期望畢業後的工作產業、領域及職務:"
        
    elif index == 21:
        text = "您期望能在實驗室中學習到哪些事物:"  

    elif index == 22:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您預計待在實驗室或學校的時間:",
                actions=[
                    MessageTemplateAction(
                        label="1-3天",
                        text="1-3天"
                    ),
                    MessageTemplateAction(
                        label="4-6天",
                        text="4-6天"
                    ),
                    MessageTemplateAction(
                        label="每天",
                        text="每天"
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 23:
        text = "您對自我的期望與目標:"    
    elif index == 4:
        text = "我們已收到您的資料，謝謝您的耐心填答，請稍等媒合結果"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
        t = threading.Thread(target = getResult, args = (uuid,))
        t.start()
        #回傳結束符號
        return "end"
        
    else:
       text = "您好" 
    '''   
    line_bot_api.reply_message(event.reply_token,TextSendMessage(str(index+1)+". "+text))
    return "continue"

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)