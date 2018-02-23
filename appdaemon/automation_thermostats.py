import appdaemon.appapi as appapi
from enum import Enum
from datetime import time, date, datetime, timedelta


class AutomationThermostats(appapi.AppDaemon):
    class windowsensor(Enum):
        OPEN = '22'
        CLOSED = '23'

    class weekday(Enum):
        MONDAY = 0
        TUESDAY = 1
        WEDNESDAY = 2
        THURSDAY = 3
        FRIDAY = 4
        SATURDAY = 5
        SUNDAY = 6

    schedule = {
        weekday.MONDAY: {
            time(6): "Heat",
            time(8): "Heat Eco",
            time(16): "Heat",
            time(23,59): "Heat Eco"
        },
        weekday.TUESDAY: {
            time(6): "Heat",
            time(8): "Heat Eco",
            time(16): "Heat",
            time(23,59): "Heat Eco"
        },
        weekday.WEDNESDAY: {
            time(6): "Heat",
            time(8): "Heat Eco",
            time(16): "Heat",
            time(23,59): "Heat Eco"
        },
        weekday.THURSDAY: {
            time(6): "Heat",
            time(8): "Heat Eco",
            time(16): "Heat",
            time(23,59): "Heat Eco"
        },
        weekday.FRIDAY: {
            time(6): "Heat",
            time(8): "Heat Eco",
            time(16): "Heat",
            time(23,59): "Heat Eco"
        },
        weekday.SATURDAY: {
            time(8): "Heat",
            time(23, 59): "Heat Eco"
        },
        weekday.SUNDAY: {
            time(8): "Heat",
            time(23,59): "Heat Eco"
        }
    }

    bathroom_schedule = {
        weekday.MONDAY: {
            time(6,30): 25
        },
        weekday.TUESDAY: {
            time(6,30): 25
        },
        weekday.WEDNESDAY: {
            time(6,30): 25
        },
        weekday.THURSDAY: {
            time(6,30): 25
        },
        weekday.FRIDAY: {
            time(6,30): 25
        },
        weekday.SATURDAY: {
            time(8,15): 25
        },
        weekday.SUNDAY: {
            time(8,15): 25
        }
    }

    def initialize(self):
        self.listen_state(self.bathroom_window, "sensor.fenstersensor_badezimmer_access_control")
        self.listen_state(self.livingroom_window, "sensor.fenstersensor_wohnzimmer_access_control")

        today = date.today()
        for weekday in self.schedule:
            for scheduled_time, scheduled_mode in self.schedule[weekday].items():
                next_scheduled_datetime = datetime.combine(self.calc_next_date(weekday, today), scheduled_time)
                if next_scheduled_datetime < datetime.now():
                    next_scheduled_datetime = next_scheduled_datetime + timedelta(weeks=1)
                self.log("Scheduling mode {} for weekday {}, time {}, first run {}".format(scheduled_mode, weekday.name, scheduled_time, next_scheduled_datetime))
                handle = self.run_every(self.switch_to_mode, next_scheduled_datetime, 7 * 24 * 60 * 60, mode=scheduled_mode)

        for weekday in self.bathroom_schedule:
            for scheduled_time, scheduled_temperature in self.bathroom_schedule[weekday].items():
                next_scheduled_datetime = datetime.combine(self.calc_next_date(weekday, today), scheduled_time)
                if next_scheduled_datetime < datetime.now():
                    next_scheduled_datetime = next_scheduled_datetime + timedelta(weeks=1)
                self.log("Scheduling temperature {} for weekday {}, time {}, first run {}".format(scheduled_temperature, weekday.name, scheduled_time, next_scheduled_datetime))
                self.run_every(self.bathroom_high, next_scheduled_datetime, 7 * 24 * 60 * 60, temperature=scheduled_temperature)

        self.log("Initialized AutomationThermostats")

    def switch_to_mode(self, kwargs):
        self.log("Trying to switch to mode {}".format(kwargs['mode']))
        windowstate_wohnzimmer = self.entities.sensor.fenstersensor_wohnzimmer_access_control.state
        windowstate_badezimmer = self.entities.sensor.fenstersensor_badezimmer_access_control.state

        if windowstate_wohnzimmer == self.windowsensor.OPEN.value:
            self.log("Living room window OPEN, not switching mode")
            return

        entities = [
            "climate.thermostat_wohnzimmer_heat",
            "climate.thermostat_arbeitszimmer_heat",
            "climate.thermostat_schlafzimmer_heat",
            "climate.thermostat_kuche_heat",
        ]
        if windowstate_badezimmer == self.windowsensor.CLOSED.value:
            entities.append("climate.thermostat_badezimmer_heat")
        else:
            self.log("Bathroom window open")

        for entity in entities:
            self.log('Calling service climate/set_operation_mode {{ entity_id: "{}", operation_mode: "{}"}}'.format(entity, kwargs['mode']))
            self.call_service("climate/set_operation_mode",
                          entity_id=entity,
                          operation_mode=kwargs['mode'])

    def bathroom_high(self, kwargs):
        self.log('Calling service climate/set_temperature {{ entity_id: "{}", temperature: "{}"}}'.format("climate.thermostat_badezimmer_heat", kwargs['temperature']))
        self.call_service("climate/set_temperature",
                          entity_id="climate.thermostat_badezimmer_heat",
                          temperature=kwargs['temperature'])
        self.run_at(self.bathroom_low, (datetime.now() + timedelta(minutes=30)))

    def bathroom_low(self, kwargs):
        self.log('Calling service climate/set_temperature {{ entity_id: "{}", temperature: "{}"}}'.format("climate.thermostat_badezimmer_heat", "20"))
        self.call_service("climate/set_temperature",
                          entity_id="climate.thermostat_badezimmer_heat",
                          temperature="20")
        # self.log('Calling service climate/set_operation_mode {{ entity_id: "{}", operation_mode: "{}"}}'.format("climate.thermostat_badezimmer_heat", "Off"))
        # self.call_service("climate/set_operation_mode",
        #                   entity_id="climate.thermostat_badezimmer_heat",
        #                   operation_mode="Off")

    def bathroom_window(self, entity, attribute, old, new, kwargs):
        windowstate_wohnzimmer = self.entities.sensor.fenstersensor_wohnzimmer_access_control.state
        if new == self.windowsensor.OPEN.value:
            self.log('Calling service climate/set_operation_mode {{ entity_id: "{}", operation_mode: "{}"}}'.format("climate.thermostat_badezimmer_heat", "Off"))
            self.call_service("climate/set_operation_mode",
                              entity_id="climate.thermostat_badezimmer_heat",
                              operation_mode="Off")
        elif windowstate_wohnzimmer == self.windowsensor.CLOSED.value:
            scheduled_mode = self.get_current_scheduled_mode()
            self.log('Calling service climate/set_operation_mode {{ entity_id: "{}", operation_mode: "{}"}}'.format("climate.thermostat_badezimmer_heat", scheduled_mode))
            self.call_service("climate/set_operation_mode",
                              entity_id= "climate.thermostat_badezimmer_heat",
                              operation_mode= scheduled_mode)

    def livingroom_window(self, entity, attribute, old, new, kwargs):
        if new == self.windowsensor.OPEN.value:
            self.log('Calling service climate/set_operation_mode {{ entity_id: "{}", operation_mode: "{}"}}'.format("group_thermostats", "Off"))
            self.call_service("climate/set_operation_mode",
                              entity_id="group.thermostats",
                              operation_mode="Off")
        else:
            entities = [
                "climate.thermostat_wohnzimmer_heat",
                "climate.thermostat_arbeitszimmer_heat",
                "climate.thermostat_schlafzimmer_heat",
                "climate.thermostat_kuche_heat",
            ]
            windowstate_badezimmer = self.entities.sensor.fenstersensor_badezimmer_access_control.state
            if windowstate_badezimmer == self.windowsensor.CLOSED.value:
                entities.append("climate.thermostat_badezimmer_heat")

            for entity in entities:
                scheduled_mode = self.get_current_scheduled_mode()
                self.log('Calling service climate/set_operation_mode {{     entity_id: "{}", operation_mode: "{}"}}'.format(entity, scheduled_mode))
                self.call_service("climate/set_operation_mode",
                                  entity_id=entity,
                                  operation_mode=scheduled_mode)

    def get_current_scheduled_mode(self):
        now = datetime.now()
        todays_schedule = self.schedule[self.weekday(now.weekday())]
        todays_times = sorted(todays_schedule.keys())

        # If the current time is earlier than today's earliest scheduled time, look up yesterday's last planned time
        # and return it
        if now < datetime.combine(now.date(), todays_times[0]):
            yesterday = now.date() - timedelta(days=1)
            yesterdays_schedule = self.schedule[self.weekday(yesterday.weekday())]
            yesterdays_times = sorted(yesterdays_schedule.keys())
            return yesterdays_schedule[yesterdays_times[-1]]

        # If the queried time and the scheduled time are an exact match, return that time. Otherwise a scheduled time
        # will be effective only one minute later
        if now.time() in todays_times:
            return todays_schedule[now.time()]

        # Add 'now' to the list of scheduled times and sort the resulting list
        todays_times.append(now.time())
        todays_times = sorted(todays_times)

        # Now get the time from the index _before_ the just inserted time representing now
        todays_most_recent_time = todays_times[todays_times.index(now.time()) - 1]

        return todays_schedule[todays_most_recent_time]

    def calc_next_date(self, scheduled_weekday: weekday, today: date):
        days_ahead = scheduled_weekday.value - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
        return today + timedelta(days=days_ahead)