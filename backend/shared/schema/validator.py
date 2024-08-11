import cerberus


class Validator(cerberus.Validator):
    def _normalize_coerce_integer(self, value):
        return int(value)
