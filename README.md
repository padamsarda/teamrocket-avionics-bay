# TeamRocket Avionics Bay

Flight-computer bay for a Ø70 mm rocket (64 mm ID). Two perfboards sit back to back with their parts facing out:
- **Board 1:** 3 IMUs and 3 barometers, with every IMU chip on the rocket axis, plus two pyro channels (different-vendor MOSFETs) and the buzzer.
- **Board 2:** ESP32-DevKitC, SD logging (SDMMC 1-bit) and the 3.3 V buck.

It has two printable removable mounts. The earlier single-board layout and its mounts are kept for reference.

**Site:** https://padamsarda.github.io/teamrocket-avionics-bay/ · **3D viewer:** https://padamsarda.github.io/teamrocket-avionics-bay/viewer/

```
docs/                     ← GitHub Pages root
├── index.html            landing page with every download
├── viewer/               interactive 3D layout (three.js)
├── cad/
│   ├── mounts_sandwich/  CURRENT: V1 slide-in rails · V2 frame + 6 grommets (STL, STEP parts, assemblies)
│   ├── mounts/           superseded single-board mounts
│   ├── boards/           board models with IC-centre markers + IC_centres.csv
│   ├── layout/           exact placements exported from the viewer
│   └── sources/          unmodified KiCad / Espressif / SparkFun source files + licenses
└── scripts/              CadQuery build scripts
```

GrabCAD-derived boards (GY-BMP280, GY-63, DevKitC V4) are replaced by redistributable stand-ins in the same frames; links to the originals are on the site.

License: CAD files CC BY-SA 4.0 (they derive from KiCad, Espressif and SparkFun CC BY-SA 4.0 material). Scripts MIT.
