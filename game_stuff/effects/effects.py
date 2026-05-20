import json
from typing import Optional

from game_stuff.helpers import OPERATION_MAP


class EffectResult:
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

    def __getitem__(self, attr: str) -> int:
        return getattr(self, attr)

    def __setitem__(self, attr: str, value: int):
        if hasattr(self, attr):
            self.__dict__[attr] = self.__dict__[attr] + value
            return
        self.__dict__[attr] = value


class Effect:
    __slots__ = ('identifier', 'target_attr', 'application_op', 'duration')

    def __init__(self, identifier: str, target_attr: str, application_op: str, duration: int = 1):
        if application_op not in OPERATION_MAP:
            raise ValueError(f"{application_op} is not a valid operator.")

        self.identifier: str = identifier
        self.target_attr: str = target_attr
        self.application_op: str = application_op
        self.duration: int = duration

    def __call__(self, *, receiver: object, value: int, previous: Optional[EffectResult] = None) -> EffectResult:
        if not hasattr(receiver, self.target_attr):
            raise ValueError(f"Receiver lacks target attribute: '{self.target_attr}'.")

        current_value = getattr(receiver, self.target_attr)
        op_func = OPERATION_MAP[self.application_op]
        value_change = int(op_func(current_value, value) - current_value)

        if previous:
            previous[self.target_attr] = value_change
            return previous

        return EffectResult(**{self.target_attr: value_change})


def apply_effects(effects: EffectResult, receiver: object):
    for attr, delta in effects.__dict__.items():
        current_value = getattr(receiver, attr)
        setattr(receiver, attr, current_value + delta)


def load_effect(json_data: str) -> Effect:
    primitive = json.loads(json_data)

    required_keys = set(Effect.__slots__)
    if not required_keys.issubset(primitive):
        raise ValueError(f"Malformed effect definition: {primitive}")

    effect_kwargs = {key: primitive[key] for key in required_keys}

    return Effect(**effect_kwargs)
