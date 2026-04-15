#!/usr/bin/env python3
"""
Lesson 02 reference: preprocess before infer.
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
OSD_DISPLAY_TEXT = 0
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "RoadSign"]


def pgie_src_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
    num_rects = 0
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
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_ROADSIGN: 0,
        }
        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        print(
            "Frame Number=",
            frame_number,
            "Number of Objects=",
            num_rects,
            "Vehicle_count=",
            obj_counter[PGIE_CLASS_ID_VEHICLE],
            "Person_count=",
            obj_counter[PGIE_CLASS_ID_PERSON],
        )
        stream_index = "stream{0}".format(frame_meta.pad_index)
        global perf_data
        perf_data.update_fps(stream_index)
        l_user_meta = batch_meta.batch_user_meta_list
        while l_user_meta is not None:
            try:
                user_meta = pyds.NvDsUserMeta.cast(l_user_meta.data)
            except StopIteration:
                break
            if user_meta.base_meta.meta_type == pyds.NVDS_PREPROCESS_BATCH_META:
                preprocess_batchmeta = pyds.GstNvDsPreProcessBatchMeta.cast(
                    user_meta.user_meta_data
                )
                roi_cnt = 0
                for roi_meta in preprocess_batchmeta.roi_vector:
                    display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
                    display_meta.num_labels = 1
                    txt_params = display_meta.text_params[0]
                    txt_params.display_text = f"Roi:{roi_cnt}"
                    txt_params.x_offset = int(roi_meta.roi.left)
                    txt_params.y_offset = int(roi_meta.roi.top)
                    txt_params.font_params.font_name = "Serif"
                    txt_params.font_params.font_size = 10
                    txt_params.font_params.font_color.red = 1.0
                    txt_params.font_params.font_color.green = 1.0
                    txt_params.font_params.font_color.blue = 1.0
                    txt_params.font_params.font_color.alpha = 1.0
                    txt_params.set_bg_clr = 1
                    txt_params.text_bg_clr.red = 0.0
                    txt_params.text_bg_clr.green = 0.0
                    txt_params.text_bg_clr.blue = 0.0
                    txt_params.text_bg_clr.alpha = 0.5
                    pyds.nvds_add_display_meta_to_frame(roi_meta.frame_meta, display_meta)
                    print(
                        f"frame {roi_meta.frame_meta.frame_num} src {roi_meta.frame_meta.source_id} roi {roi_cnt}"
                    )
                    roi_cnt += 1
            try:
                l_user_meta = l_user_meta.next
            except StopIteration:
                break
        try:
            l_frame = l_frame.next
        except StopIteration:
            break
    return Gst.PadProbeReturn.OK


def cb_newpad(decodebin, decoder_src_pad, data):
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)
    if gstname.find("video") != -1 and features.contains("memory:NVMM"):
        bin_ghost_pad = source_bin.get_static_pad("src")
        if not bin_ghost_pad.set_target(decoder_src_pad):
            sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")


def decodebin_child_added(child_proxy, Object, name, user_data):
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)


def create_source_bin(index, uri):
    bin_name = "source-bin-%02d" % index
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin


def main(args):
    global perf_data
    perf_data = PERF_DATA(len(args))
    number_sources = len(args)
    platform_info = PlatformInfo()
    Gst.init(None)

    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    preprocess = Gst.ElementFactory.make("nvdspreprocess", "preprocess")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = Gst.ElementFactory.make("fakesink", "fakesink")

    pipeline.add(streammux)
    pipeline.add(preprocess)
    pipeline.add(pgie)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)

    for i, uri in enumerate(args):
        source_bin = create_source_bin(i, uri)
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
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
    except:
        pass
    pipeline.set_state(Gst.State.NULL)
    return 0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", nargs="+", required=True)
    return parser.parse_args().input


if __name__ == "__main__":
    sys.exit(main(parse_args()))
