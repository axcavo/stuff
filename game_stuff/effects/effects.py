from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Iterator

import _util


class _LedgerEntry:
    __slots__ = ('value', 'duration', 'effect_id')

    def __init__(self, value: int, duration: int, effect_id: str):
        self.value = value
        self.duration = duration
        self.effect_id = effect_id

    def __repr__(self) -> str:
        return f"[value: {self.value}, duration: {self.duration}]"


class EffectLedger:
    __slots__ = ('_data',)

    def __init__(self) -> None:
        self._data: defaultdict[str, list[_LedgerEntry]] = defaultdict(list)

    def __repr__(self) -> str:
        return repr(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, item) -> int:
        return item in self._data

    def __getitem__(self, item) -> list[_LedgerEntry]:
        return self._data[item]

    def __setitem__(self, key, value) -> None:
        self._data[key] = value

    def __iter__(self) -> Iterator[tuple[str, list[_LedgerEntry]]]:
        return iter(self._data.items())

    def put(self, effect_id: str, entry: _LedgerEntry) -> None:
        self._data[effect_id].append(entry)

    def pop(self, effect_id: str) -> list[_LedgerEntry]:
        return self._data.pop(effect_id)

    def snapshot(self) -> list[tuple[str, list[_LedgerEntry]]]:
        return list(self._data.items())


class EffectValueProtocol(ABC):
    identifier: str

    def __init__(self) -> None:
        if not hasattr(self, 'identifier'):
            raise AttributeError("Protocol must define an identifier.")

    def apply(self, entries: list[_LedgerEntry]) -> int:
        return self._apply(entries)

    @abstractmethod
    def _apply(self, entries: list[_LedgerEntry]) -> int:
        pass


class EffectDurationProtocol(ABC):
    identifier: str

    def __init__(self) -> None:
        if not hasattr(self, 'identifier'):
            raise AttributeError("Protocol must define an identifier.")

    def apply(self, entries: list[_LedgerEntry]) -> None:
        return self._apply(entries)

    @abstractmethod
    def _apply(self, entries: list[_LedgerEntry]) -> None:
        pass


class EffectApplicationProtocol:
    __slots__ = ('duration_protocol', 'value_protocol')

    def __init__(self, duration_protocol: EffectDurationProtocol, value_protocol: EffectValueProtocol) -> None:
        self.duration_protocol = duration_protocol
        self.value_protocol = value_protocol


class Effect:
    __slots__ = ('identifier', 'target_attr', 'appl_operator', 'duration')

    def __init__(self, identifier: str, target_attr: str, appl_operator: str, duration: int):
        if not appl_operator in _util.ARITHMETIC_OPERATOR_MAP:
            raise AttributeError(f"Unknown arithmetic operator: {appl_operator}.")

        self.identifier = identifier
        self.target_attr = target_attr
        self.appl_operator = appl_operator
        self.duration = duration

    def preprare(self, value: int, duration: int | None = None) -> "PreparedEffect":
        return PreparedEffect(effect=self, value=value, duration=duration or self.duration)


class PreparedEffect:
    __slots__ = ('effect', 'value', 'duration')

    def __init__(self, effect: Effect, value: int, duration: int):
        self.effect = effect
        self.value = value
        self.duration = duration

    def __call__(self, receiver: object, previous: EffectLedger | None = None) -> EffectLedger:
        if not hasattr(receiver, self.effect.target_attr):
            raise AttributeError(f"{receiver} is missing target attribute: '{self.effect.target_attr}'.")

        total = _util.ARITHMETIC_OPERATOR_MAP[self.effect.appl_operator](
            getattr(receiver, self.effect.target_attr), self.value
        )
        delta = int(total - getattr(receiver, self.effect.target_attr))

        entry = _LedgerEntry(delta, self.duration, self.effect.identifier)
        ledger = previous or EffectLedger()
        ledger.put(self.effect.target_attr, entry)

        return ledger


def resolve_effects(ledger: EffectLedger, context: dict[str, EffectApplicationProtocol]) -> dict[str, int]:
    resolved = {}

    for attr, entries in ledger.snapshot():
        grouped = defaultdict(list)
        for entry in entries:
            grouped[entry.effect_id].append(entry)

        total = 0
        for effect_id, group in grouped.items():
            protocol = context[effect_id]

            total += protocol.value_protocol.apply(group)
            protocol.duration_protocol.apply(group)

        resolved[attr] = total

        ledger[attr] = [entry for entry in entries if entry.duration > 0]
        if not ledger[str]:
            ledger.pop(attr)

    return resolved


def apply_effects(receiver: object, resolved: dict[str, int]) -> None:
    for attr, delta in resolved.items():
        value = getattr(receiver, attr) + delta
        setattr(receiver, attr, value)
