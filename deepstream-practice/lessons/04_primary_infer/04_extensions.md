# Lesson 04 Extensions

## Co ban

1. In ten tung element truoc khi link de thay `nvinfer`, `nvvideoconvert`, `nvdsosd`
   nam o dau trong pipeline.
2. In them `pgie.get_property("batch-size")` va doi chieu voi `streammux`.
3. Mo `dstest1_pgie_config.txt`, tim cac dong `onnx-file`, `model-engine-file`,
   `labelfile-path`, `batch-size`, `network-mode`, va tu giai thich tung dong bang 1 cau.
4. Doi sang config variant trong `exercises/07_config_variants/pgie_trafficcamnet.txt`.

## Nang hon nhung van trong boundary lesson

1. Sua `pre-cluster-threshold` trong config va ghi lai bbox thay doi ra sao.
2. Thu dung sai duong dan config de quan sat bus `ERROR`.
3. In ra sink ma `create_sink(platform_info)` da chon va doi chieu voi nen tang may dang
   chay.
4. Doi sink de xem output thay vi chi dung sink mac dinh, nhung ghi ro day la phan mo
   rong portability chứ khong phai infer logic cot loi.
