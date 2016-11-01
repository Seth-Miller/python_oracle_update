#!/usr/bin/python

import sys
import os
import cx_Oracle
import yaml


debug_on = True
dry_run = True


def debug(message=''):
   if debug_on:
      print(message)

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

def display_sp_parameter(cursor, dbname, dbparm):
   locdml = """
            select sid, name, value
            from v$spparameter
            where name = :arg1
            """
   cursor.execute(locdml,
           arg1 = dbparm)
   print('{0:10s} {1:10s} {2:30s} {3:80s}'.format('DBNAME', 'SID', 'PARAMETER', 'VALUE'))
   for locresult in cursor:
      print('{0:10s} {1:10s} {2:30s} {3:80s}'.format(dbname, locresult[0], locresult[1], locresult[2]))





if dry_run:
   print('================================================================')
   print('Dry run mode is enabled, no changes will be name to the database')
   print('================================================================')

mylist = read_config('example.cfg')

myyaml = read_yaml('parameters.yaml')

myinstances = get_instances(mylist)

print

for mydatabase in myyaml['databases_to_update']:
   updatedb = mydatabase['name']
   username = mydatabase['username']
   password = mydatabase['password']

   try:
      stophere = mydatabase['stop']
   except:
      stophere = False

   try:
      connectdb = mydatabase['connection']
   except:
      connectdb = mydatabase['name']

   print('Updating database ' + updatedb)
   debug()
   debug('Connecting with username ' + username)
   debug('Connection name is ' + connectdb)

   connection = cx_Oracle.connect (user = username, password = password, dsn = connectdb, mode = cx_Oracle.SYSDBA)
   curdb = connection.cursor()

   for instname in myinstances[updatedb]:
      updateinstance = instname['instance']
      updatenode = instname['node']
      updateinterconnects = ':'.join(myyaml['cluster_nodes'][instname['node']]['cluster_interconnects'])
      ddl = 'alter system set cluster_interconnects = "' + updateinterconnects + '" scope = spfile sid = \'' + updateinstance + '\''

      debug()
      debug('   Instance ' + updateinstance  + ' on node ' + updatenode + ' will be updated with cluster_interconnect "' + updateinterconnects + '"')
      debug('   DDL: ' + ddl)

      if not dry_run:
         curdb.execute(ddl)

   print
   display_sp_parameter(curdb, updatedb, 'cluster_interconnects')

   if stophere:
      print
      print('Encountered stop')
      print

   print('================================================================')
   print('================================================================')
   print

   if stophere:
      exit(0)

