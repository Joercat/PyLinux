class Terminal {
    constructor() {
        this.output = document.getElementById('terminal-output');
        this.input = document.getElementById('terminal-input');
        this.promptElement = document.getElementById('prompt');
        this.socket = null;
        this.sid = null;
        this.commandHistory = [];
        this.historyIndex = -1;
        this.currentPrompt = '';
        this.isBooted = false;
        this.autoSaveInterval = null;

        this.init();
    }

    init() {
        this.connectSocket();
        this.setupEventListeners();
        this.startAutoSave();
    }

    connectSocket() {
        this.socket = io({
            transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
            this.addOutput('Connecting to system...', 'system-message');
        });

        this.socket.on('connected', (data) => {
            this.sid = data.sid;
            this.loadAndBoot();
        });

        this.socket.on('boot_message', (data) => {
            this.addOutput(data.message, 'boot-message');
            this.scrollToBottom();
        });

        this.socket.on('boot_complete', (data) => {
            this.isBooted = true;
            this.currentPrompt = data.prompt;
            this.updatePrompt();
            this.addOutput('');
            this.addOutput('Welcome to Linux Terminal 1.0 LTS', 'system-message');
            this.addOutput('');
            this.addOutput('Type "help" for available commands.', 'system-message');
            this.addOutput('');
            this.input.disabled = false;
            this.input.focus();
        });

        this.socket.on('output', (data) => {
            if (data.output) {
                this.addOutput(data.output, 'output-line');
            }
            if (data.prompt) {
                this.currentPrompt = data.prompt;
                this.updatePrompt();
            }
            this.scrollToBottom();
        });

        this.socket.on('shutdown_complete', () => {
            this.isBooted = false;
            this.addOutput('');
            this.addOutput('System halted. Refresh page to restart.', 'shutdown-screen');
            this.input.disabled = true;
        });

        this.socket.on('filesystem_data', async (data) => {
            await storage.saveFilesystem(data.data);
        });

        this.socket.on('filesystem_loaded', (data) => {
            if (data.success) {
                this.boot();
            }
        });

        this.socket.on('disconnect', () => {
            this.addOutput('Connection lost. Please refresh the page.', 'error-line');
            this.input.disabled = true;
        });
    }

    async loadAndBoot() {
        const savedFS = await storage.loadFilesystem();
        if (savedFS) {
            this.socket.emit('load_filesystem', {
                sid: this.sid,
                data: savedFS
            });
        } else {
            this.boot();
        }
    }

    boot() {
        this.socket.emit('boot', { sid: this.sid });
    }

    setupEventListeners() {
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory('up');
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory('down');
            } else if (e.key === 'Tab') {
                e.preventDefault();
            } else if (e.key === 'c' && e.ctrlKey) {
                e.preventDefault();
                this.input.value = '';
                this.addOutput(this.currentPrompt + '^C');
            } else if (e.key === 'l' && e.ctrlKey) {
                e.preventDefault();
                this.clearScreen();
            }
        });

        this.input.addEventListener('input', () => {
            this.historyIndex = -1;
        });

        document.addEventListener('click', () => {
            if (this.isBooted) {
                this.input.focus();
            }
        });
    }

    handleCommand() {
        const command = this.input.value.trim();
        
        if (!this.isBooted) {
            return;
        }

        this.addOutput(this.currentPrompt + command, 'prompt-line');

        if (command) {
            this.commandHistory.unshift(command);
            if (this.commandHistory.length > 1000) {
                this.commandHistory.pop();
            }

            if (command === 'clear') {
                this.clearScreen();
                this.input.value = '';
                return;
            }

            this.socket.emit('command', {
                sid: this.sid,
                command: command
            });
        } else {
            this.addOutput('');
        }

        this.input.value = '';
        this.historyIndex = -1;
    }

    navigateHistory(direction) {
        if (this.commandHistory.length === 0) return;

        if (direction === 'up') {
            if (this.historyIndex < this.commandHistory.length - 1) {
                this.historyIndex++;
                this.input.value = this.commandHistory[this.historyIndex];
            }
        } else if (direction === 'down') {
            if (this.historyIndex > 0) {
                this.historyIndex--;
                this.input.value = this.commandHistory[this.historyIndex];
            } else if (this.historyIndex === 0) {
                this.historyIndex = -1;
                this.input.value = '';
            }
        }
    }

    addOutput(text, className = '') {
        const line = document.createElement('div');
        line.textContent = text;
        if (className) {
            line.className = className;
        }
        this.output.appendChild(line);
    }

    updatePrompt() {
        this.promptElement.textContent = this.currentPrompt;
    }

    clearScreen() {
        this.output.innerHTML = '';
    }

    scrollToBottom() {
        this.output.scrollTop = this.output.scrollHeight;
    }

    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            if (this.isBooted && this.sid) {
                this.socket.emit('save_filesystem', { sid: this.sid });
            }
        }, 30000);
    }

    saveFilesystem() {
        if (this.isBooted && this.sid) {
            this.socket.emit('save_filesystem', { sid: this.sid });
        }
    }
}

function shutdown() {
    if (terminal && terminal.isBooted) {
        terminal.socket.emit('command', {
            sid: terminal.sid,
            command: 'shutdown'
        });
    }
}

window.addEventListener('beforeunload', () => {
    if (terminal) {
        terminal.saveFilesystem();
    }
});

const terminal = new Terminal();
