# passageway-sdk

Write a [passageway](https://passageway.marceltov.de/) connector as three small functions. No dependencies.

```python
from passageway_sdk import Connector

class Notes(Connector):
    def versions(self): ...      # {id: version} for every item
    def fetch(self, ids): ...    # an item record per id

Notes.main()
```

The SDK dispatches the mode, reads the ids, buffers the output (all or nothing), maps errors to exit codes and validates each item. Reference: https://passageway.marceltov.de/reference/sdk/ and the [guide](https://passageway.marceltov.de/guides/write-a-connector/).
