SELECT *
FROM tickers
    MATCH_RECOGNIZE (
        PARTITION BY symbol
        ORDER BY ts
        MEASURES
            START_ROW.ts AS start_tstamp,
            LAST(PRICE_DOWN.ts) AS bottom_tstamp,
            LAST(PRICE_UP.ts) AS end_tstamp
        ONE ROW PER MATCH
        AFTER MATCH SKIP TO LAST PRICE_UP
        PATTERN (START_ROW PRICE_DOWN{5,} PRICE_UP)
        DEFINE
            PRICE_DOWN AS
                (LAST(PRICE_DOWN.price, 1) IS NULL AND PRICE_DOWN.price < START_ROW.price) OR
                    PRICE_DOWN.price < LAST(PRICE_DOWN.price, 1),
            PRICE_UP AS
                PRICE_UP.price > LAST(PRICE_DOWN.price, 1)
    ) MR;
