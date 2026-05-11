# Battery Engineering Power Basics

Tai lieu nay ghi lai cong thuc co ban nhat de tinh dien ap, dong dien va cong suat trong bundle battery engineering.

## 1. Cong thuc co ban

Voi mach DC, cong thuc nen nho la:

```text
P = V x I
```

Trong do:

- `P`: cong suat, don vi `W`
- `V`: dien ap, don vi `V`
- `I`: dong dien, don vi `A`

Neu biet 2 gia tri, co the suy ra gia tri con lai:

```text
P = V x I
I = P / V
V = P / I
```

## 2. Cach hieu theo dau vao

Neu dang tinh phia dau vao:

```text
Cong suat vao = Dien ap vao x Dong vao
Pin = Vin x Iin
Iin = Pin / Vin
Vin = Pin / Iin
```

## 3. Cach hieu theo dau ra

Neu dang tinh phia dau ra:

```text
Cong suat ra = Dien ap ra x Dong ra
Pout = Vout x Iout
Iout = Pout / Vout
Vout = Pout / Iout
```

## 4. Neu co ton hao hieu suat

Trong he co inverter, UPS, DC-DC hoac charger, cong suat vao va ra khong bang nhau.

Neu hieu suat la `eta`:

```text
Pin = Pout / eta
Iin = Pout / (Vin x eta)
```

Vi du:

- Tai AC can `300 W`
- Inverter hieu suat `90%`
- Pack pin `24 V`

Khi do:

```text
Pin = 300 / 0.9 = 333.3 W
Iin = 333.3 / 24 = 13.9 A
```

## 5. Vi du nhanh

### Vi du 1: tinh dong tu cong suat va dien ap

```text
P = 120 W
V = 12 V
I = P / V = 120 / 12 = 10 A
```

### Vi du 2: cung 120 W nhung tang dien ap

```text
12 V -> I = 10 A
24 V -> I = 5 A
48 V -> I = 2.5 A
```

Day la ly do he pin dien ap cao hon thuong giam dong dien va giam ap luc len day.

### Vi du 3: tinh cong suat

```text
V = 25.6 V
I = 20 A
P = V x I = 25.6 x 20 = 512 W
```

## 6. Ghi chu quan trong

- Cong thuc `P = V x I` la cong thuc co ban cho DC.
- Voi AC, neu muon chinh xac hon can tinh them he so cong suat `PF`.
- Trong battery engineering bundle, phan lon tinh nhanh cho phia pack pin deu dua tren logic DC, sau do moi them hieu suat cua inverter hay bo chuyen doi.
- Neu can tinh BMS, fuse, wire sizing, phai dung dong dien thuc te o phia pin, khong chi nhin cong suat tai phia load.
