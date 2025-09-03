package com.jonathanschnabel;

import org.apache.flink.table.functions.ScalarFunction;


public class SubstringFunction extends ScalarFunction {
    public String eval(String str, Integer begin, Integer end) {
        return str.substring(begin, end);
    }
}
