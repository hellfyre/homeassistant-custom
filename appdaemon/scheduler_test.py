import appdaemon.appapi as appapi
import appdaemon.conf as conf
import datetime
import time

class SchedulerTest(appapi.AppDaemon):
    def initialize(self):
        self.run_daily(self.dump_schedule, datetime.time(6,5))
        self.run_daily(self.dump_schedule, datetime.time(6,35))
        self.run_daily(self.dump_schedule, datetime.time(7,35))
        self.run_daily(self.dump_schedule, datetime.time(8,5))
        self.run_daily(self.dump_schedule, datetime.time(16,5))
        self.run_daily(self.dump_schedule, datetime.time(22,5))
        self.run_daily(self.dump_schedule, datetime.time(0,5))
        self.log("Scheduler test initialized")

    def dump_schedule(self, kwargs):
        self.log("--------------------------------------------------")
        self.log("Scheduler Table")
        self.log("--------------------------------------------------")
        for name in conf.schedule.keys():
            self.log("{}:".format(name))
            for entry in sorted(
                    conf.schedule[name].keys(),
                    key=lambda uuid_: conf.schedule[name][uuid_]["timestamp"]
            ):
                self.log(
                    "  Timestamp: {} - data: {}".format(
                        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
                            conf.schedule[name][entry]["timestamp"]
                        )),
                        conf.schedule[name][entry]
                    )
                )
        self.log("--------------------------------------------------")