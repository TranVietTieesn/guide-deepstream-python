# Lesson 03 Extensions

## Co ban

1. Doi `batch-size` thanh 2 trong khi van chi co 1 source.
   - Quan sat: ban nghi muxer se cho dieu gi, va log cho ban dau hieu nao?
2. In ra `batch-size`, `width`, `height`, `batched-push-timeout` truoc khi PLAYING.
   - Quan sat: ban da cau hinh muxer dung theo y dinh chua?
3. Thu doi `width` va `height`.
   - Quan sat: muxer dang chuan bi output frame size theo cach nao?

## Nang hon nhung van trong boundary lesson

1. Them source thu hai va request them `sink_1`.
   - Quan sat: workflow request pad thay doi nhu the nao khi so source tang len?
2. Co y request sai ten pad.
   - Quan sat: loi xuat hien o luc nao, va bai hoc o day la gi?
3. Giai thich bang loi cua ban vi sao `nvstreammux` van can mat trong bai 1 source,
   thay vi tra loi theo kieu "sample cua NVIDIA viet the".
