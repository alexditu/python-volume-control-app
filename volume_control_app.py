#!/usr/bin/env python3
"""
Linux Volume Control Flask App
A web-based volume controller using PulseAudio via pulsectl library
"""

from flask import Flask, render_template, jsonify, request
import pulsectl
import threading
import time

app = Flask(__name__)

class VolumeController:
    def __init__(self):
        self.step = 5  # Volume step percentage
        self.pulse = None
        self._lock = threading.Lock()
        self.connect()

    def connect(self):
        """Connect to PulseAudio server"""
        try:
            if self.pulse:
                self.pulse.close()
            self.pulse = pulsectl.Pulse('volume-control-web-app')
        except Exception as e:
            print(f"Failed to connect to PulseAudio: {e}")
            self.pulse = None

    def get_default_sink(self):
        """Get the default sink (main audio output)"""
        with self._lock:
            try:
                if not self.pulse:
                    self.connect()

                server_info = self.pulse.server_info()
                default_sink_name = server_info.default_sink_name

                sinks = self.pulse.sink_list()
                for sink in sinks:
                    if sink.name == default_sink_name:
                        return sink

                # Fallback to first sink if default not found
                return sinks[0] if sinks else None
            except Exception as e:
                print(f"Error getting default sink: {e}")
                return None

    def get_current_volume(self):
        """Get current volume level and mute status"""
        try:
            sink = self.get_default_sink()
            if not sink:
                return {
                    'volume': 0,
                    'is_muted': False,
                    'status': 'error',
                    'error': 'No audio sink found'
                }

            # Convert volume to percentage (PulseAudio uses 0.0-1.0, we want 0-100)
            volume_percent = int(sink.volume.value_flat * 100)

            return {
                'volume': volume_percent,
                'is_muted': bool(sink.mute),
                'status': 'success',
                'sink_name': sink.description or sink.name
            }
        except Exception as e:
            return {
                'volume': 0,
                'is_muted': False,
                'status': 'error',
                'error': f'Failed to get volume: {str(e)}'
            }

    def set_volume(self, volume_percent):
        """Set volume to specific percentage"""
        try:
            sink = self.get_default_sink()
            if not sink:
                return False

            # Clamp volume between 0 and 100
            volume_percent = max(0, min(100, volume_percent))

            # Convert percentage to PulseAudio volume (0.0-1.0)
            volume_float = volume_percent / 100.0

            with self._lock:
                self.pulse.volume_set_all_chans(sink, volume_float)

            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False

    def volume_up(self):
        """Increase volume by step amount"""
        current = self.get_current_volume()
        if current['status'] == 'success':
            new_volume = min(100, current['volume'] + self.step)
            return self.set_volume(new_volume)
        return False

    def volume_down(self):
        """Decrease volume by step amount"""
        current = self.get_current_volume()
        if current['status'] == 'success':
            new_volume = max(0, current['volume'] - self.step)
            return self.set_volume(new_volume)
        return False

    def toggle_mute(self):
        """Toggle mute status"""
        try:
            sink = self.get_default_sink()
            if not sink:
                return False

            with self._lock:
                self.pulse.mute(sink, not sink.mute)

            return True
        except Exception as e:
            print(f"Error toggling mute: {e}")
            return False

    def __del__(self):
        """Clean up PulseAudio connection"""
        if self.pulse:
            self.pulse.close()

# Initialize volume controller
volume_ctrl = VolumeController()

@app.route('/')
def index():
    """Main page with volume controls"""
    return render_template('index.html')

@app.route('/api/volume', methods=['GET'])
def get_volume():
    """API endpoint to get current volume"""
    return jsonify(volume_ctrl.get_current_volume())

@app.route('/api/volume/up', methods=['POST'])
def volume_up():
    """API endpoint to increase volume"""
    success = volume_ctrl.volume_up()
    current = volume_ctrl.get_current_volume()
    return jsonify({
        'success': success,
        'volume': current['volume'],
        'is_muted': current['is_muted']
    })

@app.route('/api/volume/down', methods=['POST'])
def volume_down():
    """API endpoint to decrease volume"""
    success = volume_ctrl.volume_down()
    current = volume_ctrl.get_current_volume()
    return jsonify({
        'success': success,
        'volume': current['volume'],
        'is_muted': current['is_muted']
    })

@app.route('/api/volume/mute', methods=['POST'])
def toggle_mute():
    """API endpoint to toggle mute"""
    success = volume_ctrl.toggle_mute()
    current = volume_ctrl.get_current_volume()
    return jsonify({
        'success': success,
        'volume': current['volume'],
        'is_muted': current['is_muted']
    })

@app.route('/api/volume/set', methods=['POST'])
def set_volume():
    """API endpoint to set specific volume level"""
    data = request.get_json()
    if not data or 'volume' not in data:
        return jsonify({'success': False, 'error': 'Volume value required'}), 400

    try:
        volume = int(data['volume'])
        success = volume_ctrl.set_volume(volume)
        current = volume_ctrl.get_current_volume()
        return jsonify({
            'success': success,
            'volume': current['volume'],
            'is_muted': current['is_muted']
        })
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid volume value'}), 400

if __name__ == '__main__':
    print("Starting Linux Volume Control Server with pulsectl...")
    print("Access from your phone at: http://<your-ip>:5000")
    print("To find your IP: ip addr show | grep 'inet ' | grep -v 127.0.0.1")
    print("\nMake sure to install pulsectl: pip install pulsectl")
    app.run(host='0.0.0.0', port=5000, debug=True)