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

        env.createTemporarySystemFunction("SubstringFunction", SubstringFunction.class);

        Table mytable = env.fromValues(
            DataTypes.ROW(
                DataTypes.FIELD("id", DataTypes.BIGINT()),
                DataTypes.FIELD("name", DataTypes.STRING())
            ),
            row(1, "Alice"),
            row(2, "Bob"),
            row(3, "Charlie"),
            row(4, "Derek")
        );

        Table substring_name = mytable.select(
            $("id"),
            call("SubstringFunction", $("name"), 1, 3)
        );

        env.executeSql(
            "CREATE TABLE print_results (id BIGINT, name STRING) WITH ('connector' = 'print')"
        );

        substring_name.executeInsert("print_results");
    }
}
