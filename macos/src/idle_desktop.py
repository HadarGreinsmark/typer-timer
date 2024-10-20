import ctypes as _ctypes
import ctypes.util as _ctypes_util


class Reader:
    def __init__(self):
        # Load IOKit and CoreFoundation
        self.iokit = _ctypes.cdll.LoadLibrary(_ctypes_util.find_library("IOKit"))
        self.cf = _ctypes.cdll.LoadLibrary(_ctypes_util.find_library("CoreFoundation"))

        # Constants
        self.kIOMasterPortDefault = 0
        self.kCFAllocatorDefault = None

        # Function definitions for IOKit and CoreFoundation functions
        self.iokit.IOServiceMatching.restype = _ctypes.c_void_p
        self.iokit.IOServiceMatching.argtypes = [_ctypes.c_char_p]

        self.iokit.IOServiceGetMatchingService.restype = _ctypes.c_void_p
        self.iokit.IOServiceGetMatchingService.argtypes = [
            _ctypes.c_void_p,
            _ctypes.c_void_p,
        ]

        self.iokit.IORegistryEntryCreateCFProperty.restype = _ctypes.c_void_p
        self.iokit.IORegistryEntryCreateCFProperty.argtypes = [
            _ctypes.c_void_p,
            _ctypes.c_void_p,
            _ctypes.c_void_p,
            _ctypes.c_uint32,
        ]

        self.cf.CFStringCreateWithCString.restype = _ctypes.c_void_p
        self.cf.CFStringCreateWithCString.argtypes = [
            _ctypes.c_void_p,
            _ctypes.c_char_p,
            _ctypes.c_uint32,
        ]

        self.cf.CFNumberGetValue.restype = _ctypes.c_int
        self.cf.CFNumberGetValue.argtypes = [
            _ctypes.c_void_p,
            _ctypes.c_uint32,
            _ctypes.c_void_p,
        ]

        self.cf.CFRelease.restype = None
        self.cf.CFRelease.argtypes = [_ctypes.c_void_p]

        # CoreFoundation number types
        self.kCFNumberSInt64Type = 4

        # Create a matching dictionary for IOHIDSystem
        self.matching_dict = self.iokit.IOServiceMatching(b"IOHIDSystem")

        # Get the IOHIDSystem service
        self.iohid_system = self.iokit.IOServiceGetMatchingService(
            self.kIOMasterPortDefault, self.matching_dict
        )

        if self.iohid_system:
            # Create CFString for the "HIDIdleTime" property
            self.hid_idle_time_key = self.cf.CFStringCreateWithCString(
                self.kCFAllocatorDefault, b"HIDIdleTime", 0x08000100
            )
        else:
            raise RuntimeError("IOHIDSystem service not found.")

    def get_idle_time(self):
        """Retrieve the current system idle time in seconds."""
        # Get the HIDIdleTime property from IOHIDSystem
        hid_idle_time_value = self.iokit.IORegistryEntryCreateCFProperty(
            self.iohid_system, self.hid_idle_time_key, self.kCFAllocatorDefault, 0
        )

        if hid_idle_time_value:
            # Prepare to store the result
            idle_time_ns = _ctypes.c_uint64()

            # Extract the idle time value (which is in nanoseconds)
            self.cf.CFNumberGetValue(
                hid_idle_time_value,
                self.kCFNumberSInt64Type,
                _ctypes.byref(idle_time_ns),
            )

            # Release the CFNumber object
            self.cf.CFRelease(hid_idle_time_value)

            # Convert nanoseconds to seconds and return
            idle_time_sec = idle_time_ns.value / 1e9
            return idle_time_sec
        else:
            raise RuntimeError("Failed to retrieve HIDIdleTime property.")

    def close(self):
        """Clean up resources by releasing CoreFoundation objects."""
        if self.hid_idle_time_key:
            self.cf.CFRelease(self.hid_idle_time_key)
