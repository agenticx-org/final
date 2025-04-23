import unittest
from researchinc.service.code_executor import CodeExecutor


class TestCodeExecutor(unittest.TestCase):
    """Test cases for the CodeExecutor class."""

    def test_globals_locals_availability(self):
        """Test that globals_locals are available inside the exec() function."""
        # Initialize the CodeExecutor with some initial globals
        initial_globals = {
            "test_var": "test_value",
            "test_function": lambda x: x * 2
        }
        executor = CodeExecutor(initial_globals)
        
        # Create a code snippet that prints out the available globals_locals
        code_snippet = """
# Print all available globals_locals
print("Available globals_locals:")
# Create a copy of globals() to avoid the "dictionary changed size during iteration" error
globals_copy = dict(globals())
for key, value in globals_copy.items():
    if not key.startswith('__'):
        print(f"{key}: {value}")
        
# Try to access the initial globals
print(f"test_var: {test_var}")
print(f"test_function(5): {test_function(5)}")

# Try to access the inference_repository
print(f"inference_repository available: {inference_repository is not None}")
"""
#         code_snippet = """
# print("Hello, world!")
# result = inference_repository.find_total_scores_by_user()
# print(result)
# """
        # Execute the code snippet
        result = executor.execute(code_snippet)
        print(result)


if __name__ == "__main__":
    unittest.main() 