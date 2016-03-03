import os
import frontend
import unittest
import tempfile

class appTestCase(unittest.TestCase):
	def setUp(seld):
		self.db_fd,frontend.app.config['MYSQL_DATABASE_USER']=tempfile.mkstemp()
		self.app =frontend.app.test_client()
		frontend.init_db()
		
	def tearDonw(self):
		os.close(self.dbfd)
		os.unlink(frontend.app.config['MYSQL_DATABASE_USER'])
	
	def test_empty_db(self):
		rv=self.frontend.get('/')
		assert 'Check-in Beacon' in rv.data
		assert 'asbddddddd' in rv.data