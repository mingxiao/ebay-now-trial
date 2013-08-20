'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import math
import munkres

class MunkresCaller():
    def pickup_cost(self,order,courier):
        """
        Cost for a courier to pick up an order
        """
        return self.distance(order.pickup_lat,order.pickup_lon,courier.lat,courier.lon)
    
    def order_cost(self,order):
        """
        Cost for an order to go from point A to B
        """
        return self.distance(order.pickup_lat, order.pickup_lon, order.dropoff_lat, order.dropoff_lon)
    
    def delivery_cost(self,order, courier):
        """
        Total cost to delivery = pickup cost + order cost
        """
        return self.pickup_cost(order,courier) + self.order_cost(order)

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
                matrix[i].append(self.delivery_cost(order, courier))
        return matrix
    
    def lowest_cost(self,orders,couriers):
        """
        Given a list of orders and couriers return a list of tuple of indexes that 
        specify which order is assigned to which courier
        """
        matrix = self.form_matrix(orders, couriers)
        mkres = munkres.Munkres()
        indexes = mkres.compute(matrix)
        return indexes
    
    
    
    
    