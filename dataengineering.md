# Data Engineering Principles

## What is data engineering?

Data engineering is about building software that collects, processes, stores,
and display data. Such software has to move data (potentially a lot of data)
from source systems to target systems, verify data quality, transform data to server
some purpose, and store it in a way that is secure and reliable. Data
ultimately needs to be analyzed, so data stores often have to be connected to
data visualization systems.

A data engineer has to build systems with the above-mentioned properties. In
addition, she must write software that is easily maintained, testable,
version-controlled (e.g. manage software code using git), robust (i.e. manages
errors such as unexpected inputs or outputs), extensible, and follows other
good software engineering practices.

Many excellent discussions about data engineering have been written and made
accessible for free on the web. In [this
article](https://medium.com/@richard534/getting-started-with-data-engineering-3d2e728d0c1f),
Richard Taylor describes how data engineers are responsible for designing and
maintaining the software and infrastructure architecture that supports
data-driven decisions. He also describes the technical landscape that data
engineers live in. In an
[article](https://www.freecodecamp.org/news/the-rise-of-the-data-engineer-91be18f1e603/) that aimed at being a manifesto for data engineering, Maxime Beauchemin describes a consensual view about data engineering, its roles, the skills it requests, and its responsabilities.

In this document we describe several properties that one should keep in mind
when designing and implementing software that processes data.

## Analysis reproducibility

*Reproducibility* is a property of a program that allows it to be run and
reproduce past results at any time, using the original data.

Imagine you have a program that downloads data every day and saves it as an
immutable artifact, does some analysis, and saves the results. If you realize that a past result is wrong, you would like to find the original input data and reproduce the error. Once you correct your program, you would then like to correct past results by re-running the program on past data.

Analysis reproducibility depends on your data to be stored as *immutable
artifacts*, and also on another property of your program called *determinism*.

## Data immutability

*Immutability* is a property of data object that prevents it to be changed. Once
the data value is defined, it cannot changed and will remain the same until the
object is deleted.

Immutability is an important property of data *artifacts* (a file stored on disk, an in-memory object, etc) because it allows re-processing of data at any time. For example, if a data processing program delivers wrong results for some reason, data immutability ensures the data is still available for debugging and re-processing at any time in the future.

## Deterministic data storage and program behavior

In order to obtain reproducible analysis results, one has to enforce
determinism when storing data and writing a the program that performs the
analysis.

Deterministic data storage means that the location of a file will always be the
same for a given program and a given set of input parameters defined by the
user. In other words, the same input results in the same output. When
re-running a past analysis, this will allow the program to find past data and
process it, which is necessary for analysis reproducibility.

A deterministic program will always give the same output given the same input.
This is not necessarily difficult to achieve in theory. In practice, a crucial
aspect is to allow the program user to explicitly define input parameters, for
example using function arguments, a configuration file, etc. The program should
not accept implicit input such as system date and time.

Let's take the example of a scheduled data analysis that runs at defined time
intervals. The program downloads data at 9AM every morning, performs some
analysis, and saves the results in a file. The programmer should design the
program to take the date and time as input settings (e.g. function parameters),
and add these to the path where files are stored. This achieves both storage
and program determinism, and allows the user to manually re-run the program on
old data by manually passing the date and time.

## Program idempotency

*Idempotency* is a property of programs that allows them to be run multiple
times without changing the result after the initial run. For example, the "on"
button on a TV remote is idempotent: initially pressing "on" turns the TV on
but pressing the "on" button additional times does not affect the TV state
anymore. Likewise, the "off" button on the TV remote is idempotent.

Let's take the example of an automated data processing program that downloads data and loads it into a database on a daily basis. One day, the server running the program crashes just after data loading but before the program finishes. After the server restarts, it may re-run the program on the same data since the previous run did not finish. If the program is not idempotent, it may load duplicate data into the database and lead to wrong data analysis results. In this case, there are several ways to enforce idempotency during data loading. The program could delete data corresponding to the runtime date. Another possibility is to skip the data loading step if such data is detected. The preferrable option depends on the ultimate goal of this program.

## Data validation

A data processing program should validate the data it receives. Validation of
output data may be necessary: if the program is deterministic and
its components are thoroughly tested, this limits the opportunities for output
data to be invalid.

Valid data is by definition necessary for a program to produce correct results.
Invalid data may not always result in the program encounter an error and stop,
but produce subtle errors that are difficult to identify.

Data validation checks for several data properties, including:

* a file name has the correct format
* file encoding is as expected (utf-8, latin-1, etc)
* data items have the correct format (e.g. dates are correctly formated,
  integers have only numeric characters, etc)
* a CSV file has the correct number number of columns
* a CSV file has the correct column names
* a CSV file has the expected delimiter

The list of possible data validation steps can be very large, the required
steps depend on the specific case.

## Automated and scheduled programs

Many data processing programs must run regularly, for example daily. Automating
program runs has many benefits including fewer errors, less manual labor, etc.
There are many systems that allow scheduling of programs. Some of the best
tools include [cron](https://en.wikipedia.org/wiki/Cron) jobs and [Apache Airflow](https://airflow.apache.org).

Cron is a time-based job scheduler in Unix-based systems. Cron jobs are useful
for scheduling tasks such as system maintenance-related tasks.

Airflow is an open-source scheduling software written in Python and including a web
interface. It is easy to use, allows the setup of complex jobs, and offers extensive logging, monitoring and alerting features.

## Stateless compute resources

Computers and operating systems can fail at any time: fatal OS errors, loss of power,
hardware failues, etc. can stop your data analysis tasks. This may
lead to the loss of data stored on the computer running your program. Data
analysis programs must be designed with these failures in mind, and save data
redundantly on a highly available storage system. This way, if the server
running your program fails and must stop, the same or a different server can
start and resume the program close to where it stopped, using data saved on a
storage independant of server health and performance.
