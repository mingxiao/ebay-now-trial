'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import webapp2
import jinja2
import os
from models import Courier
import assign
from google.appengine.ext import db

jinja_env = jinja2.Environment(autoescape=True,
                               loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),'templates')))

class NewCourierPage(webapp2.RequestHandler):
    """
    Handler for adding a new courier
    """
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        template = jinja_env.get_template('courier.html')
        self.response.out.write(template.render())
    
    def post(self):
        c_id = self.request.get("id")
        c_lat = self.request.get('lat')
        c_lon = self.request.get('lon')
        #do some error handling
        try:
            c_id = int(c_id)
            c_lat = float(c_lat)
            c_lon = float(c_lon)
            #check if courier already exists
            pastCourier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",c_id).get()
            if pastCourier:
                self.response.set_status(302,'Courier already exists')
            else:
                courier = Courier(courierId=c_id,lat = c_lat,lon=c_lon)
                courier.put()
            #when a courier is added, we assign it an order
            assign.assignDelivery()
        except ValueError:
            self.response.set_status(303,'Invalid Values')
        
class CourierCompletePage(webapp2.RequestHandler):
    """
    Handler for when the courier completes a delivery
    """
    @db.transactional(xg=True)
    def update(self,courier,order):
        """
        Update courier to be active and set the state of the order to 'delivered'
        """
        courier.online = True
        courier.orderId = None
        courier.put()
        
        order.state = "delivered"
        order.put()
    
    def get(self,courier_id):
        self.response.out.write(courier_id)
        courier_id = int(courier_id)
        handle = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id)
        courier = handle.get()
        if courier:
            order = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",courier.orderId).get()
            if order:
                self.update(courier,order)
                #assign it a new delivery
                assign.assignDelivery()
            else:
                self.response.set_status(301,message='No order found')
        else:
            self.response.set_status(300,message='No courier found')
    
class OnlineCourier(webapp2.RequestHandler):
    """
    Handler to set a courier to online
    """
    def get(self):
        pass
    
    @db.transactional
    def update(self,courier):
        courier.online = True
        courier.put()
        
    def post(self,courier_id):
        courier_id = int(courier_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        if courier:
            self.update(courier)
            assign.assignDelivery()
        else:
            self.response.set_status(300,message="No courier found")
            
class OfflineCourier(webapp2.RequestHandler):
    """
    Handler to set a courier to offline
    """
    @db.transactional
    def update(self,courier):
        courier.online = False
        courier.put()
    
    def post(self,courier_id):
        courier_id = int(courier_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        if courier:
            self.update(courier)
        else:
            self.response.set_status(300,'Courier does not exists')
            
class AcceptCourier(webapp2.RequestHandler):
    
    @db.transactional(xg=True)
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
    
    def post(self,courier_id,order_id):
        courier_id = int(courier_id)
        order_id = int(order_id)
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",courier_id).get()
        order = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",order_id).get()
        if courier is not None and order is not None:
            self.update(order, courier)
        elif courier is None:
            self.response.set_status(300,"Courier does not exists")
        else:
            self.response.set_status(301,"Order does not exists")
            
app = webapp2.WSGIApplication([('/courier/new', NewCourierPage),
                               ('/courier/(\d+)/complete',CourierCompletePage),
                               ('/courier/(\d+)/online',OnlineCourier),
                               ('/courier/(\d+)/offline',OfflineCourier),
                               ('/courier/(\d+)/accept/(\d+)',AcceptCourier)], debug=True)