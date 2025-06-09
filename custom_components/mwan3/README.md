# MWAN3 Home Assistant Integration

This integration allows you to monitor your OpenWrt router's MWAN3 interfaces in Home Assistant. It provides real-time status updates for each MWAN3 interface, including connection status, uptime, and other relevant metrics.

## Features

- Monitor multiple MWAN3 interfaces
- Real-time status updates
- Configurable scan interval
- Custom friendly names for each router
- Detailed interface statistics

## Installation

### HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository to HACS
3. Search for "MWAN3" in the HACS store
4. Click "Download"
5. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `mwan3` folder to your `custom_components` directory
3. Restart Home Assistant

## Configuration

1. In Home Assistant, go to Settings > Devices & Services
2. Click "Add Integration"
3. Search for "MWAN3"
4. Enter your router's details:
   - Host: Your router's IP address and port (e.g., 192.168.1.1:8080)
   - Username: Your router's admin username
   - Password: Your router's admin password
   - Friendly Name: A custom name for this router
   - Scan Interval: How often to check for updates (in seconds)

## Requirements

- OpenWrt router with MWAN3 installed
- Router must be accessible via HTTP/HTTPS
- Admin credentials for the router

## Sensor Attributes

Each interface sensor provides the following attributes:

- `status`: Current status of the interface
- `enabled`: Whether the interface is enabled
- `score`: Interface score
- `up`: Whether the interface is up
- `age`: Interface age
- `turn`: Interface turn
- `online`: Online status
- `uptime`: Interface uptime
- `lost`: Lost packets
- `offline`: Offline status
- `running`: Whether the interface is running
- `track_ip`: List of tracked IP addresses

## Troubleshooting

If you encounter any issues:

1. Check that your router is accessible from Home Assistant
2. Verify your credentials are correct
3. Ensure MWAN3 is properly installed and configured on your router
4. Check the Home Assistant logs for detailed error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 