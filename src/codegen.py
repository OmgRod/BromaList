import os
import subprocess
import sys

def codegen():
    source_dir = os.path.abspath("./bindings/codegen")
    build_dir = os.path.abspath("./bindings/codegen/build")
    executable = os.path.join(build_dir, "Codegen.exe")

    # Create build directory if it doesn't exist
    os.makedirs(build_dir, exist_ok=True)

    # Step 1: Configure CMake
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

    # Step 2: Build with CMake
    cmake_build_cmd = [
        "cmake",
        "--build", build_dir,
        "--config", "Release"  # or Debug if you want
    ]

    print("Building project...")
    result = subprocess.run(cmake_build_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Build failed:")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    # Step 3: Run the executable with the specified arguments
    if not os.path.isfile(executable):
        print(f"Executable not found: {executable}")
        sys.exit(1)

    args = [
        executable,
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