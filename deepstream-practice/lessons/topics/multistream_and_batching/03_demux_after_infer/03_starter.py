#!/usr/bin/env python3
"""
Lesson 03 starter: demux after infer.
"""

import argparse
import math
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.platform_info import PlatformInfo


perf_data = None
MUXER_OUTPUT_WIDTH = 540
MUXER_OUTPUT_HEIGHT = 540
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 640
TILED_OUTPUT_HEIGHT = 360


def create_source_bin(index, uri):
    # TODO 1: Tao source bin nhu lesson 01.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(args):
    global perf_data
    perf_data = PERF_DATA(len(args))
    number_sources = len(args)
    platform_info = PlatformInfo()
    Gst.init(None)

    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvstreamdemux = Gst.ElementFactory.make("nvstreamdemux", "nvstreamdemux")
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    pipeline.add(streammux)
    pipeline.add(queue1)
    pipeline.add(pgie)
    pipeline.add(nvstreamdemux)

    is_live = False
    for i, uri_name in enumerate(args):
        if uri_name.find("rtsp://") == 0:
            is_live = True
        source_bin = create_source_bin(i, uri_name)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        srcpad.link(sinkpad)

    if is_live:
        streammux.set_property("live-source", 1)
    streammux.set_property("width", MUXER_OUTPUT_WIDTH)
    streammux.set_property("height", MUXER_OUTPUT_HEIGHT)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", "ds_demux_pgie_config.txt")

    pipeline.add(queue1)
    streammux.link(queue1)
    queue1.link(pgie)
    pgie.link(nvstreamdemux)

    for i in range(number_sources):
        queue = Gst.ElementFactory.make("queue", "demux-queue-%u" % i)
        conv = Gst.ElementFactory.make("nvvideoconvert", "demux-conv-%u" % i)
        osd = Gst.ElementFactory.make("nvdsosd", "demux-osd-%u" % i)
        sink = Gst.ElementFactory.make("nveglglessink", "demux-sink-%u" % i)
        for element in (queue, conv, osd, sink):
            pipeline.add(element)
        srcpad = nvstreamdemux.request_pad_simple("src_%u" % i)
        sinkpad = queue.get_static_pad("sink")
        srcpad.link(sinkpad)
        queue.link(conv)
        conv.link(osd)
        osd.link(sink)

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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True)
    return parser.parse_args().input


if __name__ == "__main__":
    sys.exit(main(parse_args()))
