# statuscake
Build ZHA network topology map.

The [`statuscake`](https://github.com/stewiem2000/statuscake) binary sensor platform for [Home Assistant](https://www.home-assistant.io) allows you get the status for all of your monitors from your account on [StatusCake](https://statuscake.com).

# Installation Instructions

1. Install the statuscake custom component
- https://github.com/stewiem2000/statuscake

# Configuration

To enable the sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
binary_sensor:
  - platform: statuscake
    api_user: YOUR_USERNAME
    api_key: YOUR_API_KEY
```

## api_user, required, string:
Your StatusCake username.

## api_key, required, string:
Your StatusCake API key.

To get your API key, go to [My Account](https://app.statuscake.com/User.php) on the StatusCake website, at the bottom, under "Manage API Keys", you will find the "Default Key" or you can "Generate New Key".