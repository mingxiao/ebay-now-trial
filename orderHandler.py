'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
from models import Order
import assign

from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True,
                               loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

class NewOrderHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('newOrder.html')
        self.response.out.write(template.render())

    def post(self):
        try:
            id = int(self.request.get("id"))
            plat = float(self.request.get("plat"))
            plon = float(self.request.get("plon"))
            dlat = float(self.request.get("dlat"))
            dlon = float(self.request.get("dlon"))
            #check if order already exists
            pastOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",id).get()
            if pastOrder is None:
                order = Order(orderId =id,pickup_lat=plat,pickup_lon=plon,dropoff_lat=dlat,dropoff_lon=dlon)
                order.put()
                assign.assignDelivery()
                self.redirect('/order/needPickup')
            else:
                self.response.set_status(333,"Order already exists")
                self.response.headers['Content-Type'] = 'text/html'
                template = jinja_env.get_template('newOrder.html')
                d = {'error':'Order {} already exists'.format(id)}
                self.response.out.write(template.render())
        except ValueError:
            self.response.set_status(344,'Invalid values')
            self.response.headers['Content-Type'] = 'text/html'
            template = jinja_env.get_template('newOrder.html')
            d = {'error':'Invalid input parameters'}
            self.response.out.write(template.render(d))

class ListPickupHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('listPickupOrder.html')
        orders = db.GqlQuery("SELECT * FROM Order WHERE state = :1","needPickup").fetch(20)
        d = {"orders":orders}
        self.response.out.write(template.render(d))

class ListEnRouteHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('listEnRouteOrder.html')
        orders = db.GqlQuery("SELECT * FROM Order WHERE state = :1","enRoute").fetch(20)
        d = {"orders":orders}
        self.response.out.write(template.render(d))
        
class ListDeliveredHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('listDeliveredOrder.html')
        orders = db.GqlQuery("SELECT * FROM Order WHERE state = :1","delivered").fetch(20)
        d = {"orders":orders}
        self.response.out.write(template.render(d))

app = webapp2.WSGIApplication([('/order/new', NewOrderHandler),
                               ('/order/delivered',ListDeliveredHandler),
                               ('/order/enRoute',ListEnRouteHandler),
                               ('/order/needPickup',ListPickupHandler)], debug=True)