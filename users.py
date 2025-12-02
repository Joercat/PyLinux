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
                    username = parts[0]
                    uid = int(parts[2])
                    gid = int(parts[3])
                    home = parts[5]
                    shell = parts[6]
                    self.users[username] = {
                        'uid': uid,
                        'gid': gid,
                        'home': home,
                        'shell': shell,
                        'gecos': parts[4]
                    }
                    if uid >= self.next_uid:
                        self.next_uid = uid + 1
        
        group_content = self.filesystem.read_file('/etc/group') or ''
        for line in group_content.strip().split('\n'):
            if line and ':' in line:
                parts = line.split(':')
                if len(parts) >= 4:
                    groupname = parts[0]
                    gid = int(parts[2])
                    members = parts[3].split(',') if parts[3] else []
                    self.groups[groupname] = {
                        'gid': gid,
                        'members': members
                    }
                    if gid >= self.next_gid:
                        self.next_gid = gid + 1

    def add_user(self, username, home=None, shell='/bin/bash', groups=None):
        if username in self.users:
            return f"useradd: user '{username}' already exists\n"
        
        uid = self.next_uid
        self.next_uid += 1
        gid = self.next_gid
        self.next_gid += 1
        
        if home is None:
            home = f'/home/{username}'
        
        self.users[username] = {
            'uid': uid,
            'gid': gid,
            'home': home,
            'shell': shell,
            'gecos': username.title()
        }
        
        self.groups[username] = {
            'gid': gid,
            'members': []
        }
        
        passwd_line = f"{username}:x:{uid}:{gid}:{username.title()}:{home}:{shell}\n"
        current_passwd = self.filesystem.read_file('/etc/passwd') or ''
        self.filesystem.write_file('/etc/passwd', current_passwd + passwd_line)
        
        shadow_line = f"{username}:$6$rounds=4096$salt$hash:{19000}:0:99999:7:::\n"
        current_shadow = self.filesystem.read_file('/etc/shadow') or ''
        self.filesystem.write_file('/etc/shadow', current_shadow + shadow_line)
        
        group_line = f"{username}:x:{gid}:\n"
        current_group = self.filesystem.read_file('/etc/group') or ''
        self.filesystem.write_file('/etc/group', current_group + group_line)
        
        self.filesystem.mkdir(home, parents=True)
        self.filesystem.chown(home, username, username)
        
        bashrc = self.filesystem.read_file('/etc/skel/.bashrc') or self.filesystem.read_file('/root/.bashrc') or ''
        profile = self.filesystem.read_file('/etc/skel/.profile') or self.filesystem.read_file('/root/.profile') or ''
        
        self.filesystem.write_file(f'{home}/.bashrc', bashrc)
        self.filesystem.write_file(f'{home}/.profile', profile)
        
        if groups:
            for g in groups:
                if g in self.groups:
                    self.groups[g]['members'].append(username)
        
        return ''

    def del_user(self, username, remove_home=False):
        if username not in self.users:
            return f"userdel: user '{username}' does not exist\n"
        
        if username == 'root':
            return "userdel: cannot remove root user\n"
        
        user_info = self.users[username]
        
        del self.users[username]
        
        if username in self.groups:
            del self.groups[username]
        
        for group in self.groups.values():
            if username in group['members']:
                group['members'].remove(username)
        
        passwd_content = self.filesystem.read_file('/etc/passwd') or ''
        new_passwd = '\n'.join(line for line in passwd_content.split('\n') if not line.startswith(f'{username}:'))
        self.filesystem.write_file('/etc/passwd', new_passwd)
        
        shadow_content = self.filesystem.read_file('/etc/shadow') or ''
        new_shadow = '\n'.join(line for line in shadow_content.split('\n') if not line.startswith(f'{username}:'))
        self.filesystem.write_file('/etc/shadow', new_shadow)
        
        group_content = self.filesystem.read_file('/etc/group') or ''
        new_group = '\n'.join(line for line in group_content.split('\n') if not line.startswith(f'{username}:'))
        self.filesystem.write_file('/etc/group', new_group)
        
        if remove_home:
            self.filesystem.delete(user_info['home'], recursive=True)
        
        return ''

    def add_group(self, groupname):
        if groupname in self.groups:
            return f"groupadd: group '{groupname}' already exists\n"
        
        gid = self.next_gid
        self.next_gid += 1
        
        self.groups[groupname] = {
            'gid': gid,
            'members': []
        }
        
        group_line = f"{groupname}:x:{gid}:\n"
        current_group = self.filesystem.read_file('/etc/group') or ''
        self.filesystem.write_file('/etc/group', current_group + group_line)
        
        return ''

    def del_group(self, groupname):
        if groupname not in self.groups:
            return f"groupdel: group '{groupname}' does not exist\n"
        
        if groupname == 'root':
            return "groupdel: cannot remove root group\n"
        
        del self.groups[groupname]
        
        group_content = self.filesystem.read_file('/etc/group') or ''
        new_group = '\n'.join(line for line in group_content.split('\n') if not line.startswith(f'{groupname}:'))
        self.filesystem.write_file('/etc/group', new_group)
        
        return ''

    def get_user(self, username):
        return self.users.get(username)

    def get_group(self, groupname):
        return self.groups.get(groupname)

    def user_exists(self, username):
        return username in self.users

    def group_exists(self, groupname):
        return groupname in self.groups
