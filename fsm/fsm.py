#!/usr/bin/env python3

import enum
import typing
from dataclasses import dataclass

try:
    import graphviz
except ImportError:
    graphviz = None
    
from fsm.utils import import_string



class DuplicateOperationError(Exception):
    pass


class InvalidStateError(Exception):
    pass


@dataclass
class Transition:
    operation: typing.Union[typing.Callable, str]
    from_state: typing.Union[enum.Enum, None]
    to_state: enum.Enum


class StateMachine:
    default_state: typing.Optional[enum.Enum] = None
    state: typing.Optional[enum.Enum] = None
    operations: typing.Dict[str, typing.Callable] = None

    def __init__(
        self,
        states: enum.EnumMeta,
        default_state: enum.Enum,
        transitions: typing.List[Transition],
    ):
        self.states = states
        self.default_state = default_state
        self.state = default_state
        self._transitions = transitions

    def _lazy_load_transitions(self):
        # Delay loading transition operations to avoid circular imports
        if self.operations is None and self._transitions is not None:
            for ts in self._transitions:
                self.add_transition(ts)

    def __getattr__(self, name):
        self._lazy_load_transitions()
        if name in self.operations:
            action = name
            transition = self.operations[action]
            if self.state != transition.from_state:
                raise InvalidStateError()

            return self.executor(transition)

    def add_transition(self, transition: Transition):
        if self.operations is None:
            self.operations = {}

        operation = transition.operation
        if type(operation) == str:
            operation = import_string(operation)

        action = operation.__name__
        if action in self.operations:
            raise DuplicateOperationError()

        transition.operation = operation
        self.operations[action] = transition

    def executor(self, transition: Transition):
        def wrapper(*args, **kwargs):
            result = transition.operation(*args, **kwargs)
            self.state = transition.to_state
            return result

        return wrapper

    @property
    def graph(self):
        if graphviz is None:
            return "Graphviz is not available"

        dot = graphviz.Digraph(comment="State transitions")
        for state in self.states:
            dot.node(state.name)

        self._lazy_load_transitions()
        for name, transition in self.operations.items():
            dot.edge(transition.from_state.name, transition.to_state.name, label=name)
        return dot
