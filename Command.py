from logging import exception
from sqlite3.dbapi2 import Time
from dosdefence import *
from os import getenv
from function import *
import sqlite3
from interact_with_imgur import uploadAndGetPhoto
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random
import time

# preparation
userStatus = {}
userUpdate = {}
map_charroom_folder = {}
map_undo = {}

def startbot(update, bot):
    if(isDos(update)): return
    Send(update, "hihi, 我是{0}".format(GetConfig("name")))
    Send(update, "按 /help 取得說明")

def help(update, bot):
    if(isDos(update)): return
    Send(update, GetConfig("helpText"))

def cd(update, bot):
    chat_id = update.message.chat_id

    text = update.message.text.split(' ')
    if len(text) ==2:
        text = text[1]
    else:
        text = ''
    map_charroom_folder.update({chat_id: text})

    if text == '':
        Send(update, '切換至 帳本列表')
    else:
        Send(update, '切換至帳本 {0}'.format(text))

def ls(update, bot):
    chat_id = update.message.chat_id

    if chat_id not in map_charroom_folder or map_charroom_folder[chat_id]=='':
        sql = sqlite3.connect('Database.db')
        cur = sql.cursor()
        cur.execute('Select folder from Data where chatroomid = {0}'.format(chat_id))
        data = cur.fetchall()
        if len(data) == 0:
            Send(update, '目前沒有帳本')
        else:
            Send(update, '目前帳本:\n'+ '\n'.join(data))
    else:
        sql = sqlite3.connect('Database.db')
        cur = sql.cursor()
        folderText = ''
        if chat_id in map_charroom_folder:
            folderText = pureString(map_charroom_folder[chat_id])
        else:
            folderText = '*'
        cur.execute("select * from Data where folder GLOB '{0}' and chatroomid = '{1}'".format(folderText, chat_id))
        fetchdata = cur.fetchall()
        cur.close()
        sql.close()


        data = []
        for i in fetchdata:
            data.append([i[1], i[2], i[3], i[4]])
        data = sortList(data)
        Send(update, '目前帳本：{0}'.format(map_charroom_folder[chat_id]))
        if len(data) == 0:
            Send(update, '沒有紀錄')
        else:   
            ret = ''
            for i in data:
                ret += '{0} 欠 {1} {3} {2}元\n'.format(i[0], i[1], i[2], i[3])
            Send(update, ret)

def sortList(data):
    return data

def add(update, bot):
    chat_id = update.message.chat_id
    folder = ''
    if chat_id in map_charroom_folder:
        folder = pureString(map_charroom_folder[chat_id])
    else:
        Reply(update, '請先切換帳本(/cd name)')
        return
    
    try:
        text = ' '.join(update.message.text.split(' ')[1:])

        sql = sqlite3.connect('Database.db')
        cur = sql.cursor()
        chat_id = update.message.chat_id
        debtor = text.split('欠')[0].replace(' ', '')
        if '我' in debtor:
            try:
                debtor = ('@' + update.message.from_user.username)
            except:
                debtor = ('@' + update.message.from_user.full_name)
            
        text = removeSpace('欠'.join(text.split('欠')[1:]))
        try:
            creditor, content, val = text.split(' ')
            val = int(val)
            print(creditor, content, val)
        except:
            Reply(update, '格式錯誤：我欠 @id 午餐 50')
            return

        timeNow = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("Insert into Data values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"
            .format(chat_id, debtor, creditor, val, content, folder, timeNow ))
        cur.execute("Insert into Data values('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')"
            .format(chat_id, debtor, creditor, val, content, folder, timeNow ))
        deleteText = "Delete from Data where time = '{0}' and chatroomid = '{1}'".format(timeNow, chat_id)
        map_undo.update({chat_id:deleteText})

        sql.commit()
        cur.close()
        sql.close()

        Reply(update, '記錄完成')
    except:

        Reply(update, '記錄失敗')
    

def removeSpace(text: str):
    ret = ''
    i = 0
    for i in range(len(text)):
        if text[i] !=' ':
            break
    return text[i:]

def undo(update, bot):
    chat_id = update.message.chat_id
    if chat_id in map_undo:
        sql = sqlite3.connect('Database.db')
        cur = sql.cursor()
        cur.execute(map_undo[chat_id])
        sql.commit()
        cur.close()
        sql.close()

        del map_undo[chat_id]
        Send(update, '還原上一步')
    else:
        Send(update, '沒有上一步')

def dump(update, bot):
    if(isDos(update)): return
    userID = getUserID(update)
    if not isDeveloper(userID, False): return
    
    sql = sqlite3.connect( getenv("DATABASENAME") ) 
    cur = sql.cursor()
    cur.execute('select * from Data')
    data = cur.fetchall()
    ret = ''
    for i in data:
        for j in i:
            ret += j + ','
        ret += '\n'
    cur.close()

    cur = sql.cursor()
    cur.execute('select * from Config')
    data = cur.fetchall()
    ret += '\n'
    for i in data:
        for j in i:
            ret += j + ','
        ret += '\n'
    cur.close()
    sql.close()

    Send(update, ret)
    Send(update, '請妥善保管上則訊息\n使用 /load 可以還原備份檔')

def load(update, bot):
    if(isDos(update)): return
    userID = getUserID(update)
    if not isDeveloper(userID, False): return

    userStatus.update({userID:"waitLoad"})
    Reply(update, '請輸入還原訊息', True)
    

