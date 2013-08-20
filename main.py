'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True, 
                                       loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('index.html')
        self.response.out.write(template.render())

app = webapp2.WSGIApplication([('/', MainPage),], debug=True)