# ngrok Permanent Tunnel Setup

This replaces temporary tunnels with ngrok tunnels that use a reserved domain or custom domain.

## Why this is needed

- Temporary tunnel URLs change every restart.
- Permanent ngrok tunnels need a reserved domain or custom domain.
- The server only needs to start ngrok with a preconfigured authtoken.

## One-time setup (done from a machine/network that can access the ngrok dashboard)

1. Reserve two permanent endpoints in ngrok:
   - `api.<your-domain>` -> `http://127.0.0.1:8000`
   - `tts.<your-domain>` -> `http://127.0.0.1:8882`
2. Copy your ngrok authtoken from the dashboard.

## Server setup

1. Install ngrok in user space on the server and authenticate once:

```bash
mkdir -p ~/.local/bin
curl -fsSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip -o /tmp/ngrok.zip
unzip -o /tmp/ngrok.zip -d ~/.local/bin
chmod +x ~/.local/bin/ngrok
~/.local/bin/ngrok config add-authtoken <your-ngrok-authtoken>
```

2. Create `/home/raid/sqora/sqora/.env.tunnel`:

```bash
NGROK_BIN=/home/raid/.local/bin/ngrok
NGROK_API_DOMAIN=api.<your-domain>
NGROK_TTS_DOMAIN=tts.<your-domain>
```

If those domain variables are left empty, the services will start temporary tunnels instead of permanent ones.

3. Install user services:

```bash
mkdir -p ~/.config/systemd/user
cp ops/systemd/sqora-ngrok-api.service ~/.config/systemd/user/
cp ops/systemd/sqora-ngrok-tts.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now sqora-ngrok-api.service
systemctl --user enable --now sqora-ngrok-tts.service
```

4. Validate:

```bash
systemctl --user --no-pager --full status sqora-ngrok-api.service
systemctl --user --no-pager --full status sqora-ngrok-tts.service
```

## Production cutover

1. Set Vercel variables:
   - `VITE_API_URL=https://api.<your-domain>`
   - `VITE_TTS_URL=https://tts.<your-domain>`
2. Redeploy production.
3. Disable the old tunnel units after validation:

```bash
systemctl --user disable --now sqora-tunnel-api.service || true
systemctl --user disable --now sqora-tunnel-tts.service || true
```
