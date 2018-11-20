from .auth import Auth
import base64
import flask
from passlib.hash import sha256_crypt

class BasicAuth(Auth):
    def __init__(self, app, username_pwhash_list, sha256salt,
                 loginmsg='User Visible Realm'):
        Auth.__init__(self, app)
        self._username_pwhash_list = username_pwhash_list
        self._sha256salt = sha256salt
        # Storing username & password hash for app can readily access it
        self._username = ''
        self._pwhash=''
        self._loginmsg = loginmsg
        # Auxiliary: Storing password corresponding to hash: Just for speedup:
        #  as tend found frequent authorization requests during session,
        #  save hash for password, as I guess hash calculation otherwise is
        #  slightly slow
        self._pw_aux=None

    def is_authorized(self):
        header = flask.request.headers.get('Authorization', None)
        if not header:
            return False
        username_password = base64.b64decode(header.split('Basic ')[1])
        username_password_utf8 = username_password.decode('utf-8')
        username, password = username_password_utf8.split(':')
        if (self._pw_aux == password):
            passwordhash = self._pwhash
        else:
            passwordhash = sha256_crypt.using(salt=self._sha256salt).hash(password)
            self._pw_aux = password
            self._pwhash = passwordhash
        for pair in self._username_pwhash_list:
            if pair[0] == username and pair[1] == passwordhash:
                self._username = username
                return True

        return False

    def login_request(self):
        return flask.Response(
            'Login Required',
            headers={'WWW-Authenticate': 'Basic realm="{}"'.format(
                self._loginmsg)},
            status=401)

    def auth_wrapper(self, f):
        def wrap(*args, **kwargs):
            if not self.is_authorized():
                return flask.Response(status=403)

            response = f(*args, **kwargs)
            return response
        return wrap

    def index_auth_wrapper(self, original_index):
        def wrap(*args, **kwargs):
            if self.is_authorized():
                return original_index(*args, **kwargs)
            else:
                return self.login_request()
        return wrap
