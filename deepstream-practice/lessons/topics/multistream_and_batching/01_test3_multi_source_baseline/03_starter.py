#!/usr/bin/env python3
"""
Lesson 01 starter: multi-source baseline.
"""

from pathlib import Path
from os import environ
import argparse
import configparser
import math
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.platform_info import PlatformInfo


PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
OSD_PROCESS_MODE = 0
OSD_DISPLAY_TEXT = 1
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "RoadSign"]
perf_data = None
measure_latency = False
no_display = False
silent = False
file_loop = False


def pgie_src_pad_buffer_probe(pad, info, u_data):
    # TODO 1: Doc batch metadata va update FPS.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def cb_newpad(decodebin, decoder_src_pad, data):
    # TODO 2: Bat video pad NVMM va set target cho ghost pad.
    _ = decodebin
    _ = decoder_src_pad
    _ = data


def decodebin_child_added(child_proxy, Object, name, user_data):
    # TODO 3: Theo doi child-added va drop-on-latency.
    _ = child_proxy
    _ = Object
    _ = name
    _ = user_data


def create_source_bin(index, uri):
    # TODO 4: Tao source bin + uridecodebin + ghost pad.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(args, requested_pgie=None, config=None, disable_probe=False):
    global perf_data
    perf_data = PERF_DATA(len(args))

    input_sources = args
    number_sources = len(input_sources)
    platform_info = PlatformInfo()
    Gst.init(None)

    pipeline = Gst.Pipeline()
    is_live = False
    if not pipeline:
        print("Unable to create Pipeline", file=sys.stderr)

    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        print("Unable to create NvStreamMux", file=sys.stderr)

    pipeline.add(streammux)

    for i in range(number_sources):
        uri_name = input_sources[i]
        if uri_name.find("rtsp://") == 0:
            is_live = True
        source_bin = create_source_bin(i, uri_name)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        if srcpad and sinkpad:
            srcpad.link(sinkpad)

    queue1 = Gst.ElementFactory.make("queue", "queue1")
    queue2 = Gst.ElementFactory.make("queue", "queue2")
    queue3 = Gst.ElementFactory.make("queue", "queue3")
    queue4 = Gst.ElementFactory.make("queue", "queue4")
    queue5 = Gst.ElementFactory.make("queue", "queue5")
    for q in (queue1, queue2, queue3, queue4, queue5):
        pipeline.add(q)

    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = Gst.ElementFactory.make("fakesink", "fakesink") if no_display else None
    if not sink:
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")

    if is_live:
        streammux.set_property("live-source", 1)
    streammux.set_property("width", MUXER_OUTPUT_WIDTH)
    streammux.set_property("height", MUXER_OUTPUT_HEIGHT)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("sync", 0 if no_display else 1)

    if config:
        pgie.set_property("config-file-path", config)
    else:
        pgie.set_property("config-file-path", "dstest3_pgie_config.txt")

    for element in (pgie, tiler, nvvidconv, nvosd, sink):
        pipeline.add(element)

    streammux.link(queue1)
    queue1.link(pgie)
    pgie.link(queue2)
    queue2.link(tiler)
    tiler.link(queue3)
    queue3.link(nvvidconv)
    nvvidconv.link(queue4)
    queue4.link(nvosd)
    nvosd.link(queue5)
    queue5.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    pgie_src_pad = pgie.get_static_pad("src")
    if pgie_src_pad and not disable_probe:
        pgie_src_pad.add_probe(Gst.PadProbeType.BUFFER, pgie_src_pad_buffer_probe, 0)

    print("Starting pipeline")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(prog="deepstream_test3")
    parser.add_argument("-i", "--input", nargs="+", required=True)
    parser.add_argument("-c", "--configfile", default=None)
    parser.add_argument(
        "-g",
        "--pgie",
        default=None,
        choices=["nvinfer", "nvinferserver", "nvinferserver-grpc"],
    )
    parser.add_argument("--no-display", action="store_true", default=False)
    parser.add_argument("--file-loop", action="store_true", default=False)
    parser.add_argument("--disable-probe", action="store_true", default=False)
    parser.add_argument("-s", "--silent", action="store_true", default=False)
    args = parser.parse_args()
    global no_display, silent, file_loop
    no_display = args.no_display
    silent = args.silent
    file_loop = args.file_loop
    return args.input, args.pgie, args.configfile, args.disable_probe


if __name__ == "__main__":
    stream_paths, pgie, config, disable_probe = parse_args()
    sys.exit(main(stream_paths, pgie, config, disable_probe))
