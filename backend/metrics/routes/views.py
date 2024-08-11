from metrics.util.validation import validate_route_parameter
from metrics.views import apply_view, view_namespaces, views_list
from sanic import Blueprint
from sanic.request import Request
from sanic.response import json

blueprint = Blueprint("views", "/view")

# TODO: view parameter validation
@blueprint.route("/", methods=["GET"])
async def list_views(request: Request):
    data = [
        {
            "namespace": view.NAMESPACE,
            "display_name": view.DISPLAY_NAME,
            "description": view.DESCRIPTION,
            "depends_on": list(view.DEPENDS_ON),
        }
        for view in views_list
    ]
    return json(data)


# TODO: view parameter validation
@blueprint.route("/<view_namespace>", methods=["GET"])
@validate_route_parameter(
    "view_namespace",
    lambda view_namespace: view_namespace in view_namespaces,
    f"View must be one of: {', '.join(view_namespaces)}",
)
async def get_view(request: Request, view_namespace: str):
    view_data = await apply_view(
        view_namespace, request.args, request.app.ctx.metric_store
    )
    return json(view_data)
