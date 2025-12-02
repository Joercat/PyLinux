class UserManager:
    def __init__(self, filesystem):
        self.filesystem = filesystem
        self.users = {}
        self.groups = {}
        self.next_uid = 1001
        self.next_gid = 1001

    def initialize(self):
        passwd_content = self.filesystem.read_file('/etc/passwd') or ''
        for line in passwd_content.strip().split('\n'):
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 7:
                    self.users[parts[0]] = {
                        'uid': int(parts[2]), 'gid': int(parts[3]),
                        'home': parts[5], 'shell': parts[6]
                    }
                    if int(parts[2]) >= self.next_uid:
                        self.next_uid = int(parts[2]) + 1

    def add_user(self, username, home=None, shell='/bin/bash', groups=None):
        if username in self.users:
            return f"useradd: user '{username}' already exists\n"
        
        uid = self.next_uid
        self.next_uid += 1
        gid = self.next_gid
        self.next_gid += 1
        
        home = home or f'/home/{username}'
        
        self.users[username] = {'uid': uid, 'gid': gid, 'home': home, 'shell': shell}
        self.groups[username] = {'gid': gid, 'members': []}
        
        passwd_line = f"{username}:x:{uid}:{gid}:{username}:{home}:{shell}\n"
        current = self.filesystem.read_file('/etc/passwd') or ''
        self.filesystem.write_file('/etc/passwd', current + passwd_line)
        
        self.filesystem.mkdir(home, parents=True)
        return ''

    def del_user(self, username, remove_home=False):
        if username not in self.users:
            return f"userdel: user '{username}' does not exist\n"
        if username == 'root':
            return "userdel: cannot remove root\n"
        
        home = self.users[username]['home']
        del self.users[username]
        if username in self.groups:
            del self.groups[username]
        
        if remove_home:
            self.filesystem.delete(home, recursive=True)
        return ''

    def add_group(self, groupname):
        if groupname in self.groups:
            return f"groupadd: group '{groupname}' already exists\n"
        
        gid = self.next_gid
        self.next_gid += 1
        self.groups[groupname] = {'gid': gid, 'members': []}
        return ''

    def del_group(self, groupname):
        if groupname not in self.groups:
            return f"groupdel: group '{groupname}' does not exist\n"
        del self.groups[groupname]
        return ''
