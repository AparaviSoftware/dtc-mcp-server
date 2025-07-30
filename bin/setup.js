#!/usr/bin/env node

const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get package root and venv paths using path.resolve for cross-platform compatibility
const packageRoot = path.resolve(__dirname, '..');
const venvPath = path.resolve(packageRoot, '.venv');

// Platform-specific paths
const isWin = process.platform === 'win32';
const pythonCommand = isWin ? 'python' : 'python3';
const venvPython = isWin
  ? path.resolve(venvPath, 'Scripts', 'python.exe')
  : path.resolve(venvPath, 'bin', 'python');
const venvPip = isWin
  ? path.resolve(venvPath, 'Scripts', 'pip.exe')
  : path.resolve(venvPath, 'bin', 'pip');

function logToStderr(message) {
  process.stderr.write(`${message}\n`);
}

function runCommand(command, args, options = {}) {
  logToStderr(`Running: ${command} ${args.join(' ')}`);

  // Always redirect stdout to stderr to match shell script behavior
  const result = spawnSync(command, args, {
    stdio: ['inherit', 'pipe', 'inherit'],
    encoding: 'utf8',
    ...options
  });

  if (result.stdout) {
    logToStderr(result.stdout);
  }

  if (result.error) {
    logToStderr(`Error executing command: ${result.error.message}`);
    return false;
  }

  if (result.status !== 0) {
    logToStderr(`Command failed with exit code: ${result.status}`);
    return false;
  }

  return true;
}

function checkPythonVersion() {
  logToStderr('\nChecking Python version...');
  const result = spawnSync(pythonCommand, ['--version'], {
    encoding: 'utf8',
    stdio: ['inherit', 'pipe', 'inherit']
  });

  if (result.error || result.status !== 0) {
    logToStderr(`Error: ${pythonCommand} not found. Please install Python 3.8 or later.`);
    process.exit(1);
  }

  const version = result.stdout.trim();
  logToStderr(`Found ${version}`);
}

function createVirtualEnv() {
  logToStderr('\nSetting up Python virtual environment...');

  // Check if venv already exists
  if (fs.existsSync(venvPath)) {
    logToStderr('Virtual environment already exists, skipping creation.');
    return true;
  }

  // Create virtual environment
  return runCommand(pythonCommand, ['-m', 'venv', venvPath]);
}

function installDependencies() {
  logToStderr('\nInstalling Python dependencies...');
  const mainRequirementsPath = path.resolve(packageRoot, 'requirements.txt');
  const SDKRequirementsPath = path.resolve(packageRoot, 'requirements-testpypi.txt');

  // Upgrade pip first
  if (!runCommand(venvPip, ['install', 'pip'])) {
    return false;
  }

  // Install main requirements
  logToStderr('\nInstalling main requirements...');
  if (!runCommand(venvPip, ['install', '-r', mainRequirementsPath])) {
    return false;
  }

  // Install test PyPI requirements
  logToStderr('\nInstalling Aparavi SDK requirements...');
  return runCommand(venvPip, ['install', '-r', SDKRequirementsPath]);
}

function setup() {
  logToStderr('Starting MCP server setup...');

  // Check Python installation
  checkPythonVersion();

  // Create virtual environment
  if (!createVirtualEnv()) {
    logToStderr('Failed to create virtual environment');
    process.exit(1);
  }

  // Install dependencies
  if (!installDependencies()) {
    logToStderr('Failed to install dependencies');
    process.exit(1);
  }

  logToStderr('\n✅ Setup completed successfully!');
}

// Run setup if this script is called directly
if (require.main === module) {
  setup();
}
