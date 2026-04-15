#!/usr/bin/env python3
"""
Exercise 09: RTSP source walkthrough.

Pipeline ý tưởng:
    uridecodebin(source-bin) -> nvstreammux -> nvinfer -> nvvideoconvert
    -> nvdsosd -> fakesink

Mục tiêu:
- Hiểu vì sao RTSP thường dùng `uridecodebin` / source bin.
- Hiểu sự khác nhau giữa file source và live source.
- Hiểu vì sao `streammux.set_property("live-source", True)` quan trọng.

Cách chạy:
    python3 archive/exercises/09_rtsp_source_walkthrough.py rtsp://user:pass@host:554/path
"""

import os
import sys

sys.path.append(
    "/home/vtea/opt/nvidia/deepstream/deepstream-9.0/sources/deepstream_python_apps/apps"
)

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst


MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "07_config_variants", "pgie_trafficcamnet.txt"
)


def on_message(bus, message, loop):
    if message.type == Gst.MessageType.EOS:
        print("EOS: RTSP walkthrough xong.")
        loop.quit()
    elif message.type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ERROR: {err}")
        if debug:
            print(f"DEBUG: {debug}")
        loop.quit()
    return True


def make_element(factory_name, name):
    element = Gst.ElementFactory.make(factory_name, name)
    if not element:
        raise RuntimeError(f"Không tạo được element: {factory_name}")
    return element


def cb_newpad(decodebin, decoder_src_pad, source_bin):
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps(None)
    if not caps:
        print("Không lấy được caps từ decodebin.")
        return

    caps_features = caps.get_features(0)
    if not caps_features.contains("memory:NVMM"):
        print("Bỏ qua pad không đúng NVMM, cần xem lại source / decode path.")
        return

    ghost_pad = source_bin.get_static_pad("src")
    if ghost_pad and not ghost_pad.set_target(decoder_src_pad):
        print("Không gán được ghost pad target.")


def create_source_bin(index, uri):
    bin_name = f"source-bin-{index:02d}"
    source_bin = Gst.Bin.new(bin_name)
    if not source_bin:
        raise RuntimeError("Không tạo được source bin")

    uri_decode_bin = make_element("uridecodebin", f"uri-decode-bin-{index}")
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, source_bin)

    source_bin.add(uri_decode_bin)
    ghost_pad = Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC)
    if not ghost_pad:
        raise RuntimeError("Không tạo được ghost pad cho source bin")
    source_bin.add_pad(ghost_pad)

    return source_bin


def main(args):
    if len(args) != 2:
        print(f"usage: {args[0]} <rtsp-uri>", file=sys.stderr)
        return 1

    uri = args[1]
    if not uri.startswith("rtsp://"):
        print("Bài này cho RTSP URI, ví dụ rtsp://...", file=sys.stderr)
        return 1

    Gst.init(None)

    pipeline = Gst.Pipeline.new("exercise-09-pipeline")
    source_bin = create_source_bin(0, uri)
    streammux = make_element("nvstreammux", "stream-muxer")
    pgie = make_element("nvinfer", "primary-inference")
    nvvidconv = make_element("nvvideoconvert", "video-convert")
    nvosd = make_element("nvdsosd", "onscreendisplay")
    sink = make_element("fakesink", "fake-sink")

    streammux.set_property("batch-size", 1)
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    streammux.set_property("live-source", True)
    pgie.set_property("config-file-path", PGIE_CONFIG_PATH)
    sink.set_property("sync", False)

    for element in (source_bin, streammux, pgie, nvvidconv, nvosd, sink):
        pipeline.add(element)

    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = source_bin.get_static_pad("src")
    if not sinkpad or not srcpad:
        raise RuntimeError("Không lấy được pad để nối source bin vào nvstreammux")
    if srcpad.link(sinkpad) != Gst.PadLinkReturn.OK:
        raise RuntimeError("Không link được source bin -> nvstreammux.sink_0")

    for upstream, downstream, label in (
        (streammux, pgie, "nvstreammux -> nvinfer"),
        (pgie, nvvidconv, "nvinfer -> nvvideoconvert"),
        (nvvidconv, nvosd, "nvvideoconvert -> nvdsosd"),
        (nvosd, sink, "nvdsosd -> fakesink"),
    ):
        if not upstream.link(downstream):
            raise RuntimeError(f"Không link được {label}")

    bus = pipeline.get_bus()
    loop = GLib.MainLoop()
    bus.add_signal_watch()
    bus.connect("message", on_message, loop)

    print("Running RTSP walkthrough...")
    print("URI =", uri)
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except KeyboardInterrupt:
        print("Stop by user.")
    finally:
        pipeline.set_state(Gst.State.NULL)

    # TODO: Thêm `latency` cho `rtspsrc` nếu cần truy cập sâu hơn qua source bin.
    # TODO: Đổi `fakesink` thành sink hiển thị nếu muốn xem live output.
    # TODO: Thử bỏ `live-source=True` và quan sát vấn đề timestamp / batching.
    #
    # SELF-CHECK:
    # - Tại sao bài RTSP không còn dùng `filesrc -> h264parse` trực tiếp?
    # - Ghost pad của source bin giải quyết bài toán gì?
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
