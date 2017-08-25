#! /usr/bin/env python

import sys,json,os

_out_ = "_output.root"
_tag_ = sys.argv[1]
print(_tag_)

_file_ = open("out")
jobs = json.load(_file_)
for job in jobs:
    if (job["status"] == "done"):
        #print(job["status"], job["taskname"],job["taskname"][:-1]+_out_)
        if _tag_ in job["taskname"]:
            print(job["taskname"][:-1]+_out_)

