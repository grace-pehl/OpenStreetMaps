# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 14:49:10 2015

@author: Pehl
"""

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client.pehl

'''
# find number of unique users
pipeline = "[{"$group":{"_id":"$created.uid", "count":{"$sum":1}}}]"
result = db.osm.aggregate(pipeline)
n = 0
for document in result:
    n += 1
print n
'''
# find top 5 users

pipeline = "[{"$group" :{ "_id" : "$created.user",
                          "count" : {"$sum" : 1 }}},
             { "$sort" : { "count" : -1 }},
             { "$limit" : 5}]"
result = db.osm.aggregate(pipeline)

for document in result:
    print(document)
