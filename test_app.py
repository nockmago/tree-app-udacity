import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Tree, Forest, Farmer

# these variables will be used to test endpoints that require authorization
ADMIN_TOKEN = os.environ['ADMIN_TOKEN']
FARMER_TOKEN = os.environ['FARMER_TOKEN']

class TreeAppTestCase(unittest.TestCase):
    """This class represents the tree app test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "tree_test"
        self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.admin_headers = {
            "Authorization": ADMIN_TOKEN
        }

        self.farmer_headers = {
            "Authorization": FARMER_TOKEN
        }

        self.new_forest = {
            "name": "Foresta", 
            "Location": "Angola"
            }

        self.new_farmer = {
            "name": "Gino Gianni"
        }

        self.edit_farmer = {
            "name": "Paulo"
        }

        self.new_tree= {
            "farmer_id": 1,
            "forest_id": 1, 
            "name": 'Platano',
            "quantity": 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_trees(self):
        res = self.client().get("/trees")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["trees"]))

    def test_get_forests(self):
        res = self.client().get("/forests")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["forests"]))

    def test_get_farmers(self):
        res = self.client().get("/farmers")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["farmers"]))

    def test_get_one_farmer(self):
        res = self.client().get("/farmers/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["farmer"])

    def test_404_if_farmer_not_found(self):
        res = self.client().get("/farmers/124")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"], 'resource not found')

    def test_get_one_forest(self):
        res = self.client().get("/forests/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["forest"])
        self.assertTrue(data["trees"])
        self.assertTrue(data["number_of_trees"])
    
    def test_create_farmer(self): 
        res = self.client().post("/farmers", json=self.new_farmer, headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["farmers"])
    
    def test_create_farmer_unauthorized(self): 
        res = self.client().post("/farmers", json=self.new_farmer, headers=self.farmer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)

    def test_patch_farmer(self): 
        res = self.client().patch("/farmers/1", json=self.edit_farmer, headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["modified"])

    def test_patch_farmer_bad_request(self): 
        res = self.client().patch("/farmers/1", headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
    
    def test_create_forest(self): 
        res = self.client().post("/forests", json=self.new_forest, headers=self.admin_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["forests"])
    
    def test_create_forest_unauthorized(self): 
        res = self.client().post("/forests", json=self.new_forest, headers=self.farmer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 401)
        self.assertEqual(data["success"], False)
    
    def test_create_tree(self): 
        res = self.client().post("/trees", json=self.new_tree, headers=self.farmer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        self.assertTrue(data["total_trees"])
    
    def test_create_tree_bad_request(self): 
        res = self.client().post("/trees", headers=self.farmer_headers)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)

    def test_delete_tree(self): 
        res = self.client().delete("/trees/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["deleted"])
        self.assertTrue(data["total_trees"])
    
    def test_delete_tree_404(self): 
        res = self.client().delete("/trees/2929")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)



# make the test conveniently executable
if __name__ == "__main__":
    unittest.main()
