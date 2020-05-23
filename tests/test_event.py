#!/usr/bin/env python3

from houston import Event


def test_event_trigger():
    og_event = Event(
        "test 0"
        )
    new_event = og_event.trigger(
        "test 1"
        )

    assert new_event.ancestor == og_event
    assert new_event in og_event.successors
