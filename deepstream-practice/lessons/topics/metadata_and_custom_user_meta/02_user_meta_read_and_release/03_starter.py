#!/usr/bin/env python3
"""
Lesson 02 starter: read and release custom user meta.
"""

import sys

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds


def bus_call(bus, message, loop):
    # TODO 1: Xu ly EOS, WARNING va ERROR.
    _ = bus
    _ = message
    _ = loop
    return True


def fakesink_sink_pad_buffer_probe(pad, info, u_data):
    # TODO 2: Doc frame_user_meta_list va release custom payload.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def main(args):
    if len(args) != 2:
        sys.stderr.write("usage: %s <h264 stream file>\n" % args[0])
        sys.exit(1)

    Gst.init(None)

    pipeline = Gst.Pipeline.new("custom-user-meta-pipeline")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    queue = Gst.ElementFactory.make("queue", "queue")
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    sink = Gst.ElementFactory.make("fakesink", "fakesink")

    source.set_property("location", args[1])
    streammux.set_property("width", 1280)
    streammux.set_property("height", 720)
    streammux.set_property("batch-size", 1)

    for element in (source, h264parser, decoder, streammux, queue, queue1, sink):
        pipeline.add(element)

    # TODO 3: Link source, parser va decoder.
    source.link(h264parser)
    h264parser.link(decoder)

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    srcpad.link(sinkpad)

    streammux.link(queue)
    queue.link(queue1)
    queue1.link(sink)

    sinkpad_probe = sink.get_static_pad("sink")
    sinkpad_probe.add_probe(
        Gst.PadProbeType.BUFFER, fakesink_sink_pad_buffer_probe, 0
    )

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
