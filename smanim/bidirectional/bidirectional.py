import ast
from typing import NamedTuple
from smanim.canvas import BROWSER_ENV
from smanim.mobject.mobject import Mobject


# linecache doesn't work in pyodide, so mock it
# also file contents must be cached before running: from smanim import *
# in javascript, run in pyodide:
# from smanim.bidirectional.custom_linecache import CustomLineCache
# CustomLineCache.cache(__name__, "${curCode}")

if BROWSER_ENV:
    from smanim.bidirectional.custom_linecache import CustomLineCache as linecache
else:
    import linecache

__all__ = ["trace_assignments", "global_trace_assignments", "reset_bidirectional"]


class FunctionTodo(NamedTuple):
    line_to_process: str | None
    var_to_capture: str | None


# The goal is to capture all variable assignment to mobjects made by the user and to update the mobjects with inspected data after their line is run
# Line events occur before the execution of any statement in python
# When a line event is an assignment to a mobject, attach metadata about the var name and line number to the mobject
# Lines must be processed after it completely runs or the function returns
# Beware that a mobject may enter a new frame context that needs its own processing before the assignment completes
# e.g. `mob = CustomMobject()` and inside CustomMobject `s = Square()`
# Edge Case: The last line cannot be an assign anyway, because it must be canvas.draw() in browser


# called to reset global state without re-importing all modules on pyodide side

processed_lines = set()

# map from frame_id => metadata for var assign capture
# line events
function_todos: dict[str, FunctionTodo] = {}


def reset_bidirectional():
    global processed_lines, function_todos
    function_todos = {}
    processed_lines = set()


def update_mobject_metadata(
    mobject: Mobject, var_to_capture: str, line_to_process: int
):
    print(
        f"Updated mobject with data from assignment with var: {var_to_capture} at line {line_to_process}.\nMobject: {mobject}"
    )
    mobject.parent = None
    mobject.subpath = var_to_capture
    mobject.direct_lineno = line_to_process


# Note: does not handle recursion right now, but it is possible by tracking call depth
def trace_assignments(frame, event, arg):
    current_file = frame.f_code.co_filename

    frame_id = id(frame)

    if frame.f_globals.get("__name__", "_NotNamed") == "__main__":
        lineno = frame.f_lineno
        if event == "line":
            line = linecache.getline(current_file, lineno).strip()
            # Capture previous line_to_process after it has been executed
            if frame_id in function_todos:
                line_to_process, var_to_capture = function_todos[frame_id]

                if line_to_process is not None and lineno > line_to_process:
                    value = frame.f_locals.get(var_to_capture, "Unavailable")
                    if isinstance(value, Mobject):
                        update_mobject_metadata(
                            mobject=value,
                            var_to_capture=var_to_capture,
                            line_to_process=line_to_process,
                        )

                    del function_todos[frame_id]

            if line and not line.startswith("#") and lineno not in processed_lines:
                processed_lines.add(lineno)
                try:
                    tree = ast.parse(line, mode="exec")
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign) and len(node.targets) == 1:
                            target = node.targets[0]
                            if isinstance(target, ast.Name):
                                # Schedule this line to capture value after its execution
                                function_todos[frame_id] = FunctionTodo(
                                    line_to_process=lineno,
                                    var_to_capture=target.id,
                                )
                except SyntaxError:
                    pass

        if event == "return":
            if frame_id in function_todos:
                line_to_process, var_to_capture = function_todos[frame_id]
                if line_to_process is not None and lineno >= line_to_process:
                    value = frame.f_locals.get(var_to_capture, "Unavailable")
                    if isinstance(value, Mobject):
                        update_mobject_metadata(
                            mobject=value,
                            var_to_capture=var_to_capture,
                            line_to_process=line_to_process,
                        )
                    del function_todos[frame_id]

    return trace_assignments


def global_trace_assignments(frame, event, arg):
    if event == "line" and frame.f_globals.get("__name__", "_NotNamed") == "__main__":
        return trace_assignments(frame, event, arg)
    return trace_assignments


# sys.settrace(trace_assignments)

# sys._getframe().f_trace = trace_assignments

# in case i need to settrace directly in global frame
# https://stackoverflow.com/questions/55998616/how-to-trace-code-run-in-global-scope-using-sys-settrace
# can lead to double calling
