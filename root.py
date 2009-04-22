#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('Hello world!')

def main():
  application = webapp.WSGIApplication([
      ('/', MainHandler)
      ], debug=True)
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
