#!/usr/bin/env python3

# Author: Durai Murugan Sakthivadivel <durais@netapp.com>
# Role: Professional Services Consultant

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.objectid import ObjectId
from prettytable import PrettyTable

dbclient = ""
ApiTkn = ""
Url = ""


def prnt_table(docs):
    tbl = PrettyTable()
    tbl.field_names = ["VM_Name", "OS", "Processors", "Power_State", "Power_Off_Days", "Capacity_Total", "Capacity_Used", "ESXi_Host"]
    for doc in docs['data']:
        tbl.add_row([(str(doc['VM_Name']))[0:30],(str(doc['OS']))[0:30],doc['Processors'],doc['Power_State'],doc['Power_Off_Days'],doc['Capacity_Total'],doc['Capacity_Used'],doc['ESXi_Host']])
    print(tbl)


def update_db(data):
    global dbclient
    mclient = MongoClient(dbclient)
    db = mclient.cloud_insight
    col = db.vm_pwroff
    reslt = col.insert_one(data)
    print(reslt)
    docs = col.find_one({"_id": ObjectId(reslt.inserted_id)})
    prnt_table(docs)


def data_collector():
    global ApiTkn
    global Url
    DateRng = input("Enter no.of day to check for PowerOff State: ")
    DateCmp = (datetime.now() - timedelta(int(DateRng))).strftime("%Y-%m-%d %X")
    RptDic = {"data":[]}
    OutRslt = ""
    headers = {'X-CloudInsights-ApiKey': ApiTkn,
                 'Accept': 'application/json'}
    try:
        response = requests.get(Url, headers=headers)
    except requests.RequestException as e:
        print("REST API invoke error: " + str(e))
    if response.status_code == 200:
        Rslt = json.loads(response.text)
        for data in Rslt['results']:
            RptData = {}
            PwroffDate = ""
            if data['powerStateChangeTime'] is not None:
                PwroffDate = (data['powerStateChangeTime']).replace("T"," ").replace("+0000","")
                PwroffDate = ["NA" if PwroffDate > DateCmp else str((datetime.now() - datetime.strptime(PwroffDate, "%Y-%m-%d %X")).days) + " days"][0]
            else:
                PwroffDate = "> Max log retention days"
            if PwroffDate != "NA":
                RptData["VM_Name"] = data['name']
                RptData["OS"] = data['os']
                RptData["Power_State"] = data['powerState']
                RptData["Power_Off_Days"] = PwroffDate
                RptData["Capacity_Total"] = [round(data['capacity']['total']['value']/1024,2) if data['capacity'].get('total') is not None else "NA"][0]
                RptData["Capacity_Used"] = [round(data['capacity']['used']['value']/1024,2) if data['capacity'].get('used') is not None else "NA"][0]
                RptData["Processors"] = data['processors']
                RptData["ESXi_Host"] = data['host']['name']
                #print(RptData)
                RptDic["data"].append(RptData)
        #prnt_table(RptDic)
        update_db(RptDic)
        # Enable below code if you want save output to json file
        #with open(os.path.join(sys.path[0], "output.json"), 'w') as f:
        #    f.write(json.dumps(RptDic))


if __name__ == "__main__":
    data_collector()
