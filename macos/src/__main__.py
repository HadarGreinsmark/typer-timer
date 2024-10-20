import datetime
import time

import idle_desktop

from Foundation import *
from AppKit import *
from PyObjCTools import AppHelper

start_time = NSDate.date()


class MyApplicationAppDelegate(NSObject):
    state = "idle"

    active_counter_secs = 0
    idle_time_reader = idle_desktop.Reader()
    active_history = []

    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")

        self.statusItem = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        print(self.statusItem)
        self.statusItem.setTitle_("...")
        self.statusItem.setHighlightMode_(TRUE)
        self.statusItem.setEnabled_(TRUE)

        statusBarButton = self.statusItem.button()
        print(statusBarButton)
        rectInWindow = statusBarButton.convertRect_toView_(
            statusBarButton.bounds(), None
        )
        screenRect = statusBarButton.window().convertRectToScreen_(rectInWindow)
        stringRect = NSStringFromRect(screenRect)
        NSLog(stringRect)

        # Get the timer going
        self.timer = (
            NSTimer.alloc().initWithFireDate_interval_target_selector_userInfo_repeats_(
                start_time, 5.0, self, "tick:", None, True
            )
        )
        NSRunLoop.currentRunLoop().addTimer_forMode_(self.timer, NSDefaultRunLoopMode)
        self.timer.fire()

    def sync_(self, notification):
        print("sync")

    def tick_(self, notification):
        idle_time_sec = self.idle_time_reader.get_idle_time()
        tick_time = datetime.datetime.now()
        is_active = idle_time_sec < 5.0
        if is_active:
            self.active_history.append(tick_time)
        while self.active_history and tick_time - self.active_history[
            0
        ] > datetime.timedelta(minutes=5):
            self.active_history.pop(0)

        if len(self.active_history) < 4:
            self.active_counter_secs = 0
        else:
            self.active_counter_secs += 5
        self.statusItem.setTitle_(f"{self.active_counter_secs/60:.0f}m ⏰")


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    delegate = MyApplicationAppDelegate.alloc().init()
    app.setDelegate_(delegate)
    # image = NSImage.alloc().initWithContentsOfFile_("/Users/bluenred/Work/netdrive-2/UI/res/NetDrive.png")
    AppHelper.runEventLoop()
