from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage

import requests
import random
from bs4 import BeautifulSoup  
from datetime import datetime

dict_data = {
    '政治':1,
    '財經':17,
    '國際':2,
    '社會':6,
    '影劇':9,
    '體育':10,
    '3C':20,
    '時尚':30,
    '遊戲':24,
    '生活':5
}
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                try:
                    # 抓 title
                    title = []
                    u = "https://www.ettoday.net/news/news-list-2023-"+str(datetime.today().month)+"-"+str(datetime.today().day)+"-"+str(dict_data[event.message.text])+".htm"
                    res = requests.get(u)
                    soup = BeautifulSoup(res.content, "lxml")
                    soup = soup.find("div", class_="part_list_2")
                    domian = "https://www.ettoday.net"
                    a = soup.find_all("h3")[random.randint(0,len(soup.find_all("h3"))-1)]
                    p = a.a.string
                    if p != None:
                        p = p.split('／')
                        if len(p) > 1:
                            title.append(p[1])
                        else:
                            title.append(p[0])

                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        [TextSendMessage(text=title[0]), TextSendMessage(text=domian + str(a).split('<a href="')[1].split('"')[0])]
                    )
                except:
                    line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TextSendMessage(text='請輸入類別：政治、財經、國際、社會、影劇、體育、3C、時尚、遊戲、生活')
                    )
                    
        return HttpResponse()
    else:
        return HttpResponseBadRequest()