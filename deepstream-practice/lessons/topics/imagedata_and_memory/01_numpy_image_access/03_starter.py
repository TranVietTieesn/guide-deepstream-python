#!/usr/bin/env python3
"""
Lesson 01 starter: NumPy image access on multistream.
"""

import argparse
import math
import os
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import cv2
import numpy as np
import pyds

from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.platform_info import PlatformInfo

perf_data = None
frame_count = {}
saved_count = {}
folder_name = ""
platform_info = None

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 1920
TILED_OUTPUT_HEIGHT = 1080
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "RoadSign"]
MIN_CONFIDENCE = 0.3
MAX_CONFIDENCE = 0.4


def tiler_sink_pad_buffer_probe(pad, info, u_data):
    # TODO 1: Doc batch meta, access RGBA image va save copy.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def draw_bounding_boxes(image, obj_meta, confidence):
    # TODO 2: Ve bbox len image copy neu can.
    _ = image
    _ = obj_meta
    _ = confidence
    return image


def cb_newpad(decodebin, decoder_src_pad, data):
    # TODO 3: Bat dynamic pad va ghost pad.
    _ = decodebin
    _ = decoder_src_pad
    _ = data


def decodebin_child_added(child_proxy, Object, name, user_data):
    # TODO 4: Set drop-on-latency / decoder memtype neu can.
    _ = child_proxy
    _ = Object
    _ = name
    _ = user_data


def create_source_bin(index, uri):
    # TODO 5: Tao source bin.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(args):
    global perf_data
    perf_data = PERF_DATA(len(args) - 2)
    number_sources = len(args) - 2

    global folder_name
    folder_name = args[-1]
    if os.path.exists(folder_name):
        sys.stderr.write(
            "The output folder %s already exists. Please remove it first.\n"
            % folder_name
        )
        sys.exit(1)

    os.mkdir(folder_name)
    global platform_info
    platform_info = PlatformInfo()

    Gst.init(None)
    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
    filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = (
        Gst.ElementFactory.make("nv3dsink", "nv3d-sink")
        if platform_info.is_platform_aarch64() or platform_info.is_integrated_gpu()
        else Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    )

    streammux.set_property("width", MUXER_OUTPUT_WIDTH)
    streammux.set_property("height", MUXER_OUTPUT_HEIGHT)
    streammux.set_property("batch-size", number_sources)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", "dstest_imagedata_config.txt")
    filter1.set_property(
        "caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
    )
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("sync", 0)
    sink.set_property("qos", 0)

    for element in (
        streammux,
        pgie,
        nvvidconv1,
        filter1,
        tiler,
        nvvidconv,
        nvosd,
        sink,
    ):
        pipeline.add(element)

    is_live = False
    for i in range(number_sources):
        uri_name = args[i + 1]
        if uri_name.find("rtsp://") == 0:
            is_live = True
        source_bin = create_source_bin(i, uri_name)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        srcpad.link(sinkpad)

    if is_live:
        streammux.set_property("live-source", 1)

    streammux.link(pgie)
    pgie.link(nvvidconv1)
    nvvidconv1.link(filter1)
    filter1.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    tiler_sink_pad = tiler.get_static_pad("sink")
    tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, tiler_sink_pad_buffer_probe, 0)
    GLib.timeout_add(5000, perf_data.perf_print_callback)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


def parse_args():
    parser = argparse.ArgumentParser(
        prog="deepstream_imagedata-multistream.py",
        description="deepstream_imagedata-multistream takes multiple URI streams as input",
    )
    parser.add_argument("-i", "--input", nargs="+", required=True)
    parser.add_argument("output_folder")
    return parser.parse_args().input + [parser.parse_args().output_folder]


if __name__ == "__main__":
    sys.exit(main(parse_args()))
