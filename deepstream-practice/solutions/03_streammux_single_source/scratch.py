#!/usr/bin/env python3
"""
Lesson 03 solution: single-source streammux.

Pipeline muc tieu:
    filesrc -> h264parse -> nvv4l2decoder -> nvstreammux -> fakesink

Hoan thanh cac TODO tu 03_starter.py
Tham khao 05_reference.py neu can
"""

import os
import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


MUXER_BATCH_TIMEOUT_USEC = 33000


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("da doc het pipeline")
        loop.quit()
    elif message == Gst.MessageType.ERROR:
        err, debug = message.parser_error() 
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element va raise `RuntimeError` neu that bai.
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc {factory_name}")
    return element


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("lesson-03-pipeline")

    # TODO 3: Tao day du element.
    source = make_element("filesrc", "file-src")
    parser = make_element("h264parse", "parser")
    decoder = make_element("nvv4l2decoder", "decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    sink = make_element("fakesink", "fake-sink")

    if not pipeline or not source or not parser or not decoder or not streammux or not sink:
        print("Tao day du element truoc.", file=sys.stderr)
        return 1

    # TODO 4: Set property cho source, streammux, va sink.
    source.set_property("location", input_path)
    sink.set_property("sync", False)
    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    # TODO 5: Add element vao pipeline.
    pipeline.add(source)
    pipeline.add(parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(sink)
    # TODO 6: Link static chain `filesrc -> h264parse -> nvv4l2decoder`.
    if not source.link(parser):
        raise RuntimeError("Khong link duoc filesrc -> h264parser")
    
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc h264parser -> nvv4l2decoder")

    # TODO 7: Xin request pad `sink_0` tu `nvstreammux`.
    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Khong xin duoc request pad sink_0 tu nvstreammux")

    # TODO 8: Lay `decoder.src` static pad.
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Khong lay duoc src pad tu decoder")

    # TODO 9: Link `decoder.src -> streammux.sink_0`.
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc decoder.src -> streammux.sink_0")
    
    # TODO 10: Link `nvstreammux -> fakesink`.
    if not streammux.link(sink):
        raise RuntimeError("Khong link duoc nvstreammux -> fakesink")

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running streammux single-source exercise...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
