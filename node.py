#!/usr/bin/python
from pypuppetdb import connect
import datetime, optparse, sys

def get_events(db, node, days=1):
    data = {}
    now = datetime.datetime.utcnow()
    for r in db.node(node).reports():
        delta = now - r.start.replace(tzinfo=None)
        if delta.days >= days:
            continue

        for e in db.events('["=", "report", "{0}"]'.format(r.hash_)):
            res = "%s[%s]" % (e.item['type'], e.item['title'])
            new = ''
            if e.item['new']:
                new = '%s' % (e.item['new'], )

            event = '%-40s %-10s %s' % (res, e.item['property'], new[:20])
            if data.has_key(event):
                data[event] += 1
            else:
                data[event] = 1
    return(data)

#####

parser = optparse.OptionParser()
parser.set_defaults(nodes=[], days=1)
parser.add_option('--days', type="int", dest='days')
(options, nodes) = parser.parse_args()

if not len(nodes):
    sys.stderr.write("Syntax: %s node1 [node2 node3...]\n" % sys.argv[0])
    sys.exit(1)

db = connect()

# get data and show report
print ' '*10, "*** Puppet node(s) report for last %i day(s) ***\n" % \
              (options.days)

data = {}
for n in nodes:
    print 'Node:', n
    for event,count in get_events(db, n, options.days).iteritems():
        if data.has_key(event):
            data[event] += count
        else:
            data[event] = count

print
if data:
    for event in sorted(data, key=data.get, reverse=True):
        print '%3ix %s' % (data[event], event)
else:
    print 'No events'
