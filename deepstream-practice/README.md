# DeepStream Practice

Workspace nay la khu vuc hoc chinh cua repo, theo huong `guide-first`:

1. hoc tu curriculum trong `lessons/`,
2. tu code trong `03_starter.py`,
3. roi moi doi chieu voi `05_reference.py` va sample goc trong `../apps/`.

`../apps/` la kho sample DeepStream Python de tham chieu implementation, khong phai
entry point chinh khi hoc.

## Cau truc

- `lessons/beginning/`: track nhap mon cot loi, hoc tu de den kho.
- `lessons/topics/`: cac track nang cao theo chu de.
- `lessons/_template/`: template de bien soan lesson moi.
- `archive/`: bai tap va noi dung cu duoc giu lai de doi chieu.
- `notes/`: roadmap, mapping, va tai lieu bo tro.
- `solutions/`: scratch/solution ho tro qua trinh luyen tap.

## Entry points nen mo truoc

1. `./README.md`
2. `lessons/beginning/README.md`
3. `lessons/beginning/00_path.md`
4. Sau khi xong phan nen tang, mo `lessons/topics/README.md`
5. Tiep theo doc `lessons/topics/00_path.md`
6. Chon mot topic va hoc theo `00_path.md` cua topic do

## Lesson format

Phan lon stage trong curriculum dung format 5 file:

- `01_guide.md`: giai thich bai toan, concept, mental model, data flow.
- `02_coding_guide.md`: chi tiet cac buoc code, API can dung, cac cho can luu y.
- `03_starter.py`: file de tu trien khai.
- `04_extensions.md`: bai mo rong va bien the.
- `05_reference.py`: ban doi chieu sau khi da tu lam.

## Beginning track

`lessons/beginning/` la prerequisite path on dinh cho nguoi moi:

- GStreamer bootstrap va decode chain
- streammux, infer, batch meta
- OSD overlay, multisource batching
- RTSP walkthrough

Hay hoc track nay tuan tu theo `00_path.md` truoc khi chuyen sang topic tracks.

## Topic tracks hien tai

Trong `lessons/topics/` hien co cac nhom chu de:

- `baseline_pipeline`
- `multistream_and_batching`
- `imagedata_and_memory`
- `metadata_and_custom_user_meta`
- `tracking_and_analytics`
- `egress_and_brokering`
- `vision_extensions`

Moi topic co:

- `00_path.md` de dinh tuyen stage,
- cac thu muc stage nhu `01_*`, `02_*`, ...
- trong moi stage: `01_guide.md` -> `05_reference.py`.

Mapping giua app goc va lesson track xem tai `notes/04_apps_to_lessons_roadmap.md`.

## Thu tu hoc de xuat

1. Hoan thanh `lessons/beginning/`.
2. Mo `lessons/topics/00_path.md`.
3. Chon topic phu hop voi muc tieu hien tai.
4. Di het tung stage trong topic theo thu tu.
5. Khi can doi chieu implementation goc, moi quay sang `../apps/`.

## Ghi chu

- Luon doc `01_guide.md` truoc khi mo code.
- Co gang tu lam `03_starter.py` truoc khi xem `05_reference.py`.
- `archive/` la noi tham chieu lich su, khong phai noi bat dau hoc.
- Neu mot lesson nhac toi sample app goc, hay xem no nhu tai lieu doi chieu, khong phai bai hoc chinh.
