import { spawn } from 'child_process';

async function runCommand(command: string, args: string[]): Promise<void> {
  return new Promise((resolve, reject) => {
    const proc = spawn(command, args, { stdio: 'inherit' });
    proc.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`Command ${command} failed with code ${code}`));
    });
  });
}

async function launchBackend() {
  console.log("Checking python path...");
  await runCommand('python3', ['-c', 'import sys; print(sys.path)']);

  console.log("Starting backend...");
  await runCommand('python3', ['-m', 'uvicorn', 'backend.server:app', '--host', '0.0.0.0', '--port', '8000', '--reload']);
}

launchBackend().catch(console.error);
