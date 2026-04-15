#!/usr/bin/env python3
"""
Lesson 04 starter: RTSP in, RTSP out.
"""

import argparse
import math
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst, GstRtspServer

from common.bus_call import bus_call
from common.platform_info import PlatformInfo


ts_from_rtsp = False
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720


def cb_newpad(decodebin, decoder_src_pad, data):
    # TODO 1: Bat video NVMM pad va link vao source bin.
    _ = decodebin
    _ = decoder_src_pad
    _ = data


def decodebin_child_added(child_proxy, Object, name, user_data):
    # TODO 2: Neu can, set source NTP sync cho RTSP input.
    _ = child_proxy
    _ = Object
    _ = name
    _ = user_data


def create_source_bin(index, uri):
    # TODO 3: Tao source bin cho RTSP source.
    _ = index
    _ = uri
    raise NotImplementedError("TODO: implement create_source_bin()")


def create_rtsp_server(port, codec):
    # TODO 4: Tao RTSP server output.
    _ = port
    _ = codec
    raise NotImplementedError("TODO: implement create_rtsp_server()")


def main(args):
    Gst.init(None)
    platform_info = PlatformInfo()
    number_sources = len(args)
    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    caps = Gst.ElementFactory.make("capsfilter", "filter")
    encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
    rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    for element in (
        streammux,
        pgie,
        tiler,
        nvvidconv,
        nvosd,
        nvvidconv_postosd,
        caps,
        encoder,
        rtppay,
        sink,
    ):
        pipeline.add(element)

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
    pgie.set_property("config-file-path", "dstest1_pgie_config.txt")
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    encoder.set_property("bitrate", 4000000)
    encoder.set_property("insert-sps-pps", 1)
    sink.set_property("host", "224.224.255.255")
    sink.set_property("port", 5400)
    sink.set_property("async", False)
    sink.set_property("sync", 1)
    caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"))

    streammux.link(pgie)
    pgie.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(nvvidconv_postosd)
    nvvidconv_postosd.link(caps)
    caps.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    create_rtsp_server(8554, "H264")

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
