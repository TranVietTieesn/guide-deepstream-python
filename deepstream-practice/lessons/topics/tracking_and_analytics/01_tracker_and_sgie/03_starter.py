#!/usr/bin/env python3
"""
Lesson 01 starter: tracker and SGIE.
"""

import configparser
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.bus_call import bus_call
from common.platform_info import PlatformInfo

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000


def osd_sink_pad_buffer_probe(pad, info, u_data):
    # TODO 1: Doc frame/object meta va past-frame tracker meta.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def main(args):
    if len(args) < 2:
        sys.stderr.write("usage: %s <h264_elementary_stream>\n" % args[0])
        sys.exit(1)

    platform_info = PlatformInfo()
    Gst.init(None)

    pipeline = Gst.Pipeline()
    source = Gst.ElementFactory.make("filesrc", "file-source")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    sgie1 = Gst.ElementFactory.make("nvinfer", "secondary1-nvinference-engine")
    sgie2 = Gst.ElementFactory.make("nvinfer", "secondary2-nvinference-engine")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = (
        Gst.ElementFactory.make("nv3dsink", "nv3d-sink")
        if platform_info.is_platform_aarch64() or platform_info.is_integrated_gpu()
        else Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    )

    source.set_property("location", args[1])
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batch-size", 1)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", "dstest2_pgie_config.txt")
    sgie1.set_property("config-file-path", "dstest2_sgie1_config.txt")
    sgie2.set_property("config-file-path", "dstest2_sgie2_config.txt")

    config = configparser.ConfigParser()
    config.read("dstest2_tracker_config.txt")
    for key in config["tracker"]:
        if key == "tracker-width":
            tracker.set_property("tracker-width", config.getint("tracker", key))
        if key == "tracker-height":
            tracker.set_property("tracker-height", config.getint("tracker", key))
        if key == "gpu-id":
            tracker.set_property("gpu_id", config.getint("tracker", key))
        if key == "ll-lib-file":
            tracker.set_property("ll-lib-file", config.get("tracker", key))
        if key == "ll-config-file":
            tracker.set_property("ll-config-file", config.get("tracker", key))

    for element in (
        source,
        h264parser,
        decoder,
        streammux,
        pgie,
        tracker,
        sgie1,
        sgie2,
        nvvidconv,
        nvosd,
        sink,
    ):
        pipeline.add(element)

    source.link(h264parser)
    h264parser.link(decoder)
    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    srcpad.link(sinkpad)
    streammux.link(pgie)
    pgie.link(tracker)
    tracker.link(sgie1)
    sgie1.link(sgie2)
    sgie2.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    osdsinkpad = nvosd.get_static_pad("sink")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

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
