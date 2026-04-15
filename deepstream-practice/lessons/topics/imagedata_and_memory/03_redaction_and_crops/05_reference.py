#!/usr/bin/env python3
"""
Lesson 03 reference: redaction and crops on multistream.
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
        l_obj = frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        is_first_obj = True
        save_image = False
        obj_counter = {
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BAG: 0,
            PGIE_CLASS_ID_FACE: 0,
        }
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1

            if obj_meta.class_id == PGIE_CLASS_ID_FACE:
                obj_meta.rect_params.border_width = 0
                obj_meta.rect_params.has_bg_color = 1
                obj_meta.rect_params.bg_color.red = 0.0
                obj_meta.rect_params.bg_color.green = 0.0
                obj_meta.rect_params.bg_color.blue = 0.0
                obj_meta.rect_params.bg_color.alpha = 1.0
            elif obj_meta.class_id == PGIE_CLASS_ID_PERSON:
                obj_meta.rect_params.border_width = 0
                obj_meta.rect_params.has_bg_color = 1
                obj_meta.rect_params.bg_color.red = 0.0
                obj_meta.rect_params.bg_color.green = 0.0
                obj_meta.rect_params.bg_color.blue = 0.0
                obj_meta.rect_params.bg_color.alpha = 0.5

            if (
                saved_count["stream_{}".format(frame_meta.pad_index)] % 10 == 0
                and obj_meta.class_id == PGIE_CLASS_ID_FACE
            ):
                if is_first_obj:
                    is_first_obj = False
                    n_frame = pyds.get_nvds_buf_surface(
                        hash(gst_buffer), frame_meta.batch_id
                    )
                    n_frame = crop_object(n_frame, obj_meta)
                    frame_copy = np.array(n_frame, copy=True, order="C")
                    frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_RGBA2BGRA)
                    if platform_info.is_integrated_gpu():
                        pyds.unmap_nvds_buf_surface(
                            hash(gst_buffer), frame_meta.batch_id
                        )
                save_image = True

            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        print(
            "Frame Number=",
            frame_number,
            "Number of Objects=",
            num_rects,
            "Face_count=",
            obj_counter[PGIE_CLASS_ID_FACE],
            "Person_count=",
            obj_counter[PGIE_CLASS_ID_PERSON],
        )
        stream_index = "stream{0}".format(frame_meta.pad_index)
        global perf_data
        perf_data.update_fps(stream_index)
        if save_image:
            img_path = "{}/stream_{}/frame_{}.jpg".format(
                folder_name, frame_meta.pad_index, frame_number
            )
            cv2.imwrite(img_path, frame_copy)
        saved_count["stream_{}".format(frame_meta.pad_index)] += 1
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def crop_object(image, obj_meta):
    rect_params = obj_meta.rect_params
    top = int(rect_params.top)
    left = int(rect_params.left)
    width = int(rect_params.width)
    height = int(rect_params.height)
    crop_img = image[top : top + height, left : left + width]
    return crop_img


def cb_newpad(decodebin, decoder_src_pad, data):
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)
    if gstname.find("video") != -1:
        if features.contains("memory:NVMM"):
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write(
                    "Failed to link decoder src pad to source bin ghost pad\n"
                )
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")


def decodebin_child_added(child_proxy, Object, name, user_data):
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)
    if not platform_info.is_integrated_gpu() and name.find("nvv4l2decoder") != -1:
        Object.set_property("cudadec-memtype", 2)


def create_source_bin(index, uri):
    bin_name = "source-bin-%02d" % index
    nbin = Gst.Bin.new(bin_name)
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
