package com.jonathanschnabel;

import org.apache.flink.table.functions.ScalarFunction;


public class SumFunction extends ScalarFunction {

    public Integer eval(Integer a, Integer b) {
        return a + b;
    }

    public Integer eval(Integer... values) {
        Integer result = 0;
        for (Integer val : values) {
            result += val;
        }
        return result;
    }

    public Integer eval(String a, String b) {
        return Integer.valueOf(a) + Integer.valueOf(b);
    }
}
