# Reference catalog

## Locally collected material

| Material | Location and provenance | Status |
|---|---|---|
| PG1316S assembly and alternate keycap STEP; two reference footprints | [PG1316S notes](pg1316s/README.md), collected from Mike Holscher's mikefive repository | Community references; not proof of physical fit. Retain attribution; upstream licensing must be confirmed before redistribution beyond this existing collection |
| MSK-12C02 STEP and derived footprint | [Project library notes](../hardware/pcb/lib/README.md), LCSC C431540 via easyeda2kicad | Project uses this model locally; redistribution terms not recorded |
| Project PG1316S, face-down XIAO and locating-post footprints; XIAO symbol | Same project library | Project-specific designs; source comparisons documented there |

The production KiCad library stays with the boards. The PG1316S community reference models stay here and are referenced by project-relative paths. Stock KiCad parts require KiCad's installed libraries. The XIAO footprint has no attached model.

## Linked references not archived locally

- Kailh CPG1316S01D02 datasheet — authoritative dimensional reference, linked in the [resource chapter](../buildbook/chapters/resources.md).
- Seeed XIAO STEP archive and v1.1 KiCad project — original controller geometry sources, linked in the project library notes; neither archive is included.
- MSK-12C02 manufacturer datasheet — source of land-pattern checks; linked through LCSC, not archived.
- Chalk and other community repositories — comparison evidence, not vendored dependencies.
- ZMK, KiCad and build123d documentation — external documentation, not local snapshots.

Source URLs and author notes are preserved in the linked catalogs. Download dates, source revisions and redistribution permissions are not fully recorded; do not invent them. Local archival of additional third-party documents requires checking their terms first. Website generation does not fetch external references or imply that they are bundled.
