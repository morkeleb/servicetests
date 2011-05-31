'''
Created on 16 apr 2010

@author: Morten Nielsen

You may change this code as you see fit, but you are expected to provide a
reference back to the original author, Morten Nielsen.

http://www.morkeleb.com
'''
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
import os
import time
import unittest
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.urlfetch_stub import URLFetchServiceStub, \
  _API_CALL_DEADLINE
from httplib import HTTPResponse

APP_ID = u'js-e-a'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'morten.dalgaard.nielsen@gmail.com'  # set to '' for no logged in user

class ServiceTestCase(unittest.TestCase):
  ''' 
  defines a test case, with appengine test stubs setup.
  Has methods to access email messages sent during the tested methods executed
  
  This class assists in creating AAA tests for appengine.
  Arrange, act and assert.
  Where the arrange step isn't duplicated between tests.

  '''
  class LoggingMailStub(mail_stub.MailServiceStub):
    '''
     
    '''
    def __init__(self,
               host=None,
               port=25,
               user='',
               password='',
               enable_sendmail=False,
               show_mail_body=False,
               service_name='mail'):
      """Constructor.

      Args:
        host: Host of SMTP mail server.
        post: Port of SMTP mail server.
        user: Sending user of SMTP mail.
        password: SMTP password.
        enable_sendmail: Whether sendmail enabled or not.
        show_mail_body: Whether to show mail body in log.
        service_name: Service name expected for all calls.
      """
      super(mail_stub.MailServiceStub, self).__init__(service_name)
      self._smtp_host = host
      self._smtp_port = port
      self._smtp_user = user
      self._smtp_password = password
      self._enable_sendmail = enable_sendmail
      self._show_mail_body = show_mail_body
      self.messages = []

    def _GenerateLog(self, method, message, log):
      self.messages.append(message)
      return
    
  class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)
    def __repr__(self):
        args = ['%s=%s' % (k, repr(v)) for (k, v) in vars(self).items()]
        return 'Struct(%s)' % ', '.join(args)

  class UrlFetchStub(urlfetch_stub.URLFetchServiceStub):
    """Stub version of the urlfetch API to be used with apiproxy_stub_map."""

    def __init__(self, service_name='urlfetch'):
      """Initializer.

      Args:
        service_name: Service name expected for all calls.
      """
      self.responses = {};
      super(URLFetchServiceStub, self).__init__(service_name)
    
    def _RetrieveURL(self, url, payload, method, headers, request, response,
                   follow_redirects=True, deadline=_API_CALL_DEADLINE):
      
      response.set_content(self.responses[url])
      
    def setContent(self, url, c):
      
      self.responses[url] = c

  def setUp(self):
    # Ensure we're in UTC.
    os.environ['TZ'] = 'UTC'
    os.environ['SERVER_PORT'] = "8080";
    os.environ['SERVER_NAME'] = "localhost";
    os.environ['APPLICATION_ID'] = APP_ID    
    apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    stub = datastore_file_stub.DatastoreFileStub(APP_ID, None)
    apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
    apiproxy_stub_map.apiproxy.RegisterStub(
    'user', user_service_stub.UserServiceStub())
    os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
    os.environ['USER_EMAIL'] = LOGGED_IN_USER
    self.fetch_stub = ServiceTestCase.UrlFetchStub()
    apiproxy_stub_map.apiproxy.RegisterStub(
    'urlfetch', self.fetch_stub)
    self.mail_stub = ServiceTestCase.LoggingMailStub()
    apiproxy_stub_map.apiproxy.RegisterStub(
    'mail', self.mail_stub) 
    self.memcache_stub = memcache_stub.MemcacheServiceStub()
    apiproxy_stub_map.apiproxy.RegisterStub('memcache', self.memcache_stub)
  def getMessages(self):
    '''
    returns a list of messages that were sent during the test run.
    This is to be used for assertions. 
    '''  
  
    return self.mail_stub.messages;
  def setResponse(self, url, content):
    '''
    sets  the content that will be returned for a given url when fetched
    '''
    self.fetch_stub.setContent(url, content)

