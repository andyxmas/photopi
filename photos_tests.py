import os
import photos
import unittest
import tempfile


class PhotosTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, photos.app.config['DATABASE'] = tempfile.mkstemp()
        photos.app.config['TESTING'] = True
        self.app = photos.app.test_client()
        photos.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(photos.app.config['DATABASE'])

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'No photos here so far' in rv.data

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
	rv = self.login('marco', 'lionel-christmas')
        assert 'You were logged in' in rv.data
        rv = self.logout()
        assert 'You were logged out' in rv.data
	rv = self.login('something', 'lionel-christmas')
        assert 'Invalid username' in rv.data
        rv = self.login('marco', 'lkjsdf')	
        assert 'Invalid password' in rv.data

    def test_adding_photos(self):
        self.login('admin', 'default')
        rv = self.app.post('/add', data=dict(
            title='<Hello>',
            text='<strong>HTML</strong> allowed here'
        ), follow_redirects=True)
        assert 'No entries here so far' not in rv.data
        assert '&lt;Hello&gt;' in rv.data
        assert '<strong>HTML</strong> allowed here' in rv.data

if __name__ == '__main__':
    unittest.main()
