from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageTemplateAction, ConfirmTemplate, PostbackTemplateAction, CarouselTemplate, CarouselColumn, URITemplateAction
import os
#創建UserAnswer資料夾
path = "UserAnswer"
if not os.path.isdir(path):
    os.mkdir(path)
    print(" create dir successful")

def selectedQuestion(event, index,uuid,line_bot_api):
    response = ""
    #從1開始才是第1題的答案
    if index !=0:
        f = open(path+"/"+uuid+".txt", 'a')
        #把答案寫進檔案裡
        f.write(event.message.text + "\n")

    if index == 0:
        response = TextSendMessage("您的姓名:")

    elif index == 1:
        response = TemplateSendMessage(
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
        #line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    elif index == 2:
        response = TextSendMessage("您有興趣加入的實驗室或指導教授:")
        
    elif index == 3:
        response = TextSendMessage("您擁有哪些專長/專業:")   
    elif index == 4:
        response = TextSendMessage("我們已收到您的資料，謝謝您的耐心填答，請稍等媒合結果")
        #line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
        #回傳結束符號
        return "end"
        
    else:
       response = TextSendMessage("您好")
    line_bot_api.reply_message(event.reply_token, response)
    return "continue"
