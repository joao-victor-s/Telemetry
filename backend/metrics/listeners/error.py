from sanic import Blueprint
from sanic.exceptions import SanicException, ServerError
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse, json

blueprint = Blueprint("exception")


@blueprint.exception(Exception)
def error_handler(request: Request, exception: Exception) -> HTTPResponse:
    status_code = 500
    message = "Internal server error"
    if isinstance(exception, SanicException) and not isinstance(exception, ServerError):
        status_code = exception.status_code
        message = str(exception)
    else:
        logger.error("Unhandled exception: %s", exception)

    return json({"error": message}, status=status_code)
