#!/usr/bin/python

# Campbell-Lange Workshop
# Started by Sebastian Ritter

# Calculate the sha1sum of files in a mailstore pool and update an SQL
# database accordingly

from datetime import datetime
from hashlib import sha1
import os, sys
import psycopg2
from datetime import datetime

DB_NAME ='<dbname>'
DB_USER ='<dbuser>'
DB_PASSWORD ='<dbpass>'
DB_HOST = '<host_if_any>'

# The log table
LOG_TABLE = 'log'

# The column in the database representing the hash 
HASH_COL ='t_sha1sum'
# The column in the database representing the creation time of the mail entry 
CREATED_COL ='dt_created'
# The column in the database representing whether or not the row exists 
PROCESSED_COL ='b_processed'
# The absolute path to the directory which contains the store. 
BASE_DIR ='/mailstore/'
# The interval to go back from today (must be castable to interval)
INTERVAL = '6 weeks' 
# LOGGING FILE PATH (Make sure permissions are granted to write to this file)
LOG_FILE = '/tmp/clwmail_summer_log.txt'


def PyObject (cursor, class_type):
	'''
		This method takes a connection cursor result sequence
		and yields the objects instance of the type passed to it. Each dictionary's key,value pair
		corresponds to {'column name':row value }. '''

	# Get all returned rows from db query.
	rows = cursor.fetchall()

	# Go through each row  
	for i in range(cursor.rowcount):
		thisdict = {}
		for j in range(len(cursor.description)):
			# cursor.description[x][0] corresponds to the name of the xth column
			thisdict[cursor.description[j][0]]=rows[i][j]
		# yield the class instance of the row.
		yield  class_type(**thisdict)
				

	cursor.close()	

class SQLCreator (object):
	''' Super class which is meant to be subclassed '''
	
	# instantiated with database information
	# creates a connections and a cursor for the db.
	def __init__(self,host ='localhost', dbname ='', user='', password=''):
		self.connection =  None
		self.cursor = None  
		self.db_name = dbname

		try:
			# Create connection to database with the following details
			self.connection = psycopg2.connect('host=%s dbname=%s user=%s password=%s' % (host, dbname, user, password))
			self.cursor = self.connection.cursor()
		except psycopg2.OperationalError:
			raise

	# Executes a query on the database
	def execute(self,query, class_type = None):
		try:
			# this executes the query
			self.cursor.execute(query)
		except psycopg2.ProgrammingError:
			# If an error occured make sure we
			# rollback the cursor transaction.
			# (cursors automatically perform the begin;)
			self.rollback()
			raise
		else:
			# If query ran succesfully commit it
			self.commit()
			# If we have a result and class type
			if self.cursor.rowcount and class_type:
				# call the generator
				return PyObject(self.cursor, CLWMail.Log)
			else:
				# otherwise retunr None
				return None

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()


