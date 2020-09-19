# File Compression and Archiving

## Overview

When storing files or transfering them over the network, it is often convenient
to compress them and package them into a single archive. This saves both space
and time.

Python's standard library provides tools to deal with file compression and
archiving, such as the `zipfile` library.


## The `zipfile` library

The `zipfile` [library](https://docs.python.org/3.7/library/zipfile.html) defines
classes and functions to work with ZIP archives. A ZIP archive is a file which
stores files (usually) compressed with a compression algorithm (DEFLATE,
Burrows-Wheeler, etc).

The `ZipFile` class allows to open a ZIP file for reading, writing, and
appending. It also allows to chose the compression method and the compression
level.

### Extracting ZIP archives

We can open a ZIP archive and display the list of files it stores. The method
`namelist()` returns a list of file names.

```
import zipfile

with zipfile.ZipFile("data.zip", "r") as f:
    f.namelist()
```

We can extract a single file at a time, or all files at once. We can specify
the path where to extract files with the `path` argument, which is useful if we
use, say, a temporary directory.

```
import os
import zipfile

from tempfile import TemporaryDirectory
# extract a single file in the current directory
with zipfile.ZipFile("data.zip", "r") as f:
    f.extract("file1.csv")

# extract all files in a temporary directory
with TemporaryDirectory() as temp_dir:
    with zipfile.ZipFile("data.zip", "r") as f:
        f.extract_all(path=temp_dir)
```

### Creating ZIP archives

We create a new ZIP archive by using `ZipFile` in *write* mode (`"w"`):

```
import zipfile

to_compress = ("readme.txt", "description.txt", "data.csv")
with zipfile.ZipFile("archive.zip", "w") as f:
    for name in to_compress:
        f.write(name)
```

You can also append files to an existing archive with the *append* mode
(`"a"`):

```
import zipfile

with zipfile.ZipFile("archive.zip", "a") as f:
    f.write("new_data.csv")
```
