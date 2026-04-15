# Imagedata And Memory Topic

Day la topic ve truy cap image buffer va memory backend:

- `apps/deepstream-imagedata-multistream`
- `apps/deepstream-imagedata-multistream-cupy`
- `apps/deepstream-imagedata-multistream-redaction`

## What this topic teaches

- Access `imagedata` from batch buffers
- Modify in-place vs copy-and-save
- Unified memory versus GPU memory access
- OpenCV/Numpy/CuPy buffer handling
- Face redaction and cropped output

## Suggested lesson order

1. `./01_numpy_image_access/01_guide.md`
2. `./01_numpy_image_access/02_coding_guide.md`
3. `./01_numpy_image_access/03_starter.py`
4. `./01_numpy_image_access/04_extensions.md`
5. `./01_numpy_image_access/05_reference.py`
6. `./02_cupy_gpu_access/01_guide.md`
7. `./02_cupy_gpu_access/02_coding_guide.md`
8. `./02_cupy_gpu_access/03_starter.py`
9. `./02_cupy_gpu_access/04_extensions.md`
10. `./02_cupy_gpu_access/05_reference.py`
11. `./03_redaction_and_crops/01_guide.md`
12. `./03_redaction_and_crops/02_coding_guide.md`
13. `./03_redaction_and_crops/03_starter.py`
14. `./03_redaction_and_crops/04_extensions.md`
15. `./03_redaction_and_crops/05_reference.py`

## Boundary

- Giu mot topic rieng cho buffer access va image post-processing.
- Khong mix voi segmentation masks hay optical flow trong cung lesson goc.
- Neu can object metadata, chi dung phan can thiet de tim crop hoac annotate.
- Lesson 01 tap trung vao NumPy + unified memory.
- Lesson 02 tap trung vao CuPy + GPU buffer access.
- Lesson 03 tap trung vao redaction va crop workflow.
