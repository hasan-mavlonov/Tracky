import time
import logging
logger = logging.getLogger(__name__)

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        logger.debug(f"Authentication processing took {end_time - start_time:.2f} seconds")
        return response