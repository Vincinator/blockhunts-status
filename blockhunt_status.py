#! /usr/bin/python

import signal
import json
import time
import os.path
import sys
import datetime
import argparse
from shutil import copyfile
import shutil
def inithunts():
    if (os.path.isfile('blockhunts.json') is not True):
        # Create the blockhunts file
        data = {"stats": { "total": 0, "today": 0, "blocksize_min": 20, "streak_days": 0, "home_hunts_total": 0,"mobile_hunts_total": 0, "aborted_hunts_total": 0, "aborted_hunts_home": 0, "aborted_hunts_mobile": 0, "last_hunt":"none", "longest_streak": 0, "active_starttime": "none"},"hunts": [ ]}
        with open('blockhunts.json', "w+") as outfile:
            json.dump(data,outfile, indent=4)

def loadjson():
    with open('blockhunts.json') as json_file:
        d = json.load(json_file)
    return d

def writejson(json_data):
    with open('blockhunts.json', '+w') as json_file:
        json.dump(json_data, json_file, indent=4)

def updatestats(json_data):
    total = 0
    today = 0
    streak_days = 0
    home_hunts_total = 0
    mobile_hunts_total = 0
    aborted_hunts_total = 0 
    aborted_hunts_home = 0
    aborted_hunts_mobile = 0
    last_hunt = "none"
    longest_streak = 0
    todaydate = datetime.datetime.now() 
    for hunt in json_data["hunts"]:
        if hunt["location"] == "mobile":
            if hunt["success"] == "succeeded":
                total += 1
                mobile_hunts_total += 1
            else:
                aborted_hunts_total += 1
                aborted_hunts_mobile += 1
        elif hunt["location"] == "home":
            if hunt["success"] == "succeeded":
                total += 1
                home_hunts_total += 1
            else:
                aborted_hunts_total += 1
                aborted_hunts_home += 1
        if hunt["streak"] > longest_streak:
            longest_streak = hunt["streak"]
        if deltadays(gettimeformat(todaydate), hunt["date"])== 0:
            today += 1
            
        if deltadays(last_hunt, hunt["date"]) >= 0:
            if hunt["streak"] > streak_days:
                streak_days = hunt["streak"]
    json_data["stats"]["total"] = total
    json_data["stats"]["mobile_hunts_total"] = mobile_hunts_total
    json_data["stats"]["home_hunts_total"] = home_hunts_total
    json_data["stats"]["aborted_hunts_total"] =  aborted_hunts_total
    json_data["stats"]["aborted_hunts_mobile"] = aborted_hunts_mobile
    json_data["stats"]["aborted_hunts_home"] =   aborted_hunts_home
    json_data["stats"]["streak_days"] = streak_days 
    json_data["stats"]["today"] = today
    json_data["stats"]["longest_streak"] = longest_streak
    return json_data


def deletelast(json_data):
    json_data["hunts"] = json_data["hunts"][:-1]
    json_data = updatestats(json_data)
    writejson(json_data)

def gettimeformat(dt):
    return str(dt.strftime("%d-%m-%Y %H:%M:%S"))

def addhunt(json_data, location, success):
    now = datetime.datetime.now()
    strtime = str(now.strftime("%d-%m-%Y %H:%M:%S"))
    json_data["hunts"].append({"date": strtime,"location": location, "success": str(success), "streak": 1})  
    if success == "succeeded": 
        delta = deltadays(json_data["stats"]["last_hunt"],strtime )
        if delta == 1:
            json_data["stats"]["streak_days"] += 1
        elif delta != 0:
            json_data["stats"]["streak_days"] = 0
        if json_data["stats"]["longest_streak"] < json_data["stats"]["streak_days"]:
            json_data["stats"]["longest_streak"] = json_data["stats"]["streak_days"]
        json_data["stats"]["last_hunt"] = strtime
    else:
        json_data["stats"]["aborted_hunts_total"] += 1
    # save the streak day count to the hunt (last in list since we appended) 
    json_data["hunts"][-1]["streak"] = json_data["stats"]["streak_days"] 
    json_data = updatestats(json_data) 
    writejson(json_data) 
    
# Return 0 if day1 and day2 are the same
# Return positive number (delta days between day1 and day2) if day2 is more recent than day1
# Return negative if day1 is more recent.
def deltadays(day_str1, day_str2):
    if(day_str1 == "none"):
        return 1
    date_format="%d-%m-%Y %H:%M:%S"
    d1 = datetime.datetime.strptime(day_str1, date_format)
    d2 = datetime.datetime.strptime(day_str2, date_format)
    delta = (d2.date() - d1.date())
    return delta.days

