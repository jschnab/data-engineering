CREATE TABLE customers (
    id DECIMAL(38) PRIMARY KEY NOT ENFORCED -- BIGINT does not work
    , name STRING
    , country STRING
    , zip STRING
) WITH (
    'connector' = 'jdbc'
    , 'url' = 'jdbc:mysql://localhost:3306/customerdb'
    , 'table-name' = 'customers'
    , 'username' = '<paste-username-here>'
    , 'password' = '<paste-password-here>'
);
