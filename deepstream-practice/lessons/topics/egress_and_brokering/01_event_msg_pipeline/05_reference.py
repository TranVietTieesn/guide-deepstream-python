#!/usr/bin/env python3
"""
Lesson 01 reference: event message pipeline.
"""

import sys
from optparse import OptionParser

sys.path.append("../")

import gi

gi.require_version("Gst", "1.0")
from gi.repository import GLib, Gst

import pyds

from common.bus_call import bus_call
from common.platform_info import PlatformInfo
from common.utils import long_to_uint64

MAX_DISPLAY_LEN = 64
MAX_TIME_STAMP_LEN = 32
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1920
MUXER_OUTPUT_HEIGHT = 1080
MUXER_BATCH_TIMEOUT_USEC = 33000
PGIE_CONFIG_FILE = "dstest4_pgie_config.txt"
MSCONV_CONFIG_FILE = "dstest4_msgconv_config.txt"
input_file = None
schema_type = 0
proto_lib = None
conn_str = "localhost;2181;testTopic"
cfg_file = None
topic = None
no_display = False
pgie_classes_str = ["Vehicle", "TwoWheeler", "Person", "Roadsign"]


def generate_vehicle_meta(data):
    obj = pyds.NvDsVehicleObject.cast(data)
    obj.type = "sedan"
    obj.color = "blue"
    obj.make = "Bugatti"
    obj.model = "M"
    obj.license = "XX1234"
    obj.region = "CA"
    return obj


def generate_person_meta(data):
    obj = pyds.NvDsPersonObject.cast(data)
    obj.age = 45
    obj.cap = "none"
    obj.hair = "black"
    obj.gender = "male"
    obj.apparel = "formal"
    return obj


def generate_event_msg_meta(data, class_id):
    meta = pyds.NvDsEventMsgMeta.cast(data)
    meta.sensorId = 0
    meta.placeId = 0
    meta.moduleId = 0
    meta.sensorStr = "sensor-0"
    meta.ts = pyds.alloc_buffer(MAX_TIME_STAMP_LEN + 1)
    pyds.generate_ts_rfc3339(meta.ts, MAX_TIME_STAMP_LEN)
    if class_id == PGIE_CLASS_ID_VEHICLE:
        meta.type = pyds.NvDsEventType.NVDS_EVENT_MOVING
        meta.objType = pyds.NvDsObjectType.NVDS_OBJECT_TYPE_VEHICLE
        meta.objClassId = PGIE_CLASS_ID_VEHICLE
        obj = pyds.alloc_nvds_vehicle_object()
        obj = generate_vehicle_meta(obj)
        meta.extMsg = obj
        meta.extMsgSize = sys.getsizeof(pyds.NvDsVehicleObject)
    if class_id == PGIE_CLASS_ID_PERSON:
        meta.type = pyds.NvDsEventType.NVDS_EVENT_ENTRY
        meta.objType = pyds.NvDsObjectType.NVDS_OBJECT_TYPE_PERSON
        meta.objClassId = PGIE_CLASS_ID_PERSON
        obj = pyds.alloc_nvds_person_object()
        obj = generate_person_meta(obj)
        meta.extMsg = obj
        meta.extMsgSize = sys.getsizeof(pyds.NvDsPersonObject)
    return meta


def osd_sink_pad_buffer_probe(pad, info, u_data):
    frame_number = 0
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
    if not batch_meta:
        return Gst.PadProbeReturn.OK
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break
        is_first_object = True
        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            txt_params = obj_meta.text_params
            txt_params.display_text = pgie_classes_str[obj_meta.class_id]
            obj_counter[obj_meta.class_id] += 1
            txt_params.font_params.font_name = "Serif"
            txt_params.font_params.font_size = 10
            txt_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
            txt_params.set_bg_clr = 1
            txt_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
            if is_first_object and (frame_number % 30) == 0:
                user_event_meta = pyds.nvds_acquire_user_meta_from_pool(batch_meta)
                if user_event_meta:
                    msg_meta = pyds.alloc_nvds_event_msg_meta(user_event_meta)
                    msg_meta.bbox.top = obj_meta.rect_params.top
                    msg_meta.bbox.left = obj_meta.rect_params.left
                    msg_meta.bbox.width = obj_meta.rect_params.width
                    msg_meta.bbox.height = obj_meta.rect_params.height
                    msg_meta.frameId = frame_number
                    msg_meta.trackingId = long_to_uint64(obj_meta.object_id)
                    msg_meta.confidence = obj_meta.confidence
                    msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)
                    user_event_meta.user_meta_data = msg_meta
                    user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                    pyds.nvds_add_user_meta_to_frame(frame_meta, user_event_meta)
                else:
                    print("Error in attaching event meta to buffer\n")
                is_first_object = False
            try:
                l_obj = l_obj.next
            except StopIteration:
                break
        try:
            l_frame = l_frame.next
        except StopIteration:
            break
    print(
        "Frame Number =",
        frame_number,
        "Vehicle Count =",
        obj_counter[PGIE_CLASS_ID_VEHICLE],
        "Person Count =",
        obj_counter[PGIE_CLASS_ID_PERSON],
    )
    return Gst.PadProbeReturn.OK


