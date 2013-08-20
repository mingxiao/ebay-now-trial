'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
from models import Courier
import munkresCaller

from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True,
                               loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

class CourierPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('courier.html')
        self.response.out.write(template.render())
    
    def post(self):
        c_id = self.request.get("id")
        c_lat = self.request.get('lat')
        c_lon = self.request.get('lon')
        
        c_id = int(c_id)
        c_lat = float(c_lat)
        c_lon = float(c_lon)
        courier = Courier(courierId=c_id,lat = c_lat,lon=c_lon)
        courier.put()
        
        
class CourierCompletePage(webapp2.RequestHandler):
    
    @db.transactional
    def update(self,courier):
        courier.online = True
        oldOrderId = courier.orderId
        courier.orderId = None
        courier.put()
        
        order = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",oldOrderId).get()
        order.state = "delivered"
        order.put()
    
    def get(self,courier_id):
        self.response.out.write(courier_id)
        courier_id = int(courier_id)
        handle = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id)
        courier = handle.get()
        if courier:
            self.update(courier)
            self.response.out.write("Complete success")
        else:
            self.response.out.write("No courier found")
    
class OnlineCourier(webapp2.RequestHandler):
    
    @db.transactional
    def update(self,courier):
        courier.online = True
        courier.put()
        
    def get(self,courier_id):
        courier_id = int(courier_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        if courier:
            self.update(courier)
            self.response.out.write("set courier {} to online".format(courier.courierId))
        else:
            self.response.out.write("online: courier {} does not exist".format(courier_id))
            
class OfflineCourier(webapp2.RequestHandler):
    
    @db.transactional
    def update(self,courier):
        courier.online = False
        courier.put()
    
    def get(self,courier_id):
        courier_id = int(courier_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        if courier:
            self.update(courier)
            self.response.out.write("set courier {} to offline".format(courier.courierId))
        else:
            self.response.out.write("offline: courier {} does not exist".format(courier_id))
            
class AcceptCourier(webapp2.RequestHandler):
    
    def update(self,order,courier):
        """
        Atmoic update of order and courier
        """
        #set courier to offline
        courier.online= False
        courier.orderId = order.orderId
        courier.put()
        #change state of order
        order.state = "enRoute"
        order.courierId = courier.courierId
        order.put()
    
    def get(self,courier_id,order_id):
        courier_id = int(courier_id)
        order_id = int(order_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        order = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",order_id).get()
        if courier is not None and order is not None:
            self.update(order, courier)
            self.response.out.write("update SUCCESS")
        else:
            self.response.out.write("update FAIL")
            
    
app = webapp2.WSGIApplication([('/courier', CourierPage),
                               ('/courier/(\d+)/complete',CourierCompletePage),
                               ('/courier/(\d+)/online',OnlineCourier),
                               ('/courier/(\d+)/offline',OfflineCourier),
                               ('/courier/(\d+)/accept/(\d+)',AcceptCourier)], debug=True)