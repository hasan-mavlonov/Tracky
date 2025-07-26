import logging
import time

from django.http import HttpResponsePermanentRedirect

logger = logging.getLogger(__name__)


class RedirectFromRenderMiddleware:
    """
    Redirect requests from Render subdomain to custom domain.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if "tracky-d764.onrender.com" in host:
            new_url = request.build_absolute_uri().replace("tracky-d764.onrender.com", "tracky.one")
            return HttpResponsePermanentRedirect(new_url)
        return self.get_response(request)


class TimingMiddleware:
    """
    Logs how long authentication processing takes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        logger.debug(f"Authentication processing took {end_time - start_time:.2f} seconds")
        return response
