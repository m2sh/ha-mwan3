# MWAN3 Home Assistant Integration

This is a custom Home Assistant integration for monitoring MWAN3 (Multi-WAN) status on OpenWrt routers. It provides real-time status information about your MWAN3 interfaces, including their connection status, tracking information, and detailed statistics.

## Features

- Monitor multiple WAN interfaces configured in MWAN3
- Real-time status updates (every 30 seconds)
- Tracks interface status (online/offline)
- Additional attributes:
  - Enabled status
  - Score
  - Connection state (up/down)
  - Age
  - Turn count
  - Online count
  - Uptime
  - Lost packets
  - Offline count
  - Running state
  - Track IP information (status, latency, packet loss)
- Secure authentication with your router
- Easy configuration through Home Assistant UI

## Prerequisites

- OpenWrt router with MWAN3 installed and configured
- MWAN3 web interface enabled on your router
- Home Assistant instance (version 2023.1.0 or newer recommended)

## Installation

1. Download this repository
2. Copy the `custom_components/mwan3` directory to your Home Assistant's `custom_components` directory
3. Restart Home Assistant
4. Go to Home Assistant UI → Settings → Devices & Services
5. Click the "+ Add Integration" button
6. Search for "MWAN3"
7. Enter your router's details:
   - Router IP Address (e.g., 192.168.1.1)
   - Username (your router's admin username)
   - Password (your router's admin password)

## Configuration

The integration requires the following information to connect to your router:

- **Router IP Address**: The IP address of your OpenWrt router
- **Username**: Your router's admin username
- **Password**: Your router's admin password

## Usage

After installation, the integration will create sensors for each MWAN3 interface configured on your router. Each sensor will show:

- Current status (online/offline)
- Additional attributes:
  - Enabled: Whether the interface is enabled in MWAN3
  - Score: Current interface score
  - Up: Whether the interface is up
  - Age: Interface age
  - Turn: Number of times the interface has turned
  - Online: Number of times the interface has been online
  - Uptime: Current uptime in seconds
  - Lost: Number of lost packets
  - Offline: Number of times the interface has been offline
  - Running: Whether the interface is running
  - Track IP: List of tracking IPs with their status, latency, and packet loss

You can use these sensors in:
- Home Assistant dashboards
- Automations
- Scripts
- Templates

### Example Dashboard Card

```yaml
type: entities
entities:
  - entity: sensor.router_alias_adsl
  - entity: sensor.router_alias_lte
title: MWAN3 Status
```

### Example Automation

```yaml
automation:
  - alias: "Notify on MWAN3 Interface Down"
    trigger:
      platform: state
      entity_id: sensor.router_alias_adsl
      to: "offline"
    action:
      - service: notify.mobile_app
        data:
          message: "MWAN3 Adsl interface is down!"
```

## Troubleshooting

If you encounter any issues:

1. Check that MWAN3 is properly installed and configured on your router
2. Verify that the web interface is accessible at `http://<router-ip>/cgi-bin/luci/admin/status/mwan/interface_status`
3. Ensure your router's credentials are correct
4. Check the Home Assistant logs for any error messages

Common issues:
- "Could not connect to router": Verify the router's IP address and that it's accessible from your Home Assistant instance
- "Invalid authentication": Check your username and password
- "Unexpected error": Check the Home Assistant logs for detailed error messages

## Development

This integration is built using:
- Python 3.9+
- Home Assistant Core
- aiohttp for async HTTP requests

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you need help or have questions:
1. Check the [Home Assistant forums](https://community.home-assistant.io/)
2. Open an issue on GitHub
3. Check the [OpenWrt MWAN3 documentation](https://openwrt.org/docs/guide-user/network/wan/multiwan/mwan3) 