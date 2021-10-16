#!/usr/bin/env python3

import enum
import unittest

from fsm import fsm


class BillStatus(enum.Enum):
    NEW = 0
    DRAFT = 1
    PENDING_APPROVAL = 2
    DENIED = 3
    PENDING_PAYMENT = 4
    PAID = 5


def states():
    return BillStatus


def transitions(states):
    def accept_bill(owner):
        return True

    def submit_bill(approver):
        return True

    def approve_bill(approver):
        return True

    def deny_bill(approver):
        return True

    def fix_bill(ap_clerk):
        return True

    def pay_bill(transaction):
        return True

    return [
        fsm.Transition(
            operation=accept_bill, from_state=states.NEW, to_state=states.DRAFT
        ),
        fsm.Transition(
            operation=submit_bill,
            from_state=states.DRAFT,
            to_state=states.PENDING_APPROVAL,
        ),
        fsm.Transition(
            operation=approve_bill,
            from_state=states.PENDING_APPROVAL,
            to_state=states.PENDING_PAYMENT,
        ),
        fsm.Transition(
            operation=deny_bill,
            from_state=states.PENDING_APPROVAL,
            to_state=states.DENIED,
        ),
        fsm.Transition(
            operation=fix_bill, from_state=states.DENIED, to_state=states.DRAFT
        ),
        fsm.Transition(
            operation=pay_bill, from_state=states.PENDING_PAYMENT, to_state=states.PAID
        ),
    ]


class TestStateMachine(unittest.TestCase):
    def setUp(self):
        self.states = states()
        self.transitions = transitions(self.states)

    def tearDown(self):
        pass

    def test_can_accept_bill(self):
        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.NEW,
            transitions=self.transitions,
        )

        assert sm.state == self.states.NEW, sm.state
        assert sm.accept_bill is not None, sm.operations
        sm.accept_bill(owner="foo")
        assert sm.state == self.states.DRAFT

    def test_can_submit_bill(self):
        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.DRAFT,
            transitions=self.transitions,
        )

        assert sm.submit_bill is not None
        sm.submit_bill(approver="foo")
        assert sm.state == self.states.PENDING_APPROVAL

    def test_can_fix_bill(self):
        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.DENIED,
            transitions=self.transitions,
        )

        assert sm.fix_bill is not None
        sm.fix_bill(ap_clerk="foo")
        assert sm.state == self.states.DRAFT

    def test_invalid_transition(self):
        """Cannot call a non-existent operation."""

        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.NEW,
            transitions=self.transitions,
        )

        with self.assertRaises(TypeError):
            sm.something(foo="bar")

    def test_invalid_state(self):
        """Cannot pay a bill in NEW state."""

        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.NEW,
            transitions=self.transitions,
        )

        with self.assertRaises(fsm.InvalidStateError):
            sm.pay_bill(transaction="foo")

    def test_multiple_transitions(self):
        sm = fsm.StateMachine(
            states=self.states,
            default_state=self.states.NEW,
            transitions=self.transitions,
        )

        # Bill starts with NEW state
        assert sm.state == self.states.NEW

        # Bill can only go to DRAFT state from here
        with self.assertRaises(fsm.InvalidStateError):
            # Can't submit a NEW bill
            sm.submit_bill(approver="foo")

        with self.assertRaises(fsm.InvalidStateError):
            # Can't approve a NEW bill
            sm.approve_bill(approver="foo")

        sm.accept_bill(owner="foo")
        assert sm.state == self.states.DRAFT

        # Bill can be moved to submitted state once it has been edited
        with self.assertRaises(fsm.InvalidStateError):
            # Can't approve a DRAFT bill
            sm.approve_bill(approver="foo")

        sm.submit_bill(approver="foo")
        assert sm.state == self.states.PENDING_APPROVAL

        # Bill can be denied and stays as Denied
        sm.deny_bill(approver="foo")
        assert sm.state == self.states.DENIED

        # Denied bill can be moved back to DRAFT
        sm.fix_bill(ap_clerk="foo")
        assert sm.state == self.states.DRAFT
