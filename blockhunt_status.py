#! /usr/bin/python

import json
import os.path
import sys
import datetime
import argparse
from shutil import copyfile
import shutil
def inithunts():
    if (os.path.isfile('blockhunts.json') is not True):
        # Create the blockhunts file
        data = {"stats": { "total": 0,"blocksize_min": 20, "streak_days": 0, "home_hunts_total": 0,"mobile_hunts_total": 0, "aborted_hunts_total": 0, "aborted_hunts_home": 0, "aborted_hunts_mobile": 0, "last_hunt":"none", "longest_streak": 0},"hunts": [ ]}
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
    streak_days = 0
    home_hunts_total = 0
    mobile_hunts_total = 0
    aborted_hunts_total = 0 
    aborted_hunts_home = 0
    aborted_hunts_mobile = 0
    last_hunt = "none"
    longest_streak = 0
    
    for hunt in json_data["hunts"]:
        print(hunt)
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
    
    json_data["stats"]["longest_streak"] = longest_streak
    return json_data


def deletelast(json_data):
    print(json_data)
    json_data["hunts"] = json_data["hunts"][:-1]
    json_data = updatestats(json_data)
    print(json_data)
    writejson(json_data)


def addhunt(json_data, location, success):
    now = datetime.datetime.now()
    strtime = str(now.strftime("%d-%m-%Y %H:%M"))
    json_data["hunts"].append({"date": strtime,"location": location, "success": str(success), "streak": 1})  
    if location == "mobile":
        if success != "succeeded":
            json_data["stats"]["aborted_hunts_mobile"] += 1
        else: 
            json_data["stats"]["mobile_hunts_total"] +=1
    elif location == "home":
        if success != "succeeded":
            json_data["stats"]["aborted_hunts_home"] += 1
        else:
            json_data["stats"]["home_hunts_total"] += 1
    if success == "succeeded": 
        json_data["stats"]["total"] += 1 
        delta = deltadays(json_data["stats"]["last_hunt"],strtime )
        if delta == 1:
            json_data["stats"]["streak_days"] += 1
        else:
            json_data["stats"]["streak_days"] = 0
    
        if json_data["stats"]["longest_streak"] < json_data["stats"]["streak_days"]:
            json_data["stats"]["longest_streak"] = json_data["stats"]["streak_days"]
        json_data["stats"]["last_hunt"] = strtime
    else:
        json_data["stats"]["aborted_hunts_total"] += 1
    # save the streak day count to the hunt (last in list since we appended) 
    json_data["hunts"][-1]["streak"] = json_data["stats"]["streak_days"] 
    
    writejson(json_data) 
    
# Return 0 if day1 and day2 are the same
# Return positive number (delta days between day1 and day2) if day2 is more recent than day1
# Return negative if day1 is more recent.
def deltadays(day_str1, day_str2):
    if(day_str1 == "none"):
        return 1
    date_format="%d-%m-%Y %H:%M"
    d1 = datetime.datetime.strptime(day_str1, date_format)
    d2 = datetime.datetime.strptime(day_str2, date_format)
    delta = d2 - d1
    return delta.days

def getstats(option):
    data = loadjson()
    if(option == "all"):
        return data["stats"]
    if(option == "total"):
        return data["stats"]["total"]
    if(option == "total_home"):
        return data["stats"]["home_hunts_total"]
    if(option == "total_mobile"):
        return data["stats"]["mobile_hunts_total"]


def backuphunts(method):

    if (os.path.isfile('blockhunts.json')):
        if method == "copy":
            copyfile('blockhunts.json', 'backup_copy_blockhunts' + datetime.datetime.now().isoformat() + '.json')
        if method == "move":
            shutil.move('blockhunts.json', 'blockhunts' + datetime.datetime.now().isoformat() + '.json')
    else:
        print("no blockhunts.json found")

def main():
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
        choices=['all', 'total', 'total_home', 'total_mobile'],
        help='Get Stats about blockhunts')

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
        inithunts()
        addhunt(loadjson(), args.location, args.success)    
    elif args.subcommand == 'stats':
        print(getstats(args.option))  
    elif args.subcommand == 'backup':
        backuphunts(args.method)
    elif args.subcommand == 'delete':
        deletelast(loadjson())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
