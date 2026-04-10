#!/usr/bin/env python3
"""
Lesson 02 - SCRATCH FILE

File nay de test, thu nghiem, debug thoai mai.
Sau khi chay on, chuyen code sach sang solution.py
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

# TODO: Test your code here. Add print debug, comment thoai mai.

def on_message(bus, message, loop):
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("EOS: Da doc het du lieu")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(err)
        if debug:
            print(f"Debug: {debug}")
        loop.quit()

    return True

def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        print(f"Khong tao duoc element {factory_name}")
        return 1
    return element

def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-any-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)
    pipeline = Gst.Pipeline.new("scratch-02")
    source = make_element("filesrc", "file-src")
    h264parse = make_element("h264parse", "h264-parse")
    decoder = make_element("nvv4l2decoder", "decoder")
    sink = make_element("fakesink", "fake-sink")

    source.set_property("location", input_path)
    sink.set_property("sync", False)

    pipeline.add(source)
    pipeline.add(h264parse)
    pipeline.add(decoder)
    pipeline.add(sink)

    if not source.link(h264parse):
        print("Loi: Khong the link filesrc -> h264parse", file=sys.stderr)
        return 1

    if not h264parse.link(decoder):
        print("Loi: Khong the link h264parse -> nvv4l2decoder", file=sys.stderr)
        return 1

    if not decoder.link(sink):
        print("Loi: Khong the link nvv4l2decoder -> fakesink", file=sys.stderr)
        return 1
    
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Playingggg")
    pipeline.set_state(Gst.State.PLAYING)
    loop.run()
    pipeline.set_state(Gst.State.NULL)
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
