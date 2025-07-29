#!/usr/bin/env node

const { spawn, spawnSync } = require('child_process');
const path = require('path');

// Get package root directory using normalized paths
const packageRoot = path.resolve(__dirname, '..');
const pythonScriptPath = path.resolve(packageRoot, 'mcp-server.py');
const setupScript = path.resolve(__dirname, 'setup.js');
const venvPath = path.resolve(packageRoot, '.venv');

// Run setup script
const setup = spawnSync('node', [setupScript], {
  stdio: 'inherit'
});

if (setup.status !== 0) {
  console.error('Failed to setup Python environment');
  process.exit(1);
}

// Get the Python path based on OS using normalized paths
const pythonPath = process.platform === 'win32'
  ? path.resolve(venvPath, 'Scripts', 'python.exe')
  : path.resolve(venvPath, 'bin', 'python');

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
