#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Get the path to the Python script relative to this file
const pythonScriptPath = path.join(__dirname, '..', 'mcp-server.py');

// Spawn Python process
const pythonProcess = spawn('python3', [pythonScriptPath], {
  stdio: 'inherit', // Inherit stdio streams
  env: process.env  // Pass through environment variables
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