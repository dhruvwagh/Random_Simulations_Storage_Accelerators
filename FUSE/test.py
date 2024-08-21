import os
import time

def test_virtual_storage(mount_point):
    print("Starting FUSE Virtual Storage Test")
    print("-----------------------------------")

    # Test file creation and writing
    print("1. Creating and writing to a file")
    with open(os.path.join(mount_point, "test1.txt"), "w") as f:
        f.write("Hello, Virtual World!")
    print("   File created and written")

    # Test reading from file
    print("\n2. Reading from the file")
    with open(os.path.join(mount_point, "test1.txt"), "r") as f:
        content = f.read()
    print(f"   File content: {content}")

    # Test appending to file
    print("\n3. Appending to the file")
    with open(os.path.join(mount_point, "test1.txt"), "a") as f:
        f.write(" Appended content.")
    print("   Content appended")

    # Test reading after append
    print("\n4. Reading file after append")
    with open(os.path.join(mount_point, "test1.txt"), "r") as f:
        content = f.read()
    print(f"   File content: {content}")

    # Test creating multiple files
    print("\n5. Creating multiple files")
    for i in range(2, 5):
        with open(os.path.join(mount_point, f"test{i}.txt"), "w") as f:
            f.write(f"This is test file {i}")
    print("   Multiple files created")

    # Test listing directory contents
    print("\n6. Listing directory contents")
    files = os.listdir(mount_point)
    print(f"   Files in directory: {files}")

    # Test file deletion
    print("\n7. Deleting a file")
    os.remove(os.path.join(mount_point, "test2.txt"))
    print("   test2.txt deleted")

    # Test listing directory contents after deletion
    print("\n8. Listing directory contents after deletion")
    files = os.listdir(mount_point)
    print(f"   Files in directory: {files}")

    print("\nFUSE Virtual Storage Test Completed")

if __name__ == "__main__":
    mount_point = "/tmp/virtual_storage"
    test_virtual_storage(mount_point)