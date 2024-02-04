import unittest
from app import app, db
from app.models import User, Article
import json

class TestArticleManagement(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_article(self):
        print("Test: Ajout d'un article")
        # Create admin
        admin_data = {
            'email': 'admin@example.com',
            'password': 'AdminPass123',
            'firstName': 'Admin',
            'lastName': 'User',
            'nature': 'Nature',
            'field': 'Field'
        }
        response = self.app.post('/admin/create', json=admin_data)
        self.assertEqual(response.status_code, 201)

        # Login as admin
        login_data = {
            'email': 'admin@example.com',
            'password': 'AdminPass123'
        }
        response = self.app.post('/signin', json=login_data)
        self.assertEqual(response.status_code, 200)
        access_token = json.loads(response.data)['access_token']

        # Add article
        article_data = {
            'pdf_url': 'https://mobile-systems.cl.cam.ac.uk/papers/sensys23.pdf'
        }
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.app.post('/article/add', json=article_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        print("Résultat du test: [OK] Article ajouté avec succès")

if __name__ == '__main__':
    unittest.main()
