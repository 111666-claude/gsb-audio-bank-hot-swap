# Sound-bank hot swap

Banks load localized sound variants by `(bank, generation, sound, locale)`.
Loading a newer generation replaces that bank's older generation. An unload
event names a bank and generation; it must not evict a newer generation that
has already arrived. For a sound, exact-locale variants take precedence over
English fallbacks. Within that locale, variants are ordered by higher priority,
then bank ID. `resolve` returns as many variants as fit a **shared remaining**
byte budget, never a partial variant.

`Work` counts candidate entries examined by resolutions. Old generations,
unloaded banks and unrelated sounds must not make a hot sound lookup rescan
the full asset history.
