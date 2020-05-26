#!/usr/bin/env python3

# until python 4.0 i must import this
# https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

import enum
import time
import string
import random

from typing import Optional, Dict, List


class EventTag(str, enum.Enum):
    Default = "default"
    Warning = "warning"
    Error = "error"
    Bug = "bug"


class Event:

    def __init__(
        self,
        etype: str,
        data: Dict = {},
        eid: Optional[str] = None,
        tag: EventTag = EventTag.Default
            ):

        self.etype = etype
        self.data = data

        if eid:
            self.eid = eid
        else:
            self.eid = ''.join(
                [random.choice(
                    string.ascii_letters + string.digits
                    ) for i in range(24)]
                )
        self.tag = tag

        self.timestamp = time.time()
        self.timeline: Optional[Timeline] = None
        self.ancestor: Optional[Event] = None
        self.successors: List[Event] = []

    def trigger(
        self,
        etype: str,
        data: Dict = {},
        eid: Optional[str] = None,
        tag: EventTag = EventTag.Default
            ) -> Event:

        nevt = Event(
            etype,
            data=data,
            eid=eid,
            tag=tag
            )

        nevt.ancestor = self
        self.successors.append(nevt)

        if self.timeline:
            self.timeline.place(nevt)

        return nevt

    def as_json(self) -> Dict:
        ret = {
            "etype": self.etype,
            "tag": self.tag,
            "data": self.data,
            "eid": self.eid,
            "timestamp": self.timestamp
        }
        if self.ancestor:
            ret["ancestor"] = self.ancestor.eid

        if len(self.successors) > 0:
            ret["successors"] = [
                succ.eid for succ in self.successors
                ]

        return ret


class Timeline:

    class OutOfBounds(Exception):
        pass

    def __init__(
        self,
        name: str,
        tid: Optional[str] = None
            ):

        assert isinstance(name, str)

        self.name = name

        if tid:
            self.tid = tid
        else:
            self.tid = ''.join(
                [random.choice(
                    string.ascii_letters + string.digits
                    ) for i in range(24)]
                )
        self.begin: float = time.time()
        self.end: Optional[float] = None
        self.parent: Optional[Timeline] = None
        self.events: Dict[Event] = {}
        self.childs: Dict[Timeline] = {}

    def getev(self, eid: str) -> Event:
        return self.events[eid]

    def getchild(self, name: str) -> Timeline:

        if name == self.name:
            return self

        for child in self.childs.values():
            ret = child.getchild(name)
            if ret:
                return ret

        return None

    def place(self, evt: Event) -> Event:
        # if self.end and (evt.timestamp > self.end):
        #     raise Timeline.OutOfBounds

        evt.timeline = self
        self.events[evt.eid] = evt

        return evt

    def fork(self, name: str, tid: Optional[str] = None) -> Timeline:
        nline = Timeline(name, tid=tid)
        nline.parent = self
        self.childs[nline.tid] = nline
        return nline

    def join(self) -> None:

        for child in self.childs.values():
            child.join()

        self.end = time.time()

    def reset(self) -> None:
        self.begin = time.time()
        self.events = {}
        self.childs = {}
        self.end = None

    def as_json(self) -> Dict:
        ret = {
            "tid": self.tid,
            "name": self.name,
            "begin": self.begin,
            "events": [evt.as_json() for evt in self.events.values()],
            "childs": [
                child.as_json() for child in self.childs.values()
                ]
        }
        if self.end:
            ret["end"] = self.end

        return ret


ROOT_TIMELINE = Timeline("root")


def reset_root_timeline() -> None:
    ROOT_TIMELINE = Timeline("root")


def get_timeline(*args) -> Timeline:
    if len(args) == 0:
        return ROOT_TIMELINE

    ret = ROOT_TIMELINE.getchild(args[0])
    if ret:
        return ret

    return ROOT_TIMELINE.fork(args[0])
