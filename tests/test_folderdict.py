"""
Use named temporary folder to fecilitate test cases,
Write test cases for
1) get,set,delete
2) file not found error
3) keys
4) contains
"""
import tempfile
import os

from boltons.folderdict import FolderDict

with tempfile.TemporaryDirectory() as directory_name:
    folder_dict = FolderDict(directory_name)
    folder_dict["File1"] = "Sample file1"

    assert os.listdir(directory_name) == ["File1"]
    assert open(os.path.join(directory_name, "File1")).read() == "Sample file1"

    val = folder_dict.pop("File1")
    assert val == "Sample file1"

    try:
        new_value = folder_dict["Another File"]
    except FileNotFoundError:
        val = "Correct exception raised"

    assert val == "Correct exception raised"

    folder_dict["File2"] = "Sample file2"
    folder_dict["File3"] = "Sample file3"
    folder_dict["File4"] = "Sample file4"

    assert sorted(os.listdir(directory_name)) == sorted(folder_dict.keys())

    assert os.path.isfile(os.path.join(directory_name, "File2"))
    assert os.path.isfile(os.path.join(directory_name, "File3"))








