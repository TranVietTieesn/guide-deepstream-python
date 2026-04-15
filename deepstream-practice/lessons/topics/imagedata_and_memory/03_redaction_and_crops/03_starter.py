#!/usr/bin/env python3
"""
Lesson 03 starter: redaction and crops on multistream.
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

PGIE_CLASS_ID_PERSON = 0
PGIE_CLASS_ID_BAG = 1
PGIE_CLASS_ID_FACE = 2
MAX_DISPLAY_LEN = 64
MUXER_OUTPUT_WIDTH = 720
MUXER_OUTPUT_HEIGHT = 576
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 720
TILED_OUTPUT_HEIGHT = 576
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
pgie_classes_str = ["Person", "Bag", "Face"]
MIN_CONFIDENCE = 0.3
MAX_CONFIDENCE = 0.4


def tiler_sink_pad_buffer_probe(pad, info, u_data):
    # TODO 1: Redaction va crop face image.
    _ = pad
    _ = info
    _ = u_data
    return Gst.PadProbeReturn.OK


def crop_object(image, obj_meta):
    # TODO 2: Cat theo rect params.
    _ = image
    _ = obj_meta
    return image


def cb_newpad(decodebin, decoder_src_pad, data):
    # TODO 3: Bat dynamic pad va ghost pad.
    _ = decodebin
    _ = decoder_src_pad
    _ = data


def decodebin_child_added(child_proxy, Object, name, user_data):
    # TODO 4: Set drop-on-latency / cudadec-memtype neu can.
    _ = child_proxy
    _ = Object
    _ = name
    _ = user_data


def create_source_bin(index, uri):
    # TODO 5: Tao source bin.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def main(uri_inputs):
    number_sources = len(uri_inputs)
    global perf_data
    perf_data = PERF_DATA(number_sources)

    global folder_name
    folder_name = "out_crops"
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
    pgie.set_property("config-file-path", "config_infer_primary_peoplenet.txt")
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
        os.mkdir(folder_name + "/stream_" + str(i))
        frame_count["stream_" + str(i)] = 0
        saved_count["stream_" + str(i)] = 0
        uri_name = uri_inputs[i]
        if uri_name.find("rtsp://") == 0:
            is_live = True
        source_bin = create_source_bin(i, uri_name)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        srcpad.link(sinkpad)

    if is_live:
        streammux.set_property("live-source", 1)

    if not platform_info.is_integrated_gpu():
        mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
        streammux.set_property("nvbuf-memory-type", mem_type)
        nvvidconv.set_property("nvbuf-memory-type", mem_type)
        nvvidconv1.set_property("nvbuf-memory-type", mem_type)
        tiler.set_property("nvbuf-memory-type", mem_type)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True)
    args = parser.parse_args()
    return args.input


if __name__ == "__main__":
    sys.exit(main(parse_args()))
