# Metadata And Custom User Meta Topic

Day la topic ve metadata tu nhin bang huong "bindings and custom payload":

- `apps/deepstream-custom-binding-test`

## What this topic teaches

- `NvDsUserMeta`
- Attach custom Python-side data to frames
- Read custom data at a downstream pad
- Copy and release custom structs safely

## Suggested lesson order

1. `./01_user_meta_attach_upstream/01_guide.md`
2. `./01_user_meta_attach_upstream/02_coding_guide.md`
3. `./01_user_meta_attach_upstream/03_starter.py`
4. `./01_user_meta_attach_upstream/04_extensions.md`
5. `./01_user_meta_attach_upstream/05_reference.py`
6. `./02_user_meta_read_and_release/01_guide.md`
7. `./02_user_meta_read_and_release/02_coding_guide.md`
8. `./02_user_meta_read_and_release/03_starter.py`
9. `./02_user_meta_read_and_release/04_extensions.md`
10. `./02_user_meta_read_and_release/05_reference.py`

## Boundary

- Dung custom meta nhu mot feature rieng, khong tron voi tracking hay analytics.
- Moi extension nen xoay quanh vong doi cua custom payload va memory ownership.
- Lesson 01 tap trung vao upstream attach.
- Lesson 02 tap trung vao downstream readback va release.
