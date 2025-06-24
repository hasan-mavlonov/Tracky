# ====== products/rfid_reader.py ======
import ctypes
import time
import threading
import logging
from ctypes import c_int, byref, create_string_buffer
from django.core.cache import cache
from collections import defaultdict

logger = logging.getLogger(__name__)

class RFIDReader:
    def __init__(self):
        try:
            self.dll = ctypes.windll.LoadLibrary('C:\\Users\\user\\PycharmProjects\\Tracky\\products\\SWHidApi.dll')
            self.initialize_reader()
            self.tag_timestamps = defaultdict(float)
            self.last_cleanup = time.time()
            self.tag_registry = {}
        except Exception as e:
            logger.error(f"RFID Init Error: {e}")
            raise

    def initialize_reader(self):
        if self.dll.SWHid_GetUsbCount() == 0:
            raise RuntimeError("No USB Device Found")
        if self.dll.SWHid_OpenDevice(0) != 1:
            raise RuntimeError("Failed to Open Device")

        self.dll.SWHid_ClearTagBuf()
        self.dll.SWHid_SetDeviceOneParam(0xFF, 2, 1)
        self.dll.SWHid_StartRead(0xFF)

    def parse_tag_data(self, arrBuffer, iLength):
        raw = bytearray(arrBuffer)
        bPackLength = raw[iLength]
        ant = raw[1 + iLength + 1]
        rssi = raw[1 + iLength + bPackLength - 1]
        tag_id_bytes = raw[1 + iLength + 2: 1 + iLength + bPackLength - 1]
        tag_id = ''.join('{:02X}'.format(b) for b in tag_id_bytes)
        return tag_id, bPackLength, ant, rssi

    def cleanup_old_tags(self):
        now = time.time()
        stale = [k for k, t in self.tag_timestamps.items() if t < now - 5]
        for k in stale:
            del self.tag_timestamps[k]
            self.tag_registry.pop(k, None)
        self.last_cleanup = now

    def run(self):
        while True:
            try:
                arrBuffer = create_string_buffer(9182)
                iTagLength = c_int(0)
                iTagNumber = c_int(0)

                ret = self.dll.SWHid_GetTagBuf(arrBuffer, byref(iTagLength), byref(iTagNumber))
                now = time.time()

                if ret and iTagNumber.value > 0:
                    iLength = 0
                    current_tags = set()

                    for _ in range(iTagNumber.value):
                        tag_id, bPackLength, ant, rssi = self.parse_tag_data(arrBuffer, iLength)
                        current_tags.add(tag_id)
                        self.tag_timestamps[tag_id] = now

                        if tag_id not in self.tag_registry:
                            self.tag_registry[tag_id] = {"count": 1, "rssi": rssi, "antenna": ant}
                        else:
                            self.tag_registry[tag_id]["count"] += 1
                            self.tag_registry[tag_id]["rssi"] = rssi

                        iLength += bPackLength

                    if now - self.last_cleanup > 1:
                        self.cleanup_old_tags()

                    active_tags = [tag for tag in current_tags if self.tag_timestamps[tag] >= now - 5]
                    cache.set('current_rfids', active_tags, timeout=1)

            except Exception as e:
                logger.error(f"Reader loop error: {e}")
                time.sleep(1)
            time.sleep(0.05)

def start_rfid_reader():
    try:
        reader = RFIDReader()
        t = threading.Thread(target=reader.run, daemon=True)
        t.start()
        return True
    except Exception as e:
        logger.error(f"Failed to start RFID: {e}")
        return False
