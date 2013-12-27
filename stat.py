import pymongo
from bson import Code


client = pymongo.connection.Connection()
db = client.ad_server_01

cursor = db.statistics.group(
   key={'code_id': 1},
   condition={},
   reduce=Code('function(obj, prev) { prev.count++; }'),
   initial={'count': 0}
)

print '=== Statistics ===\n'
for obj in cursor:
    obj_name = db.codes.find_one(obj['code_id'])['name']
    print "ID: %s" % obj['code_id']
    print "Name: %s" % obj_name
    print "Impressions: %s" % int(obj['count'])
    print