class CLWMail (SQLCreator):
	''' Subclass of SQLCreator representing the CLWMail database. Takes db specific connection
        parameters. It also provides methods which are on a tabular level. Row specific operations
		are provided by the inner classes of this outer class '''

	def __init__(self,host = DB_HOST, dbname  = DB_NAME, user = DB_USER, password = DB_PASSWORD):
		''' Call super class __init__ method to create connection and get cursor'''
		SQLCreator.__init__(self,host, dbname , user, password)
		cursor = self.connection.cursor()

	def getintervalmails(self, log_table = LOG_TABLE, interval = INTERVAL, 
							   created_col = CREATED_COL, processed_col = PROCESSED_COL):
		''' This method creates a query which will return all mail logs which are within 
			the interval specified in the settings file whose b_processed boolean is false '''	

		query = '''SELECT 
						* 
				   FROM 
						%s 
				   WHERE 
						CAST(%s AS DATE) >= CAST ( ( now () - CAST ('%s' AS INTERVAL )) AS DATE ) 
						AND 
						%s  = 'f'
							
					ORDER BY %s ;''' % (log_table, created_col, interval, processed_col, created_col)

		# Send query to be executed.
		result = self.execute(query, CLWMail.Log)
		
		# Remember that result is a generator.
		return result;

	class Log (object):
		''' An inner class to the CLWMail class. It represents a specific table in the
		    database. Each attribute of the Log class corresponds to a column in the table ''' 

		def __init__(self, n_id = None, dt_created = None, t_message_date = None,
					 t_orig_id = None, t_recipients = None, t_subject = None,
					 n_size = None, t_from = None, t_to = None, t_message_id = None,
					 t_cc = None, t_sha1sum = None, dt_processed = None, t_path = None,
					 b_processed = None) :

			self.n_id	 		=  n_id  
			self.dt_created		=  dt_created  
			self.t_message_date	=  t_message_date
			self.t_message_id  	=  t_message_id  
			self.t_orig_id		=  t_orig_id   
			self.t_recipients	=  t_recipients 
			self.t_subject		=  t_subject 
			self.n_size			=  n_size 
			self.t_from			=  t_from 
			self.t_to			=  t_to 
			self.t_cc			=  t_cc 
			self.t_sha1sum		=  t_sha1sum 
			self.dt_processed	=  dt_processed 
			self.b_processed	=  b_processed 
			self.t_path			=  t_path 
			self._outer_cls		=  CLWMail()

		def updateProcessed(self,log_table = LOG_TABLE):
			''' Update log file. This will set the sha1 sum if 
				it was computed, but will always set the 
				b_processed boolean to true '''

			query = '''UPDATE
							%s 
					   SET 
							t_sha1sum = '%s',
							b_processed = 't'

					   WHERE 
							n_id = %s ;''' % (log_table, self.t_sha1sum, self.n_id)

			self._outer_cls.execute(query)


class Summer(object):
	''' This class uses its methods 
		to iterate through a list of Log objects
		and computes their sha1 sum. '''

	# A static connector to the database
	CONNECTOR = CLWMail()
	# THe file which will contain any errors
	LOG_FILE  = LOG_FILE

	def __init__ (self,log_list = [], base_maildir = BASE_DIR):
		# The mailstore location
		self.base_dir = base_maildir
		# A pointer to the log file
		self.file_pointer = None
		# Make a pointer to the log file.
		try:
			self.file_pointer = open(Summer.LOG_FILE,'a')
		except IOError, e:
			print e
		else:
			# If the mailstore is not found, then
			# indicate and exit.
			if not  os.path.isdir(self.base_dir):
				print 'MailStore not found. Exiting...'
				sys.exit()

	def computesha (self):
		# Initialize log file
		self._init_run()
		
		# Get the mail logs within interval
		logs = Summer.CONNECTOR.getintervalmails()

		# If there are such logs
		if logs :
			# Iterate through and compute sha1
			for mail_log in logs:

					# Get the date of the mail for the directory.
					mail_log.dt_date = mail_log.dt_created.strftime("%Y-%m-%d")

					# See if the file exists.
					try:
						mail_file = open (self.base_dir +'%(dt_date)s/%(t_message_id)s' % mail_log.__dict__, 'r')
					except IOError, d :
						# If not write to the log
						self._write_log('%s: %s' % ( mail_log.t_message_id, str(d)))
					else:
						# calculate sha1sum from contents of file
						s = sha1()
						for m in mail_file:
							s.update(m)
						mail_log.t_sha1sum = s.hexdigest()
						mail_file.close()
						# Verbose printing.
						print '%s: %s' % (mail_log.t_message_id ,mail_log.t_sha1sum)

					# update the mail_log row in the db. We call this for all log objects
					# regardless of whether or not the sha1 sum was computed as we also
					# set the processed boolean to true.
					mail_log.updateProcessed()
		else:
				# if not logs are found for the interval that we are searching,
				# write it to the log and verbose print to the caller.
				self._write_log('No mail logs found for %s interval.' % INTERVAL)
				print 'No mail logs found in %s interval.' % INTERVAL
					
					
		# Finish run
		self._end_run()

	def _write_log(self,text):
		try:
			f = self.file_pointer
			f.write(text + '\n')
		except IOError, e:
			print e
		
	def _init_run(self):
		self._write_log('Starting Run at %s' % str(datetime.now()))

	def _end_run(self):
		try:
			self._write_log('End Run at %s' % str(datetime.now()))
			self.file_pointer.close()
		except IOError, e:
			print e

if __name__ == "__main__":
	summer = Summer()
	summer.computesha()
