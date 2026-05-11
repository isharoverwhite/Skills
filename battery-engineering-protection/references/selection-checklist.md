# Selection Checklist

Use this file when the user needs the practical checklist behind the raw calculator output.

## BMS Checklist

- Match chemistry and exact series count.
- Verify both charge current and discharge current, not just one side.
- Check peak current if inverter startup or motor surge exists.
- Prefer low-temperature charge protection for LFP.
- For common `li-ion` 3.7 V packs, verify charger cutoff, cell voltage window, and balancing thresholds carefully.
- Prefer communication support when the battery must integrate with an inverter-charger or monitoring system.
- Consider stronger balancing for reused cells, large packs, or long strings.
- Add enough temperature sensors for the pack size and hot spots.

## Fuse Checklist

- Use a DC-rated fuse or breaker with sufficient interrupt rating.
- Put the main battery fuse close to the battery positive terminal.
- Verify the fuse rating protects the chosen conductor.
- Do not choose the fuse solely from what the load wants.
- For inverter systems, consider fuse and holder behavior during surge and fault events.

## Wire Checklist

- Check both voltage drop and heating.
- Low-voltage, high-current systems often become cable-heavy very quickly.
- Verify lug size, bend radius, strand class, and insulation rating.
- Real current capacity depends on bundling, ambient, ventilation, and enclosure path.
- If the math points to very large conductors, reconsider the bus voltage before locking in the hardware.

## Output Caveats

- These results are screening guidance, not final sign-off.
- Local code, equipment datasheets, and real fault-current behavior still control the final answer.
