#!/usr/bin/python
import subprocess
import re
from pypuppetdb import connect

def show_report(name, data):
    print name+':'
    if data:
        for k in sorted(data.keys()):
            print '    %-30s %s' % (k, data[k])
    else:
        print '    none'
    print

def get_unreported(db):
    data = {}
    for n in db.nodes(unreported=24, with_status=True):
        if n.status == 'unreported':
            if n.unreported_time:
                data[ n.name ] = n.unreported_time
            else:
                data[ n.name ] = 'unknown'
    return(data)

def get_sysupdates(db):
    data = {}
    for f in db.facts('sysupdate_count'):
        if not f.value in ('','0'):
            data[ f.node ] = f.value
    return(data)

def get_pending_certs():
    p = subprocess.Popen('puppet cert list',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    data = {}
    for line in p.stdout.readlines():
        match = re.match('^\s*"([^"]+)"\s*\(', line)
        if match:
            data[ match.group(1) ] = ''
    return(data)

#####

db = connect()

print ' '*20, "*** Puppet global daily report ***\n"
show_report('Unsigned CA requests', get_pending_certs())
show_report('Unreported nodes', get_unreported(db))
show_report('Pending system updates', get_sysupdates(db))
