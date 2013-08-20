'''
Created on Aug 19, 2013

@author: mingxiao10016
'''
from courierHandler import AcceptCourier, CourierCompletePage, NewCourierPage, \
    OfflineCourier, OnlineCourier
from google.appengine.datastore import datastore_stub_util
from google.appengine.ext import db, testbed
from google.appengine.ext.db import Query
from models import Courier, Order
from orderHandler import NewOrderHandler
import orderHandler
import unittest
import webapp2
import webtest

class NewCourierPageTest(unittest.TestCase):
    
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/courier/new', NewCourierPage)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        
    def testCourierPageTest(self):
        response = self.testapp.get('/courier/new')
        self.assertEqual(response.status_int, 200)
        
    def testInsertCourier(self):
        #create courier and there are no orders awaiting pickup
        params = {'id': 1, 'lat': 1.0,'lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(200,response.status_int)
        p2 = {'id': 2, 'lat': 11.0,'lon':22.0}
        response = self.testapp.post('/courier/new', p2)
        self.assertEqual(200,response.status_int)
        self.assertEqual(2, len(Courier.all().fetch(20)))
        
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertNotEqual(None, courier)
        
    def testInsertCourier2(self):
        #populate with some orders awaiting pickup 
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=2,pickup_lat=10.0,pickup_lon=10.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=3,pickup_lat=10.0,pickup_lon=1.0,dropoff_lat=12.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=4,pickup_lat=1.0,pickup_lon=10.0,dropoff_lat=2.0,dropoff_lon=12.0)
        order.put()
        #create a new courier
        params = {'id': 1, 'lat': 10.0,'lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(200,response.status_int)
        #check courier assigned correct order
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertEqual(3,courier.orderId)
        self.assertEqual(False,courier.online)
        #check that the assigned order is enRoute
        posOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = 3").get()
        self.assertEqual(1,posOrder.courierId)
        self.assertEqual('enRoute',posOrder.state)
        #check that the other orders are still unassigned
        for id in [1,2,4]:
            negOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",id).get()
            self.assertEqual(None,negOrder.courierId)
            self.assertEqual('needPickup',negOrder.state)
        #check that other couriers do not exist
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 3").get()
        self.assertEqual(None, courier)
        
    def testInsertCourier3(self):
        #bad value for id
        params = {'id': 's', 'lat': 1.0,'lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(303, response.status_int)
        
    def testInsertCourier4(self):
        #bad value for lat/lon
        params = {'id': 1, 'lat': 'bar','lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(303, response.status_int)
        
    def testInsertCourier5(self):
        #invalid inputs with previously existing courier/order, make sure they did not change
        #populate with courier/order
        courier = Courier(courierId=1,lat=2.0,lon=3.0)
        courier.put()
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        #post invalid input
        params = {'id': 1, 'lat': 'bar','lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(303, response.status_int)
        #check previous courier and order did not change
        posCourier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertEqual(True, posCourier.online)
        self.assertEqual(None, posCourier.orderId)
        posOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual(None,posOrder.courierId)
        self.assertEqual('needPickup',posOrder.state)
        
    def testInsertCourier6(self):
        #create a courier that already exists in our database
        courier = Courier(courierId=1,lat=2.0,lon=3.0)
        courier.put()
        params = {'id': 1, 'lat': 5.1,'lon':2.0}
        response = self.testapp.post('/courier/new', params)
        self.assertEqual(302, response.status_int)
        
    def tearDown(self):
        self.testbed.deactivate()
        
class CourierCompletePageTest(unittest.TestCase):
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/courier/(\d+)/complete', CourierCompletePage)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        
    def testGet1(self):
        #courier and order found
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        courier = Courier(courierId=1,lat=2.0,lon=3.0,orderId=1)
        courier.put()
        self.testapp.get('/courier/1/complete')
        
        result_courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertEqual(True, result_courier.online)
        self.assertEqual(None, result_courier.orderId)
        result_order = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual('delivered',result_order.state)
        
    def testGet2(self):
        #courier not found
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        courier = Courier(courierId=1,lat=2.0,lon=3.0,orderId=1)
        courier.put()
        self.assertEqual(1,len(Courier.all().fetch(20)))
        # if the courier is not found, nothing should be changed
        response = self.testapp.get('/courier/2/complete')
        self.assertEqual(300,response.status_int)
        
    def testGet3(self):
        #courier found, but order not found
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        courier = Courier(courierId=7,lat=2.0,lon=3.0,orderId=7)
        courier.put()
        response = self.testapp.get('/courier/7/complete')
        self.assertEqual(301,response.status_int)
        
    def tearDown(self):
        self.testbed.deactivate()
        
class OnlineCourierTest(unittest.TestCase):
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/courier/(\d+)/online', OnlineCourier)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
    
    def testPost(self):
        #courier exists, no orders to assign
        courier = Courier(courierId=7,lat=2.0,lon=3.0,online=False)
        courier.put()
        response = self.testapp.post('/courier/7/online')
        self.assertEqual(200,response.status_int)
        result_courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 7").get()
        self.assertEqual(True,result_courier.online)
        
    def testPost2(self):
        #courier does not exists
        courier = Courier(courierId=1,lat=2.0,lon=3.0,online=False)
        courier.put()
        response = self.testapp.post('/courier/7/online')
        self.assertEqual(300,response.status_int)
        
    def testPost3(self):
        #when courier comes online, assign it a package
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=2,pickup_lat=10.0,pickup_lon=10.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=3,pickup_lat=10.0,pickup_lon=1.0,dropoff_lat=12.0,dropoff_lon=2.0)
        order.put()
        order = Order(orderId=4,pickup_lat=1.0,pickup_lon=10.0,dropoff_lat=2.0,dropoff_lon=12.0)
        order.put()
        
        courier = Courier(courierId=7,lat=2.0,lon=3.0,online=False)
        courier.put()
        response = self.testapp.post('/courier/7/online')
        self.assertEqual(200,response.status_int)
        #check that courier 1 is assigned order 1
        courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 7").get()
        self.assertEqual(1,courier.orderId)
        self.assertEqual(False,courier.online)
        #check order 1 is assigned to courier 1
        posOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual('enRoute',posOrder.state)
        self.assertEqual(7,posOrder.courierId)
        #check that the other orders are still unassigned
        for id in [2,3,4]:
            negOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = :1",id).get()
            self.assertEqual('needPickup',negOrder.state)
            self.assertEqual(None,negOrder.courierId)
    
    def tearDown(self):
        self.testbed.deactivate()
        
class OfflineCourierTest(unittest.TestCase):
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/courier/(\d+)/offline', OfflineCourier)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        
    def testPost(self):
        #courier exists
        courier = Courier(courierId=7,lat=2.0,lon=3.0,online=True)
        courier.put()
        response = self.testapp.post('/courier/7/offline')
        self.assertEqual(200,response.status_int)
        result_courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 7").get()
        self.assertEqual(False,result_courier.online)
        
    def testPost2(self):
        #courier does not exists
        courier = Courier(courierId=1,lat=2.0,lon=3.0,online=False)
        courier.put()
        response = self.testapp.post('/courier/7/offline')
        self.assertEqual(300,response.status_int)
    
    def tearDown(self):
        self.testbed.deactivate()
        
class AcceptCourierTest(unittest.TestCase):
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/courier/(\d+)/accept/(\d+)', AcceptCourier)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        
    def testPost1(self):
        #courier and order exists
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        courier = Courier(courierId=7,lat=2.0,lon=3.0,orderId=7)
        courier.put()
        response = self.testapp.post('/courier/7/accept/1')
        self.assertEqual(200, response.status_int)
        #check that courier has properly changed
        result_courier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 7").get()
        self.assertEqual(1, result_courier.orderId)
        #check order has properly changed
        result_order = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual('enRoute',result_order.state)
                
    def testPost2(self):
        #courier exists, order does not exists
        courier = Courier(courierId=7,lat=2.0,lon=3.0,orderId=7)
        courier.put()
        response = self.testapp.post('/courier/7/accept/1')
        self.assertEqual(301, response.status_int)
    
    def testPost3(self):
        #courier does not exists, order exists
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        response = self.testapp.post('/courier/7/accept/1')
        self.assertEqual(300, response.status_int)
    
    def tearDown(self):
        self.testbed.deactivate()
        
class NewOrderHandlerTest(unittest.TestCase):
    def setUp(self):
        myApp = webapp2.WSGIApplication([('/order/new', NewOrderHandler)])
        self.testapp = webtest.TestApp(myApp)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(probability=1)
        # Initialize the datastore stub with this policy.
        self.testbed.init_datastore_v3_stub(consistency_policy=self.policy)
        
    def testPost(self):
        #populate couriers
        courier = Courier(courierId=1,lat=2.0,lon=3.0)
        courier.put()
        courier = Courier(courierId=2,lat=12.0,lon=13.0)
        courier.put()
        courier = Courier(courierId=3,lat=2.0,lon=13.0)
        courier.put()
        courier = Courier(courierId=4,lat=12.0,lon=3.0)
        courier.put()
        params ={'id':1,'plat':4.0,'plon':4.0,'dlat':11.0,'dlon':11.0}
        self.testapp.post('/order/new',params)
        order = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual(1, order.courierId)
        #should have been assigned to courier 1
        posCourier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertEqual(False,posCourier.online)
        self.assertEqual(1,posCourier.orderId)
        
        #check that the other couriers are available and have not been assigned
        for id in range(2,5):
            negCourier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = :1",id).get()
            self.assertEqual(True, negCourier.online)
            self.assertEqual(None,negCourier.orderId)
            
    def testPost2(self):
        #test using invalid inputs, no other orders/couriers exists
        params ={'id':1,'plat':'foo','plon':4.0,'dlat':11.0,'dlon':11.0}
        response = self.testapp.post('/order/new',params)
        self.assertEqual(303, response.status_int)
        
    def testPost3(self):
        #invalid input, other courier/order exists, make sure were not changed.
        #populate with courier and order
        courier = Courier(courierId=1,lat=2.0,lon=3.0)
        courier.put()
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        #submit invalid input
        params ={'id':'a','plat':3.0,'plon':4.0,'dlat':11.0,'dlon':11.0}
        response = self.testapp.post('/order/new',params)
        self.assertEqual(303, response.status_int)
        #check courier and order was unchanged
        posCourier = db.GqlQuery("SELECT * FROM Courier WHERE courierId = 1").get()
        self.assertEqual(True, posCourier.online)
        self.assertEqual(None, posCourier.orderId)
        posOrder = db.GqlQuery("SELECT * FROM Order WHERE orderId = 1").get()
        self.assertEqual(None,posOrder.courierId)
        self.assertEqual('needPickup',posOrder.state)
        
    def testPost4(self):
        #create an order that already exists in our database
        order = Order(orderId=1,pickup_lat=1.0,pickup_lon=1.0,dropoff_lat=2.0,dropoff_lon=2.0)
        order.put()
        params ={'id':1,'plat':3.0,'plon':4.0,'dlat':11.0,'dlon':11.0}
        response = self.testapp.post('/order/new',params)
        self.assertEqual(302, response.status_int)
    
    def tearDown(self):
        self.testbed.deactivate()

class QueryTest(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
    
    def testQuery(self):
        courier = Courier(courierId=1,lat=2.0,lon=3.0,online=True)
        courier.put()
        courier = Courier(courierId=2,lat=12.0,lon=13.0,online=False)
        courier.put()
        courier = Courier(courierId=14,lat=2.0,lon=3.0,online=True)
        courier.put()
        courier = Courier(courierId=51,lat=2.0,lon=3.0,online=True)
        courier.put()
        q = Query(Courier)
        q.filter("online = ", True)
        for courier in q:
            self.assertNotEqual(2, courier.courierId)
    
if __name__=='__main__':
    unittest.main()