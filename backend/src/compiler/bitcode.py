import subprocess
import os

def compile_to_bitcode(source_path, output_dir):
    """
    Compile a C/C++ source file to LLVM bitcode (.bc) using clang.
    """
    os.makedirs(output_dir, exist_ok=True)
    bc_path = os.path.join(output_dir, "program.bc")

    cmd = [
        "clang", "-emit-llvm", "-c", source_path, "-o", bc_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Compilation failed:\n{result.stderr}")

    return bc_path
