# Lesson Template

Dung template nay khi tao mot lesson moi trong `deepstream-practice/lessons/`.

## Muc tieu

Moi lesson phai day theo thu tu:

1. Hieu khai niem va mental model.
2. Doc huong dan thuc hanh de biet can go gi va vi sao.
3. Tu code lai tu file khung.
4. Lam them bai mo rong van nam trong cung pham vi bai hoc.
5. Chi doi chieu dap an sau khi da tu thu.

## Cau truc bat buoc

- `01_guide.md`: day khai niem, flow du lieu, implementation checklist, failure modes,
  self-check, extensions.
- `02_coding_guide.md`: day cach code theo thu tu viet file, giai thich syntax, ham
  goi, gia tri tra ve, va buoc tiep theo.
- `03_starter.py`: file khung co `TODO` mang tinh trien khai. Nguoi hoc phai tu viet
  phan vua hoc.
- `04_extensions.md`: cac bai mo rong trong cung boundary cua lesson.
- `05_reference.py`: ban chay duoc, sach se, dung de doi chieu sau cung.

## Nguyen tac viet `01_guide.md`

- Phai co cac section: `What you will build`, `Why it matters`, `Mental model`,
  `Implementation checklist`, `Common failure modes`, `Self-check`, `Extensions`.
- Giai thich theo dong chay du lieu va lifecycle cua pipeline, khong mo ta mo ho.
- Neu co the, doi chieu khai niem GStreamer nen tang voi docs da cross-check.
- Dung vi du nho va ngon; guide khong nen bien thanh mot sample code dai.

## Nguyen tac viet `03_starter.py`

- Giu imports va bo khung app de nguoi hoc tap trung vao bai hoc.
- `TODO` phai buoc nguoi hoc tu lap trinh phan vua hoc, khong chi doi 1-2 dong.
- `TODO` nen duoc danh so hoac gan nhan theo `02_coding_guide.md` de nguoi hoc biet
  minh dang o buoc nao.
- Moi `TODO` nen tuong ung voi mot moc ky thuat ro rang:
  tao element, add/link, bus callback, request pad, probe, overlay...
- File phai hop le ve mat cu phap de nguoi hoc co diem bat dau ro rang.

## Nguyen tac viet `02_coding_guide.md`

- Phai day theo trinh tu code that su, khong chi nhac lai khai niem.
- Moi block nen tra loi duoc 5 cau hoi:
  goi ham nao, dung de lam gi, tra ve cai gi o muc khai niem, khi nao can check loi,
  va sau dong do thuong viet gi tiep.
- Neu callback co tham so la, phai noi ro tham so nao duoc dung trong lesson.
- Phai co phan map truc tiep sang tung `TODO` trong `03_starter.py`.
- Nguoi chua quen syntax Python/GStreamer van phai lan theo duoc.

## Nguyen tac viet `04_extensions.md`

- Bat dau bang 2-3 bai mo rong co ban, sau do moi toi bai nang hon.
- Khong nhao sang chu de cua lesson sau.
- Moi extension phai noi ro: thay doi gi, quan sat gi, rut ra ket luan gi.

## Nguyen tac viet `05_reference.py`

- Day la ban doi chieu sau cung, khong phai diem vao chinh.
- Code nen sach hon ban starter: argument parsing ro, log toi thieu, cleanup day du.
- Khong nhet them nhieu "meo" ngoai pham vi lesson.
