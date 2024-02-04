import unittest
import json

from flask import jsonify
from app import app, db
from app.models import User

class TestUserManagement(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_admin_creation_login(self):
        print("Test: Création et connexion d'un administrateur")
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

        print("Résultat du test: [OK] Administrateur créé et connecté avec succès")
        
        # Create moderator (while logged in as admin)
        moderator_data = {
            'email': 'moderator@example.com',
            'password': 'ModPass123',
            'firstName': 'Moderator',
            'lastName': 'User',
            'nature': 'Nature',
            'field': 'Field'
        }
        headers = {'Authorization': 'Bearer ' + access_token}
        response = self.app.post('/moderator/create', json=moderator_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn('user', json.loads(response.data))
        moderator_data = json.loads(response.data)['user']
        print("Moderator Data:", moderator_data)
        print("Résultat du test: [OK] Moderateur créé avec succès")
        
        # Update moderator (while logged in as admin)
        moderator_id = json.loads(response.data)['user']['id']
        update_data = {
            'email': 'updated@example.com'
        }
        response = self.app.put(f'/user/update/{moderator_id}', json=update_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        print("Résultat du test: [OK] Moderateur mis à jour avec succès")

        # Get moderator (while logged in as admin)
        response = self.app.get('/moderators', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('moderators', json.loads(response.data))
        moderators_data = json.loads(response.data)
        print("Moderators Data:", moderators_data)
        self.assertIn('moderators', moderators_data)
        print("Résultat du test: [OK] Liste des modérateurs récupérée avec succès")

        # Logout
        response = self.app.post('/signout', headers=headers)
        self.assertEqual(response.status_code, 200)
        print("Résultat du test: [OK] Déconnexion réussie")

        with app.app_context():
            # Si les opérations de test réussissent, vous pouvez renvoyer un message de succès
            return jsonify({'message': 'Tests executed successfully'}), 200



if __name__ == '__main__':
    unittest.main()
