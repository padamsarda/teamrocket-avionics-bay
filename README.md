# TeamRocket Avionics Bay

Flight-computer bay for a Ø70 mm rocket (64 mm ID): 3 IMUs + 3 barometers on one vertical perfboard with every IMU chip on the rocket axis, ESP32-DevKitC, SD logging (SDMMC 1-bit), two pyro channels with different-vendor MOSFETs, and two printable removable mounts.

**Site:** https://padamsarda.github.io/teamrocket-avionics-bay/ · **3D viewer:** https://padamsarda.github.io/teamrocket-avionics-bay/viewer/

```
docs/                     ← GitHub Pages root
├── index.html            landing page with every download
├── viewer/               interactive 3D layout (three.js)
├── cad/
│   ├── mounts/           V1 slide-in rails · V2 backplate (STL to print, STEP parts, full assemblies)
│   ├── boards/           board models with IC-centre markers + IC_centres.csv
│   ├── layout/           exact placements exported from the viewer
│   └── sources/          unmodified KiCad / Espressif / SparkFun source files + licenses
└── scripts/              CadQuery build scripts
```

GrabCAD-derived boards (GY-BMP280, GY-63, DevKitC V4) are replaced by redistributable stand-ins in the same frames; links to the originals are on the site.

License: CAD files CC BY-SA 4.0 (they derive from KiCad, Espressif and SparkFun CC BY-SA 4.0 material). Scripts MIT.
