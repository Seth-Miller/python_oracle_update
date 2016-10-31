#!/usr/bin/python

import sys
import os
import cx_Oracle
import yaml
from pprint import pprint



def parse_line(input):
    key, value = input.split('=')
    key = key.strip()  # handles key = value as well as key=value
    value = value.strip()
    return {key : value}

myresource = {}
mylist = []
myinstances = {}

with open('example.cfg') as fp:
   for line in fp:
      line = line.strip()
      if line:
         myresource.update(parse_line(line))
      else:
         mylist.append(myresource)
         myresource = {}
mylist.append(myresource)

#pprint(mylist)

for myelement in mylist:
   if myelement['CARDINALITY_ID'] == '1':
      myinstances[myelement['DB_UNIQUE_NAME']] = []
      for key, value in myelement.iteritems():
         if key.split('(')[0] == 'USR_ORA_INST_NAME@SERVERNAME':
            myinstances[myelement['DB_UNIQUE_NAME']].append({'instance' : value, 'node' : key.split('(')[1].split(')')[0]})


pprint(myinstances)


stream = file('parameters.yaml', 'r')

myyaml = yaml.load(stream)


for mydatabase in myyaml['databases_to_update']:
   updatedb = mydatabase['name']
   localsid = mydatabase['localsid']

   print('Updating database ' + updatedb)
   print('Local SID is ' + localsid)

   connection = cx_Oracle.connect (mode = cx_Oracle.SYSDBA)
   cursor = connection.cursor()
   os.environ["ORACLE_SID"] = localsid

   for instname in myinstances[updatedb]:
      updateinstance = instname['instance']
      updatenode = instname['node']
      updateinterconnects = ':'.join(myyaml['cluster_nodes'][instname['node']]['cluster_interconnects'])

      print('   Instance ' + updateinstance  + ' on node ' + updatenode + ' will be updated with cluster_interconnect "' + updateinterconnects + '"')
      ddl = 'alter system set cluster_interconnects = "' + updateinterconnects + '" scope = spfile sid = \'' + updateinstance + '\''
      print('   DDL: ' + ddl)

      cursor.execute(ddl)

   cursor.execute("""
           select sid, name, value
           from v$spparameter
           where name = :arg1
           """,
           arg1 = 'cluster_interconnects')

   for result in cursor:
      print(result)

exit ()



username = 'system'
password = 'oracle_4U'
databaseName = "rac1/orcl"

try:
   connection = cx_Oracle.connect (username,password,databaseName)
except cx_Oracle.DatabaseError, exception:
   print('Failed to connect to {0}'.format(databaseName))
   exit (1)



exit()
