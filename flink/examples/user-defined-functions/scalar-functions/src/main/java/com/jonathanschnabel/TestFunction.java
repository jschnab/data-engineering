package com.jonathanschnabel;

import java.math.BigDecimal;
import java.time.Instant;

import org.apache.flink.table.annotation.DataTypeHint;
import org.apache.flink.table.annotation.InputGroup;
import org.apache.flink.table.functions.ScalarFunction;
import org.apache.flink.types.Row;


public class TestFunction extends ScalarFunction {

    @DataTypeHint("DECIMAL(12, 3)") 
    public BigDecimal eval(Double a, Double b) {
        return BigDecimal.valueOf(a + b);
    }
}
