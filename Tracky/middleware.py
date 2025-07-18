import time
import logging
logger = logging.getLogger(__name__)

class TimingAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        from django.contrib.auth.middleware import AuthenticationMiddleware
        AuthenticationMiddleware().process_request(request)
        end_time = time.time()
        logger.debug(f"AuthenticationMiddleware took {end_time - start_time:.2f} seconds")
        response = self.get_response(request)
        return response