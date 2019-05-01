import json
import re
import os
import time
import random
import math
import datetime
import requests
import subprocess
import getshedule

from pyrogram import Client, api, Filters
from pyrogram.api import functions, types
from pyrogram.errors.exceptions import FloodWait, InternalServerError
from pyrogram import Client, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

name_login = 'settings/login_shedule.json'


files = [
    name_login,
]

login_shedule = {}


try:
    for cur_file in files:
        # getting name of current file
        name = cur_file.split('/')[-1].split('.')[0]
        file = open(cur_file, 'r', encoding="utf8")

        locals()[name] = json.loads(file.read())

        print('%s data has been uploaded' % name)
        file.close()
    del file, name, files
except Exception as msg:
    print('Нарушена целостность структуры. Файл: '+name)
    print(msg)
    raise SystemExit(1)


def state_wrapper(rule, key):
    if rule and rule.get(key):
        return rule.get(key)

    return False


def main():
    print('[SHEDULER] started')

    app = Client(
        login_shedule['token'],
        api_id = login_shedule["api_id"],
        api_hash = login_shedule["api_hash"]
    )


    def send_message(app, send_to, text = None, photo = None):
        while True:
            try:
                if photo:
                    if text and len(text) > 0:
                        app.send_photo(send_to, photo, text)
                    else:
                        app.send_photo(send_to, photo)
                elif text and len(text) > 0:
                    app.send_message(send_to, text)
                
                break
            except FloodWait as e:
                print('neeed wait a bit %i before send message'%e.x)
                time.sleep(e.x)
            except Exception:
                pass


    @app.on_message(Filters.incoming & Filters.command(['start']))
    def welcomer(client, message):
        data_msg = message['text'].split(' ')

        print(data_msg)

        user = message['chat']['id']
        username = '*username*'

        if message['chat']['first_name']:
            username = message['chat']['first_name']

        send_message(app, user, "Здравствуй, %s!" % username)


    @app.on_message(Filters.incoming & Filters.command('help'))
    def help(client, message):
        sender = message['chat']['id']

        app.send_message(sender, "/sh [смещение относительно текущей недели] - расписание для 61ПГ\n/shb [смещение относительно текущей недели] - расписание для 61БС")
    

    @app.on_message(Filters.incoming & Filters.command(['sh', 'shb']))
    def sheduler(client, message):
        sender = message['chat']['id']
        data_msg = message['text'].split(' ')
        diff = 0

        if len(data_msg) > 1:
            diff = int(data_msg[1])
            try:
                getshedule.update(diff)
            except Exception:
                pass

        if datetime.datetime.today().isoweekday() == 7:
            cur_time = int(time.time()) + 86400
        else:
            cur_time = int(time.time()) + 86400 * 2 - 86400 * datetime.datetime.today().isoweekday()
        
        cur_time = cur_time - cur_time % 86400
        cur_time = cur_time + diff * 604800
        cur_time = cur_time * 1000

        uid = 4930
        if data_msg[0] == '/shb':
            uid = 4933

        name_file = 'shedule/%i_%i.json' % (cur_time, uid)
        file_ = open(name_file, 'r')
        data_file = json.loads(file_.read())
        file_.close()

        answer = 'Последнее обновление **%s**\n' % (datetime.datetime.fromtimestamp(data_file['last_update']).strftime('%d-%m-%Y %H:%M:%S'))
        answer += 'Расписание на __%s - %s__\n\n' % (datetime.datetime.fromtimestamp(cur_time/1000 - 86400).strftime('%d.%m'), datetime.datetime.fromtimestamp(cur_time/1000 + 432000).strftime('%d.%m'))
        
        for day in sorted(data_file['shedule'].keys()):
            if day == '1':
                answer += 'Понедельник:\n'
            elif day == '2':
                answer += '\nВторник:\n'
            elif day == '3':
                answer += '\nСреда:\n'
            elif day == '4':
                answer += '\nЧетверг:\n'
            elif day == '5':
                answer += '\nПятница:\n'
            elif day == '6':
                answer += '\nСуббота:\n'
            
            for subj_id in sorted(data_file['shedule'][day]):
                subj = data_file['shedule'][day][subj_id]

                answer += '%s - %s (%s) [%s-%s]\n%s\n' % (subj_id, subj['title'], subj['type'], subj['korpus'], subj['room'], subj['name_prep'])
        
        send_message(app, sender, answer)


    app.run()


if __name__ == '__main__':
    main()
