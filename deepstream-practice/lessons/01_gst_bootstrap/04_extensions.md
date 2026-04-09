# Lesson 01 Extensions

## Co ban

1. In ra ten tung element trong pipeline bang `pipeline.iterate_elements()`.
   - Quan sat: pipeline cua ban dang chua chinh xac nhung element nao?
2. Log state transition cua pipeline.
   - Quan sat: co nhin thay `NULL -> READY -> PAUSED -> PLAYING` khong?
3. Doi `fakesink` thanh `filesink`.
   - Quan sat: byte co duoc ghi ra file khong, va dieu do noi gi ve vai tro cua
     `filesrc` trong bai nay?

## Nang hon nhung van trong boundary lesson

1. Bo bus watch va chay lai.
   - Quan sat: app con nhan `EOS`/`ERROR` theo callback nua khong?
   - Ket luan: `GLib.MainLoop()` va bus watch dang phoi hop nhu the nao?
2. Co y truyen mot duong dan khong ton tai.
   - Quan sat: loi xuat hien o dau, va `ERROR` message cho ban biet gi?
3. Doi ten pipeline va in ten `message.src` khi co `STATE_CHANGED`.
   - Quan sat: khong chi pipeline, cac element ben trong cung co the phat state
     message.
