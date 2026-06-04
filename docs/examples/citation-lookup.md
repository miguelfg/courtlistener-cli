# Citation Lookup Examples

Look up citations in text:

```bash
uv run courtlistener-cli citation-lookup text --text "See Brown v. Board of Education, 347 U.S. 483 (1954)."
uv run courtlistener-cli citation-lookup text --text "Roe v. Wade, 410 U.S. 113 (1973); Miranda v. Arizona, 384 U.S. 436 (1966)." --format json --output ./output
```

Look up a structured citation:

```bash
uv run courtlistener-cli citation-lookup citation --volume 347 --reporter "U.S." --page 483
uv run courtlistener-cli citation-lookup citation --volume 410 --reporter "U.S." --page 113 --output ./output
```
