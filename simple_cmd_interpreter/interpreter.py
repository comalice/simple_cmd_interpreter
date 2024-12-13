import inspect  # provides appropriate docstring resolution on abstractmethods
from typing import Any, Dict


class InterpreterException(Exception):
    pass

class Interpreter:
    """Given a parser output and a map of values to Callables, eval the parser output."""
    IGNORE = ["summary"]

    def __init__(self, _map: Dict, prepend_help=""):
        self._map = _map
        self.prepend_help = prepend_help

    def eval(self, command: str):
        cmd_list = command.strip().split()

        _out = self._eval(cmd_list, self._map)

        # Handle interpreter exceptions.
        if type(_out[-1]) is InterpreterException:
            return f"{str(_out[-1])}\n{'-' * 80}\n" + self.prepend_help + f"{self._render_help([], self._map)}"

        return _out

    def _eval(self, cmd_list, _map: Any):
        #
        # Base Case
        #
        # If "map" is a function, call it with the remainder of the cmd_list as params.
        if callable(_map):
            try:
                _out = None
                if cmd_list:
                    _out = _map(*cmd_list)

                else:
                    _out = _map()

                # Handle functions that return None.
                if _out is None:
                    _out = True

                return [_out]

            except TypeError as e:
                raise InterpreterException(f"Command failed with params `{','.join(cmd_list)}` and "
                                             f"with exception `{e}`\n\n")

        # Check for "help" and render help strings for each method.
        if cmd_list and cmd_list[-1] == "help":
            # Strip off 'help' and evaluate docstrings.
            return self.prepend_help + self._render_help(cmd_list[:-1], _map)

        # We are out of params in cmd_list, but our map is not callable. In this case we use the "default" field.
        if not cmd_list and not callable(_map):
            return self._eval(cmd_list[1:], _map["default"])

        #
        # Recursive Case
        #
        # Dictionary - index in, call recursively.
        if type(_map) is dict:
            if cmd_list[0] not in _map:
                raise InterpreterException(f"Command '{cmd_list[0]}' not found in {[x for x, _ in _map.items()]}.")
                # return [*cmd_list,
                #         InterpreterException(f"Command '{cmd_list[0]}' not found in {[x for x, _ in _map.items()]}.")]

            # Strip first value off cmd_list, call recursively.
            _out = self._eval(cmd_list[1:], _map[cmd_list[0]])
            if type(_out) is InterpreterException:
                return [*cmd_list, _out]
            elif type(_out) is list and type(_out[-1]) is InterpreterException:
                return [*cmd_list[:-1], *_out]
            return _out

        # TODO List - Not sure what needs to happen here. Inspect semantics of lists in the map.
        # TODO Literals - Not sure what needs to happen here.
        #  Further dereferencing shouldn't happen within a map dict, the base case should always be a Callable.

    def _render_help(self, cmd_list, _map, indent=0):
        #
        # Base Case
        #
        if callable(_map):
            _c = ""
            if cmd_list:
                _c = cmd_list[0]

            # TODO sort out why inherited method docstrings are not inherited
            # See https://docs.python.org/3/library/inspect.html#inspect.getdoc
            if inspect.getdoc(_map):
                _c += ": " + inspect.getdoc(_map) + "\n"

            return _c

        else:
            # If we have commands, drill in.
            if cmd_list:
                try:
                    result = self._render_help(cmd_list[1:], _map[cmd_list[0]], indent=indent + 2)
                    if result:
                        # Try to grab a command summary.
                        summary = ""
                        if _map[cmd_list[0]].get("summary"):
                            summary = _map[cmd_list[0]]["summary"]
                        return cmd_list[0] + ": " + summary + "\n" + result

                    return cmd_list[0]
                except KeyError as e:
                    raise InterpreterException(f"{cmd_list[0]} not found in {[x for x, _ in _map.items() if x not in Interpreter.IGNORE]}.")

            # No commands, render the whole tier of commands.
            else:
                _out = ""
                for k, v in [(l, m) for l, m in _map.items() if l not in Interpreter.IGNORE]:
                    _out += " " * indent + k + "\n" + self._render_help([], v, indent=indent + 2)

                return _out

        print("ERROR: we fell out the bottom")


if __name__ == '__main__':
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
            "default": lambda: "Displaying status.",
        }
    }

    i = Interpreter(test_map)
    print(i.eval("help"))
    print(i.eval("test"))
    print(i.eval("test help"))
    print(i.eval("device"))
    print(i.eval("device help"))
    print(i.eval("device connect name"))
    print(i.eval("device connect name1 name2"))
    print(i.eval("device status name"))
    print(i.eval("this command does not exist"))
