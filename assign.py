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
def assign(order, courier):
    order.courierId = courier.courierId
    order.state = 'enRoute'
    order.put()
    
    courier.online = False
    courier.orderId = order.orderId
    courier.put()
    
#def toList(ordersQuery):
#    result = []
#    order = ordersQuery.get()
#    while order.orderId is not None:
#        print 'here'
#        result.append(order)
#        print order.orderId
#        order = ordersQuery.get()
#    return result

def assignDelivery():
    #issue every time you get() a record, we decrease that record list by 1
    couriers = availableCouriers()
    orders = idleOrders()
    indexes = munkresCaller.MunkresCaller().lowest_cost(orders, couriers)
    prevOrders = []
    prevCouriers = []
    for r,c in indexes:
        #everytime we get() a record, that record is removed from the record list,so we have
        #to calculate new offsets
        rOffset = sum(i < r for i in prevOrders)
        cOffset = sum(i < c for i in prevCouriers)
        order = orders.get(offset = r - rOffset)
        courier = couriers.get(offset = c- cOffset)
        prevOrders.append(r)
        prevCouriers.append(c)
        assign(order,courier)
    
    
    
    
