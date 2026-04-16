#!/usr/bin/env python3
"""
Lesson 02 reference: nvdsanalytics rules.
"""

import configparser
import math
import sys

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.FPS import PERF_DATA
from common.bus_call import bus_call
from common.platform_info import PlatformInfo

perf_data = None
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 33000
TILED_OUTPUT_WIDTH = 1280
TILED_OUTPUT_HEIGHT = 720
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "RoadSign"]
OSD_PROCESS_MODE = 0
OSD_DISPLAY_TEXT = 1


def nvanalytics_src_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
    num_rects = 0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    if not batch_meta:
        return Gst.PadProbeReturn.OK
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_ROADSIGN: 0,
        }
        print("#" * 50)
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            l_user_meta = obj_meta.obj_user_meta_list
            while l_user_meta is not None:
                try:
                    user_meta = pyds.NvDsUserMeta.cast(l_user_meta.data)
                    if (
                        user_meta.base_meta.meta_type
                        == pyds.NvDsMetaType.NVDS_OBJ_META_NVDSANALYTICS
                    ):
                        user_meta_data = pyds.NvDsAnalyticsObjInfo.cast(
                            user_meta.user_meta_data
                        )
                        if user_meta_data.dirStatus:
                            print(
                                "Object {0} moving in direction: {1}".format(
                                    obj_meta.object_id, user_meta_data.dirStatus
                                )
                            )
                        if user_meta_data.lcStatus:
                            print(
                                "Object {0} line crossing status: {1}".format(
                                    obj_meta.object_id, user_meta_data.lcStatus
                                )
                            )
                        if user_meta_data.ocStatus:
                            print(
                                "Object {0} overcrowding status: {1}".format(
                                    obj_meta.object_id, user_meta_data.ocStatus
                                )
                            )
                        if user_meta_data.roiStatus:
                            print(
                                "Object {0} roi status: {1}".format(
                                    obj_meta.object_id, user_meta_data.roiStatus
                                )
                            )
                except StopIteration:
                    break
                try:
                    l_user_meta = l_user_meta.next
                except StopIteration:
                    break
            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        l_user = frame_meta.frame_user_meta_list
        while l_user is not None:
            try:
                user_meta = pyds.NvDsUserMeta.cast(l_user.data)
                if (
                    user_meta.base_meta.meta_type
                    == pyds.NvDsMetaType.NVDS_FRAME_META_NVDSANALYTICS
                ):
                    user_meta_data = pyds.NvDsAnalyticsFrameMeta.cast(
                        user_meta.user_meta_data
                    )
                    if user_meta_data.objInROIcnt:
                        print("Objs in ROI: {0}".format(user_meta_data.objInROIcnt))
                    if user_meta_data.objLCCumCnt:
                        print(
                            "Linecrossing Cumulative: {0}".format(
                                user_meta_data.objLCCumCnt
                            )
                        )
                    if user_meta_data.objLCCurrCnt:
                        print(
                            "Linecrossing Current Frame: {0}".format(
                                user_meta_data.objLCCurrCnt
                            )
                        )
                    if user_meta_data.ocStatus:
                        print("Overcrowding status: {0}".format(user_meta_data.ocStatus))
            except StopIteration:
                break
            try:
                l_user = l_user.next
            except StopIteration:
                break

        print(
            "Frame Number=",
            frame_number,
            "stream id=",
            frame_meta.pad_index,
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
        try:
            l_frame = l_frame.next
        except StopIteration:
            break
        print("#" * 50)

    return Gst.PadProbeReturn.OK


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
    if not PlatformInfo().is_integrated_gpu() and name.find("nvv4l2decoder") != -1:
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


def main(args):
    if len(args) < 2:
        sys.stderr.write("usage: %s <uri1> [uri2] ... [uriN]\n" % args[0])
        sys.exit(1)

    global perf_data
    perf_data = PERF_DATA(len(args) - 1)
    number_sources = len(args) - 1
    platform_info = PlatformInfo()

    Gst.init(None)
    pipeline = Gst.Pipeline()
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    nvanalytics = Gst.ElementFactory.make("nvdsanalytics", "analytics")
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
    pgie.set_property("config-file-path", "dsnvanalytics_pgie_config.txt")
    nvanalytics.set_property("config-file", "config_nvdsanalytics.txt")
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0 * number_sources) / tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    sink.set_property("qos", 0)

    config = configparser.ConfigParser()
    config.read("dsnvanalytics_tracker_config.txt")
    for key in config["tracker"]:
        if key == "tracker-width":
            tracker.set_property("tracker-width", config.getint("tracker", key))
        if key == "tracker-height":
            tracker.set_property("tracker-height", config.getint("tracker", key))
        if key == "gpu-id":
            tracker.set_property("gpu_id", config.getint("tracker", key))
        if key == "ll-lib-file":
            tracker.set_property("ll-lib-file", config.get("tracker", key))
        if key == "ll-config-file":
            tracker.set_property("ll-config-file", config.get("tracker", key))

    for element in (
        streammux,
        pgie,
        tracker,
        nvanalytics,
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
        if not source_bin:
            sys.stderr.write(" Unable to create source bin \n")
            return 1
        pipeline.add(source_bin)
        sinkpad = streammux.request_pad_simple("sink_%u" % i)
        srcpad = source_bin.get_static_pad("src")
        srcpad.link(sinkpad)

    if is_live:
        streammux.set_property("live-source", 1)

    streammux.link(pgie)
    pgie.link(tracker)
    tracker.link(nvanalytics)
    nvanalytics.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    nvanalytics_src_pad = nvanalytics.get_static_pad("src")
    nvanalytics_src_pad.add_probe(
        Gst.PadProbeType.BUFFER, nvanalytics_src_pad_buffer_probe, 0
    )
    GLib.timeout_add(5000, perf_data.perf_print_callback)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
