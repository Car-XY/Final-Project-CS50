const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess;

function startFlask() {
  const isDev = !app.isPackaged;
  const exePath = isDev
    ? 'python'
    : path.join(process.resourcesPath, 'backend', 'app.exe');
  const args = isDev ? ['backend/app.py'] : [];

  //remove this when out of development
  flaskProcess = spawn(exePath, args, {
    env: { ...process.env, FLASK_ENV: 'development' }
  });

  flaskProcess.stdout.on('data', (data) => console.log(`Flask: ${data}`));
  flaskProcess.stderr.on('data', (data) => console.error(`Flask error: ${data}`));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    },
  });

  // Give Flask a moment to start before loading
  setTimeout(() => win.loadURL('http://localhost:5000'), 800);
}

app.whenReady().then(() => {
  startFlask();
  createWindow();
});

app.on('window-all-closed', () => {
  if (flaskProcess) flaskProcess.kill();
  if (process.platform !== 'darwin') app.quit();
});