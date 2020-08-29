# Transform

## Introduction

In an Extract Transform Load (ETL) pipeline, the "transform" step will process
the data in order to prepare them for downstream steps, such as loading. For
example, it may be required to change the data structure, clean the data to
remove invalid values, etc.

It is important to store raw data in a durable storage system before any
processing, to allow reproducibility. Also, it is preferable to load data in a
database before performing any transformation. This will facilitate access by
end users, and leverage the power of database languages (SQL etc) for data
transformation. However, one may have to perform these transformations in
Python. The Python standard library contains the `csv` module for operations on
comma-separated values (CSV) files. Another very populat data transformation and
analysis library is [`pandas`](https://pandas.pydata.org).

## What is a CSV file?

CSV stands for "comma-separated values`. It is a two-dimensional format which
presents data in a spreadsheet-like way, with data attributes stored as columns
and data records stored as rows.

The CSV format has been around for a very long time, but a consensual
definition was proposed relatively recently, and is described in
[RFC4180](https://tools.ietf.org/html/rfc4180.html). Despite this
standardization effort, most data providers interpret the CSV format rather
freely and it is not rare to encounter trouble when loading a "raw" CSV file
into a relational database.

## Python standard library's `csv` module

The [`csv` module](https://docs.python.org/3/library/csv.html#module-csv)
provides classes and other utilities to read and write CSV files. 

### csv reader

The first example uses the `reader` function, which returns a reader object, to read the
contents of the file `friends.csv`.

`friends.csv`
```
id,name,birthday,height
1,alice,1990-01-01,1.75
2,ben,1990-01-02,1.76
3,charlie,1990-01-03,1.77
```

```
import csv

with open("friends.csv") as f:
    reader = csv.reader(f)
    columns = next(reader)
    print("columns:", columns)
    for row in reader:
        print(row)
```

The `reader` object is iterable so we can use the builtin function `next`,
which returns the next element, to read the column names. We then use the for
loop to go through all rows in the file.

### csv DictReader

The `DictReader` function returns a reader object which maps the data in each
row to a dictionary whose keys are given by the optional `fieldnames` parameter, that
is to say that `fieldnames` specifies column names. If this parameter is omitted,
the values of the first row serve as column names.

```
import csv

with open("friends.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print("Name:", row["name"])
```

If a row has more fields than `fieldnames`, the remaining data is put in a list
and stored with the field name specified by the `DictReader` optional parameter
`restkey` (defaults to None).

If a row has fewer fields than `fieldnames`, the missing values are filled with
the value specified by the optional parameter `restval` (defaults to None).

`friends_2.csv`
```
1,alice,1990-01-01,1.75
2,ben,1990-01-02,1.76,USA
3,charlie,1990-01-03
```

```
import csv

COLUMN_NAMES = ("id", "name", "birthday", "height")

with open("friends_2.csv") as f:
    reader = csv.DictReader(
        f,
        fieldnames=COLUMN_NAMES,
        restkey="rest",
        restval="NULL",
    )
    for row in reader:
        print(row)
```

### Other read parameters

One can specify other parameters when reading a CSV file, such as the field
delimiter, the quote character, and the escape character.

Although the comma (,) is usually used for CSV files, the pipe (|) is often
used because it's less frequent or even absent from text and pipe-separated
files are less likely to be perturbed by commas in the text fields.

To avoid field separation to be perturbed by commas or newline characters within text
fields, one can quote fields. RFC4180 says that one should only use
double-quotes, but some programs (such as Microsoft Excel) do not use double
quotes.

Another way to allow text fields to contain the field delimiter (e.g. comma) is
to escape them using a specified escape character.

Let's use these parameters to read files with a formatting of their own. The
file `friends_3.csv` uses pipes as field delimiters.

`friends_3.csv`
```
id|name|birthday|height|address
1|alice|1990-01-01|1.75|101 Forest St, Albany, NY
2|ben|1990-01-02|1.76|22 Pond Avenue, Philadelphia, PA
3|charlie|1990-01-03|1.77|3 Nature Place, Little Rock, AR
```

```
import csv

with open("friends_3.csv") as f:
    reader = csv.DictReader(f, delimiter="|")
    for row in reader:
        print(row)
```

The file `friends_4.csv` uses double quotes to quote the address field. The double
quote is the default `quotechar` value, we write it for illustration purposes.

`friends_4.csv`
```
id,name,birthday,height,address
1,alice,1990-01-01,1.75,"101 Forest St, Albany, NY"
2,ben,1990-01-02,1.76,"22 Pond Avenue, Philadelphia, PA"
3,charlie,1990-01-03,1.77,"3 Nature Place, Little Rock, AR"
```

```
import csv

with open("friends_4.csv") as f:
    reader = csv.DictReader(f, quotechar='"')
    for row in reader:
        print(row)
```

The file `friends_5.csv` uses a backslash (\) to escape commas within text
fields while field delimiters are also commas.

`friends_5.csv`
```
id,name,birthday,height,address
1,alice,1990-01-01,1.75,101 Forest St\, Albany\, NY
2,ben,1990-01-02,1.76,22 Pond Avenue\, Philadelphia\, PA
3,charlie,1990-01-03,1.77,3 Nature Place\, Little Rock\, AR
```

```
import csv

with open("friends_5.csv") as f:
    reader = csv.DictReader(f, escapechar="\\")
    for row in reader:
        print(row)
```

Note that to specify the backslash as an escape character, we need to escape it
using another backslash otherwise it will escape the double quote which
terminates the string.

### csv writer and DictWriter

The function `writer` allows to write a CSV from a list containing row fields.

```
import csv

with open("new_friends.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["4", "derek", "1990-01-04", "1.78"])
    writer.writerow(["5", "eric", "1990-01-05", "1.79"])
```

The function DictWriter allows to write a CSV from a dictionary where keys
contain column names and values contain values for the corresponding columns.

```
import csv

COLUMN_NAMES = ("id", "name", "birthday", "height")

with open("new_friends.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=COLUMN_NAMES)
    writer.writeheader()  # write column names
    writer.writerow({"id": "6", "name": "filip", "birthday": "1990-01-06", "height": "1.80"})

    writer.writerow({"id": "7", "name": "gerard", "birthday": "1990-01-07", "height": "1.81"})
```

### More on quoting

We have seen the use of the optional parameter `quotchar`.  Whether quoting is used
or not depends on the optional parameter `quoting`, which can take the following values:

* csv.QUOTE_NONE: the writer object will never quote fields, you need to make
  sure that delimiters that occur in the data are escaped
* csv.QUOTE_MINIMAL: the writer object will only quote fields which contain
  special characters (e.g. delimiter, quotechar, lineterminator).
* csv.QUOTE_NONNUMERIC: the writer object will quote all non-numeric fields,
  the reader will convert all non-quoted fields to `float`
* csv.QUOTE_ALL: the writer object will quote all fields

### Dialects

Rather than individually passing all the parameters which are used to control
how to read or write data, we can group them into a *dialect* object. The `csv`
module includes three dialects:

* excel: default export format for Microsoft Excel
* excel-tabs: default export format for Excel-generated TAB-delimited files
* unix: uses `\n` as newline character and quoting all fields

You can register your own dialect and use it to read and write CSV files:

```
import csv

csv.register_dialect(
    "pipes",  # dialect name
    delimiter="|",
    quotechar='"',
    escapechar="\\",
    quoting=csv.QUOTE_ALL,
)

with open("myfile.csv") as f:
    reader = csv.DictReader(f, dialect="pipes")  # use a custome dialect
    for row in reader:
        print(row)
```
