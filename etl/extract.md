# Extract data

## Overview

Data extraction is often the first step of a data processing pipeline, such as
an Extract Transform Load (ETL) pipeline. We'll discuss how to download and
extract data from common data sources (HTTP servers, FTP servers, SFTP server,
APIs, web scraping, etc). We'll make the effort of using mainly the standard
Python library, but also introduce third party libraries where relevant, as
these libraries often offer a higher level interface to these processes, making
the job of the data engineer easier and more efficient.

## Download files via HTTP

The `urllib` library provides a nice set of functions to interact with Uniform
Resource Locators (URLs). The module `urllib.request` can fetch URLs using
several protocols including HTTP (HyperText Transfer Protocol), which is the
foundation of data transfer on the web.

Let's download a CSV file from the [UC Irvine machine learning
repository](https://archive.ics.uci.edu/ml/index.php). We'll download a CSV
file which contains a dataset for prediction of diabetes risk.

```
import urllib.request

# writing URL on 2 lines to keep line length < 79 characters (PEP8)
URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00529/"
    "diabetes_data_upload.csv"
)

with urllib.request.urlopen(URL) as response:
    contents = response.read()
```

HTTP is based on client requests and server responses. The function `urlopen`
returns a response in the form of a *file-like object*, so we can call the
method `read()` on it. We use a context manager (`with`) which will manage file
opening and closing for us, even in the case of an error.

The method `read()` of the response returns bytes, not a string, so we need to
decode them to perform string operations. Also, the response is iterable.

```
with urllib.request.urlopen(URL) as response:
    for line in response:
        print(line.decode("utf-8").rstrip())  # remove newline characters
```

Usually we want to store the URL content in a file. This is easily done with
the help of the `shutil` library, which provides an interface for high level
operations on files. We open the output file in `wb` mode to write bytes.

```
with urllib.request.urlopen(URL) as response:
    with open("diabetes.csv", "wb") as outfile:
        shutil.copyfileobj(response, outfile)
```

As an exercise, write a script which takes two command line arguments: a URL
and a file name. Your script will download the URL and store it under the
provided file name.

If you would like to learn more about this topic, read [this
tutorial](https://docs.python.org/3/library/urllib.request.html) about
`urllib`, where they discuss error management, authentication, the use of
proxies, etc.
