package com.jonathanschnabel;

import java.io.InputStream;
import java.io.IOException;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;

import java.util.Map;

import org.apache.flink.table.api.EnvironmentSettings;
import static org.apache.flink.table.api.Expressions.*;  // if non-static import, have to use Expressions.$ for columns
import org.apache.flink.table.api.TableEnvironment;
import org.apache.flink.table.functions.TemporalTableFunction;


class FileReader {

    public String readSqlFile(String path) throws IOException {
        InputStream stream = getClass().getResourceAsStream(path);
        return new String(stream.readAllBytes(), StandardCharsets.UTF_8);
    }
}


public class App {

    public static void main(String[] args) throws Exception {

        EnvironmentSettings settings = EnvironmentSettings
            .newInstance()
            .inStreamingMode()
            .build();

        TableEnvironment env = TableEnvironment.create(settings);

        FileReader file_reader = new FileReader();

        String orders_sql = file_reader.readSqlFile("/create_orders_table.sql");
        env.executeSql(orders_sql);

        String currency_sql = file_reader.readSqlFile("/create_currency_table.sql");
        env.executeSql(currency_sql);

        TemporalTableFunction rates = env
            .from("currency")
            .createTemporalTableFunction($("update_time"), $("k_currency"));

        env.createTemporarySystemFunction("rates", rates);

        String view_sql = file_reader.readSqlFile("/orders_currency_join.sql");
        env.executeSql(view_sql).print();
    }
}
