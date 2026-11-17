# Exposes the QIDI Box AHT20 humidity as a Klipper temperature sensor.
#
# Fluidd charts only temperatures. This sensor type reports %RH in the
# "temperature" field, so a [temperature_sensor] that uses it appears as a
# line on the Fluidd Thermals chart. The chart shows the unit as °C.

REPORT_TIME = 1.


class BoxHumidity:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        # Klipper object that holds the humidity reading.
        self.source_name = config.get('source', 'aht20_f heater_box1')
        self.source = self.mcu = None
        self.callback = None
        self.printer.register_event_handler('klippy:ready', self._handle_ready)

    # Sensor interface that temperature_sensor calls.
    def setup_minmax(self, min_temp, max_temp):
        pass

    def setup_callback(self, callback):
        self.callback = callback

    def get_report_time_delta(self):
        return REPORT_TIME

    def _handle_ready(self):
        # The source object exists only after all config sections load.
        self.source = self.printer.lookup_object(self.source_name)
        self.mcu = self.printer.lookup_object('mcu')
        self.reactor.register_timer(self._sample, self.reactor.NOW)

    def _sample(self, eventtime):
        humidity = self.source.get_status(eventtime).get('humidity')
        if humidity is not None and self.callback is not None:
            self.callback(self.mcu.estimated_print_time(eventtime), humidity)
        return eventtime + REPORT_TIME


def load_config(config):
    # A [box_humidity] section loads this module and registers the sensor type.
    pheaters = config.get_printer().load_object(config, 'heaters')
    pheaters.add_sensor_factory('box_humidity', BoxHumidity)
