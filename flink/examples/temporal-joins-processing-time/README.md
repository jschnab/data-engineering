## Debugging the Java app

Trying to implement the processing time temporal join using a table function,
as documented
[here](https://nightlies.apache.org/flink/flink-docs-release-2.1/docs/dev/table/sql/queries/joins/#processing-time-temporal-join).

When we run the app, we get the following error:

```
 Non rowtime timeAttribute [TIMESTAMP_LTZ(3) *PROCTIME*] passed as the argument to TemporalTableFunction
```

However, a watermark cannot be defined on a processing-time column, so looks
like we are stuck.
