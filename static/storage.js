class PersistentStorage {
    constructor() {
        this.dbName = 'LinuxTerminalDB';
        this.dbVersion = 1;
        this.storeName = 'filesystem';
        this.db = null;
        this.initDB();
    }

    initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => {
                console.error('IndexedDB error:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id' });
                }
            };
        });
    }

    async saveFilesystem(data) {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.put({
                id: 'filesystem',
                data: data,
                timestamp: Date.now()
            });

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    }

    async loadFilesystem() {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get('filesystem');

            request.onsuccess = () => {
                const result = request.result;
                resolve(result ? result.data : null);
            };

            request.onerror = () => reject(request.error);
        });
    }

    async clearFilesystem() {
        if (!this.db) await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete('filesystem');

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    }
}

const storage = new PersistentStorage();
