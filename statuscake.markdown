---
title: StatusCake
description: Instructions on how to set up StatusCake within Home Assistant.
ha_category:
  - System Monitor
ha_release: 0.113.2
ha_iot_class: Cloud Polling
ha_codeowners:
  - '@stewiem2000'
ha_domain: statuscake
---

The `statuscake` binary sensor platform allows you get the status for all of your monitors from your account on [StatusCake]( https://statuscake.com).

## Configuration

To enable the sensor, add the following lines to your `configuration.yaml`:

```yaml
# Example configuration.yaml entry
binary_sensor:
  - platform: statuscake
    api_user: YOUR_USERNAME
    api_key: YOUR_API_KEY
```

{% configuration %}
api_user:
  description: Your StatusCake username.
  required: true
  type: string
api_key:
  description: Your StatusCake API key.
  required: true
  type: string
{% endconfiguration %}

All the data will be fetched from [StatusCake](https://statuscake.com).

To get your API key, go to [My Account](https://app.statuscake.com/User.php) on the StatusCake website, at the bottom, under "Manage API Keys", you will find the "Default Key" or you can "Generate New Key".