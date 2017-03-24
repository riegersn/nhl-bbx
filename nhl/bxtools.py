import re
import bz2
import urllib
import urllib2
import cookielib
import datetime as dt
import simplejson as json
from urllib import quote, unquote, urlencode
from base64 import b64decode, b64encode

def encode(data):
   """
   simple method used to encode sensitive strings (not too sensitive) in the registry
   """
   
   data = dquote(b64encode(dquote(data)))
   data = dquote(b64encode(bz2.compress(data)))
   return data


def decode(data):
   """
   simple method used to dencode sensitive strings (not too sensitive) in the registry
   """
   
   data = b64decode(dunquote(data))
   data = bz2.decompress(data)
   data = dunquote(b64decode(dunquote(data)))
   return data


def dunquote(data):
   """
   unquote double quoted strings (used for encode/decode)
   """
   
   return unquote(unquote(data))


def dquote(data):
   """
   double quote a string (used for encode/decode)
   """
   return quote(quote(data))


class login:
   """
   old school login method, as opposed to using the mc http
   class, which will not always grab all available cookies from a login request
   """
   
   __post_url = ''
   __post_data = {}
   __cookies = {}
   __cookies_merged = ''
   __user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/2007091417 Firefox/2.0.0.7'
   __headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
   __result_text = ''


   def __init__(self, url, data):
      self.__post_url = url
      self.__post_data = data


   def override_user_agent(self, userAgent):
      self.__user_agent = userAgent


   def set_additional_headers(self, data):
      self.__headers = dict(self.__headers.items() + data.items())


   def commit(self):
      self.__headers['User-Agent'] = self.__user_agent
      cj = cookielib.CookieJar()
      cookiesProcessor = urllib2.HTTPCookieProcessor(cj)
      opener = urllib2.build_opener(cookiesProcessor)
      urllib2.install_opener(opener)
      params = urlencode(self.__post_data)
      req = urllib2.Request(self.__post_url, params, self.__headers)
      response = urllib2.urlopen(req)
      self.__result_text = response.read()
      cookie = ""
      for index, val in enumerate(cj):
         cookie += val.name + "=" + val.value + "; "
         self.__cookies[val.name] = val.value
      self.__cookies_merged = cookie


   def get_cookies(self):
      return self.__cookies


   def get_merged_cookies(self):
      return self.__cookies_merged


   def get_result(self):
      return self.__result_text
