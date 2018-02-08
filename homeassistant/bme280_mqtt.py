import homeassistant.loader as loader
import logging

DOMAIN = 'bme280_mqtt'
_LOGGER = logging.getLogger(DOMAIN)

DEPENDENCIES = ['mqtt']

DEFAULT_TOPICS = [ 'sensors/+/+', 'sensors/+/+/unit' ]

HASS = None

def message_received(topic, payload, qos):
    """Handle new MQTT messages."""
    topic_parts = topic.split("/")
    if len(topic_parts) >= 3:
        entity_id = "bme280_mqtt.{}_{}".format(topic_parts[1], topic_parts[2])
        if len(topic_parts == 3):
            HASS.states.set(entity_id, payload)
        elif len(topic_parts == 4) and topic_parts[3] == 'unit':
            HASS.states.set(entity_id, None, {'unit': payload})

def setup(hass, config):
    """Set up the BME280 MQTT component."""
    _LOGGER.info("Loading component BME280 MQTT")
    mqtt = loader.get_component('mqtt')
    # We no longer support custom topics
    topics = DEFAULT_TOPICS
    HASS = hass

    # Subscribe our listener to our topics.
    for topic in topics:
        _LOGGER.info("Subscribing to topic {}".format(topic))
        mqtt.subscribe(hass, topic, message_received)

    # Return boolean to indicate that initialization was successful.
    return True
