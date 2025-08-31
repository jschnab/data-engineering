package com.jonathanschnabel;

import java.io.InputStream;
import java.io.IOException;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.StandardCharsets;

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

        String create_model = file_reader.readSqlFile("/create_model.sql");
        env.executeSql(create_model);
    }
}
