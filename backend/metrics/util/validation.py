from functools import wraps
from json import dumps as json_dumps
from types import FunctionType

import shared.schema as schema
from sanic.exceptions import InvalidUsage, NotFound


def validate_route_parameter(
    parameter_name: str, validation_function: FunctionType, error_msg: str
) -> FunctionType:
    def decorator(handler_func: FunctionType):
        @wraps(handler_func)
        def decorated_handler(request, *args, **kwargs):
            parameter_value = kwargs.get(parameter_name, None)
            if not validation_function(parameter_value):
                raise NotFound(error_msg)
            return handler_func(request, *args, **kwargs)

        return decorated_handler

    return decorator


def parse_schema(body: str = None, parameters: str = None):
    def decorator(handler_func: FunctionType):
        if body:
            body_validator = schema.Validator(schema.registry.get(body))
        if parameters:
            parameters_validator = schema.Validator(schema.registry.get(parameters))

        def _validate_single(
            name: str, validator: schema.Validator, document: dict
        ) -> dict:
            if not validator.validate(document):
                formatted_errors = ", ".join(validator.errors)
                raise InvalidUsage(f"Invalid {name} schema: {formatted_errors}")
            return validator.normalized(document)

        @wraps(handler_func)
        def decorated_handler(request, *args, **kwargs):
            if body:
                parsed_body = _validate_single("body", body_validator, request.json)
                request.body = json_dumps(parsed_body)

            if parameters:
                parsed_parameters = _validate_single(
                    "parameters", parameters_validator, request.args
                )
                for parameter, parsed_value in parsed_parameters.items():
                    request.args[parameter] = parsed_value

            return handler_func(request, *args, **kwargs)

        return decorated_handler

    return decorator
