import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from nanomemo import Memory

print("Importing Memory...")
memory = Memory("./test_memory_init")
print("Memory initialized successfully")

# Test basic operations
memory.write(
    path="test.md",
    content="# Test\nHello world",
    summary="Test file",
    tags=["test"]
)
print("Write successful")

content = memory.read("test.md")
print(f"Read successful: {content[:20]}...")
