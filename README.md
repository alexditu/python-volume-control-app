# Linux Volume Control Flask App - Setup Instructions

A web-based volume controller for Linux systems using PulseAudio, accessible remotely from your phone.

## Prerequisites

- Linux system with PulseAudio (most modern distributions)
- Python 3.6+ installed
- `pactl` command available (usually pre-installed with PulseAudio)

## Setup Instructions

### 1. Create the project structure
```bash
mkdir volume_control
cd volume_control
mkdir templates
```

### 2. Create the main application file
Save the Python Flask code as `app.py` in the main directory.

### 3. Create the HTML template
Save the HTML template as `templates/index.html` in the templates folder.

### 4. Python setup
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install flask pulsectl
```

### 5. Run the application
```bash
python volume_control_app.py
```

The server will start on port 5000 and be accessible from any device on your network.

## Features

- **Real-time volume display** - Shows current volume percentage and mute status
- **Three main buttons** - Volume Down, Mute/Unmute, Volume Up
- **Volume slider** - For precise volume control
- **Visual feedback** - Progress bar and color changes when muted
- **Mobile-friendly** - Responsive design that works great on phones
- **Auto-refresh** - Updates volume display every 2 seconds
- **Error handling** - Shows connection or system errors

## Accessing from your phone

### 1. Find your Linux system's IP address
```bash
ip addr show | grep 'inet ' | grep -v 127.0.0.1
```

### 2. Open your phone's browser
Navigate to:
```
http://YOUR_IP_ADDRESS:5000
```

For example: `http://192.168.1.100:5000`

## Project Structure
```
volume_control/
├── app.py                 # Main Flask application
└── templates/
    └── index.html         # Web interface template
```

## API Endpoints

The app provides several REST API endpoints:

- `GET /api/volume` - Get current volume and mute status
- `POST /api/volume/up` - Increase volume by 5%
- `POST /api/volume/down` - Decrease volume by 5%
- `POST /api/volume/mute` - Toggle mute status
- `POST /api/volume/set` - Set specific volume level

## Customization

### Change volume step size
Edit the `step` value in the `VolumeController` class in `app.py`:
```python
def __init__(self):
    self.step = 10  # Change from 5 to 10 for larger steps
```

### Change server port
Modify the last line in `app.py`:
```python
app.run(host='0.0.0.0', port=8080, debug=True)  # Changed from 5000 to 8080
```

### Run in production mode
For production use, disable debug mode:
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

## Troubleshooting

### PulseAudio not found
If you get errors about `pactl` not being found:
```bash
# Install PulseAudio utilities (Ubuntu/Debian)
sudo apt install pulseaudio-utils

# Install PulseAudio utilities (Fedora/CentOS)
sudo dnf install pulseaudio-utils
```

### Permission issues
If the app can't control volume, ensure your user is in the audio group:
```bash
sudo usermod -a -G audio $USER
```
Then log out and back in.

### Firewall blocking access
If you can't access from your phone, check if port 5000 is blocked:
```bash
# Ubuntu/Debian
sudo ufw allow 5000

# Fedora/CentOS
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Running as a service
To run the app automatically at startup, create a systemd service:

1. Create `/etc/systemd/system/volume-control.service`:
```ini
[Unit]
Description=Volume Control Web App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/volume_control
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable volume-control
sudo systemctl start volume-control
```

## Security Notes

- The app runs on all network interfaces (`0.0.0.0`) for remote access
- Consider using a reverse proxy (nginx) with SSL for secure connections
- The app provides system-level volume control, so limit network access as needed
- For local network use only, this setup is generally safe

## Alternative Sound Systems

While this app uses PulseAudio (most common), you can modify it for other systems:

- **ALSA**: Replace `pactl` commands with `amixer`
- **PipeWire**: Usually compatible with PulseAudio commands
- **OSS**: Use `ossmix` commands

## License

This code is provided as-is for personal use. Feel free to modify and distribute.