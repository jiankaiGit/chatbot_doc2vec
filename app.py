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
labImage = {1:"https://i.imgur.com/iufU8tU.jpg",2:"https://i.imgur.com/iufU8tU.jpg",3:"https://i.imgur.com/iufU8tU.jpg",4:"https://i.imgur.com/iufU8tU.jpg",5:"https://i.imgur.com/iufU8tU.jpg",6:"https://i.imgur.com/iufU8tU.jpg",7:"https://i.imgur.com/iufU8tU.jpg",
            8:"https://i.imgur.com/iufU8tU.jpg",9:"https://i.imgur.com/iufU8tU.jpg",10:"https://i.imgur.com/iufU8tU.jpg",11:"https://i.imgur.com/iufU8tU.jpg",12:"https://i.imgur.com/iufU8tU.jpg",13:"https://i.imgur.com/iufU8tU.jpg",14:"https://i.imgur.com/iufU8tU.jpg"}
labMappingTable = {1:"行動數位服務實驗室(MA 402)",2:"高科技產業研究實驗室(T2 409)",3:"人力資源管理實驗室(MA 403)",4:"企業分析與平價實驗室(MA 504)",5:"企業營運管理實驗室(T2 302-2)",6:"電子商務實驗室(T2 409)",7:"行銷與人工智慧實驗室(MA 504)",
                   8:"口碑行銷實驗室(MA 401)",9:"張譯尹教授的實驗室(T2 410)",10:"數據分析與決策實驗室(T2 302-2)",11:"黃美慈教授的實驗室(MA 403)",12:"全球行銷創新實驗室(MA 402)",13:"行為科學管理實驗室(T2 410)",14:"腦科學行銷策略實驗室(MA 401)"}

labPro = {1:"曾盛恕 教授",2:"張順教 教授",3:"葉穎蓉 教授",4:"郭啟賢 教授",5:"鄭仁偉 教授",6:"欒斌 教授",7:"吳克振 教授",
          8:"林孟彥 教授",9:"張譯尹 教授",10:"呂志豪 教授",11:"黃美慈 教授",12:"盛麗慧 教授",13:"謝亦泰 教授",14:"王蕙芝 教授"}

