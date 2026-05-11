# Layout Heuristics

Use this file when the user needs help choosing form factors or understanding why one layout is more practical than another.

## Common Cylindrical Geometry Presets

These presets describe physical size only. They do not imply exact electrical capacity.

| Format | Diameter (mm) | Height (mm) |
| --- | --- | --- |
| `12700` | 12 | 70 |
| `14500` | 14 | 50 |
| `18650` | 18 | 65 |
| `21700` | 21 | 70 |
| `26650` | 26 | 65 |
| `32700` | 32 | 70 |
| `38120` | 38 | 120 |
| `4680` | 46 | 80 |

## Geometry Tradeoffs

- Common `18650` and `21700` cells are often generic `li-ion` 3.7 V parts unless the exact chemistry is known.
- Smaller cylindrical cells can give finer-grained layout flexibility, but they require more total cells, more welds, and more interconnect complexity.
- Larger cylindrical cells reduce part count, but the pack becomes coarser: each extra `P` step adds a larger chunk of Ah and volume.
- Prismatic cells can make very compact low-part-count packs, but they need stronger attention to terminal clearance, compression, and mechanical support.

## Practical Layout Rules

- A mathematically smallest footprint is not always the easiest pack to build.
- Very long one-row layouts are often awkward for enclosure design even if they use less area.
- More layers reduce footprint but usually worsen thermal path, maintenance access, and wiring complexity.
- Leave real margin for holders, fish paper, padding, busbars, BMS, cable bends, and wall thickness.

## Recommended Goal Modes

- `balanced`: Best default. Keeps the pack compact without forcing extreme aspect ratios.
- `compact`: Bias toward the smallest raw envelope volume.
- `footprint`: Bias toward the smallest plan area, even if the pack becomes taller.
- `flat`: Bias toward lower height, even if footprint increases.

## Caveats

- Cylindrical cells are modeled with a rectangular grouped-envelope estimate, not a true honeycomb nest.
- Real terminal caps, holders, tabs, or busbars can change the best orientation.
- Prismatic cells may have orientation restrictions from the manufacturer; check the datasheet before trusting a rotated layout.
