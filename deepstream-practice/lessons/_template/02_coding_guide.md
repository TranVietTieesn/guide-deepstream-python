# Coding Guide Template

Dung file nay de day nguoi hoc "code bai nay nhu the nao" theo trinh tu thuc hanh.

## Before You Code

- File nay nhan input gi?
- Chay bang lenh nao?
- Can import gi va import do dung de lam gi?

## Build Order

1. Viet callback va helper nao truoc?
2. Trong `main(args)`, parse input the nao?
3. Tao pipeline/element o dau?
4. Set property o dau?
5. Add/link o dau?
6. Bus/main loop/state transition o dau?

## Function-By-Function Walkthrough

### `on_message(...)`

- Ham nay duoc goi khi nao?
- Tham so nao quan trong trong lesson nay?
- Ban can xu ly nhung `MessageType` nao?

### `main(args)`

- `args` den tu dau?
- Thu tu viet tung block la gi?
- Sau moi block, ban nen kiem tra dieu gi?

### Helper functions

- Neu co `make_element(...)`, giai thich vi sao nen tach ra.
- Neu co helper pad/probe, giai thich no tra ve gi va duoc goi o dau.

## Syntax Notes

- Ham nao tra ve element?
- Ham nao tra ve pad?
- Ham nao tra ve bool?
- Ham nao khong tra ve gia tri ban can dung tiep?

## Starter Mapping

- `TODO 1`:
- `TODO 2`:
- `TODO 3`:

Mac dinh, hay map truc tiep sang `03_starter.py`.

## Mini Checkpoints

- Sau block tao element, ban phai co gi trong tay?
- Sau block link, pipeline da noi xong den dau?
- Sau block bus/main loop, app da san sang `PLAYING` chua?
