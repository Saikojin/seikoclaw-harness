#!/usr/bin/env node
/**
 * Godot MCP Dynamic Stdio Bridge for Antigravity & AI Agents
 * 
 * Auto-detects the active Godot project (via GODOT_PROJECT_PATH, cwd, or scanning parent/workspace directories with project.godot),
 * computes the deterministic local port and routing pin (ProjectIdentity v2), and spawns the GameDev-MCP-Server stdio transport.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const os = require('os');

// 1. Resolve GameDev-MCP-Server binary
const defaultServerPath = path.join(os.homedir(), '.ai-game-dev', 'server', 'win-x64', 'gamedev-mcp-server.exe');
const serverExe = process.env.GODOT_MCP_SERVER_EXE || process.env.UNITY_MCP_SERVER_EXE || defaultServerPath;

if (!fs.existsSync(serverExe)) {
    process.stderr.write(`[godot-mcp-server] Error: GameDev-MCP-Server binary not found at ${serverExe}\n`);
    process.stderr.write(`Run: godot-cli install-plugin <project> --with-server\n`);
    process.exit(1);
}

// 2. Deterministic Port & Pin Algorithm (ProjectIdentity v2)
// Parity with com.IvanMurzak.McpPlugin.AgentConfig.ProjectIdentity and @baizor/gamedev-cli-core
function derivePinAndPort(projectRoot) {
    let normalized = projectRoot.replace(/[/\\]+$/, '').replace(/\\/g, '/').toLowerCase();
    const hash = crypto.createHash('sha256').update(normalized, 'utf8').digest();
    const pin = hash.subarray(0, 4).toString('hex');
    const portOffset = hash.readUInt32LE(0) % 10000;
    const port = 20000 + portOffset;
    return { pin, port };
}

// 3. Find active Godot project
function findActiveGodotProject() {
    // A. Explicit environment variable
    if (process.env.GODOT_PROJECT_PATH && fs.existsSync(path.join(process.env.GODOT_PROJECT_PATH, 'project.godot'))) {
        return path.resolve(process.env.GODOT_PROJECT_PATH);
    }

    // B. Current working directory
    const cwd = process.cwd();
    if (fs.existsSync(path.join(cwd, 'project.godot'))) {
        return cwd;
    }

    // C. Search parent directories
    let curr = cwd;
    while (curr && path.dirname(curr) !== curr) {
        if (fs.existsSync(path.join(curr, 'project.godot'))) {
            return curr;
        }
        curr = path.dirname(curr);
    }

    // D. Scan common DevWorkspace locations for active Godot projects
    const devWorkspace = 'D:\\DevWorkspace';
    if (fs.existsSync(devWorkspace)) {
        try {
            const subdirs = fs.readdirSync(devWorkspace, { withFileTypes: true });
            for (const ent of subdirs) {
                if (ent.isDirectory()) {
                    const candidate = path.join(devWorkspace, ent.name);
                    if (fs.existsSync(path.join(candidate, 'project.godot'))) {
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

const projectRoot = findActiveGodotProject();
let port = 20000;
let pin = '';

if (projectRoot) {
    const derived = derivePinAndPort(projectRoot);
    port = derived.port;
    pin = derived.pin;
    process.stderr.write(`[godot-mcp-server] Bound to Godot Project: ${projectRoot} (Port: ${port}, Pin: ${pin})\n`);
} else {
    process.stderr.write(`[godot-mcp-server] Warning: No active Godot project directory found. Defaulting to port ${port}\n`);
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
    process.stderr.write(`[godot-mcp-server] Spawn error: ${err.message}\n`);
    process.exit(1);
});

child.on('exit', (code, signal) => {
    process.exit(code ?? (signal ? 1 : 0));
});
