# DeepStream Practice

Workspace nay theo huong `guide-first` va chia thanh hai tang:

1. `lessons/` la curriculum self-contained cho nguoi hoc.
2. `../apps/` la kho sample app goc de bien soan va doi chieu, khong phai prerequisite
   khi hoc.

## Cau truc

- `lessons/README.md`: index cua toan bo curriculum.
- `lessons/beginning/`: track nhap mon on dinh (`01..09`).
- `lessons/<topic>/`: track nang cao theo chu de, moi topic gom:
  - `00_path.md` (lo trinh hoc cua topic)
  - `01_<subtopic>/` ... `0N_<subtopic>/`
  - trong moi subtopic: `01_guide.md`, `02_coding_guide.md`, `03_starter.py`, `04_extensions.md`, `05_reference.py`
- `../apps/`: kho sample app goc de doi chieu implementation khi bien soan.
- `archive/exercises/`: bai tap cu da archive de doi chieu.
- `notes/`: tai lieu bo tro va roadmap.

## Thu tu hoc de xuat

1. `notes/00_learning_path.md`
2. `lessons/README.md`
3. Hoan thanh toan bo `lessons/beginning/`
4. Chon topic phu hop va theo `00_path.md` cua topic do:
   - `lessons/streaming-io/00_path.md`
   - `lessons/analytics-tracking/00_path.md`
   - `lessons/multistream/00_path.md`
   - `lessons/segmentation-opticalflow/00_path.md`
   - `lessons/preprocess-custom/00_path.md`
   - `lessons/messaging-cloud/00_path.md`
5. Doc `README.md` ngay trong topic de xem nhanh stage list va pham vi hoc tap.

## Topic Tracks (Sub-lessons)

Cac topic da duoc tach thanh nhieu chang con de tranh nhieu kien thuc trong mot guide duy nhat:

- `streaming-io`: 4 stages
- `analytics-tracking`: 4 stages
- `multistream`: 5 stages
- `segmentation-opticalflow`: 3 stages
- `preprocess-custom`: 3 stages
- `messaging-cloud`: 3 stages

Mapping app nguon cho tung topic xem tai:
`notes/04_apps_to_lessons_roadmap.md`.

## Ghi chu

- Luon doc `01_guide.md` truoc, code trong `03_starter.py`, roi moi doi chieu `05_reference.py`.
- Lesson co the tham chieu app goc trong luc bien soan, nhung ban hoc chi can `lessons/`.
- Neu can config variant/checklist cu, su dung `archive/exercises/`.
