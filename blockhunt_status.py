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
        data = {"stats": { "total": 0,"blocksize_min": 20, "streak_days": 0, "home_hunts_total": 0,"mobile_hunts_total": 0, "aborted_hunts_total": 0, "aborted_home_hunts": 0, "aborted_mobile_hunts": 0, "last_hunt":"none", "longest_streak": 0},"hunts": [ ]}
        with open('blockhunts.json', "w+") as outfile:
            json.dump(data,outfile, indent=4)

def loadjson():
    with open('blockhunts.json') as json_file:
        d = json.load(json_file)
    return d

def writejson(json_data):
    with open('blockhunts.json', '+w') as json_file:
        json.dump(json_data, json_file, indent=4)

def addhunt(json_data, location, success):
    now = datetime.datetime.now()
    strtime = str(now.strftime("%d-%m-%Y %H:%M"))
    json_data["hunts"].append({"date": strtime,"location": location, "success": str(success)})  
    if location == "mobile":
        if success != "succeeded":
            json_data["stats"]["aborted_mobile_hunts"] += 1
        else: 
            json_data["stats"]["mobile_hunts_total"] +=1
    elif location == "home":
        if success != "succeeded":
            json_data["aborted_home_hunts"] += 1
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


    writejson(json_data) 
    

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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
