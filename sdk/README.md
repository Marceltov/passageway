# passageway-sdk

Write a [passageway](https://getpassageway.com/) connector as three small functions. No dependencies; `passageway-sdk[web]` adds a polite web client for connectors that read a website.

```python
from passageway_sdk import Connector

class Notes(Connector):
    def versions(self): ...      # {id: version} for every item
    def fetch(self, ids): ...    # an item record per id

Notes.main()
```

The SDK dispatches the mode, reads the ids, buffers the output (all or nothing), maps errors to exit codes and validates each item. Reference: https://getpassageway.com/reference/sdk/ and the [guide](https://getpassageway.com/guides/write-a-connector/).
