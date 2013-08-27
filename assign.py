'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
from google.appengine.ext import db
import munkresCaller
from models import Courier
from models import Order
from google.appengine.ext.db import Query

def ordersEnRoute():
    """
    return all the orders that are currently enroute
    """
    q = Query(Order)
    q.filter("state =", "enRoute")
    return q

def couriersIdEnRoute():
    """
    Returns a list of courierIds of all the couriers who are currently on delivery given a list of
    all orders currently enRoute.
    
    enrouteOrder - a Query() object of all the orders whose state = 'enRoute'
    """
    couriers = []
    q = Query(Order,projection=["courierId"])
    q.filter("state =", "enRoute")
    for order in q:
        couriers.append(order.courierId)
    return couriers

def availableCouriers():
    """
    DEPRECATED
    Returns all available couriers. Search for all courier whose online =True
    """
    q = Query(Courier)
    q.filter("online =", True)
    return q

def allCourierIds():
    q = Query(Courier,projection=["courierId"])
    ids = []
    for c in q:
        ids.append(c.courierId)
    return ids

def availableCourierId():
    allId = allCourierIds()
    enrouteId = couriersIdEnRoute()
    for e in allId:
        if e in enrouteId:
            allId.remove(e)
    return allId

def available2():
    """
    Returns all couriers who are currently available.
    
    If GQL had a 'NOT IN' function, we would use the following:
    q = Query(Courier)
    c = couriersEnRoute()
    q.filter("courierId not in", c)
    return q
    
    However, it currently does not, we have to do a workaround
    """
    availId = availableCourierId()
    q = Query(Courier)
    q.filter("courierId in ", availId)
    return q

def unavailableCouriers():
    unavailId = couriersIdEnRoute()
    q = Query(Courier)
    q.filter("courierId in ", unavailId)
    return q

def idleOrders():
    """
    Returns a list of all orders waiting for couriers
    """
    q = Query(Order)
    q.filter("state =",'needPickup')
    return q

def assign(order, courier):
    order.courierId = courier.courierId
    order.state = 'enRoute'
    order.put()
    
def numLess(lst,num):
    return sum(i< num for i in lst)

def assignDelivery():
    #issue every time you get() a record, we decrease that record list by 1
#    couriers = availableCouriers()
    couriers = available2()
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
    
