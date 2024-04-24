import ast
import linecache
import os
import sys
from smanim.mobject.mobject import Mobject


def setup_bidirectional(file):
    target_file = os.path.abspath(file)

    processed_lines = set()
    line_to_process = None
    var_to_capture = None
    var_to_capture_frame = None

    def register_mobject(mobject: Mobject, var_to_capture: str, line_to_process: int):
        print(
            f"Registered mobject assignment with var: {var_to_capture}, value: {mobject}, at line {line_to_process}"
        )
        mobject.parent = None
        mobject.subpath = var_to_capture
        mobject.direct_lineno = line_to_process

    # Note: does not handle recursion right now, but it is possible by tracking call depth
    def trace_assignments(frame, event, arg):
        nonlocal line_to_process, var_to_capture, var_to_capture_frame
        current_file = frame.f_code.co_filename
        if current_file == target_file:
            lineno = frame.f_lineno
            if event == "line":
                line = linecache.getline(current_file, lineno).strip()
                # Capture previous line_to_process after it has been executed
                if line_to_process is not None and lineno > line_to_process:
                    value = frame.f_locals.get(var_to_capture, "Unavailable")
                    if isinstance(value, Mobject):
                        register_mobject(
                            mobject=value,
                            var_to_capture=var_to_capture,
                            line_to_process=line_to_process,
                        )

                    line_to_process = None
                    var_to_capture = None
                    var_to_capture_frame = None

                if line and not line.startswith("#") and lineno not in processed_lines:
                    processed_lines.add(lineno)
                    try:
                        tree = ast.parse(line, mode="exec")
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                                target = node.targets[0]
                                if isinstance(target, ast.Name):
                                    # Schedule this line to capture value after its execution
                                    line_to_process = lineno
                                    var_to_capture = target.id
                                    var_to_capture_frame = frame
                    except SyntaxError:
                        pass

            if event == "return":
                # covers the case where return is implicit and so does not trigger line event
                if (
                    line_to_process is not None
                    and lineno >= line_to_process
                    and var_to_capture_frame is frame
                ):
                    value = frame.f_locals.get(var_to_capture, "Unavailable")
                    if isinstance(value, Mobject):
                        register_mobject(
                            mobject=value,
                            var_to_capture=var_to_capture,
                            line_to_process=line_to_process,
                        )
                    line_to_process = None
                    var_to_capture = None
                    var_to_capture_frame = None

        return trace_assignments

    sys.settrace(trace_assignments)

    # in case i need to settrace directly in global frame
    # https://stackoverflow.com/questions/55998616/how-to-trace-code-run-in-global-scope-using-sys-settrace
    # sys._getframe().f_trace = trace_assignments
