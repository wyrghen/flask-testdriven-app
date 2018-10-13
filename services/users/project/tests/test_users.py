import json
import unittest

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase

test_user = 'example'
test_email = 'example@example.org'


def add_user(username, email):
    user = User(
        username=username,
        email=email
    )
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/users/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': test_user,
                    'email': test_email
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn(f'{test_email} was added!', data['message'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is throw if the JSON object is empty."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is trhow if the JSON object does not have a
        username key."""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps({'email': test_email}),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is throw if the email already exists."""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps({
                    'username': test_user,
                    'email': test_email
                }),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps({
                    'username': test_user,
                    'email': test_email
                }),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists',
                data['message']
            )
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user(test_user, test_email)
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn(test_user, data['data']['username'])
            self.assertIn(test_email, data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_sigle_user_incorrect_id(self):
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user(test_user, test_email)
        add_user('ala', 'ma@kota.pl')
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data['data']['users']), 2)
            self.assertIn(
                test_user,
                data['data']['users'][0]['username']
            )
            self.assertIn(
                test_email,
                data['data']['users'][0]['email']
            )
            self.assertIn(
                'ala',
                data['data']['users'][1]['username']
            )
            self.assertIn(
                'ma@kota.pl',
                data['data']['users'][1]['email']
            )
            self.assertIn('success', data['status'])

    def test_main_with_users(self):
        """Ensure the main route behaves correctly when users have
        been added to the database."""
        add_user(test_user, test_email)
        add_user('ala', 'ma@kota.pl')
        with self.client:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(test_user.encode(), response.data)
            self.assertIn(b'ala', response.data)

    def test_main_add_user(self):
        """Ensure a new user can be added to the databe."""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username=test_user, email=test_email),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'<p>No users!</p>', response.data)
            self.assertIn(test_user.encode(), response.data)


if __name__ == '__main__':
    unittest.main()
