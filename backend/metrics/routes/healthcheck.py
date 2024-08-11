from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

blueprint = Blueprint("healthcheck", "/healthcheck")


@blueprint.route("/")
async def healthcheck(request: Request):
    return json({"healthy": True})
