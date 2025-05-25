import os
import subprocess
import sys

def codegen():
    source_dir = os.path.abspath("./bindings/codegen")
    build_dir = os.path.abspath("./bindings/codegen/build")
    executable = os.path.join(build_dir, "Codegen.exe")
    release_executable = os.path.join(build_dir, "Release", "Codegen.exe")

    os.makedirs(build_dir, exist_ok=True)

    cmake_configure_cmd = [
        "cmake",
        "-S", source_dir,
        "-B", build_dir,
    ]

    print("Configuring CMake...")
    result = subprocess.run(cmake_configure_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("CMake configuration failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    cmake_build_cmd = [
        "cmake",
        "--build", build_dir,
        "--config", "Release"
    ]

    print("Building project...")
    result = subprocess.run(cmake_build_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Build failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    if os.path.isfile(executable):
        exe_to_run = executable
    elif os.path.isfile(release_executable):
        exe_to_run = release_executable
    else:
        print(f"Executable not found in expected locations:")
        print(f"  {executable}")
        print(f"  {release_executable}")
        sys.exit(1)

    args = [
        exe_to_run,
        "Win64",
        "bindings/bindings/2.2074",
        "./"
    ]

    print("Running executable:")
    print(" ".join(args))

    result = subprocess.run(args, text=True)
    if result.returncode != 0:
        print(f"Execution failed with return code {result.returncode}")
        sys.exit(1)
