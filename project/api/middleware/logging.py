"""
Middleware to log `*/api/*` requests and responses.
CREDIT: https://zeroes.dev/p/django-middleware-to-log-requests/
"""

import json
import logging
import socket
import time

from rest_framework.authtoken.models import Token

request_logger = logging.getLogger("api")


class RequestLogMiddleware:
    """
    Request Logging Middleware.

    Note: user is always "anonymous" at this level, because this middleware
    runs before DRF's TokenAuthentication class, which doesn't run until
    a view is processed. TokenAuthentication processes the Token in the Authorization
    header. We could either accept this, and log the user as "anonymous" for all
    requests here in the middleware, or we could parse the Authorization header
    here in the middleware, pull the token if present, and log the user. That will cause
    duplicate extraction of the token, once here and once in the TokenAuthentication class.
    Alternatively, we could simply log the token in the header without querying the database.

    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        log_data = {
            "remote_address": request.META["REMOTE_ADDR"],
            "server_hostname": socket.gethostname(),
            "request_method": request.method,
            "request_path": request.get_full_path(),
        }

        # log Token from Authorization header
        if "HTTP_AUTHORIZATION" in request.META:
            auth_header_val = request.META["HTTP_AUTHORIZATION"]
            token = auth_header_val.replace("Token ", "")
            try:
                user = Token.objects.get(key=token).user
                log_data["user"] = user.username
            except Token.DoesNotExist:
                log_data["user"] = "anonymous"
        else:
            log_data["user"] = "anonymous"

        # add the JSON payload of request to log_data if present
        if request.POST:
            log_data["request_body"] = request.POST.dict()

        # handle patch
        elif request.method == "PATCH":
            log_data["request_body"] = json.loads(request.body.decode("utf-8"))
        # if query params
        elif request.GET:
            log_data["request_body"] = request.GET.dict()

        # request passes on to controller
        response = self.get_response(request)

        # get the view name from request.resolver_match
        view_name = ""
        if request.resolver_match:
            view_name = request.resolver_match.view_name
        log_data["view_name"] = view_name

        # handle 204 no content
        if response.status_code == 204:
            log_data["response_body"] = "No Content"

        # add runtime to our log_data
        elif (
            response
            and "content-type" in response
            and response["content-type"] == "application/json"
        ):
            response_body = json.loads(response.content.decode("utf-8"))
            log_data["response_body"] = response_body
        log_data["run_time"] = time.time() - start_time
        request_logger.info(msg=log_data)
        return response

    # Log unhandled exceptions as well
    def process_exception(self, request, exception):
        try:
            raise exception
        except Exception as e:
            request_logger.exception("Unhandled Exception: " + str(e))
        return exception
