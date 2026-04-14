#!/usr/bin/env python3
"""
Lesson 05 starter: probe batch meta.

Hay doc theo thu tu:
1. `01_guide.md`
2. `02_coding_guide.md`
3. file nay
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.platform_info import PlatformInfo

MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = "dstest1_pgie_config.txt"


def on_message(bus, message, loop):
    _ = bus
    # TODO 1: Xu ly `EOS` va `ERROR`.
    message_type = message.type
    if message_type == Gst.MessageType.EOS:
        print("Da doc het pipeline")
        loop.quit()
    elif message_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    # TODO 2: Viet helper tao element.
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Khong khoi tao duoc element: {factory_name}")
    return element


def create_sink(platform_info):
    # TODO 3: Chon sink theo `PlatformInfo`.
    if platform_info.is_integrated_gpu():
        print("GPU integrated")
        return make_element("nv3dsink", "nv3d-sink")

    if platform_info.is_platform_aarch64():
        print("GPU aarch64")
        return make_element("nv3dsink", "nv3d-sink")

    print("using default platform display nveglglessink")
    return make_element("nveglglessink", "nvvideo-renderer")

def osd_sink_pad_buffer_probe(pad, info, user_data):
    # TODO 3: Doc `gst_buffer`, `batch_meta`, `frame_meta`, `obj_meta` va in thong tin.
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Khong the lay GstBuffer")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        print("Khong the lay NvDsBatchMeta")
        return Gst.PadProbeReturn.OK

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break
    
        print(
            f"Frame={frame_meta.frame_num} "
            f"pad_index={frame_meta.pad_index} "
            f"objects={frame_meta.num_obj_meta}"
        )

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            rect = obj_meta.rect_params
            print(
                "  "
                f"class_id={obj_meta.class_id} "
                f"confidence={obj_meta.confidence:.3f} "
                f"bbox=({rect.left:.1f},{rect.top:.1f},{rect.width:.1f},{rect.height:.1f})"
            )

            try: 
                l_obj = l_obj.next
            except StopIteration:
                break

        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK

def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <path-to-h264-file>", file=sys.stderr)
        return 1

    input_path = args[1]
    if not os.path.exists(input_path):
        print(f"Input not found: {input_path}", file=sys.stderr)
        return 1

    Gst.init(None)
    platform_info = PlatformInfo()
    # TODO 4: Tao pipeline va cac element.
    pipeline = Gst.Pipeline.new("lesson-05-pipeline")
    source = make_element("filesrc", "file-src")
    parser = make_element("h264parse", "parser")
    decoder = make_element("nvv4l2decoder", "decoder")
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "infer")
    nvvidconv = make_element("nvvideoconvert", "vidconv")
    nvosd = make_element("nvdsosd", "osd")
    # sink = make_element("fakesink", "fake-sink")
    sink = create_sink(platform_info)

    # TODO 5: Set property cho source, streammux, pgie, sink.
    source.set_property("location", input_path)
    # sink.set_property("sync", False)
    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    # TODO 6: Add element vao pipeline.
    pipeline.add(source)
    pipeline.add(parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)
    # TODO 7: Link den decoder.
    if not source.link(parser):
        raise RuntimeError("Khong link duoc source voi parser")
    if not parser.link(decoder):
        raise RuntimeError("Khong link duoc parser voi decoder")
    # TODO 8: Link vao `nvstreammux.sink_0`.
    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        raise RuntimeError("Khong xin duoc request pad sink0 tu streammux")
    
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        raise RuntimeError("Khong lay duoc pad tu deocder")

    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Khong link duoc decoder.src voi streammux.sink0")
    # TODO 9: Link downstream tu muxer den sink.
    if not streammux.link(pgie):
        raise RuntimeError("Khong link duoc streammux voi PGIE")
    
    if not pgie.link(nvvidconv):
        raise RuntimeError("Khong link duoc pgie voi video convert")
    
    if not nvvidconv.link(nvosd):
        raise RuntimeError("Khong link duoc nvvidconv voi nvosd")

    if not nvosd.link(sink):
        raise RuntimeError("Khong link duoc nvosd voi fake sink")

    # TODO 10: Lay `nvosd.sink` va gan probe vao do.
    osd_sink_pad = nvosd.get_static_pad("sink")
    osd_sink_pad.add_probe(
        Gst.PadProbeType.BUFFER,
        osd_sink_pad_buffer_probe,
        None
    )

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running metadata probe lesson...")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
