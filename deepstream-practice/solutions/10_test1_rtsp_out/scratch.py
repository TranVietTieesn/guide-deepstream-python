#!/usr/bin/env python3
"""
Lesson 03 reference: RTSP out.
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
gi.require_version("GstRtspServer", "1.0")
from gi.repository import GLib, Gst, GstRtspServer

import pyds

from common.bus_call import bus_call
from common.platform_info import PlatformInfo


PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = "pgie_trafficcamnet.txt"


def osd_sink_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
    num_rects = 0

    obj_counter = {
        PGIE_CLASS_ID_VEHICLE: 0,
        PGIE_CLASS_ID_PERSON: 0,
        PGIE_CLASS_ID_BICYCLE: 0,
        PGIE_CLASS_ID_ROADSIGN: 0,
    }

    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number = frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta
        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            obj_meta.rect_params.border_color.set(0.0, 0.0, 1.0, 0.8)
            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]
        py_nvosd_text_params.display_text = (
            "Frame Number={} Number of Objects={} Vehicle_count={} Person_count={}".format(
                frame_number,
                num_rects,
                obj_counter[PGIE_CLASS_ID_VEHICLE],
                obj_counter[PGIE_CLASS_ID_PERSON],
            )
        )
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
        print(pyds.get_string(py_nvosd_text_params.display_text))
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def on_message(bus, message, loop):
    return bus_call(bus, message, loop)


def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong tao duoc element: {factory_name}")
    return element


def create_sink(platform_info):
    if platform_info.is_integrated_gpu():
        return make_element("nv3dsink", "video-output")
    if platform_info.is_platform_aarch64():
        return make_element("nv3dsink", "video-output")
    return make_element("nveglglessink", "video-output")


def create_rtsp_server(port, codec):
    server = GstRtspServer.RTSPServer.new()
    server.props.service = str(port)
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    codec_upper = codec.upper()
    if codec_upper == "H265":
        depay = "rtph265depay"
        pay = "rtph265pay"
    else:
        depay = "rtph264depay"
        pay = "rtph264pay"

    # In RTSP factory launch syntax, "pay0" should be an RTP payloader element.
    # Using udpsrc as pay0 can trigger warnings like:
    # "GstUDPSrc has no property named 'pt'".
    factory.set_launch(
        '( udpsrc port=5400 buffer-size=524288 caps="application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96" ! rtpjitterbuffer ! %s ! %s name=pay0 pt=96 config-interval=1 )'
        % (codec_upper, depay, pay)
    )
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-test", factory)
    return server


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1
    if not os.path.exists(PGIE_CONFIG_PATH):
        print(f"Config not found: {PGIE_CONFIG_PATH}", file=sys.stderr)
        return 1

    Gst.init(None)
    platform_info = PlatformInfo()

    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    print("Creating Source \n ")
    source = make_element("filesrc", "file-source")
    print("Creating H264Parser \n")
    parser = make_element("h264parse", "h264-parser")
    print("Creating Decoder \n")
    decoder = make_element("nvv4l2decoder", "nvv4l2-decoder")
    streammux = make_element("nvstreammux", "Stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "convertor")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    nvvidconv_postosd = make_element("nvvideoconvert", "convertor_postosd")
    caps = make_element("capsfilter", "filter")
    encoder = make_element("nvv4l2h264enc", "encoder")
        

    rtppay = make_element("rtph264pay", "rtppay")
    sink = make_element("udpsink", "udpsink")

    source.set_property("location", input_path)
    if os.environ.get("USE_NEW_NVSTREAMMUX") != "yes":
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    streammux.set_property("batch-size", 1)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    nvvidconv_postosd.set_property("nvbuf-memory-type", 0)
    caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"))
    encoder.set_property("bitrate", 4000000)
    encoder.set_property("insert-sps-pps", 1)
    if platform_info.is_integrated_gpu():
        print("")
        encoder.set_property("preset-level", 1)
    # Loopback is more reliable than multicast for local RTSP testing.
    sink.set_property("host", "127.0.0.1")
    sink.set_property("port", 5400)
    sink.set_property("async", True)
    sink.set_property("sync", True)

    print("Adding elements to TPipeline \n")
    for element in (
        source,
        parser,
        decoder,
        streammux,
        pgie,
        nvvidconv,
        nvosd,
        nvvidconv_postosd,
        caps,
        encoder,
        rtppay,
        sink,
    ):
        pipeline.add(element)

    print("Linking elements in the Pipeline \n")
    if not source.link(parser):
        raise RuntimeError("Khong link duoc filesrc -> h264parse")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc h264parse -> nvv4l2decoder")

    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Unable to get the sink pad of streammux")
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Unable to get source pad of decoder")
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Unable to link decoder.src -> streammux.sink_0")

    if not streammux.link(pgie):
        raise RuntimeError("Unable to link streammux -> pgie")
    if not pgie.link(nvvidconv):
        raise RuntimeError("Unable to link pgie -> nvvidconv")
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Unable to link nvvidconv -> nvosd")
    if not nvosd.link(nvvidconv_postosd):
        raise RuntimeError("Unable to link nvosd -> nvvidconv_postosd")
    if not nvvidconv_postosd.link(caps):
        raise RuntimeError("Unable to link nvvidconv_postosd -> caps")
    if not caps.link(encoder):
        raise RuntimeError("Unable to link caps -> encoder")
    if not encoder.link(rtppay):
        raise RuntimeError("Unable to link encoder -> rtppay")
    if not rtppay.link(sink):
        raise RuntimeError("Unable to link rtppay -> udpsink")

    server = create_rtsp_server(8554, "H264")
    _ = server

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        raise RuntimeError("Unable to get sink pad of nvosd")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

