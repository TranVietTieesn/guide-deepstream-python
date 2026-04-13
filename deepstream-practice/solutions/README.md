# Solutions

Thu muc chua bai giai va file thu nghiem cho cac lesson trong `../lessons/`.

## Cau truc

```
solutions/
├── 01_gst_bootstrap/
│   ├── solution.py      # Bai giai chinh thuc (sach se)
│   ├── scratch.py       # File de test, thu nghiem, debug
│   └── notes.md         # Ghi chu ca nhan
├── 02_decode_chain/
│   └── ...
├── 04_primary_infer/
├── 05_probe_batch_meta/
├── 06_osd_overlay_counts/
├── 08_multisource_batching/
├── 09_rtsp_source_walkthrough/
└── README.md            # File nay
```

## Workflow

1. **Doc lesson**: Vao `../lessons/XX_topic/` doc `01_guide.md` va `02_coding_guide.md`
2. **Thu nghiem**: Code trong `scratch.py` thoai mai
3. **Hoan thien**: Neu muon tu giu bai giai rieng, ban phat trien tu `scratch.py`
4. **Doi chieu**: Chay `solution.py` hoac so sanh voi `../lessons/XX_topic/05_reference.py`
5. **Ghi chu**: Ghi lai kien thuc vao `notes.md`

## Checklist Tien Do

- [ ] Lesson 01: GStreamer Bootstrap
- [ ] Lesson 02: Decode Chain
- [ ] Lesson 03: Streammux Single Source
- [ ] Lesson 04: Primary Infer
- [ ] Lesson 05: Probe Batch Meta
- [ ] Lesson 06: OSD Overlay Counts
- [ ] Lesson 08: Multi-Source Batching
- [ ] Lesson 09: RTSP Source Walkthrough

## Ghi chu ve scope

- `07_config_variants` duoc xem la tai lieu config ho tro lesson 04/08, khong tach
  thanh mot thu muc `solutions/` rieng.
- `10_pipeline_debug_checklist.md` la checklist de debug, khong phai bai code de can
  `solution.py`.

## Command chay bai

```bash
# Tu root cua du an
python3 deepstream-practice/solutions/01_gst_bootstrap/solution.py <path-to-file>

# Hoac cd vao thu muc solutions
python3 01_gst_bootstrap/solution.py <path-to-file>
```
