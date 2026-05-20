import json
from collections import defaultdict
from collections.abc import dict_keys
from typing import Optional

from game_stuff.helpers import OPERATION_MAP


class _LedgerEntry:
    __slots__ = ('value', 'duration')

    def __init__(self, value: int, duration: int) -> None:
        self.duration: int = duration
        self.value: int = value

    def __repr__(self) -> str:
        return f"[value: {self.value}, duration: {self.duration}]"


class EffectLedger:
    __slots__ = '_data'

    def __init__(self, initial_data: Optional[dict[str, list[_LedgerEntry]]] = None) -> None:
        self._data: defaultdict[str, list[_LedgerEntry]] = defaultdict(
            list, initial_data or {}
        )

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, attr: str) -> bool:
        return attr in self._data

    def __getitem__(self, attr: str) -> list[_LedgerEntry]:
        return self._data[attr]

    def __setitem__(self, attr: str, entries: list[_LedgerEntry]) -> None:
        self._data[attr] = entries

    def __iter__(self):
        return iter(self._data.items())

    def __repr__(self) -> str:
        return repr(dict(self._data))

    def __delitem__(self, attr):
        self._data.__delitem__(attr)

    def put(self, attr: str, entry: _LedgerEntry) -> None:
        self._data[attr].append(entry)

    def keys(self) -> dict_keys:
        return self._data.keys()


class Effect:
    __slots__ = ('identifier', 'target_attr', 'application_op', 'duration')

    def __init__(self, identifier: str, target_attr: str, application_op: str, duration: int = 1) -> None:
        if application_op not in OPERATION_MAP:
            raise ValueError(f"{application_op} is not a valid operator.")

        self.identifier: str = identifier
        self.target_attr: str = target_attr
        self.application_op: str = application_op
        self.duration: int = duration

    def __call__(self, *, receiver: object, value: int, previous: Optional[EffectLedger] = None) -> EffectLedger:
        if not hasattr(receiver, self.target_attr):
            raise ValueError(f"Receiver lacks target attribute: '{self.target_attr}'.")

        current_value = getattr(receiver, self.target_attr)
        op_func = OPERATION_MAP[self.application_op]
        value_change = int(op_func(current_value, value) - current_value)

        data = _LedgerEntry(value_change, duration=self.duration)

        ledger = previous or EffectLedger()
        ledger.put(self.target_attr, data)
        return ledger


def _tick_effect_ledger(ledger: EffectLedger) -> None:
    for attr, entries in ledger:
        for i in range(len(entries) - 1, -1, -1):
            entries[i].duration -= 1
            if entries[i].duration <= 0:
                del entries[i]


def _del_empty_ledger_attrs(ledger: EffectLedger) -> None:
    empty_attrs = tuple(attr for attr, entries in ledger if len(entries) == 0)

    for attr in empty_attrs:
        del ledger[attr]


def apply_effects(ledger: EffectLedger, receiver: object) -> Optional[EffectLedger]:
    for attr, entries in ledger:
        delta = sum(entry.value for entry in entries)
        current_value = getattr(receiver, attr)
        setattr(receiver, attr, current_value + delta)

    _tick_effect_ledger(ledger)
    _del_empty_ledger_attrs(ledger)

    return ledger if len(ledger) > 0 else None


def load_effect(json_data: str) -> Effect:
    primitive = json.loads(json_data)

    if not isinstance(primitive, dict):
        raise ValueError("Malformed effect definition: JSON must be an object.")

    required_keys = set(Effect.__slots__)
    if not required_keys.issubset(primitive.keys()):
        raise ValueError(f"Malformed effect definition. Missing keys: {required_keys - primitive.keys()}")

    effect_kwargs = {key: primitive[key] for key in required_keys}
    return Effect(**effect_kwargs)


if __name__ == "__main__":
    def main():
        entry = _LedgerEntry(5, 1)
        ledger = EffectLedger({"xd": [entry]})

        print(ledger)

        _tick_effect_ledger(ledger)

        print(ledger)


    main()
