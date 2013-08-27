'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import math
import munkres
from google.appengine.ext.db import Query

class MunkresCaller():
    def pickup_cost(self,order,courier):
        """
        Cost for a courier to pick up an order
        """
        return self.distance(order.pickup_lat,order.pickup_lon,courier.lat,courier.lon)

    def distance(self,lat1,lon1,lat2,lon2):
            radius = 6371 # km                                                                                                                                  
            dlat = math.radians(lat2-lat1)
            dlon = math.radians(lon2-lon1)
            a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
                * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            d = radius * c
            return d
        
    def form_matrix(self,orders,couriers):
        matrix= []
        for i,order in enumerate(orders):
            matrix.append([])
            for courier in couriers:
                matrix[i].append(self.pickup_cost(order, courier))
        return matrix
    
    def is_empty(self,items):
        """
        Returns true if items is empty. Items could be a list or a cursor to a query result
        """
        if type(items) == type([]):
            return len(items) == 0
        elif type(items) == type(Query()):
            return items.count() == 0
        else:
            assert False
    
    def lowest_cost(self,orders,couriers):
        """
        Given a list of orders and couriers return a list of tuple of indexes that 
        specify which order is assigned to which courier
        """
        if self.is_empty(orders) or self.is_empty(couriers):
            return []
        matrix = self.form_matrix(orders, couriers)
        mkres = munkres.Munkres()
        indexes = mkres.compute(matrix)
        return indexes
    
    
    
    
    