import appdaemon.appapi as appapi
from datetime import datetime

class SchedulerTest(appapi.AppDaemon):
    def initialize(self):
        # self.run_every(self.scheduler_function, datetime(2018, 2, 3, 13, 28), 60, foo="bar")
        schedule = self.get_scheduler_entries()
        for name, entries in schedule.items():
            self.log("Showing entries of {}".format(name))
            for entry, entrydata in entries.items():
                self.log("Showing entrydata of {}".format(entry))
                for key, datum in entrydata.items():
                    if key == 'offset' or key == 'timestamp' or key == 'interval' or key == 'repeat':
                        self.log("{} => {}".format(key, datetime.fromtimestamp(datum)))
                    else:
                        self.log("{} => {}".format(key, datum))
        self.log("Scheduler test initialized")

    def scheduler_function(self, kwargs):
        self.log("Running scheduled task with args {}".format(kwargs))