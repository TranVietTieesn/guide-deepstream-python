#!/usr/bin/env python3
"""
Lesson 04 reference: RTSP in, RTSP out.
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
    caps = decoder_src_pad.get_current_caps() or decoder_src_pad.query_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)
    if gstname.find("video") != -1 and features.contains("memory:NVMM"):
        bin_ghost_pad = source_bin.get_static_pad("src")
        bin_ghost_pad.set_target(decoder_src_pad)


def decodebin_child_added(child_proxy, Object, name, user_data):
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)
    if ts_from_rtsp and name.find("source") != -1:
        import pyds

        pyds.configure_source_for_ntp_sync(hash(Object))


def create_source_bin(index, uri):
    bin_name = "source-bin-%02d" % index
    nbin = Gst.Bin.new(bin_name)
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)
    Gst.Bin.add(nbin, uri_decode_bin)
    nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    return nbin


def create_rtsp_server(port, codec):
    server = GstRtspServer.RTSPServer.new()
    server.props.service = str(port)
    server.attach(None)
    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch(
        '( udpsrc name=pay0 port=5400 buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96" )'
        % codec
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-test", factory)
    return server


def main(args):
    platform_info = PlatformInfo()
    number_sources = len(args)
    Gst.init(None)
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
        streammux.set_property("attach-sys-ts", 0)
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
    if platform_info.is_integrated_gpu():
        encoder.set_property("preset-level", 1)
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

    rtsp_server = create_rtsp_server(8554, "H264")
    _ = rtsp_server

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
