CREATE FUNCTION substring_function
AS 'com.jonathanschnabel.SubstringFunction'
LANGUAGE JAVA
USING JAR '<path>/scalar-function-1.0.jar'
;
