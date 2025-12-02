class FileSystemDB {
    constructor() {
        this.dbName = 'PyLinuxFS';
        this.dbVersion = 1;
        this.storeName = 'filesystem';
        this.db = null;
    }

    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = (event) => {
                console.error('IndexedDB error:', event.target.error);
                reject(event.target.error);
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                console.log('IndexedDB connected');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const store = db.createObjectStore(this.storeName, { keyPath: 'id' });
                    store.createIndex('sessionId', 'sessionId', { unique: false });
                    store.createIndex('timestamp', 'timestamp', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('sessions')) {
                    const sessionStore = db.createObjectStore('sessions', { keyPath: 'id' });
                    sessionStore.createIndex('lastAccess', 'lastAccess', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('history')) {
                    const historyStore = db.createObjectStore('history', { keyPath: 'id', autoIncrement: true });
                    historyStore.createIndex('sessionId', 'sessionId', { unique: false });
                    historyStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    async saveFilesystem(sessionId, filesystemData) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            const data = {
                id: sessionId,
                sessionId: sessionId,
                filesystem: filesystemData,
                timestamp: Date.now()
            };

            const request = store.put(data);

            request.onsuccess = () => {
                console.log('Filesystem saved to IndexedDB');
                resolve(true);
            };

            request.onerror = (event) => {
                console.error('Error saving filesystem:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    async loadFilesystem(sessionId) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get(sessionId);

            request.onsuccess = (event) => {
                const result = event.target.result;
                if (result) {
                    console.log('Filesystem loaded from IndexedDB');
                    resolve(result.filesystem);
                } else {
                    resolve(null);
                }
            };

            request.onerror = (event) => {
                console.error('Error loading filesystem:', event.target.error);
                reject(event.target.error);
            };
        });
    }

    async saveSession(sessionId, sessionData) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction(['sessions'], 'readwrite');
            const store = transaction.objectStore('sessions');

            const data = {
                id: sessionId,
                ...sessionData,
                lastAccess: Date.now()
            };

            const request = store.put(data);

            request.onsuccess = () => resolve(true);
            request.onerror = (event) => reject(event.target.error);
        });
    }

    async loadSession(sessionId) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction(['sessions'], 'readonly');
            const store = transaction.objectStore('sessions');
            const request = store.get(sessionId);

            request.onsuccess = (event) => resolve(event.target.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }

    async addToHistory(sessionId, command) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction(['history'], 'readwrite');
            const store = transaction.objectStore('history');

            const data = {
                sessionId: sessionId,
                command: command,
                timestamp: Date.now()
            };

            const request = store.add(data);

            request.onsuccess = () => resolve(true);
            request.onerror = (event) => reject(event.target.error);
        });
    }

    async getHistory(sessionId, limit = 100) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction(['history'], 'readonly');
            const store = transaction.objectStore('history');
            const index = store.index('sessionId');
            const request = index.getAll(sessionId);

            request.onsuccess = (event) => {
                const results = event.target.result;
                const sorted = results.sort((a, b) => b.timestamp - a.timestamp).slice(0, limit);
                resolve(sorted.reverse().map(r => r.command));
            };

            request.onerror = (event) => reject(event.target.error);
        });
    }

    async clearSession(sessionId) {
        return new Promise((resolve, reject) => {
            if (!this.db) {
                reject(new Error('Database not initialized'));
                return;
            }

            const transaction = this.db.transaction([this.storeName, 'sessions', 'history'], 'readwrite');
            
            transaction.objectStore(this.storeName).delete(sessionId);
            transaction.objectStore('sessions').delete(sessionId);
            
            const historyStore = transaction.objectStore('history');
            const index = historyStore.index('sessionId');
            const request = index.openCursor(sessionId);
            
            request.onsuccess = (event) => {
                const cursor = event.target.result;
                if (cursor) {
                    cursor.delete();
                    cursor.continue();
                }
            };

            transaction.oncomplete = () => resolve(true);
            transaction.onerror = (event) => reject(event.target.error);
        });
    }

    getSessionId() {
        let sessionId = localStorage.getItem('pylinux_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('pylinux_session_id', sessionId);
        }
        return sessionId;
    }
}

window.FileSystemDB = FileSystemDB;
