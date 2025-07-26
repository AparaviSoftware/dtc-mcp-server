#!/usr/bin/env node

const { spawn, spawnSync } = require('child_process');
const path = require('path');

// Get package root directory
const packageRoot = path.join(__dirname, '..');
const pythonScriptPath = path.join(packageRoot, 'mcp-server.py');
const setupScript = path.join(__dirname, 'setup.sh');
const venvPath = path.join(packageRoot, '.venv');

// Run setup script
const setup = spawnSync('bash', [setupScript], {
  stdio: 'inherit'
});

if (setup.status !== 0) {
  console.error('Failed to setup Python environment');
  process.exit(1);
}

// Get the Python path based on OS
const pythonPath = process.platform === 'win32'
  ? path.join(venvPath, 'Scripts', 'python')
  : path.join(venvPath, 'bin', 'python');

// Spawn Python process using the virtual environment
const pythonProcess = spawn(pythonPath, [pythonScriptPath], {
  stdio: 'inherit',
  env: process.env
});

// Handle process events
pythonProcess.on('error', (err) => {
  console.error('Failed to start Python process:', err);
  process.exit(1);
});

// Forward exit code from Python process
pythonProcess.on('close', (code) => {
  process.exit(code);
});

// Handle SIGINT and SIGTERM to properly clean up
process.on('SIGINT', () => {
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  pythonProcess.kill('SIGTERM');
}); 