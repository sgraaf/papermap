# PaperMap

A python package and CLI for creating paper maps.

## Package example
```python
pm = PaperMap(13.75889, 100.49722)
pm.render()
pm.save('Bangkok.pdf')
```

## CLI example
```bash
papermap 13.75889 100.4972 Bangkok.pdf
```

Both of these examples accomplish the exact same thing: creating an A4 map of Bangkok at scale 1:25000.

### Licence
PaperMap is open-source and licensed under GNU GPL, Version 3.