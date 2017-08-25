#!/usr/bin/env python
import pycurl
import os, sys, json
from StringIO import StringIO

def getJobs():
    cookie="bigpanda.cookie.txt"
    os.system("cern-get-sso-cookie -u https://bigpanda.cern.ch/ -o " + cookie)
    url="https://bigpanda.cern.ch/tasks/?tasktype=anal&display_limit=5000&username=Jing%20Li&days=60"
    c = pycurl.Curl()
    buffer = StringIO()
    c.setopt(c.URL, url)
    c.setopt(c.COOKIEFILE,cookie)
    head = ['Accept: application/json','Content-Type: application/json']
    c.setopt(c.HTTPHEADER, head)
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.perform()
    c.close()
    body = buffer.getvalue()
    jobs = json.loads(body)
    return jobs

def ifDownload(job):
    _tag_ = sys.argv[1]
    if _tag_ in job["taskname"]:
        if job["status"] == "running":
            return True
    return False

if __name__ == "__main__":
    _out_ = "_output.root"
    jobs = getJobs()
    for job in jobs:
        if ifDownload(job):
            print(job["taskname"][:-1]+_out_)
