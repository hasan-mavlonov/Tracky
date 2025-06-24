import ctypes
import time
import threading
import logging
from ctypes import c_int, byref, create_string_buffer
from collections import defaultdict

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import ProductInstance, Product
from django.db.models import F

logger = logging.getLogger(__name__)

class RFIDReader:
    def __init__(self):
        try:
            self.dll = ctypes.windll.LoadLibrary(
                'C:\\Users\\user\\PycharmProjects\\Tracky\\products\\SWHidApi.dll'
            )
            self.initialize_reader()
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

    def run(self):
        while True:
            try:
                buffer = create_string_buffer(9182)
                iTagLength = c_int(0)
                iTagNumber = c_int(0)

                ret = self.dll.SWHid_GetTagBuf(buffer, byref(iTagLength), byref(iTagNumber))
                now = time.time()

                if ret and iTagNumber.value > 0:
                    iLength = 0
                    for _ in range(iTagNumber.value):
                        tag_id, bPackLength, ant, rssi = self.parse_tag_data(buffer, iLength)
                        iLength += bPackLength
                        if tag_id:
                            self.tag_registry[tag_id] = now  # update timestamp

                    # Clean up old tags older than 1s
                    self.tag_registry = {
                        tag: ts for tag, ts in self.tag_registry.items()
                        if now - ts <= 1.0
                    }

                    cache.set('current_rfids_dict', self.tag_registry, timeout=2)

            except Exception as e:
                logger.error(f"Reader loop error: {e}")
                time.sleep(1)

            time.sleep(0.02)


def start_rfid_reader():
    try:
        reader = RFIDReader()
        t = threading.Thread(target=reader.run, daemon=True)
        t.start()
        return True
    except Exception as e:
        logger.error(f"Failed to start RFID: {e}")
        return False


def current_products(request):
    """
    Returns DB-matched products and the raw RFID tag list.
    """
    try:
        raw_rfids = cache.get('current_rfids', []) or []
        logger.debug(f"Current RFIDs from reader: {raw_rfids}")

        # Filter out empty strings
        raw_rfids = [r for r in raw_rfids if r]

        qs = (
            ProductInstance.objects
            .select_related("product")
            .filter(RFID__in=raw_rfids)
            .exclude(status__in=['SOLD', 'LOST', 'DAMAGED'])
        )

        products = []
        for inst in qs:
            r = inst.RFID.strip().upper()
            products.append({
                "rfid": r,
                "name": inst.product.name,
                "price": float(inst.product.selling_price),
                "barcode": inst.product.barcode,
                "status": inst.status,
            })

        return JsonResponse({
            "products": products,
            "raw_rfids": raw_rfids
        })
    except Exception as e:
        logger.error(f"Error in current_products: {e}")
        return JsonResponse({"products": [], "raw_rfids": []})

def current_sold_products(request):
    """
    Returns currently scanned products that are marked as SOLD in the DB.
    Used in refund flow to identify refundable products within RFID range.
    """
    try:
        tag_dict = cache.get('current_rfids_dict', {}) or {}
        raw_rfids = list(tag_dict.keys())

        logger.debug(f"Current SOLD RFIDs in range: {raw_rfids}")

        queryset = (
            ProductInstance.objects
            .select_related("product")
            .filter(RFID__in=raw_rfids, status="SOLD")
        )

        products = []
        for inst in queryset:
            products.append({
                "rfid": inst.RFID.strip().upper(),
                "name": inst.product.name,
                "price": float(inst.product.selling_price),
                "barcode": inst.product.barcode,
                "status": inst.status,
            })

        return JsonResponse({
            "products": products,
            "raw_rfids": raw_rfids
        })
    except Exception as e:
        logger.error(f"Error in current_sold_products: {e}")
        return JsonResponse({"products": [], "raw_rfids": []})
@csrf_exempt
def lookup_rfid_view(request):
    if request.method == "POST":
        try:
            rfid = request.POST.get("rfid", "").strip().upper()
            if not rfid:
                return JsonResponse({"status": "error", "message": "No RFID provided"})

            inst = ProductInstance.objects.select_related("product").filter(RFID=rfid).first()
            if inst:
                prod = inst.product
                return JsonResponse({
                    "status": "success",
                    "product": {
                        "name": prod.name,
                        "price": float(prod.selling_price),
                        "barcode": prod.barcode,
                        "status": inst.status,
                    }
                })
            return JsonResponse({"status": "not_found", "message": "RFID not found"})
        except Exception as e:
            logger.error(f"Error in lookup_rfid_view: {e}")
            return JsonResponse({"status": "error", "message": "Server error"})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