def parse_args():
    parser = OptionParser()
    parser.add_option("-c", "--cfg-file", dest="cfg_file", metavar="FILE")
    parser.add_option("-i", "--input-file", dest="input_file", metavar="FILE")
    parser.add_option("-p", "--proto-lib", dest="proto_lib", metavar="PATH")
    parser.add_option(
        "", "--conn-str", dest="conn_str", metavar="STR", default="localhost;2181;testTopic"
    )
    parser.add_option("-s", "--schema-type", dest="schema_type", default="0")
    parser.add_option("-t", "--topic", dest="topic", metavar="TOPIC")
    parser.add_option("", "--no-display", action="store_true", dest="no_display", default=False)
    (options, args) = parser.parse_args()

    global cfg_file, input_file, proto_lib, conn_str, topic, schema_type, no_display
    cfg_file = options.cfg_file
    input_file = options.input_file
    proto_lib = options.proto_lib
    conn_str = options.conn_str
    topic = options.topic
    no_display = options.no_display
    if not (proto_lib and input_file):
        print(
            "Usage: python3 deepstream_test_4.py -i <H264 filename> -p <Proto adaptor library> --conn-str=<Connection string>"
        )
        return 1
    schema_type = 0 if options.schema_type == "0" else 1
    return 0


def main(args):
    platform_info = PlatformInfo()
    Gst.init(None)
    pipeline = Gst.Pipeline()
    source = Gst.ElementFactory.make("filesrc", "file-source")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    msgconv = Gst.ElementFactory.make("nvmsgconv", "nvmsg-converter")
    msgbroker = Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")
    tee = Gst.ElementFactory.make("tee", "nvsink-tee")
    queue1 = Gst.ElementFactory.make("queue", "nvtee-que1")
    queue2 = Gst.ElementFactory.make("queue", "nvtee-que2")
    sink = (
        Gst.ElementFactory.make("fakesink", "fakesink")
        if no_display
        else (
            Gst.ElementFactory.make("nv3dsink", "nv3d-sink")
            if platform_info.is_integrated_gpu() or platform_info.is_platform_aarch64()
            else Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        )
    )

    source.set_property("location", input_file)
    streammux.set_property("width", MUXER_OUTPUT_WIDTH)
    streammux.set_property("height", MUXER_OUTPUT_HEIGHT)
    streammux.set_property("batch-size", 1)
    streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    pgie.set_property("config-file-path", PGIE_CONFIG_FILE)
    msgconv.set_property("config", MSCONV_CONFIG_FILE)
    msgconv.set_property("payload-type", schema_type)
    msgbroker.set_property("proto-lib", proto_lib)
    msgbroker.set_property("conn-str", conn_str)
    if cfg_file is not None:
        msgbroker.set_property("config", cfg_file)
    if topic is not None:
        msgbroker.set_property("topic", topic)
    msgbroker.set_property("sync", False)

    for element in (
        source,
        h264parser,
        decoder,
        streammux,
        pgie,
        nvvidconv,
        nvosd,
        tee,
        queue1,
        queue2,
        msgconv,
        msgbroker,
        sink,
    ):
        pipeline.add(element)

    source.link(h264parser)
    h264parser.link(decoder)
    sinkpad = streammux.request_pad_simple("sink_0")
    srcpad = decoder.get_static_pad("src")
    srcpad.link(sinkpad)
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(tee)
    tee_msg_pad = tee.request_pad_simple("src_%u")
    tee_render_pad = tee.request_pad_simple("src_%u")
    sink_pad = queue1.get_static_pad("sink")
    tee_msg_pad.link(sink_pad)
    sink_pad = queue2.get_static_pad("sink")
    tee_render_pad.link(sink_pad)
    queue1.link(msgconv)
    msgconv.link(msgbroker)
    queue2.link(sink)

    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    osdsinkpad = nvosd.get_static_pad("sink")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
    return 0


if __name__ == "__main__":
    ret = parse_args()
    if ret == 1:
        sys.exit(1)
    sys.exit(main(sys.argv))
