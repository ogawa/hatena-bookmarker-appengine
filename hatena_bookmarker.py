#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app

import os
import yaml
import logging
import feedparser
from hatena_api import HatenaBookmarkClient

class HatenaBookmarkerHandler(webapp.RequestHandler):
  def get(self):
    config = get_config()
    api = HatenaBookmarkClient(config['hatena_username'],
                               config['hatena_password'])
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    for feed_url in config['feeds']:
      try:
        feed = feedparser.parse(feed_url)
        logging.info("Succeeded to parse feed: %s" % feed_url)
        self.response.out.write("Succeeded to parse feed: %s\n" % feed_url)
      except Exception, e:
        logging.error(e)
        logging.info("Failed to parse feed: %s" % feed_url)
        self.response.out.write("Failed to parse feed: %s\n" % feed_url)
        pass

      for entry in feed.entries:
        entry_url = entry.link
        summary = ''
        for tag in entry.tags:
          summary += '[' + tag.term + ']'
        try:
          api.postBookmark(entry_url, summary)
          logging.info("Succeeded to post bookmark: %s" % entry_url)
          self.response.out.write("Succeeded to post bookmark: %s\n" % entry_url)
        except Exception, e:
          logging.error(e)
          logging.info("Failed to post bookmark: %s" % entry_url)
          self.response.out.write("Failed to post bookmark: %s\n" % entry_url)
          pass

def get_config():
  config = yaml.safe_load(
    open(
      os.path.join(os.path.dirname(__file__), 'hatena_bookmarker.yaml'), 'r'
      )
    )
  return config

def main():
  application = webapp.WSGIApplication([
      ('/hatena_bookmarker', HatenaBookmarkerHandler),
      ], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
