'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
import unittest
import models
import munkresCaller as mcaller

class Test(unittest.TestCase):

    def setUp(self):
        self.order = models.Order(orderId=1,pickup_lat=11.0,pickup_lon=22.0,dropoff_lat=33.0,dropoff_lon=44.0)
        self.courier = models.Courier(courierId=1,lat=88.0,lon=99.0)
        self.mkres = mcaller.MunkresCaller()
        
        self.order1 = models.Order(orderId=1,pickup_lat=1.0,pickup_lon=2.0,dropoff_lat=3.0,dropoff_lon=4.0)
        self.order2 = models.Order(orderId=2,pickup_lat=11.0,pickup_lon=21.0,dropoff_lat=31.0,dropoff_lon=41.0)
        self.orders = [self.order1,self.order2]
        
        self.courier1 = models.Courier(courierId=1,lat=11.0,lon=22.0)
        self.courier2 = models.Courier(courierId=1,lat=2.0,lon=2.0)
        self.couriers = [self.courier1,self.courier2]

    def testPickupCost(self):
        expected = 8735
        actual= self.mkres.pickup_cost(self.order, self.courier)
        self.assertAlmostEqual(expected, actual, delta = 1)
        
    def testFormMatrix(self):
        expectedMatrix = [[2472,111],[109,2323]]
        actualMatrix = self.mkres.form_matrix(self.orders, self.couriers)
        for i in range(len(expectedMatrix)):
            for j in range(len(expectedMatrix[i])):
                self.assertAlmostEqual(expectedMatrix[i][j], actualMatrix[i][j], delta=1)
                
    def testLowestCost(self):
        expected = [(0,1),(1,0)]
        actual = self.mkres.lowest_cost(self.orders, self.couriers)
        self.assertEqual(expected, actual)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()