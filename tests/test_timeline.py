#!/usr/bin/env python3
import json

from houston import Event, get_timeline


def test_getchild():
    # test 0: check if getchild returns the same tline
    #         and also if parent is root.
    test_tline0 = get_timeline("test0")

    assert test_tline0 == get_timeline().getchild("test0")
    assert test_tline0.parent == get_timeline()

    # test 1: test creating a timeline with the same name
    #           as a timeline closer to root
    test_tline1 = get_timeline("test1")
    test_tline1_0 = test_tline1.fork("test0")

    assert test_tline1_0.parent == get_timeline("test1")
    assert test_tline1_0 == get_timeline("test1").getchild("test0")


def test_timeline_place():

    # test event placement
    get_timeline("test0").place(
        Event("event #1", eid="#000")
        )

    event = get_timeline("test0").getev("#000")

    assert event.etype == "event #1"
    assert event.timeline == get_timeline("test0")

    # test if event trigger updates timeline
    event.trigger(
        "event #2",
        eid="#001"
        )

    event = get_timeline("test0").getev("#001")

    assert event.etype == "event #2"
    assert event.timeline == get_timeline("test0")


def test_fork_then_join():

    local_events = []

    # fork new timeline
    get_timeline("test1").fork("test2")

    # trigger several events
    event = get_timeline("test2").place(
        Event("event #3")
        )

    assert event.timeline == get_timeline("test2")

    local_events.append(event)
    event = event.trigger("event #4")
    local_events.append(event)
    event = event.trigger("event #5")
    local_events.append(event)
    event = event.trigger("event #6")
    local_events.append(event)
    event = event.trigger("event #7")
    local_events.append(event)

    # end timeline
    get_timeline("test2").join()

    for event in local_events:
        assert event in get_timeline("test2").events.values()


def test_dumpTimeline():
    get_timeline().join()

    tdump = get_timeline().as_json()

    # check child structure
    names = [child["name"] for child in tdump["childs"]]

    assert get_timeline("test0").name in names
    assert get_timeline("test1").name in names

    child_tline1 = [child for child in tdump["childs"] if child["name"] == "test1"]

    assert len(child_tline1) == 1

    child_tline1 = child_tline1[0]

    names = [child["name"] for child in child_tline1["childs"]]

    assert get_timeline("test1").getchild("test0").name in names
    assert len(get_timeline("test1").getchild("test0").events) == 0

    assert len(child_tline1["events"]) == 0

    # check for end in all trees, to check if root .join() worked
    def assert_end(tline_data):
        for child in tline_data["childs"]:
            assert_end(child)
        assert "end" in tline_data

    assert_end(tdump)

    with open("pytest.timeline", "w") as tline_dump_file:
        tline_dump_file.write(
            json.dumps(
                tdump,
                indent=4,
                sort_keys=True
                )
            )
