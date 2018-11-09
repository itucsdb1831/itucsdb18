import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
    "CREATE TABLE IF NOT EXISTS DUMMY (NUM INTEGER)",
    "INSERT INTO DUMMY VALUES (42)",
]

if __name__ == "__main__":
    dsn = "user='khxcpxyuayifiy'" \
          + " password='a71d836a4a3e8c9d4030a8bd40ffec8d7e43202bf75ece49c4635701c10cd21f'" \
          + " host='ec2-54-247-124-154.eu-west-1.compute.amazonaws.com'" \
          + " port=5432" \
          + " dbname=dd7j2nqkjb2bs9"
    connection = dbapi2.connect(dsn)

    cursor = connection.cursor()
    for statement in INIT_STATEMENTS:
        cursor.execute(statement)
    statement = "SELECT * FROM DUMMY"
    cursor.execute(statement)
    for row in cursor:
        num = row
        print("%s" % num)

    cursor.execute("CREATE TABLE USERS (USER_ID SERIAL PRIMARY KEY, NAME VARCHAR(20), PASSWORD VARCHAR(87))")
    connection.commit()

    cursor.close()

    connection.close();
