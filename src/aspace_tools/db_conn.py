#!/usr/bin/python3

'''ArchivesSpace database connection class'''

import csv
import json
from pathlib import Path

import sshtunnel
import paramiko
import pymysql
import yaml
import pandas as pd


#add error handling, logging
#don't forget to close the connection
class DBConn():
	"""Class to connect to ArchivesSpace database via SSH and run queries."""
	def __init__(self, config_file=None, typejson=False):
		if typejson == True:
			self.config_file = self._get_config_json(config_file)
		else:
			self.config_file = self._get_config(config_file)
		self.local_sql_hostname = self.config_file['local_sql_hostname']
		self.local_sql_username = self.config_file['local_sql_username']
		self.local_sql_password = self.config_file['local_sql_password']
		self.local_sql_database = self.config_file['local_sql_database']
		self.local_sql_port = self.config_file['local_sql_port']
		self.path_to_key = self.config_file['path_to_key']
		self.pkey = paramiko.RSAKey.from_private_key_file(self.path_to_key)
		self.sql_hostname = self.config_file['sql_hostname']
		self.sql_username = self.config_file['sql_username']
		self.sql_password = self.config_file['sql_password']
		self.sql_database = self.config_file['sql_database']
		self.sql_port = self.config_file['sql_port']
		self.ssh_host = self.config_file['ssh_host']
		self.ssh_user = self.config_file['ssh_user']
		self.ssh_port = self.config_file['ssh_port']
		self.conn = self._start_conn()

	def _get_config_json(self, cfg):
		if cfg != None:
			return json.load(open(cfg))
		else:
			return json.load(open('config.json'))

	def _get_config(self, cfg):
		"""Gets config file"""
		if cfg != None:
			if type(cfg) is str:
				#if you pass it an open file it will just return the open file
				cfg = yaml.load(open(cfg, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
		else:
			cfg = yaml.load(open(str(Path.home()) + '/config.yml', 'r', encoding='utf-8'), Loader=yaml.FullLoader)
		return cfg

	def _start_conn(self):
		"""Starts the connection."""
		connect = pymysql.connect(host=self.local_sql_hostname, user=self.local_sql_username, passwd=self.local_sql_password, db=self.local_sql_database, port=self.local_sql_port, charset="utf8mb4")
		return connect

	def _start_conn_ssh(self):
		"""Starts the connection."""
		tunnel = sshtunnel.SSHTunnelForwarder((self.ssh_host, self.ssh_port), ssh_username=self.ssh_user, ssh_pkey=self.pkey, remote_bind_address=(self.sql_hostname, self.sql_port))
		tunnel.start()
		conn = pymysql.connect(host='127.0.0.1', user=self.sql_username, passwd=self.sql_password, db=self.sql_database, port=tunnel.local_bind_port)
		return conn, tunnel

	#what is the point of creating a pandas dataframe and then converting to a list? wouldn't that take longer?? Yeah.
	def run_query_df(self, query):
		"""Runs a query. Returns a pandas dataframe"""
		data = pd.read_sql_query(query, self.conn)
		return data

	def write_query_df(self, query, filename):
		data = pd.read_sql_query(query, self.conn)
		data.to_csv(filename, index=False)
		return filename

	def run_query_gen(self, query):
		cursor = self.conn.cursor(pymysql.cursors.SSCursor)
		cursor.execute(query)
		#I think I actually just want to return the fetchall_unbuffered()
		#object and then loop through that elsewhere. In the parse_dates
		#function I'd need another helper that basically does the below...
		return cursor.fetchall_unbuffered(), [row[0] for row in cursor.description]
		# for result in cursor.fetchall_unbuffered():
		# 	yield result

	#why is the create time stuff a datetime object???
	def run_query_list(self, query):
		cursor = self.conn.cursor()
		cursor.execute(query)
		#I think this works? https://stackoverflow.com/questions/17861152/cursor-fetchall-vs-listcursor-in-python
		return list(cursor), [row[0] for row in cursor.description]

	def run_query_no_return(self, query):
		cursor = self.conn.cursor()
		cursor.execute(query)	

	def close_conn(self):
		"""Close both db connection and ssh server. Must do this before quitting Python.
		Need to find a way to do this even if user does not call method."""
		self.conn.close()

	#This works well, but not if the query data requires additional processing
	def write_output(self, query_data, output_dir, filename):
		"""Writes the query output to a CSV file."""
		column_list = list(query_data.columns)
		datalist = query_data.values.tolist()
		newfile = open(output_dir + '/' + filename + '_results.csv', 'a', encoding='utf-8', newline='')
		writer = csv.writer(newfile)
		writer.writerow(column_list)
		writer.writerows(datalist)
		newfile.close()

	#Should do the cgi thing to process HTML tags and remove
