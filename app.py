import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import secrets
import time
import threading

from kernel import Kernel
from filesystem import FileSystem
from process_manager import ProcessManager
from memory_manager import MemoryManager
from shell import Shell
from users import UserManager
from devices import DeviceManager
from systemd import SystemD
from network import NetworkManager
from package_manager import PackageManager

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

sessions = {}

class LinuxSystem:
    def __init__(self, session_id):
        self.session_id = session_id
        self.boot_time = None
        self.state = 'off'
        self.runlevel = 0
        self.memory_manager = MemoryManager()
        self.filesystem = FileSystem()
        self.user_manager = UserManager(self.filesystem)
        self.device_manager = DeviceManager()
        self.process_manager = ProcessManager()
        self.network_manager = NetworkManager()
        self.systemd = SystemD(self)
        self.package_manager = PackageManager(self.filesystem)
        self.shell = Shell(self)
        self.kernel = Kernel(self)
        self.current_user = None
        self.hostname = 'localhost'
        self.environment = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'HOME': '/root',
            'SHELL': '/bin/bash',
            'USER': 'root',
            'LOGNAME': 'root',
            'TERM': 'xterm-256color',
            'LANG': 'en_US.UTF-8',
            'PWD': '/root',
            'HOSTNAME': 'localhost',
            'PS1': '\\u@\\h:\\w\\$ ',
            'EDITOR': 'nano',
            'HISTSIZE': '1000',
            'HISTFILESIZE': '2000'
        }
        self.history = []
        self.aliases = {
            'll': 'ls -la',
            'la': 'ls -A',
            'l': 'ls -CF',
            '..': 'cd ..',
            'cls': 'clear',
            'h': 'history',
            'grep': 'grep --color=auto',
        }
        self.jobs = []
        self.last_exit_code = 0

    def boot(self, callback):
        if self.state == 'running':
            callback("[WARN] System already running\n")
            return
        self.state = 'booting'
        self.boot_time = time.time()
        self.kernel.boot(callback)
        self.state = 'running'
        self.runlevel = 5

    def shutdown(self, callback, reboot=False):
        if self.state != 'running':
            callback("[WARN] System not running\n")
            return
        self.state = 'shutting_down'
        self.systemd.stop_all_services(callback)
        self.kernel.shutdown(callback, reboot)
        if reboot:
            self.state = 'off'
            time.sleep(0.5)
            self.boot(callback)
        else:
            self.state = 'off'
            self.runlevel = 0

    def get_uptime(self):
        if self.boot_time is None:
            return 0
        return time.time() - self.boot_time

    def execute_command(self, command):
        if self.state != 'running':
            return "System not running. Boot first.\n"
        if command.strip():
            self.history.append(command)
        return self.shell.execute(command)

    def get_prompt(self):
        if self.state != 'running':
            return ""
        user = self.current_user or 'root'
        cwd = self.filesystem.cwd
        if cwd.startswith(self.environment.get('HOME', '/root')):
            cwd = '~' + cwd[len(self.environment.get('HOME', '/root')):]
        if user == 'root':
            return f"{user}@{self.hostname}:{cwd}# "
        return f"{user}@{self.hostname}:{cwd}$ "


def get_system(session_id):
    if session_id not in sessions:
        sessions[session_id] = LinuxSystem(session_id)
    return sessions[session_id]


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/status/<session_id>')
def status(session_id):
    system = get_system(session_id)
    return jsonify({
        'state': system.state,
        'uptime': system.get_uptime(),
        'memory': system.memory_manager.get_stats(),
        'processes': system.process_manager.get_count(),
        'hostname': system.hostname,
        'user': system.current_user or 'root'
    })


@socketio.on('connect')
def handle_connect():
    session_id = request.args.get('session_id', secrets.token_hex(16))
    emit('session', {'session_id': session_id})


@socketio.on('boot')
def handle_boot(data):
    session_id = data.get('session_id')
    system = get_system(session_id)
    
    def callback(msg):
        emit('output', {'data': msg})
        socketio.sleep(0.02)
    
    def boot_thread():
        system.boot(callback)
        socketio.emit('boot_complete', {'prompt': system.get_prompt()}, room=request.sid)
    
    threading.Thread(target=boot_thread).start()


@socketio.on('command')
def handle_command(data):
    session_id = data.get('session_id')
    command = data.get('command', '')
    system = get_system(session_id)
    
    if command.strip().lower() in ['shutdown', 'poweroff', 'halt']:
        def callback(msg):
            emit('output', {'data': msg})
            socketio.sleep(0.02)
        system.shutdown(callback)
        emit('shutdown_complete', {})
        return
    
    if command.strip().lower() == 'reboot':
        def callback(msg):
            emit('output', {'data': msg})
            socketio.sleep(0.02)
        system.shutdown(callback, reboot=True)
        emit('boot_complete', {'prompt': system.get_prompt()})
        return
    
    output = system.execute_command(command)
    emit('output', {'data': output, 'prompt': system.get_prompt()})


@socketio.on('sync_fs')
def handle_sync_fs(data):
    session_id = data.get('session_id')
    fs_data = data.get('filesystem')
    system = get_system(session_id)
    if fs_data:
        system.filesystem.load_from_dict(fs_data)
    emit('sync_complete', {'filesystem': system.filesystem.to_dict()})


@socketio.on('get_fs')
def handle_get_fs(data):
    session_id = data.get('session_id')
    system = get_system(session_id)
    emit('filesystem_data', {'filesystem': system.filesystem.to_dict()})


@socketio.on('tab_complete')
def handle_tab_complete(data):
    session_id = data.get('session_id')
    partial = data.get('partial', '')
    system = get_system(session_id)
    completions = system.shell.tab_complete(partial)
    emit('completions', {'completions': completions})


@socketio.on('signal')
def handle_signal(data):
    session_id = data.get('session_id')
    signal = data.get('signal')
    system = get_system(session_id)
    if signal == 'SIGINT':
        system.shell.interrupt()
        emit('output', {'data': '^C\n', 'prompt': system.get_prompt()})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
