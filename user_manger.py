import hashlib
import time

class User:
    def __init__(self, username, uid, gid, home, shell, real_name=''):
        self.username = username
        self.uid = uid
        self.gid = gid
        self.home = home
        self.shell = shell
        self.real_name = real_name
        self.password_hash = None
        self.created = time.time()
        self.last_login = None

class UserManager:
    def __init__(self):
        self.users = {}
        self.groups = {}
        self._initialize_users()

    def _initialize_users(self):
        root = User('root', 0, 0, '/root', '/bin/bash', 'root')
        user = User('user', 1000, 1000, '/home/user', '/bin/bash', 'Default User')
        
        self.users['root'] = root
        self.users['user'] = user
        
        self.groups['root'] = {'gid': 0, 'members': ['root']}
        self.groups['user'] = {'gid': 1000, 'members': ['user']}
        self.groups['sudo'] = {'gid': 27, 'members': ['user']}

    def get_user(self, username):
        return self.users.get(username)

    def user_exists(self, username):
        return username in self.users

    def add_user(self, username, uid=None, gid=None, home=None, shell='/bin/bash'):
        if self.user_exists(username):
            return False
        
        if uid is None:
            uid = max([u.uid for u in self.users.values()]) + 1
        
        if gid is None:
            gid = uid
        
        if home is None:
            home = f'/home/{username}'
        
        user = User(username, uid, gid, home, shell)
        self.users[username] = user
        return True

    def delete_user(self, username):
        if username in ['root', 'user']:
            return False
        
        if username in self.users:
            del self.users[username]
            return True
        return False

    def list_users(self):
        return list(self.users.keys())

    def get_user_info(self, username):
        user = self.get_user(username)
        if user:
            return {
                'username': user.username,
                'uid': user.uid,
                'gid': user.gid,
                'home': user.home,
                'shell': user.shell,
                'real_name': user.real_name,
                'created': user.created,
                'last_login': user.last_login
            }
        return None

    def is_in_group(self, username, groupname):
        if groupname in self.groups:
            return username in self.groups[groupname]['members']
        return False
