# Lesson 04: Primary Infer - Notes

## Trang thai

- [ ] Da chep `03_starter.py` vao `solution.py`
- [ ] Da tu dien cac TODO trong `solution.py`
- [ ] Da dung `scratch.py` de thu nghiem neu can
- [ ] Da doi chieu voi `05_reference.py`
- [ ] Da chay file ban tu lam

## Ghi chu chinh

- `config-file-path` noi code voi model/config
- `nvinfer` them metadata vao buffer sau infer
- `nvstreammux` van nam truoc `nvinfer` du chi co 1 source
- `pgie`, `nvvidconv`, `nvosd` la 3 element moi can tu tay khoi tao bang `make_element(...)`
- `create_sink(platform_info)` la helper chon sink, khong phai infer logic

## Quy uoc folder `solutions`

- `solution.py` la file ban tu lam va luyen tap
- `scratch.py` la noi test nhanh, debug, hoac thu y tuong
- `05_reference.py` trong lesson moi la file tham chieu khi can doi chieu

## Dieu muon thu them

- [ ] Doi config variant
- [ ] Sua threshold trong config
- [ ] Doi sink de quan sat output
