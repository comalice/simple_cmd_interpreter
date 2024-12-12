# Installation

`pip install simple-cmd-parser`

# Example Usage

```python
def test():
    """Test docstring.

    And we can have multiple lines, too.
      - some
      - list

      ```
      example = "code"
      ```"""
    return "Starting test."

test_map = {
    "test": lambda: "Starting test.",
    "test1": test,
    "device": {
        "connect": lambda *x: f"Connecting to device(s). {x}",
        "disconnect": lambda x: f"Disconnecting device. {x}",
        "status": lambda x: f"Displaying device status for {x}.",
        "default": lambda: "Use 'device help' for all options.",
    },
    "status": {
        "default": lambda: "Displaying test station status.",
    }
}

i = Interpreter(test_map)
print(i.eval("help"))
print(i.eval("test"))
print(i.eval("test help"))
print(i.eval("device"))
print(i.eval("device help"))
print(i.eval("device connect some-device"))
print(i.eval("device connect some-device some-device-2"))
print(i.eval("device status some-device"))
print(i.eval("this command does not exist"))
```

Output:

```
test

test1: Test docstring.

And we can have multiple lines, too.
  - some
  - list

  \```
  example = "code"
  \```

device
  connect

  disconnect

  status

  default

status
  default

['Starting test.']
test 

["Use 'device help' for all options."]
device 
  connect

  disconnect

  status

  default

["Connecting to device(s). ('rigol',)"]
["Connecting to device(s). ('rigol', 'rigol1')"]
['Displaying device status for rigol.']
Command 'this' not found in ['test', 'test1', 'device', 'status'].
--------------------------------------------------------------------------------
Usage: 
test

test1: Test docstring.

And we can have multiple lines, too.
  - some
  - list

  \```
  example = "code"
  \```

device
  connect

  disconnect

  status

  default

status
  default
```
