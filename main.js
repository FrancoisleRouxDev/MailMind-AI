const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

const venvPython = process.platform === 'win32'
    ? path.join(__dirname, 'backend', 'venv', 'Scripts', 'python.exe')
    : path.join(__dirname, 'backend', 'venv', 'bin', 'python');

let mainWindow;
let pyProc = null;

function createPythonServer() {
    const scriptPath = path.join(__dirname, 'backend', 'app.py');
    pyProc = spawn('python3', [scriptPath]);

    pyProc.stdout.on('data', (data) => {
        console.log(`[Python Server]: ${data}`);
    });

    pyProc.stderr.on('data', (data) => {
        console.error(`[Python Server Error]: ${data}`);
    });
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 850,
        minWidth: 900,
        minHeight: 600,
        titleBarStyle: 'hiddenInset',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: false,
            contextIsolation: true
        }
    });

    mainWindow.loadFile(path.join(__dirname, 'public', 'index.html'));
}

app.whenReady().then(() => {
    createPythonServer();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', () => {
    if (pyProc) pyProc.kill();
    if (process.platform !== 'darwin') app.quit();
});