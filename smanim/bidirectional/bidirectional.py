import ast
from types import FrameType
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
    end_line_to_process: str | None
    var_to_capture: str | None


# The goal is to capture all variable assignment to mobjects made by the user and to update the mobjects with inspected data after their line is run
# Line events occur before the execution of any statement in python
# When a line event is an assignment to a mobject, attach metadata about the var name and line number to the mobject
# Lines must be processed after it completely runs or the function returns
# Beware that a mobject may enter a new frame context that needs its own processing before the assignment completes
# e.g. `mob = CustomMobject()` and inside CustomMobject `s = Square()`
# Edge Case: The last line cannot be an assign anyway, because it must be canvas.draw() in browser


processed_lines = set()

# map from frame_id => metadata for var assign capture
# line events
function_todos: dict[str, FunctionTodo] = {}


# called to reset global state without re-importing all modules on pyodide side
def reset_bidirectional():
    global processed_lines, function_todos
    function_todos = {}
    processed_lines = set()


def update_mobject_metadata(
    mobject: Mobject, var_to_capture: str, line_to_process: int
):
    print(
        f"Var '{var_to_capture}' assigned at line {line_to_process} for mobject: {mobject}"
    )
    mobject.parent = None
    mobject.subpath = var_to_capture
    mobject.direct_lineno = line_to_process


# Note: does not handle recursion right now, but it is possible by tracking call depth
def trace_assignments(frame: FrameType, event, arg):
    current_file = frame.f_code.co_filename

    frame_id = id(frame)

    if frame.f_globals.get("__name__", "_NotNamed") == "__main__":
        lineno = frame.f_lineno
        if event == "line":
            expr_str, end_lineno = get_ast_node_span(current_file, lineno)

            # Capture previous line_to_process after it has been executed
            if frame_id in function_todos:
                line_to_process, end_line_to_process, var_to_capture = function_todos[
                    frame_id
                ]

                if line_to_process is not None and lineno > end_line_to_process:
                    value = frame.f_locals.get(var_to_capture, "Unavailable")
                    if isinstance(value, Mobject):
                        update_mobject_metadata(
                            mobject=value,
                            var_to_capture=var_to_capture,
                            line_to_process=line_to_process,
                        )

                    del function_todos[frame_id]

            if (
                expr_str
                and not expr_str.startswith("#")
                and lineno not in processed_lines
            ):
                processed_lines.add(lineno)
                try:
                    tree = ast.parse(expr_str, mode="exec")
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Assign) and len(node.targets) == 1:
                            target = node.targets[0]
                            if isinstance(target, ast.Name):
                                # Schedule this line to capture value after its execution
                                function_todos[frame_id] = FunctionTodo(
                                    line_to_process=lineno,
                                    var_to_capture=target.id,
                                    end_line_to_process=end_lineno,
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


# see how to use these functions in tracing_demo.py


def get_ast_node_span(file, target_lineno):
    content = "".join(linecache.getlines(file))
    root = ast.parse(content, filename=file)

    for node in ast.walk(root):
        if isinstance(node, ast.Assign):
            start_lineno = node.lineno
            end_lineno = getattr(node, "end_lineno", start_lineno)

            if start_lineno == target_lineno:
                statement_lines = []
                for lineno in range(start_lineno, end_lineno + 1):
                    statement_lines.append(linecache.getline(file, lineno).strip())
                return " ".join(statement_lines), end_lineno

    return None, None
