import datetime
import requests, json, time

def update(diff = 0):
    if datetime.datetime.today().isoweekday() == 7:
        cur_time = int(time.time()) + 86400
    else:
        cur_time = int(time.time()) + 86400 * 2 - 86400 * datetime.datetime.today().isoweekday()
    
    cur_time = cur_time - cur_time % 86400
    cur_time = cur_time + diff * 604800
    cur_time = cur_time * 1000

    def get_shedule(uid):
        req = requests.get('http://oreluniver.ru/schedule//%i///%i/printschedule' % (uid, cur_time))
        data = json.loads(req.text)

        shedule = {
            "last_update": int(time.time()),
            "shedule": {}
        }

        for el in data:
            if not shedule['shedule'].get(str(el['DayWeek'])):
                shedule['shedule'][str(el['DayWeek'])] = {}
            
            shedule['shedule'][str(el['DayWeek'])][str(el['NumberLesson'])] = {
                "title" : el['TitleSubject'],
                "type" : el['TypeLesson'],
                "korpus" : el['Korpus'],
                "room" : el['NumberRoom'],
                "name_prep": "%s %s %s" % (el['Family'], el['Name'], el['SecondName'])
            }

        name_file = 'shedule/%i_%i.json' % (cur_time, uid)

        with open(name_file, 'w') as file_:
            json.dump(shedule, file_)
                    
        file_.close()

        del file_
    
    get_shedule(4933) # bs
    get_shedule(4930) # pg

if __name__ == '__main__':
    while True:
        try:
            update()
        except Exception as e:
            print(e)
            pass
        
        time.sleep(60*30)