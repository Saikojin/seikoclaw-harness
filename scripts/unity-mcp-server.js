#!/usr/bin/env node
/**
 * Unity MCP Dynamic Stdio Bridge for Antigravity & AI Agents
 * 
 * Auto-detects the active Unity project (via UNITY_PROJECT_PATH, cwd, or running Unity process with lockfile),
 * computes the deterministic local port and routing pin, and spawns the GameDev-MCP-Server stdio transport.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

// 1. Resolve GameDev-MCP-Server binary
const defaultServerPath = path.join(os.homedir(), '.ai-game-dev', 'server', 'win-x64', 'gamedev-mcp-server.exe');
const serverExe = process.env.UNITY_MCP_SERVER_EXE || defaultServerPath;

if (!fs.existsSync(serverExe)) {
    process.stderr.write(`[unity-mcp-server] Error: GameDev-MCP-Server binary not found at ${serverExe}\n`);
    process.stderr.write(`Run: unity-mcp-cli install-plugin <project> --with-server\n`);
    process.exit(1);
}

// 2. Deterministic Port & Pin Algorithm (ProjectIdentity v2)
function derivePinAndPort(projectRoot) {
    let normalized = projectRoot.replace(/[/\\]+$/, '').replace(/\\/g, '/').toLowerCase();
    const hash = crypto.createHash('sha256').update(normalized, 'utf8').digest();
    const pin = hash.subarray(0, 4).toString('hex');
    const portOffset = hash.readUInt32LE(0) % 10000;
    const port = 20000 + portOffset;
    return { pin, port };
}

// 3. Find active Unity project
function findActiveUnityProject() {
    // A. Explicit env var
    if (process.env.UNITY_PROJECT_PATH && fs.existsSync(path.join(process.env.UNITY_PROJECT_PATH, 'Assets'))) {
        return path.resolve(process.env.UNITY_PROJECT_PATH);
    }

    // B. Current working directory
    const cwd = process.cwd();
    if (fs.existsSync(path.join(cwd, 'Assets'))) {
        return cwd;
    }

    // C. Search parent directories
    let curr = cwd;
    while (curr && path.dirname(curr) !== curr) {
        if (fs.existsSync(path.join(curr, 'Assets'))) {
            return curr;
        }
        curr = path.dirname(curr);
    }

    // D. Scan common DevWorkspace locations for active Temp/UnityLockfile
    const devWorkspace = 'D:\\DevWorkspace';
    if (fs.existsSync(devWorkspace)) {
        try {
            const subdirs = fs.readdirSync(devWorkspace, { withFileTypes: true });
            for (const ent of subdirs) {
                if (ent.isDirectory()) {
                    const candidate = path.join(devWorkspace, ent.name);
                    const lockfile = path.join(candidate, 'Temp', 'UnityLockfile');
                    if (fs.existsSync(lockfile) && fs.existsSync(path.join(candidate, 'Assets'))) {
                        return candidate;
                    }
                }
            }
        } catch (e) {
            // Ignore scan errors
        }
    }

    return null;
}

const projectRoot = findActiveUnityProject();
let port = 22958;
let pin = '';

if (projectRoot) {
    const derived = derivePinAndPort(projectRoot);
    port = derived.port;
    pin = derived.pin;
    process.stderr.write(`[unity-mcp-server] Bound to Unity Project: ${projectRoot} (Port: ${port}, Pin: ${pin})\n`);
} else {
    process.stderr.write(`[unity-mcp-server] Warning: No active Unity project directory found. Defaulting to port ${port}\n`);
}

// 4. Spawn GameDev-MCP-Server in Stdio mode
const args = [
    `client-transport=stdio`,
    `port=${port}`,
    `plugin-timeout=30000`,
    `authorization=none`
];

if (pin) {
    args.push(`project=${pin}`);
}

const child = spawn(serverExe, args, {
    stdio: ['pipe', 'pipe', 'inherit'],
    windowsHide: true
});

process.stdin.pipe(child.stdin);
child.stdout.pipe(process.stdout);

child.on('error', (err) => {
    process.stderr.write(`[unity-mcp-server] Spawn error: ${err.message}\n`);
    process.exit(1);
});

child.on('exit', (code, signal) => {
    process.exit(code ?? (signal ? 1 : 0));
});
