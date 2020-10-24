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
    text = ""
    buttons_template = ""
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
        
    elif index == 2:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您是否期望有固定座位:",
                actions=[
                    MessageTemplateAction(
                        label="是，每個人都有",
                        text="是，每個人都有"
                    ),
                    MessageTemplateAction(
                        label="是，但不用每個人都有",
                        text="是，但不用每個人都有"
                    ),
                    MessageTemplateAction(
                        label="否",
                        text="否"
                    )
                ]
            )
        )
        
    elif index == 3:
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
        
    elif index == 4:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您預計待在實驗室的時間:",
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
        
    elif index == 5:
        buttons_template = TemplateSendMessage(
            alt_text="Buttons Template",
            template=ButtonsTemplate(
                title=" ",
                text=str(index+1)+". 您期望與指導教授開會的頻率:",
                actions=[
                    MessageTemplateAction(
                        label="每周一次",
                        text="每周一次"
                    ),
                    MessageTemplateAction(
                        label="每周兩次",
                        text="每周兩次"
                    ),
                    MessageTemplateAction(
                        label="無固定",
                        text="無固定"
                    ),
                    MessageTemplateAction(
                        label="其他",
                        text="其他",
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
        return "continue"
    
    elif index == 6:
        buttons_template = TemplateSendMessage(
            alt_text="Carousel template",
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        title=str(index+1)+". 您預計的論文時程:",
                        text=" ",
                        actions=[
                            MessageTemplateAction(
                                label="碩一上開始，碩一下結束",
                                text="碩一上開始，碩一下結束"
                            ),
                            MessageTemplateAction(
                                label="碩一上開始，碩二上結束",
                                text="碩一上開始，碩二上結束"
                            ),
                            MessageTemplateAction(
                                label="碩一上開始，碩二下結束",
                                text="碩一上開始，碩二下結束"
                            )
                        ]
                    ),
                    CarouselColumn(
                        title=str(index+1)+" ",
                        text=" ",
                        actions=[
                            MessageTemplateAction(
                                label="碩一下開始，碩二上結束",
                                text="碩一下開始，碩二上結束"
                            ),
                            MessageTemplateAction(
                                label="碩一下開始，碩二下結束",
                                text="碩一下開始，碩二下結束"
                            ),
                            MessageTemplateAction(
                                label="碩二上開始，碩二下結束",
                                text="碩二上開始，碩二下結束"
                            )
                        ]
                    )
                ]
            )
        )
        
    elif index == 7:
        text = "您擁有哪些專長/專業:"   
   
    elif index == 8:
        text = "您有哪些興趣/嗜好:"

    elif index == 9:
        text = "您的人格特質/個性:"  

    elif index == 10:
        text = "您預計的論文領域及研究方向:"
        
    elif index == 11:
        text = "您所期望指導教授的領導風格:"

    elif index == 12:
        text = "您所期望實驗室的氣氛/氛圍:"
        
    elif index == 13:
        text = "您期望實驗室有哪些聚餐或活動(例如:桌遊、期末聚餐等):"       

    elif index == 14:
        text = "您參與過的專題、計劃或競賽領域:"

    elif index == 15:
        text = "您曾經或現在工作、實習或打工的產業及領域有哪些:"  

    elif index == 16:
        text = "在就讀研究所這段期間，有哪些其他規劃(例如:交換、雙聯、實習、提畢、延畢等):"

    elif index == 17:
        text = "您所期望畢業後的工作產業及領域:"
        
    elif index == 18:
        text = "您期望能在實驗室中學習到哪些事物:"  
        
    elif index == 20:
        text = "您對自我的期望與目標:"   
        
    elif index == 21:
        text = "我們已收到您的資料，謝謝您的耐心填答，請稍等媒合結果"
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text))
        #回傳結束符號
        return "end"
        
    else:
       text = "您好"

    if text == "":
        line_bot_api.reply_message(event.reply_token,buttons_template)
    else:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(str(index+1)+". "+text))
    return "continue"
