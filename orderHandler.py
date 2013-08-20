'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
from models import Order
import munkresCaller

from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True,
                               loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

class NewOrderHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('newOrder.html')
        self.availableCouriers()
        self.response.out.write(template.render())

    def post(self):
        id = int(self.request.get("id"))
        plat = float(self.request.get("plat"))
        plon = float(self.request.get("plon"))
        dlat = float(self.request.get("dlat"))
        dlon = float(self.request.get("dlon"))
        order = Order(orderId =id,pickup_lat=plat,pickup_lon=plon,dropoff_lat=dlat,dropoff_lon=dlon)
        order.put()
        
    def availableCouriers(self):
        """
        Returns all available couriers
        """
        couriers = db.GqlQuery("SELECT * FROM Courier WHERE online = True").fetch(1000)
        return couriers
#        for courier in couriers:
#            self.response.out.write(courier.courierId)
    def idleOrders(self):
        """
        Returns a list of all orders waiting for couriers
        """
        orders = db.GqlQuery("SELECT * FROM Order WHERE state= :1","needPickup").fetch(1000)
        return orders
        
    def assignDelivery(self):
        couriers = self.availableCouriers()
        orders = self.idleOrders()
        indexes = munkresCaller.MunkresCaller().lowest_cost(orders, couriers)
        pass


app = webapp2.WSGIApplication([('/order/new', NewOrderHandler),], debug=True)