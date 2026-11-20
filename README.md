# Köşe — 18 mm montaj aparatları

**Canlı 3D görüntüleyici:** [https://corner-jigs.apps.grok.bot](https://corner-jigs.apps.grok.bot)

İki 18 mm sunta/MDF’yi köşede tutan L aparat. Ortak gövde: **70×22 mm**, et **3 mm**, U kanal **18 mm**.

## 1) Kulaklı (`corner-assembly-square`)

- Dış et aşağı doğru iki yanak + arada kulak (et kalınlığının devamı, basamak yok)  
- Kulak sunta yüzüne yaslanır, gövdeden taşmaz  
- Ø2.5 mm vida: 1. yanak → kulak → 2. yanak  
- Kılavuz: üstten 36 mm, Ø3 mm  
- Yanaklar yalnızca X’te kalın (tutmak için); gövdeyi şişirmez  

Dosyalar: `models/corner-assembly-square.{scad,stl}`, `corner-body.stl`, `corner-ear.stl`

## 2) Kulaksız (`corner-plain`)

Birincinin aynı gövdesi; yanak ve kulak yok.

Dosyalar: `models/corner-plain.{scad,stl}`

## Çalıştırma

```bash
pip install numpy trimesh manifold3d
python3 models/generate_stl.py
npm install --prefix viewer
npm run dev --prefix viewer
```
