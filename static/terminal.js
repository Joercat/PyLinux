class Terminal {
    constructor() {
        this.output = document.getElementById('output');
        this.input = document.getElementById('command-input');
        this.prompt = document.getElementById('prompt');
        this.terminal = document.getElementById('terminal');
        this.bootBtn = document.getElementById('boot-btn');
        this.shutdownBtn = document.getElementById('shutdown-btn');
        this.rebootBtn = document.getElementById('reboot-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.cpuUsage = document.getElementById('cpu-usage');
        this.memUsage = document.getElementById('mem-usage');
        this.uptimeEl = document.getElementById('uptime');
        this.processesEl = document.getElementById('processes');
        
        this.socket = null;
        this.sessionId = null;
        this.isBooted = false;
        this.history = [];
        this.historyIndex = -1;
        this.currentInput = '';
        this.db = new FileSystemDB();
        this.completionIndex = -1;
        this.completions = [];
        this.updateInterval = null;
        
        this.init();
    }

    async init() {
        await this.db.init();
        this.sessionId = this.db.getSessionId();
        
        const savedHistory = await this.db.getHistory(this.sessionId, 1000);
        if (savedHistory) {
            this.history = savedHistory;
        }
        
        this.connectSocket();
        this.setupEventListeners();
        this.updateStatus('off');
        
        this.writeLine('PyLinux Terminal Emulator v1.0.0');
        this.writeLine('Press "Boot System" to start the system.');
        this.writeLine('');
    }

    connectSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.socket = io(window.location.origin, {
            query: { session_id: this.sessionId },
            transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
            console.log('Connected to server');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateStatus('off');
        });

        this.socket.on('session', (data) => {
            if (data.session_id) {
                this.sessionId = data.session_id;
                localStorage.setItem('pylinux_session_id', this.sessionId);
            }
        });

        this.socket.on('output', (data) => {
            if (data.data) {
                this.write(data.data);
            }
            if (data.prompt) {
                this.setPrompt(data.prompt);
            }
            this.scrollToBottom();
        });

        this.socket.on('boot_complete', (data) => {
            this.isBooted = true;
            this.updateStatus('on');
            this.enableControls(true);
            if (data.prompt) {
                this.setPrompt(data.prompt);
            }
            this.input.focus();
            this.startStatusUpdates();
            this.syncFilesystem();
        });

        this.socket.on('shutdown_complete', () => {
            this.isBooted = false;
            this.updateStatus('off');
            this.enableControls(false);
            this.setPrompt('');
            this.stopStatusUpdates();
        });

        this.socket.on('completions', (data) => {
            if (data.completions && data.completions.length > 0) {
                this.showCompletions(data.completions);
            }
        });

        this.socket.on('filesystem_data', async (data) => {
            if (data.filesystem) {
                await this.db.saveFilesystem(this.sessionId, data.filesystem);
            }
        });

        this.socket.on('sync_complete', async (data) => {
            if (data.filesystem) {
                await this.db.saveFilesystem(this.sessionId, data.filesystem);
            }
        });
    }

    setupEventListeners() {
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        this.input.addEventListener('input', () => this.hideCompletions());
        
        this.bootBtn.addEventListener('click', () => this.boot());
        this.shutdownBtn.addEventListener('click', () => this.shutdown());
        this.rebootBtn.addEventListener('click', () => this.reboot());
        this.clearBtn.addEventListener('click', () => this.clear());
        
        this.terminal.addEventListener('click', () => this.input.focus());
        
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'c') {
                e.preventDefault();
                this.sendSignal('SIGINT');
            } else if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                this.clear();
            } else if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                if (this.isBooted && !this.input.value) {
                    this.sendCommand('exit');
                }
            }
        });
    }

    handleKeyDown(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            this.hideCompletions();
            const command = this.input.value;
            this.sendCommand(command);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.navigateHistory(-1);
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.navigateHistory(1);
        } else if (e.key === 'Tab') {
            e.preventDefault();
            this.handleTabCompletion();
        } else if (e.key === 'Escape') {
            this.hideCompletions();
        }
    }

    handleTabCompletion() {
        const partial = this.input.value;
        if (this.isBooted && partial) {
            this.socket.emit('tab_complete', {
                session_id: this.sessionId,
                partial: partial
            });
        }
    }

    showCompletions(completions) {
        this.completions = completions;
        
        if (completions.length === 1) {
            const parts = this.input.value.split(/\s+/);
            parts[parts.length - 1] = completions[0];
            this.input.value = parts.join(' ');
            if (!completions[0].endsWith('/')) {
                this.input.value += ' ';
            }
        } else if (completions.length > 1) {
            this.writeLine('');
            this.writeLine(completions.join('  '));
            this.write(this.prompt.textContent + this.input.value);
        }
    }

    hideCompletions() {
        this.completions = [];
        this.completionIndex = -1;
    }

    navigateHistory(direction) {
        if (this.history.length === 0) return;
        
        if (this.historyIndex === -1) {
            this.currentInput = this.input.value;
        }
        
        this.historyIndex += direction;
        
        if (this.historyIndex < -1) {
            this.historyIndex = -1;
        } else if (this.historyIndex >= this.history.length) {
            this.historyIndex = this.history.length - 1;
        }
        
        if (this.historyIndex === -1) {
            this.input.value = this.currentInput;
        } else {
            this.input.value = this.history[this.history.length - 1 - this.historyIndex];
        }
        
        setTimeout(() => {
            this.input.selectionStart = this.input.selectionEnd = this.input.value.length;
        }, 0);
    }

    async sendCommand(command) {
        if (!this.isBooted) {
            this.writeLine('System not booted. Press "Boot System" to start.');
            return;
        }
        
        this.writeLine(this.prompt.textContent + command);
        this.input.value = '';
        this.historyIndex = -1;
        this.currentInput = '';
        
        if (command.trim()) {
            this.history.push(command);
            await this.db.addToHistory(this.sessionId, command);
        }
        
        this.socket.emit('command', {
            session_id: this.sessionId,
            command: command
        });
    }

    sendSignal(signal) {
        if (this.isBooted) {
            this.socket.emit('signal', {
                session_id: this.sessionId,
                signal: signal
            });
        }
    }

    async boot() {
        this.clear();
        this.updateStatus('booting');
        this.bootBtn.disabled = true;
        
        const savedFs = await this.db.loadFilesystem(this.sessionId);
        
        this.socket.emit('boot', {
            session_id: this.sessionId,
            filesystem: savedFs
        });
    }

    shutdown() {
        if (this.isBooted) {
            this.socket.emit('command', {
                session_id: this.sessionId,
                command: 'shutdown'
            });
        }
    }

    reboot() {
        if (this.isBooted) {
            this.socket.emit('command', {
                session_id: this.sessionId,
                command: 'reboot'
            });
        }
    }

    async syncFilesystem() {
        const savedFs = await this.db.loadFilesystem(this.sessionId);
        this.socket.emit('sync_fs', {
            session_id: this.sessionId,
            filesystem: savedFs
        });
    }

    saveFilesystem() {
        this.socket.emit('get_fs', {
            session_id: this.sessionId
        });
    }

    clear() {
        this.output.innerHTML = '';
    }

    write(text) {
        text = this.processAnsiCodes(text);
        
        if (text.includes('\033[2J') || text.includes('\033[H')) {
            this.clear();
            text = text.replace(/\033\[2J/g, '').replace(/\033\[H/g, '');
        }
        
        if (text.includes('\033c')) {
            this.clear();
            text = text.replace(/\033c/g, '');
        }
        
        const span = document.createElement('span');
        span.innerHTML = text;
        this.output.appendChild(span);
        this.scrollToBottom();
    }

    writeLine(text) {
        this.write(text + '\n');
    }

    processAnsiCodes(text) {
        const colorMap = {
            '30': 'color: #000',
            '31': 'color: #ff6b6b',
            '32': 'color: #51cf66',
            '33': 'color: #ffd43b',
            '34': 'color: #74c0fc',
            '35': 'color: #da77f2',
            '36': 'color: #3bc9db',
            '37': 'color: #f8f9fa',
            '90': 'color: #868e96',
            '91': 'color: #ff8787',
            '92': 'color: #69db7c',
            '93': 'color: #ffe066',
            '94': 'color: #91a7ff',
            '95': 'color: #e599f7',
            '96': 'color: #66d9e8',
            '97': 'color: #fff',
            '1': 'font-weight: bold',
            '0': ''
        };

        text = text.replace(/\033\[([0-9;]+)m/g, (match, codes) => {
            const codeList = codes.split(';');
            const styles = codeList
                .map(code => colorMap[code] || '')
                .filter(s => s)
                .join('; ');
            
            if (styles) {
                return `</span><span style="${styles}">`;
            } else {
                return '</span><span>';
            }
        });

        return '<span>' + text + '</span>';
    }

    setPrompt(promptText) {
        this.prompt.textContent = promptText;
        document.querySelector('.terminal-title').textContent = promptText.replace(/[#$]\s*$/, '');
    }

    scrollToBottom() {
        this.terminal.scrollTop = this.terminal.scrollHeight;
    }

    updateStatus(status) {
        this.statusIndicator.className = '';
        
        switch (status) {
            case 'off':
                this.statusIndicator.classList.add('status-off');
                this.statusText.textContent = 'Powered Off';
                break;
            case 'booting':
                this.statusIndicator.classList.add('status-booting');
                this.statusText.textContent = 'Booting...';
                break;
            case 'on':
                this.statusIndicator.classList.add('status-on');
                this.statusText.textContent = 'Running';
                break;
        }
    }

    enableControls(enabled) {
        this.bootBtn.disabled = enabled;
        this.shutdownBtn.disabled = !enabled;
        this.rebootBtn.disabled = !enabled;
        this.input.disabled = !enabled;
        
        if (enabled) {
            this.input.focus();
        }
    }

    startStatusUpdates() {
        this.updateInterval = setInterval(() => {
            this.updateSystemInfo();
        }, 2000);
        this.updateSystemInfo();
    }

    stopStatusUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        this.cpuUsage.textContent = '0%';
        this.memUsage.textContent = '0%';
        this.uptimeEl.textContent = '0:00:00';
        this.processesEl.textContent = '0';
    }

    async updateSystemInfo() {
        if (!this.isBooted) return;
        
        try {
            const response = await fetch(`/api/status/${this.sessionId}`);
            const data = await response.json();
            
            if (data.memory) {
                this.memUsage.textContent = data.memory.percent.toFixed(1) + '%';
            }
            
            if (data.uptime !== undefined) {
                const uptime = Math.floor(data.uptime);
                const hours = Math.floor(uptime / 3600);
                const minutes = Math.floor((uptime % 3600) / 60);
                const seconds = uptime % 60;
                this.uptimeEl.textContent = `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
            
            if (data.processes !== undefined) {
                this.processesEl.textContent = data.processes;
            }
            
            const cpuPercent = Math.random() * 15 + 5;
            this.cpuUsage.textContent = cpuPercent.toFixed(1) + '%';
            
        } catch (error) {
            console.error('Error fetching system status:', error);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.terminal = new Terminal();
});
