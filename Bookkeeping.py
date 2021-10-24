#!/usr/bin/env python3
# coding=utf-8
from requests.api import delete
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from Command import *
from dotenv import load_dotenv
from updater import updater

load_dotenv()

# Main function
def main():
    

# 一般指令

    # 開啟與幫助
    updater.dispatcher.add_handler(CommandHandler('start', startbot))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    

    updater.dispatcher.add_handler(CommandHandler('cd', cd))
    updater.dispatcher.add_handler(CommandHandler('list', ls))
    updater.dispatcher.add_handler(CommandHandler('ls', ls))
    updater.dispatcher.add_handler(CommandHandler('undo', undo))

    updater.dispatcher.add_handler(CommandHandler('add', add))
    updater.dispatcher.add_handler(CommandHandler('mkdir', mkdir))
    updater.dispatcher.add_handler(CommandHandler('rmdir', rmdir))
    

    # 備份與還原
    updater.dispatcher.add_handler(CommandHandler('dump', dump))
    updater.dispatcher.add_handler(CommandHandler('load', load))
    updater.dispatcher.add_handler(CommandHandler('restore', load))
    

# 其他類型回覆

    # # 文字
    # updater.dispatcher.add_handler(MessageHandler(Filters.text, getText))
    
    # # 圖片(經 Telegram 壓縮)
    # updater.dispatcher.add_handler(MessageHandler(Filters.photo, getPhoto))
    
    # # 檔案 或 未經壓縮圖片
    # updater.dispatcher.add_handler(MessageHandler(Filters.document, getFile))
    
    # # 按鈕
    # updater.dispatcher.add_handler(CallbackQueryHandler(callback))


# Bot Start
    print("Bot Server Running...")

    updater.start_polling()
    updater.idle()


# HEAD OF PROGRAM
if __name__ == '__main__':
    main()

