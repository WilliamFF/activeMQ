#!/usr/bin/python
"""
This script connects to activemq queues.jsp and check for al queues.

If some queue has no consumer running, it raises an alert (unless is included in 'no_consumer' tuple)
If some queue has more unprocessed items than queue_limit, raises an alert
or it returns an ok status
requires urllib2, xml.etree
Modify the variables with the right connection and credentials
"""
###

import sys
import xml.etree.ElementTree as etree
import urllib2

# change queue_limit:
queue_limit = 10

# change consumerless queues:
no_consumer = ('')

# connection options:
activemq_url = "activemq.example.com:8161"
activemq_user = "user"
activemq_pass = "pass"
activemq_jsp_url = "http://activemq.example.com:8161/admin/xml/queues.jsp"
###

critical = 0
critical_exit = []

passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, activemq_url, activemq_user, activemq_pass)
urllib2.install_opener(urllib2.build_opener(urllib2.HTTPBasicAuthHandler(passman)))

req = urllib2.Request(activemq_jsp_url)
f = urllib2.urlopen(req)
data = f.read()

tree = etree.fromstring(data)

all_queues = tree.findall('queue')
all_stats = tree.findall('queue/stats')

lista = 0
monitor = []

while lista < len(all_queues):
	monitor += [[all_queues[lista].get('name')] + [all_stats[lista].get('consumerCount')] + [all_stats[lista].get('enqueueCount')] + [all_stats[lista].get('dequeueCount')],]
	lista += 1

i = 0
while i < len(monitor):
    if monitor[i][0] in no_consumer:
      del monitor[i]
      i = 0
    i+=1

consumer = []
queue_dif = []
i = 0
while i < len(monitor):
    if monitor[i][1] not in no_consumer:
        if monitor[i][1] != '1':
            consumer += [monitor[i][0]]
        else:
            process_count = int(monitor[i][2]) - int(monitor[i][3])
            if process_count > queue_limit:
                queue_dif += [monitor[i][0], process_count]
    i +=1

if consumer != []:
    critical += 1
    critical_exit += consumer

if queue_dif != []:
    critical += 2
    critical_exit += queue_dif

elif critical == 0:
    print "All queues running and processing"
    print monitor
    sys.exit(0)
elif critical == 1:
    print critical_exit
    print monitor
    sys.exit(2)
elif critical == 2:
    print critical_exit
    print monitor
elif critical == 3:
    print "Consumers "
    print monitor
    sys.exit(2)
