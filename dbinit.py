import os
import sys

import psycopg2 as dbapi2
from passlib.hash import pbkdf2_sha256 as hasher

INIT_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS USERS (
        USER_ID SERIAL PRIMARY KEY,
        NAME VARCHAR(20),
        PASSWORD VARCHAR(87),
        IS_ACTIVE BOOLEAN DEFAULT TRUE,
        IS_ADMIN BOOLEAN DEFAULT FALSE,
        BALANCE NUMERIC(5,2) DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GAMES (
        GAME_ID SERIAL PRIMARY KEY,
        TITLE VARCHAR(100) UNIQUE,
        GENRE VARCHAR(100),
        RATING NUMERIC(3, 1) DEFAULT 0,
        VOTES INTEGER DEFAULT 0, 
        AGE_RESTRICTION INTEGER,
        PRICE NUMERIC(5, 2) DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS FRIENDS (
        USER1_ID INTEGER REFERENCES USERS (USER_ID),
        USER2_ID INTEGER REFERENCES USERS (USER_ID),
        DATE_BEFRIENDED DATE,
        IS_BLOCKED BOOLEAN DEFAULT FALSE,
        IS_FOLLOWING BOOLEAN DEFAULT FALSE,
        NUM_OF_SHARED_GAMES INTEGER DEFAULT 0,
        IS_FAVOURITE BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (USER1_ID, USER2_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS FRIEND_REQUESTS (
        USER_ID_FROM INTEGER REFERENCES USERS (USER_ID),
        USER_ID_TO INTEGER REFERENCES USERS (USER_ID),
        PRIMARY KEY (USER_ID_FROM, USER_ID_TO)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ITEMS (
        ITEM_ID SERIAL PRIMARY KEY,
        GAME_ID INTEGER REFERENCES GAMES (GAME_ID),
        NAME VARCHAR(100),
        RARITY VARCHAR(50),
        LEVEL INTEGER DEFAULT 1
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GAMES_OF_USERS (
        USER_ID INTEGER REFERENCES USERS (USER_ID),
        GAME_ID INTEGER REFERENCES GAMES (GAME_ID),
        TITLE VARCHAR(100) REFERENCES GAMES (TITLE),
        TIME_PLAYED INTEGER DEFAULT 0,
        TIME_PURCHASED DATE,
        NUM_OF_REVIEWS INTEGER DEFAULT 0,
        NUM_OF_SCREENSHOTS INTEGER DEFAULT 0,
        IS_FAVOURITE BOOLEAN DEFAULT FALSE,
        PRIMARY KEY (USER_ID, GAME_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS REVIEWS (
        REVIEW_ID SERIAL PRIMARY KEY,
        USER_ID INTEGER REFERENCES USERS (USER_ID),
        GAME_ID INTEGER REFERENCES GAMES (GAME_ID),
        CONTENT VARCHAR(500),
        LIKES INTEGER DEFAULT 0,
        DISLIKES INTEGER DEFAULT 0,
        LABEL VARCHAR(50)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS SCREENSHOTS (
        SHOT_ID SERIAL PRIMARY KEY,
        PHOTO VARCHAR(200),
        USER_ID INTEGER REFERENCES USERS (USER_ID),
        GAME_ID INTEGER REFERENCES GAMES (GAME_ID),
        CAPTION VARCHAR(200),
        DATE_ADDED DATE,
        LIKES INTEGER DEFAULT 0,
        DISLIKES INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS MARKET (
        ITEM_ID INTEGER REFERENCES ITEMS (ITEM_ID),
        USER_ID INTEGER REFERENCES USERS (USER_ID),
        PRICE NUMERIC(5, 2),
        DATE_PURCHASED DATE,
        DESCRIPTION VARCHAR(500),
        PRIMARY KEY (ITEM_ID, USER_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS SCREENSHOT_COMMENTS(
        COMMENT_ID SERIAL PRIMARY KEY,
        USER_ID INTEGER REFERENCES USERS(USER_ID),
        SCREENSHOT_ID INTEGER REFERENCES SCREENSHOTS(SHOT_ID),
        COMMENT VARCHAR(500),
        COMMENT_DATE DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS BALANCE_CODES(
        CODE VARCHAR(20) PRIMARY KEY
    )
    """,
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

    password = "asdf"
    hashed_password = hasher.hash(password)
    statement = "INSERT INTO USERS(NAME, PASSWORD, IS_ADMIN) VALUES(%s, %s, %s)"
    data = ("emre", hashed_password, True)
    cursor.execute(statement, data)

    statement = "INSERT INTO BALANCE_CODES VALUES(%s)"
    data = "1234"
    cursor.execute(statement, [data])

    statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, 12, 0.00)"
    data = ("team fortress 2", "fps")
    cursor.execute(statement, data)

    statement = """INSERT INTO ITEMS(GAME_ID, NAME, RARITY, LEVEL)
                    VALUES (1, 'Bag', 'Common', 10),
                            (1, 'Jacket', 'Rare', 25),
                            (1, 'Shoe', 'Very rare', 30)"""
    cursor.execute(statement)

    connection.commit()
    cursor.close()

    connection.close()
