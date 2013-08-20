'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
from google.appengine.ext import db
import munkresCaller
from models import Courier
from models import Order
from google.appengine.ext.db import Query

def availableCouriers():
    """
    Returns all available couriers
    """
    q = Query(Courier)
    q.filter("online =", True)
    return q
    
def idleOrders():
    """
    Returns a list of all orders waiting for couriers
    """
    q = Query(Order)
    q.filter("state =",'needPickup')
    return q
#    orders = db.GqlQuery("SELECT * FROM Order WHERE state= :1", "needPickup").fetch(1000)
#    return orders

@db.transactional(xg=True)
def assign( order, courier):
    order.courierId = courier.courierId
    order.state = 'enRoute'
    order.put()
    
    courier.online = False
    courier.orderId = order.orderId
    courier.put()

def assignDelivery():
    couriers = availableCouriers()
    orders = idleOrders()
    indexes = munkresCaller.MunkresCaller().lowest_cost(orders, couriers)
    for r, c in indexes:
        assign(orders[r], couriers[c])