lab = {1:"『目前實驗室人數』"+"\n"+"6~10人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一下開始，碩二上結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 中介效果與調節效果"+"\n"+"2. 服務創新"+"\n"+"3. 科技接受模式"+"\n"+"『實驗室氣氛』"+"\n"+"1. 輕鬆愉快"+"\n"+"2. 開心"+"\n"+"3. 無壓力"+"\n"+"『實驗室活動』"+"\n"+"1. 期初聚餐"+"\n"+"2. 期末聚餐"+"\n"+"『可習得的專業』"+"\n"+"1. SPSS"+"\n"+"2. 線性規劃"+"\n"+"*實驗室與盛麗慧教授的學生共用", 
       2:"『目前實驗室人數』"+"\n"+"6~10人"+"\n"+"『固定座位』"+"\n"+"是，每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"依教授安排"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"4~6天"+"\n"+"『主要研究方向』"+"\n"+"AI結合人資"+"\n"+"『實驗室氣氛』"+"\n"+"1. 融洽"+"\n"+"2. 友愛"+"\n"+"3. 互助"+"\n"+"*過年過節要有祝賀詞(給教授)"+"\n"+"『實驗室活動』"+"\n"+"1. 教師節慶祝"+"\n"+"2. 送舊"+"\n"+"『可習得的專業』"+"\n"+"1. 科技業的基礎知識及脈絡了解"+"\n"+"2. 理解code"+"\n"+"*實驗室與欒斌教授的學生共用", 
       3:"『目前實驗室人數』"+"\n"+"6~10人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一下開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 職家(職業家庭的衝突與增益)"+"\n"+"2. 不文明行為(主管對員工的不當對待、辱罵等)"+"\n"+"\n"+"『實驗室氣氛』"+"\n"+"1. 融洽"+"\n"+"2. 不拘謹"+"\n"+"3. 會相約吃飯、逛街"+"\n"+"『實驗室活動』"+"\n"+"1. 導生聚"+"\n"+"2. 教師節慶祝"+"3. 慶生"+"\n"+"*實驗室與黃美慈教授的學生共用", 
       4:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"是，但並非每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 稅法與稅務"+"\n"+"2. 企業評價"+"\n"+"\n"+"『實驗室氣氛』"+"\n"+"1. 融洽"+"\n"+"2. 自在"+"\n"+"*較少人待在實驗室"+"\n"+"『實驗室活動』"+"\n"+"1. 期初聚餐"+"\n"+"2. 期末聚餐"+"/n"+"『可習得的專業』"+"\n"+"Stata"+"\n"+"*實驗室與吳克振教授的學生共用",
       5:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 組織管理"+"\n"+"2. 員工對上司的諫言"+"\n"+"\n"+"『實驗室氣氛』"+"\n"+"1. 輕鬆"+"\n"+"2. 會相約出去玩"+"\n"+"『實驗室活動』"+"\n"+"聚餐"+"\n"+"*實驗室與呂志豪教授的學生共用",
       6:"『目前實驗室人數』"+"\n"+"16人以上"+"\n"+"『固定座位』"+"\n"+"是，每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 數位廣告"+"\n"+"2. 隱私"+"\n"+"3. 電商"+"\n"+"『實驗室氣氛』"+"\n"+"1. 活潑"+"\n"+"2. 歡樂"+"\n"+"3. 自由"+"\n"+"『實驗室活動』"+"\n"+"1. 慶生"+"\n"+"2. 聚餐"+"\n"+"3. 相見歡"+"\n"+"4. 小畢典"+"\n"+"5. 教師節。萬聖節，感恩節。聖誕節慶祝"+"\n"+"*碩一需選一個活動當主辦"+"\n"+"『可習得的專業』"+"\n"+"1. GA"+"\n"+"2. Python"+"\n"+"*實驗室與張順教教授的學生共用",
       7:"『目前實驗室人數』"+"\n"+"6~10人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"每週一次"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 消費者行為與行銷"+"\n"+"2. 人工智慧"+"\n"+"3. 心理學"+"\n"+"『實驗室氣氛』"+"\n"+"1. 自由"+"\n"+"2. 無壓力"+"\n"+"3. 樂於分享"+"\n"+"『實驗室活動』"+"\n"+"1. 老人陪伴(兩週一次例行活動)"+"\n"+"2. 小迎新"+"\n"+"『可習得的專業』"+"\n"+"1. Python"+"\n"+"*實驗室與郭啟賢教授的學生共用",
       8:"『目前實驗室人數』"+"\n"+"16人以上"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"每週一次"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 口碑行銷"+"\n"+"2. Google評論的影響力分析"+"\n"+"『實驗室氣氛』"+"\n"+"1. 樂於助人"+"\n"+"2. 相互分享"+"\n"+"3. 凝聚力不高(人多)"+"\n"+"『實驗室活動』"+"\n"+"1. 晨會(每週一次例行活動)"+"\n"+"2. 雙週會(兩週一次例行活動)"+"\n"+"『可習得的專業』"+"\n"+"1. Python"+"\n"+"2. Word"+"\n"+"*有第一指導教授與第二指導教授""\n"+"*實驗室與王蕙芝教授的學生共用",
       9:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"是，每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一下開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 組織(職能怎麼影響員工與主管間的關係)"+"\n"+"2. 動態能力理論"+"\n"+"3. AMO架構(能力動機跟激化)"+"\n"+"『實驗室氣氛』"+"\n"+"自由"+"\n"+"*大家很少同時待在實驗室"+"\n"+"『實驗室活動』"+"\n"+"1. 聚餐"+"\n"+"2. 團康(跟其他家合辦)"+"\n"+"『可習得的專業』"+"\n"+"1. 結構方程式"+"\n"+"2. 文字分析"+"\n"+"*實驗室與謝亦泰教授的學生共用",
       10:"『目前實驗室人數』"+"\n"+"11~15人"+"\n"+"『固定座位』"+"\n"+"是，每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一上開始，碩二上結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"4~6天"+"\n"+"『主要研究方向』"+"\n"+"1. 供應鏈管理"+"\n"+"2. 人力資源管理"+"\n"+"3. 路徑規劃"+"\n"+"『實驗室氣氛』"+"\n"+"1. 友善"+"\n"+"2. 溫暖。有人情味"+"\n"+"3. 資訊共享"+"\n"+"『實驗室活動』"+"\n"+"1. 讀書會(寒暑假例行活動)"+"\n"+"2. 聚餐"+"\n"+"3. 玩桌遊"+"\n"+"4. 打籃球"+"\n"+"5. 生日。教師節。聖誕節慶祝"+"\n"+"『可習得的專業』"+"\n"+"1. Python"+"\n"+"2. 演算法"+"\n"+"3. 聊天機器人"+"\n"+"*實驗室與鄭仁偉教授的學生共用",
       11:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩二上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 人資訓練"+"\n"+"2. 員工體驗"+"\n"+"3.學習(Team Learning。E-Learning)"+"\n"+"『實驗室氣氛』"+"\n"+"1. 輕鬆"+"\n"+"2. 無壓力"+"\n"+"『實驗室活動』"+"\n"+"1. 雙週會(兩週一次例行活動)"+"\n"+"2. 聚餐"+"\n"+"*實驗室與葉穎蓉教授的學生共用",
       12:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"是，但並非每個人都有"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"無固定"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"4~6天"+"\n"+"『主要研究方向』"+"\n"+"1. 破壞式創新"+"\n"+"2. 全球創新(企業的創新能力)"+"\n"+"『實驗室氣氛』"+"\n"+"1. 融洽"+"\n"+"2. 自由"+"\n"+"3. 互動較少"+"\n"+"『實驗室活動』"+"\n"+"聚餐(教授課程結束後，會邊開會邊聊天)"+"\n"+"『可習得的專業』"+"\n"+"1. SPSS"+"\n"+"2. 結構方程式"+"\n"+"*實驗室與曾盛恕教授的學生共用",
       13:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"是，每個人都有"+"『開會時間(以多數人為主)』"+"\n"+"兩週一次"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一上開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"1. 職場抱怨"+"\n"+"2. 人資的不確定性"+"\n"+"3. 行為研究"+"\n"+"『實驗室氣氛』"+"\n"+"1. 輕鬆"+"\n"+"2. 歡樂"+"\n"+"3. 和諧"+"\n"+"『實驗室活動』"+"\n"+"1. 期初。期末。教師節聚餐"+"\n"+"2. 春遊(爬山。吃飯)"+"\n"+"『可習得的專業』"+"\n"+"1. SPSS"+"\n"+"2. SEM"+"\n"+"3. 文字探勘"+"\n"+"*實驗室與張譯尹教授的學生共用",
       14:"『目前實驗室人數』"+"\n"+"1~5人"+"\n"+"『固定座位』"+"\n"+"否"+"\n"+"『開會時間(以多數人為主)』"+"\n"+"每週一次"+"\n"+"『論文時程(以多數人為主)』"+"\n"+"碩一下開始，碩二下結束"+"\n"+"『待在實驗室的時間(以多數人為主)』"+"\n"+"1~3天"+"\n"+"『主要研究方向』"+"\n"+"腦科學"+"\n"+"『實驗室氣氛』"+"\n"+"1. 冷清"+"\n"+"2. 互動較少"+"\n"+"\n"+"『可習得的專業』"+"\n"+"1. 剪輯影片"+"\n"+"2. 拍攝技巧"+"\n"+"3. 腦波軟體實驗操作"+"\n"+"*實驗室與林孟彥教授的學生共用"}

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
                            label='有關指導教授',
                            text=lab[index],
                            data='notResponse'
                        ),
                        PostbackTemplateAction(
                            label='有關實驗室',
                            text=lab[index],
                            data='notResponse'
                        ),
                        PostbackTemplateAction(
                            label='有關合適的人選',
                            text=lab[index],
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
    sims = model.docvecs.most_similar([inferred_vector],topn=5)
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