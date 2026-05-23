from typing import Any

from _util import RELATIONAL_OPERATOR_MAP


def _eval_path(current: Any, keys: list[str]) -> Any:
    key = keys[0]

    if key == 'any':
        if not isinstance(current, list):
            raise TypeError(f"Keyword 'any' expects a list object, but bound '{current.__class__.__name__}'.")
        return any(_eval_path(item, keys[1:]) for item in current)

    if key == 'all':
        if not isinstance(current, list):
            raise TypeError(f"Keyword 'any' expects a list object, but bound '{current.__class__.__name__}'.")
        return all(_eval_path(item, keys[1:]) for item in current)

    if not key in current:
        return False

    current = current[key]

    if len(keys) == 1:
        return current

    return _eval_path(current, keys[1:])


class Condition:
    __slots__ = ('operator', 'key', 'value')

    def __init__(self, operator: str, key: str, value: str) -> None:
        if not key:
            raise ValueError("Empty key.")

        if not value:
            raise ValueError("Empty value.")

        self.operator = operator
        self.value = value
        self.key = key

    def __call__(self, ctx: dict[str, Any]) -> bool:
        return RELATIONAL_OPERATOR_MAP[self.operator](
            _eval_path(ctx, self.key.split('.')),
            self.value
        )
