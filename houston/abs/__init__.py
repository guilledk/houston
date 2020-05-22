#!/usr/bin/env python3

# until python 4.0 i must import this
# https://www.python.org/dev/peps/pep-0563/
from __future__ import annotations

import time
import string
import random

from typing import Optional, Dict, List


class Event:

    def __init__(
        self,
        etype: str,
        data: Dict = {},
        eid: Optional[str] = None
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

        self.timestamp = time.time()

        self.timeline: Optional[Timeline] = None
        self.ancestor: Optional[Event] = None
        self.successors: List[Event] = []

    def trigger(
        self,
        etype: str,
        data: Dict = {},
        eid: Optional[str] = None
            ) -> Event:

        nevt = Event(
            etype,
            data=data,
            eid=eid
            )

        nevt.ancestor = self
        self.successors.append(nevt)

        self.timeline.place(nevt)

        return nevt

    def as_json(self) -> Dict:
        ret = {
            "etype": self.etype,
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
        tid: str
            ):

        self.tid = tid

        self.begin: float = time.time()
        self.end: Optional[float] = None
        self.events: List[Event] = []
        self.parent: Optional[Timeline] = None
        self.childs: List[Timeline] = []

    def getev(self, eid: str) -> Event:
        search = [ev for ev in self.events if eid in ev.eid]
        assert len(search) == 1
        return search[0]

    def place(self, evt: Event) -> None:
        if self.end and (evt.timestamp > self.end):
            raise OutOfBounds

        evt.timeline = self
        self.events.append(evt)

    def fork(self, ntid: str) -> Timeline:
        nline = Timeline(ntid)
        nline.parent = self
        self.childs.append(nline)
        return nline

    def join(self) -> None:
        self.end = time.time()


TIMELINES: Dict[Timeline] = {}


def getTimeline(tid: str) -> Timeline:
    if tid not in TIMELINES:
        TIMELINES[tid] = Timeline(tid)

    return TIMELINES[tid]


def dumpTimeline(tid: str) -> Dict:
    tline = getTimeline(tid)
    ret = {
        "tid": tline.tid,
        "begin": tline.begin,
        "events": [evt.as_json() for evt in tline.events],
        "childs": [
            dumpTimeline(child.tid) for child in tline.childs
            ]
    }
    if tline.end:
        ret["end"] = tline.end

    return ret
