# Tracking And Analytics Topic

Day la topic cho tracking va analytics tren object:

- `apps/deepstream-test2`
- `apps/deepstream-nvdsanalytics`

## What this topic teaches

- `nvtracker`
- Past-frame or tracker config reading
- Secondary inference chain
- `nvdsanalytics` rules and metadata
- Object-level metadata flowing through the pipeline

## Suggested lesson order

1. `./01_tracker_and_sgie/01_guide.md`
2. `./01_tracker_and_sgie/02_coding_guide.md`
3. `./01_tracker_and_sgie/03_starter.py`
4. `./01_tracker_and_sgie/04_extensions.md`
5. `./01_tracker_and_sgie/05_reference.py`
6. `./02_nvdsanalytics_rules/01_guide.md`
7. `./02_nvdsanalytics_rules/02_coding_guide.md`
8. `./02_nvdsanalytics_rules/03_starter.py`
9. `./02_nvdsanalytics_rules/04_extensions.md`
10. `./02_nvdsanalytics_rules/05_reference.py`

## Boundary

- Khong mo rong sang image access hoac GPU buffer access.
- Khong chuyen sang output broker hay RTSP publishing.
- Tap trung vao object metadata, tracker state, va analytics output.
- Lesson 01 tap trung vao tracker + SGIE + past-frame meta.
- Lesson 02 tap trung vao nvdsanalytics rules va analytics meta.
