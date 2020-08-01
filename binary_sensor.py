"""A platform to monitor StatusCake monitors."""
import logging
import voluptuous as vol

from datetime import datetime
from statuscake import StatusCake
from statuscake.exceptions import (
	StatusCakeAuthError,
	StatusCakeNotLinkedError,
	StatusCakeResponseError,
)

from homeassistant.components.binary_sensor import PLATFORM_SCHEMA, BinarySensorEntity
from homeassistant.const import (
	ATTR_ATTRIBUTION,
	ATTR_FRIENDLY_NAME,

	CONF_API_KEY,
	CONF_SCAN_INTERVAL,

	STATE_OFF,
	STATE_ON,
	STATE_PAUSED,
)
import homeassistant.helpers.config_validation as cv


from .const import (
	ATTRIBUTION,
	ATTR_TARGET,
	ATTR_TYPE,
	ATTR_UPTIME_TODAY,

	CONF_API_USER,

	DOMAIN,

	DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)



PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_API_KEY): cv.string,
	vol.Required(CONF_API_USER): cv.string,
	vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
	})


def setup_platform(hass, config, add_entities, discovery_info=None):
	"""Set up the StatusCake binary_sensors."""

	api_key				= config.get(CONF_API_KEY)
	api_user			= config.get(CONF_API_USER)
	scan_interval		= config.get(CONF_SCAN_INTERVAL)

	status_cake_client	= StatusCake(api_key=api_key, api_user=api_user)
	status_cake_data	= StatusCakeData(status_cake_client, scan_interval)

	monitors			= status_cake_data.update()

	if not monitors: # or monitors.get("stat") != "ok":
		_LOGGER.error("Error connecting to StatusCake")
		return

	devices = []
	for test_id, monitor in monitors.items():
		_LOGGER.info("Adding binary_sensor for StatusCake monitor-%s: %s", test_id, monitor.get("WebsiteName", "Unknown"))

		devices.append(
			StatusCakeBinarySensor(
				status_cake_data,
				test_id,
				monitor,
			)
		)

	add_entities(devices, True)

class StatusCakeData:
	def __init__(self, client, scan_interval=DEFAULT_SCAN_INTERVAL):
		self._client		= client
		self._scan_interval	= scan_interval
		self._last_fetch	= datetime.min
		self._monitors		= {}

	def update(self):
		# Only actually fetch updates if we've not fetched in a while (to keep within API limits)
		if(self._last_fetch >= (datetime.now() - self._scan_interval)):
			_LOGGER.debug("Returning cached StatusCake monitor data")
			return self._monitors


		_LOGGER.debug("Updating StatusCake monitors...")
		self._last_fetch = datetime.now()
		try:
			monitors = self._client.get_all_tests()

		except(	StatusCakeAuthError,
				StatusCakeNotLinkedError,
				):
			_LOGGER.error("Failed to update StatusCake monitors: Authentication Error")
			return self._monitors

		except(	StatusCakeResponseError,
				):
			_LOGGER.error("Failed to update StatusCake monitors: API Error")
			return self._monitors

		if not monitors:
			_LOGGER.error("Failed to update StatusCake monitors: no monitor data return")
			return self._monitors

		self._monitors = {}
		for monitor in monitors:
			if "TestID" not in monitor:
				_LOGGER.warning("TestID not found in monitor data")
			else:
				test_id = str(monitor["TestID"])
				self._monitors[ test_id ] = monitor

		return self._monitors

class StatusCakeBinarySensor(BinarySensorEntity):
	"""Representation of a StatusCake binary sensor."""

	def __init__(self, status_cake_data, test_id, monitor):
		"""Initialize StatusCake the binary sensor."""
		self._status_cake_data	= status_cake_data
		self._test_id			= test_id
		self._name				= monitor.get("WebsiteName", "Unknown")
		self._paused			= monitor.get("Paused", False)
		self._state				= STATE_ON if monitor.get("Status") == "Up" else STATE_OFF
		self._target			= monitor.get("WebsiteURL", "Unknown")
		self._type				= monitor.get("TestType", "unknown")
		self._uptime_today		= monitor.get("Uptime", 0)

	@property
	def unique_id(self):
		"""Return a unique ID for the binary sensor."""
		return f"statuscake_{self._type}_{self._test_id}"

	@property
	def name(self):
		"""Return the name of the binary sensor."""
		return f"StatusCake {self._type} {self._name}"

	@property
	def is_on(self):
		"""Return true if the binary sensor is on."""
		return self._state

	@property
	def state(self):
		"""Return the state of the binary sensor."""
		return STATE_PAUSED if self._paused else self._state

	@property
	def device_class(self):
		"""Return the class of this device, from component DEVICE_CLASSES."""
		return "connectivity"

	@property
	def device_state_attributes(self):
		"""Return the state attributes of the binary sensor."""
		return {	ATTR_ATTRIBUTION:	ATTRIBUTION,
					ATTR_FRIENDLY_NAME:	f"StatusCake {self._type} {self._name}",
					ATTR_TARGET:		self._target,
					ATTR_TYPE:			self._type,
					ATTR_UPTIME_TODAY:	self._uptime_today,
					}

	def update(self):
		"""Get the latest state of the binary sensor."""
		monitors = self._status_cake_data.update()
		monitor = monitors.get( self._test_id )
		if monitor is None:
			_LOGGER.warning("Failed to get new state for StatusCake monitor-%s: %s", self._test_id, self._name)
			return

		_LOGGER.debug("Updating StatusCake monitor-%s: %s", self._test_id, self._name)
		self._paused		= monitor.get("Paused", False)
		self._state			= STATE_ON if monitor.get("Status") == "Up" else STATE_OFF
		self._uptime_today	= monitor.get("Uptime", 0)