def deltaseconds(time1, time2):
    if(time1 == "none"):
        return 1
    date_format="%d-%m-%Y %H:%M:%S"
    t1 = datetime.datetime.strptime(time1, date_format)
    t2 = datetime.datetime.strptime(time2, date_format)
    delta = t2- t1
    return delta

import os
def getstats(option):
    data = loadjson()
    global currentlocation
    if(option == "all"):
        return data["stats"]
    if(option == "today"):
        return data["stats"]["today"]
    if(option == "total"):
        return data["stats"]["total"]
    if(option == "total_home"):
        return data["stats"]["home_hunts_total"]
    if(option == "total_mobile"):
        return data["stats"]["mobile_hunts_total"]
    if ((option == "polybar") and (data["stats"]["active_starttime"] != "none")):
        t1 = data["stats"]["active_starttime"] 
        t2 = datetime.datetime.now()
        delta = deltaseconds(t1,gettimeformat(t2))
        countdown = datetime.timedelta(minutes=int(data["stats"]["blocksize_min"])) -delta 

        if countdown <= datetime.timedelta(0):
            stophunt( currentlocation, "succeeded")
            return countdown
        else:
            return countdown
    return ""
def stophunt( location, success):
    if(success):
        addhunt(loadjson(),location, "succeeded")
    else:
        addhunt(loadjson(),location, "aborted") 
    json_data = loadjson()
    json_data["stats"]["active_starttime"] = "none"
    writejson(json_data)

currentlocation = "none"
def signal_handler(signal, frame):
    global currentlocation
    stophunt(currentlocation, "aborted")
    print("hunt aborted")
    sys.exit(0)

def hunt(json_data, location):
    
    #global currentlocation
    #currentlocation = location
    #minutes = json_data["stats"]["blocksize_min"]
    #seconds = minutes * 60
    #while seconds:
    #    mins, secs = divmod(seconds,60)
    #    timeformat = '{:02d}:{:02d}'.format(mins,secs)
    #    print(str(timeformat))
    #    time.sleep(1)
    #    seconds -= 1
    
    #addhunt(json_data,location, "succeeded")  
   
    if(json_data["stats"]["active_starttime"] != "none"):
        return

    json_data["stats"]["active_starttime"] = gettimeformat(datetime.datetime.now())
    writejson(json_data)
    


def backuphunts(method):

    if (os.path.isfile('blockhunts.json')):
        if method == "copy":
            copyfile('blockhunts.json', 'backup_copy_blockhunts' + datetime.datetime.now().isoformat() + '.json')
        if method == "move":
            shutil.move('blockhunts.json', 'blockhunts' + datetime.datetime.now().isoformat() + '.json')
    else:
        print("no blockhunts.json found")

def main():
    os.chdir(os.path.expanduser("~/.blockhunts")) 
    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')

    #  subparser for dump
    parser_add = subparsers.add_parser('add')
    # add a required argument
    parser_add.add_argument(
        'location',
        choices=['mobile', 'home'],
        help='Blockhunt was done at home or somwhere else (mobile)?')
    parser_add.add_argument(
        'success',
        choices=['succeeded', 'aborted'],
        help='Blockhunt completed?')
    #  subparser for upload
    parser_stats= subparsers.add_parser('stats')
    # add a required argument
    parser_stats.add_argument(
        'option',
        choices=['all','polybar', 'today', 'total', 'total_home', 'total_mobile'],
        help='Get Stats about blockhunts')

    parser_hunt = subparsers.add_parser('hunt')
    
    parser_hunt.add_argument(
        'location',
        choices=['home', 'mobile'],
        help='Start a blockhunt in one location')
    
    parser_delete= subparsers.add_parser('delete')
    
    parser_delete.add_argument(
        'option',
        choices=['last'],
        help='delete blockhunts')

    parser_backup = subparsers.add_parser('backup')
    # add a required argument
    parser_backup.add_argument(
        'method',
        choices=['copy','move'],
        help='How should the backup be performed?')

    parser_init = subparsers.add_parser('init')

    args = parser.parse_args()
    if args.subcommand =='init':
        inithunts()
    elif args.subcommand == 'add':
        addhunt(loadjson(), args.location, args.success)    
    elif args.subcommand == 'stats':
        inithunts()
        print(getstats(args.option))  
    elif args.subcommand == 'backup':
        backuphunts(args.method)
    elif args.subcommand == 'delete':
        deletelast(loadjson())
    elif args.subcommand == 'hunt':
        inithunts() 
        hunt(loadjson(), args.location)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
