from game_stuff import EffectLedger
from game_stuff.conditions.base import Condition
from game_stuff.effects.effects import PreparedEffect


class Action:
    __slots__ = ('identifier', 'use_conditions', 'success_conditions', 'effect_ids')

    def __init__(self, identifier: str, use_conditions: list[Condition], success_conditions: list[Condition],
                 effect_ids: tuple[str]) -> None:
        self.identifier = identifier
        self.use_conditions = use_conditions
        self.success_conditions = success_conditions
        self.effect_ids = effect_ids

    def __call__(self, receiver: object, effect_map: dict[str, PreparedEffect], ctx: dict) -> EffectLedger:
        ledger = EffectLedger()

        for condition in self.success_conditions:
            if not condition(ctx):
                return ledger

        for effect_id in self.effect_ids:
            effect_map[effect_id](receiver, ledger)

        return ledger

    def is_usable(self, ctx: dict) -> bool:
        for condition in self.use_conditions:
            if not condition(ctx):
                return False
        return True
