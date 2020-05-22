#!/usr/bin/env python3

import json

from datetime import datetime

from typing import Optional, Dict

from tkinter import Tk, TOP, LEFT, Y, NO, filedialog
from tkinter.ttk import Label, Frame, Button, Treeview, Notebook


def get_timeline(root_tline: Dict, tid: str) -> Optional[Dict]:

    if root_tline["tid"] == tid:
        return root_tline

    search = [
        tline for tline in root_tline["childs"]
        if tline["tid"] == tid
        ]

    if len(search) > 0:
        return search[0]

    for tline in root_tline["childs"]:
        search = get_timeline(tline, tid)
        if search:
            return search

    return None


class TimelineVisor(Frame):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.tline_data: Optional[Dict] = None

        self.selected_tline: Optional[Dict] = None

        self.build()

    def add_timeline(
        self,
        parent: Treeview,
        tdata: Dict
            ):

        newtree = self.viewtree.insert(
            parent if parent != self.viewtree else "",
            "end",
            text=tdata["tid"],
            values=(
                f"{tdata['end'] - tdata['begin']:0.3f}",
                datetime.utcfromtimestamp(tdata["begin"]).strftime('%H:%M:%S')
                )
            )

        for tline_data in tdata["childs"]:
            self.add_timeline(newtree, tline_data)

    def load_timeline_file(self):
        # load file
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Select timeline file..."
            )

        with open(filename, "r") as tline_file:
            self.tline_data = json.loads(tline_file.read())

        # clear tree view
        self.viewtree.delete(*self.viewtree.get_children())

        # fill tree
        self.add_timeline(self.viewtree, self.tline_data)

    def update_event_visor(self, event):

        # clear event visor
        self.eventtree.delete(*self.eventtree.get_children())

        # get selected timeline id
        tid = self.viewtree.item(
            self.viewtree.focus()
            )["text"]

        tline = get_timeline(self.tline_data, tid)

        self.selected_tline = tline

        sorted_events = sorted(
            tline["events"],
            key=lambda x: x["timestamp"],
            )

        # add events
        for event in sorted_events:
            self.eventtree.insert(
                "",
                "end",
                text=event["etype"],
                values=(
                    datetime.utcfromtimestamp(event["timestamp"]).strftime('%H:%M:%S')
                    ),
                tags=event["eid"]
                )

    def update_inspector(self, event):
        # get event
        eid = self.eventtree.item(
            self.eventtree.focus()
            )["tags"][0]

        search = [
            event for event in self.selected_tline["events"]
            if event["eid"] == eid
            ]

        assert len(search) == 1

        event = search[0]

        self.inspector_etype_lbl.config(
            text=f"Event \"{event['etype']}\""
            )

        self.inspector_eid_lbl.config(
            text=f"Event ID: {event['eid']}"
            )

        self.inspector_timestamp_lbl.config(
            text=f"Timestamp: {datetime.utcfromtimestamp(event['timestamp']).strftime('%H:%M:%S')}"
            )

        # clear data visor
        self.inspector_datatree.delete(*self.inspector_datatree.get_children())

        if event["data"]:
            for key, value in event["data"].items():
                self.inspector_datatree.insert(
                    "",
                    "end",
                    text=key,
                    values=(value)
                    )

    def build(self):

        load_btn = Button(
            self,
            text="Open...",
            command=self.load_timeline_file
            )
        load_btn.pack(side=TOP, pady=10)

        self.viewtree = Treeview(self)
        self.viewtree["columns"] = (
            "duration", "timestamp"
            )

        self.viewtree.heading("#0", text="ID")
        self.viewtree.heading("duration", text="Duration")
        self.viewtree.heading("timestamp", text="Timestamp")

        self.viewtree.column("#0", width=200, minwidth=200)
        self.viewtree.column("duration", width=60, minwidth=60)
        self.viewtree.column("timestamp", width=80, minwidth=80)

        self.viewtree.bind("<<TreeviewSelect>>", self.update_event_visor)

        self.viewtree.pack(side=LEFT, padx=5, pady=20, fill=Y)

        self.eventtree = Treeview(self)
        self.eventtree["columns"] = (
            "timestamp"
            )

        self.eventtree.heading("#0", text="etype")
        self.eventtree.heading("timestamp", text="Timestamp")

        self.eventtree.column("#0", width=260, minwidth=260)
        self.eventtree.column("timestamp", width=80, minwidth=80)

        self.eventtree.bind("<<TreeviewSelect>>", self.update_inspector)

        self.eventtree.pack(side=LEFT, padx=5, pady=20, fill=Y)

        self.eventinspector = Frame(self)

        self.inspector_etype_lbl = Label(
            self.eventinspector, text="Event \"\""
            )
        self.inspector_etype_lbl.grid(row=0, column=0, sticky="W")
        self.inspector_eid_lbl = Label(
            self.eventinspector, text="Event ID:"
            )
        self.inspector_eid_lbl.grid(row=1, column=0, sticky="W")
        self.inspector_timestamp_lbl = Label(
            self.eventinspector, text="Timestamp:"
            )
        self.inspector_timestamp_lbl.grid(row=2, column=0, sticky="W")

        self.inspector_datatree = Treeview(self.eventinspector)
        self.inspector_datatree["columns"] = ("value")

        self.inspector_datatree.heading("#0", text="Key")
        self.inspector_datatree.heading("value", text="Value")

        self.inspector_datatree.column("#0", width=170, minwidth=170)
        self.inspector_datatree.column("value", width=170, minwidth=170)

        self.inspector_datatree.grid(row=3, column=0)

        self.eventinspector.pack(side=LEFT, padx=5, pady=20)

        self.pack()


def main():
    root = Tk()
    root.title("Houston Telemetry Timeline Visor - v0.1.0")

    app = TimelineVisor(root)

    root.mainloop()


if __name__ == '__main__':
    main()
