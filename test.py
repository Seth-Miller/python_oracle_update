#!/usr/bin/python

import sys
import os
import cx_Oracle
import yaml



def parse_line(input):
    key, value = input.split('=')
    key = key.strip()  # handles key = value as well as key=value
    value = value.strip()
    return {key : value}


def read_config(configfile):
   locresource = {}
   loclist = []
   with open(configfile) as fp:
      for line in fp:
         line = line.strip()
         if line:
            locresource.update(parse_line(line))
         else:
            loclist.append(locresource)
            locresource = {}
   loclist.append(locresource)
   return loclist

def read_yaml(parmfile):
   locstream = file(parmfile, 'r')
   locyaml = yaml.load(locstream)
   return locyaml

def get_instances(config):
   locinstances = {}
   for locelement in config:
      if locelement['CARDINALITY_ID'] == '1':
         locinstances[locelement['DB_UNIQUE_NAME']] = []
         for key, value in locelement.iteritems():
            if key.split('(')[0] == 'USR_ORA_INST_NAME@SERVERNAME':
               locinstances[locelement['DB_UNIQUE_NAME']].append({'instance' : value, 'node' : key.split('(')[1].split(')')[0]})
   return locinstances

mylist = read_config('example.cfg')

myyaml = read_yaml('parameters.yaml')

myinstances = get_instances(mylist)



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
