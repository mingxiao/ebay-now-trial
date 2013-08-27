'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
from google.appengine.ext import db

class Order(db.Model):
    orderId = db.IntegerProperty(required = True)
    pickup_lat = db.FloatProperty(required = True)
    pickup_lon = db.FloatProperty(required = True)
    dropoff_lat = db.FloatProperty(required= True)
    dropoff_lon = db.FloatProperty(required = True)
    state = db.StringProperty(choices=set(["needPickup","enRoute","delivered"]),default='needPickup')
    courierId = db.IntegerProperty(default= None)
    created = db.DateTimeProperty(auto_now_add=True)
    
    
class Courier(db.Model):
    courierId = db.IntegerProperty(required = True)
    lat = db.FloatProperty(required = True)
    lon = db.FloatProperty(required = True)
    online = db.BooleanProperty(default = True)
    
    
    