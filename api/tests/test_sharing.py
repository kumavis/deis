
from __future__ import unicode_literals
import json

from django.test import TestCase


class TestSharing(TestCase):

    fixtures = ['test_sharing.json']

    def setUp(self):
        self.assertTrue(
            self.client.login(username='autotest-1', password='password'))

    def test_grant(self):
        # check that user 1 sees her lone formation
        response = self.client.get('/api/formations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        formation_id = response.data['results'][0]['id']
        # check that user 2 can't see any formations
        self.assertTrue(
            self.client.login(username='autotest-2', password='password'))
        response = self.client.get('/api/formations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        # give user 2 permission to user 1's formation
        self.assertTrue(
            self.client.login(username='autotest-1', password='password'))
        url = '/api/formations/{formation_id}/sharing'.format(**locals())
        body = {'user': 'autotest-2'}
        response = self.client.post(
            url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        # check that user 1 can see a formation
        self.assertTrue(
            self.client.login(username='autotest-2', password='password'))
        response = self.client.get('/api/formations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], formation_id)
        # revoke user 2's permission to user 1's formation
        self.assertTrue(
            self.client.login(username='autotest-1', password='password'))
        username = 'autotest-2'
        url = '/api/formations/{formation_id}/sharing/{username}/'.format(**locals())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_grant_errors(self):
        response = self.client.get('/api/formations')
        formation_id = response.data['results'][0]['id']
        # try to give user 2 permission to user 1's formation as user 2
        self.assertTrue(
            self.client.login(username='autotest-2', password='password'))
        url = '/api/formations/{formation_id}/sharing'.format(**locals())
        body = {'user': 'autotest-2'}
        response = self.client.post(
            url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        # try to give user 1 permission to user 1's formation as user 2
        url = '/api/formations/{formation_id}/sharing'.format(**locals())
        body = {'user': 'autotest-1'}
        response = self.client.post(
            url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_revoke(self):
        # give user 2 permission to user 1's formation
        response = self.client.get('/api/formations')
        formation_id = response.data['results'][0]['id']
        url = '/api/formations/{formation_id}/sharing'.format(**locals())
        body = {'user': 'autotest-2'}
        response = self.client.post(
            url, json.dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        # check that user 1 can see a formation
        self.assertTrue(
            self.client.login(username='autotest-2', password='password'))
        response = self.client.get('/api/formations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], formation_id)
        # revoke user 2's permission to user 1's formation
        self.assertTrue(
            self.client.login(username='autotest-1', password='password'))
        username = 'autotest-2'
        url = '/api/formations/{formation_id}/sharing/{username}/'.format(**locals())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        # check that user 1 can't see any formations
        self.assertTrue(
            self.client.login(username='autotest-2', password='password'))
        response = self.client.get('/api/formations')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

    def test_revoke_errors(self):
        # revoke user 2's permission to user 1's formation
        response = self.client.get('/api/formations')
        formation_id = response.data['results'][0]['id']
        username = 'autotest-2'
        url = '/api/formations/{formation_id}/sharing/{username}/'.format(**locals())
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
