const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    isElectron: true,
    getAppVersion: () => '1.0.0'
});