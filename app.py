from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import threading
import time
from datetime import datetime
from filesystem import FileSystem
from process_manager import ProcessManager
from memory_manager import MemoryManager
from command_handler import CommandHandler
from boot_manager import BootManager
from user_manager import UserManager
from network_manager import NetworkManager
from device_manager import DeviceManager
from package_manager import PackageManager

app = Flask(__name__, static_folder='static', template_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'linux-terminal-secret-key-2024')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

sessions = {}

class TerminalSession:
    def __init__(self, sid):
        self.sid = sid
        self.filesystem = FileSystem()
        self.memory_manager = MemoryManager()
        self.process_manager = ProcessManager(self.memory_manager)
        self.user_manager = UserManager()
        self.network_manager = NetworkManager()
        self.device_manager = DeviceManager()
        self.package_manager = PackageManager(self.filesystem)
        self.boot_manager = BootManager(
            self.filesystem,
            self.process_manager,
            self.memory_manager,
            self.device_manager,
            self.network_manager
        )
        self.command_handler = CommandHandler(
            self.filesystem,
            self.process_manager,
            self.memory_manager,
            self.user_manager,
            self.network_manager,
            self.device_manager,
            self.package_manager,
            self
        )
        self.current_user = 'root'
        self.hostname = 'localhost'
        self.is_booted = False
        self.is_shutting_down = False
        self.uptime_start = None
        self.env_vars = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
            'HOME': '/root',
            'USER': 'root',
            'SHELL': '/bin/bash',
            'TERM': 'xterm-256color',
            'LANG': 'en_US.UTF-8',
        }

    def emit(self, event, data):
        socketio.emit(event, data, room=self.sid)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@socketio.on('connect')
def handle_connect():
    sid = socketio.server.environ.get('HTTP_SEC_WEBSOCKET_KEY', str(time.time()))
    sessions[sid] = TerminalSession(sid)
    emit('connected', {'sid': sid})

@socketio.on('disconnect')
def handle_disconnect():
    sid = socketio.server.environ.get('HTTP_SEC_WEBSOCKET_KEY', str(time.time()))
    if sid in sessions:
        del sessions[sid]

@socketio.on('boot')
def handle_boot(data):
    sid = data.get('sid')
    session = sessions.get(sid)
    if session and not session.is_booted:
        def boot_sequence():
            for msg in session.boot_manager.boot():
                session.emit('boot_message', {'message': msg})
                time.sleep(0.05)
            session.is_booted = True
            session.uptime_start = time.time()
            session.emit('boot_complete', {
                'prompt': session.command_handler.get_prompt()
            })
        threading.Thread(target=boot_sequence, daemon=True).start()

@socketio.on('command')
def handle_command(data):
    sid = data.get('sid')
    command = data.get('command', '').strip()
    session = sessions.get(sid)
    
    if not session:
        emit('output', {'output': 'Session not found'})
        return
    
    if not session.is_booted:
        emit('output', {'output': 'System not booted. Please wait for boot to complete.'})
        return
    
    if command == 'shutdown' or command.startswith('shutdown '):
        session.is_shutting_down = True
        def shutdown_sequence():
            for msg in session.boot_manager.shutdown():
                session.emit('output', {'output': msg})
                time.sleep(0.05)
            session.emit('shutdown_complete', {})
            session.is_booted = False
        threading.Thread(target=shutdown_sequence, daemon=True).start()
        return
    
    if command == 'reboot':
        session.is_shutting_down = True
        def reboot_sequence():
            for msg in session.boot_manager.shutdown():
                session.emit('output', {'output': msg})
                time.sleep(0.05)
            session.is_booted = False
            time.sleep(0.5)
            for msg in session.boot_manager.boot():
                session.emit('boot_message', {'message': msg})
                time.sleep(0.05)
            session.is_booted = True
            session.uptime_start = time.time()
            session.emit('boot_complete', {
                'prompt': session.command_handler.get_prompt()
            })
        threading.Thread(target=reboot_sequence, daemon=True).start()
        return
    
    output = session.command_handler.execute(command)
    
    emit('output', {
        'output': output,
        'prompt': session.command_handler.get_prompt()
    })

@socketio.on('save_filesystem')
def handle_save_filesystem(data):
    sid = data.get('sid')
    session = sessions.get(sid)
    if session:
        fs_data = session.filesystem.serialize()
        emit('filesystem_data', {'data': fs_data})

@socketio.on('load_filesystem')
def handle_load_filesystem(data):
    sid = data.get('sid')
    fs_data = data.get('data')
    session = sessions.get(sid)
    if session and fs_data:
        session.filesystem.deserialize(fs_data)
        emit('filesystem_loaded', {'success': True})

@socketio.on('get_memory_stats')
def handle_memory_stats(data):
    sid = data.get('sid')
    session = sessions.get(sid)
    if session:
        stats = session.memory_manager.get_stats()
        emit('memory_stats', stats)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
