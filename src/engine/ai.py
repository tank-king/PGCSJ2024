from typing import Optional

import pygame

from src.engine.objects import BaseStructure, BaseObject


class State(BaseStructure):
    def __init__(self, name, fsm_parent: 'FiniteStateMachine' = None):
        self.name = name
        self.to_pop = False
        self.fsm = fsm_parent
        self.obj = None

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def pop(self):
        self.to_pop = True


class NoneState(State):
    def __init__(self, fsm):
        super().__init__('none', fsm)


class FiniteStateMachine(BaseStructure):
    def __init__(self, obj, initial_states=()):
        self.obj: obj.__class__ = obj
        self.states = {'none': NoneState(self)}
        for i in initial_states:
            self.states[i.name] = i
        self.stack: list[str] = ['none']
        self.state = self.states[self.stack[-1]]

    @property
    def current_state(self):
        return self.state.name

    def add_states(self, *args):
        for i in args:
            self.states[i.name] = i
            i.fsm = self
            self.states[i.name].obj = self.obj

    def on_state_change(self):
        pass

    def push_state(self, state: str):
        # print(state)
        if state in list(self.states.keys()):
            self.stack.append(state)
            self.state = self.states[state]
            self.state.on_enter()
            self.on_state_change()
        else:
            raise Exception(f"state {state} not registered in state machine")

    def pop_state(self):
        if len(self.stack) <= 1:
            return
        state = self.stack.pop()
        self.states[state].on_exit()
        self.states[state].to_pop = False
        self.state = self.states[self.stack[-1]]
        self.on_state_change()

    def update(self, events: list[pygame.event.Event], dt):
        # print(self.current_state, self.stack)
        self.state.update(events, dt)
        if self.state.to_pop:
            self.pop_state()
