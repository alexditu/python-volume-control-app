#!/usr/bin/env python3
"""
Linux Volume Control Flask App
A web-based volume controller using PulseAudio
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import re
import json

app = Flask(__name__)

class VolumeController:
    def __init__(self):
        self.step = 5  # Volume step percentage
    
    def get_current_volume(self):
        """Get current volume level and mute status"""
        try:
            # Get default sink info
            result = subprocess.run(['pactl', 'get-sink-volume', '@DEFAULT_SINK@'], 
                                  capture_output=True, text=True, check=True)
            volume_output = result.stdout
            
            # Parse volume percentage (looks for patterns like "50%" in the output)
            volume_match = re.search(r'(\d+)%', volume_output)
            volume = int(volume_match.group(1)) if volume_match else 0
            
            # Get mute status
            mute_result = subprocess.run(['pactl', 'get-sink-mute', '@DEFAULT_SINK@'], 
                                       capture_output=True, text=True, check=True)
            is_muted = 'yes' in mute_result.stdout.lower()
            
            return {
                'volume': volume,
                'is_muted': is_muted,
                'status': 'success'
            }
        except subprocess.CalledProcessError as e:
            return {
                'volume': 0,
                'is_muted': False,
                'status': 'error',
                'error': f'Failed to get volume: {str(e)}'
            }
        except Exception as e:
            return {
                'volume': 0,
                'is_muted': False,
                'status': 'error',
                'error': f'Unexpected error: {str(e)}'
            }
    
    def set_volume(self, volume):
        """Set volume to specific percentage"""
        try:
            # Clamp volume between 0 and 100
            volume = max(0, min(100, volume))
            subprocess.run(['pactl', 'set-sink-volume', '@DEFAULT_SINK@', f'{volume}%'], 
                         check=True)
            return True
        except subprocess.CalledProcessError:
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
            subprocess.run(['pactl', 'set-sink-mute', '@DEFAULT_SINK@', 'toggle'], 
                         check=True)
            return True
        except subprocess.CalledProcessError:
            return False

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
    print("Starting Linux Volume Control Server...")
    print("Access from your phone at: http://<your-ip>:5000")
    print("To find your IP: ip addr show | grep 'inet ' | grep -v 127.0.0.1")
    app.run(host='0.0.0.0', port=5000, debug=True)