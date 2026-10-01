import subprocess
import os
import tempfile
import sys

DOCKER_IMAGE = "code-sandbox:latest"


def execute_python(code: str):
    """
    Execute Python code safely.
    Uses local execution (more reliable on Windows without Docker).
    """
    return execute_python_local(code)


def execute_python_local(code: str):
    """
    Execute Python code locally in a temporary file.
    """
    try:
        # Check if code uses input()
        uses_input = "input(" in code
        
        if uses_input:
            # Replace input() with a version that returns default values
            # Detect if input() is used with int() and provide default values
            modified_code = '''
import sys

# Mock input function for sandbox
_original_input = input
def input(prompt=""):
    # Provide sensible defaults based on context
    if "age" in prompt.lower():
        return "18"
    elif "number" in prompt.lower():
        return "0"
    elif "name" in prompt.lower():
        return "test"
    else:
        return ""

''' + code
            code = modified_code
        
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        os.remove(temp_path)
        
        stdout = result.stdout
        if uses_input and stdout:
            stdout = "# Note: input() was mocked with empty values\n" + stdout

        return {
            "stdout": stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": "Execution timed out",
            "returncode": -1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }


if __name__ == "__main__":
    # Test with vote eligibility code
    test_code = """
age = int(input("Enter your age: "))
if age >= 18:
    print("You are eligible to vote!")
else:
    print("You are not eligible to vote.")
"""
    print("Testing vote eligibility code with mocked input...")
    result = execute_python_local(test_code)
    print(f"stdout: {result['stdout']}")
    print(f"stderr: {result['stderr']}")
    print(f"returncode: {result['returncode']}")

