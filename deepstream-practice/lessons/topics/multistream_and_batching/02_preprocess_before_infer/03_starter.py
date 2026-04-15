#!/usr/bin/env python3
"""
Lesson 02 starter: preprocess before infer.
"""

import argparse
import configparser
import math
import sys
from pathlib import Path

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.platform_info import PlatformInfo


perf_data = None
MAX_DISPLAY_LEN = 64
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 540
MUXER_OUTPUT_HEIGHT = 540
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 640
TILED_OUTPUT_HEIGHT = 360
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
OSD_PROCESS_MODE = 0
OSD_DISPLAY_TEXT = 1
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "RoadSign"]


def pgie_src_pad_buffer_probe(pad, info, u_data):
    # TODO 1: Doc preprocess user meta va frame/object meta.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def cb_newpad(decodebin, decoder_src_pad, data):
    # TODO 2: Dynamic pad handling nhu lesson 01.
    _ = decodebin
    _ = decoder_src_pad
    _ = data


def decodebin_child_added(child_proxy, Object, name, user_data):
    # TODO 3: Child-added callback nhu lesson 01.
    _ = child_proxy
    _ = Object
    _ = name
    _ = user_data


def create_source_bin(index, uri):
    # TODO 4: Tao source bin + ghost pad.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(args):
    global perf_data
    perf_data = PERF_DATA(len(args))

    Gst.init(None)
    platform_info = PlatformInfo()

    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    preprocess = Gst.ElementFactory.make("nvdspreprocess", "preprocess")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = Gst.ElementFactory.make("fakesink", "fakesink")

    for element in (streammux, preprocess, pgie, tiler, nvvidconv, nvosd, sink):
        pipeline.add(element)

    number_sources = len(args)
    for i, uri in enumerate(args):
        source_bin = create_source_bin(i, uri)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        if srcpad and sinkpad:
            srcpad.link(sinkpad)

    streammux.set_property("width", MUXER_OUTPUT_WIDTH)
    streammux.set_property("height", MUXER_OUTPUT_HEIGHT)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    preprocess.set_property("config-file-path", "config_preprocess.txt")
    pgie.set_property("config-file-path", "dstest1_pgie_config.txt")
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("sync", 0)

    streammux.link(preprocess)
    preprocess.link(pgie)
    pgie.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    pgie_src_pad = pgie.get_static_pad("src")
    if pgie_src_pad:
        pgie_src_pad.add_probe(Gst.PadProbeType.BUFFER, pgie_src_pad_buffer_probe, 0)

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
