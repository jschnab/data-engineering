package com.jonathanschnabel;

import org.apache.flink.table.api.DataTypes;
import org.apache.flink.table.api.EnvironmentSettings;
import org.apache.flink.table.api.Table;
import org.apache.flink.table.api.TableEnvironment;
import static org.apache.flink.table.api.Expressions.*;  // provides $, row, call


public class App {

    public static void main(String[] args) throws Exception {

        EnvironmentSettings settings = EnvironmentSettings
            .newInstance()
            .inStreamingMode()
            .build();

        TableEnvironment env = TableEnvironment.create(settings);

        Table mytable = env.fromValues(
            DataTypes.ROW(
                DataTypes.FIELD("sentence", DataTypes.STRING())
            ),
            row("one upon a time"),
            row("in a galaxy far, far away")
        );

        Table splitted = mytable
            // call function inline without registration
            .joinLateral(call(SplitFunction.class, $("sentence")))
            .select($("sentence"), $("word"), $("length"));

        env.executeSql(
            "CREATE TABLE print_results (sentence STRING, word STRING, length INTEGER) "
            + "WITH ('connector' = 'print')"
        );

        splitted.executeInsert("print_results");
    }
}
