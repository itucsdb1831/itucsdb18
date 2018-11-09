import os
import sys

import psycopg2 as dbapi2

INIT_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS USERS (
        USER_ID SERIAL PRIMARY KEY,
        NAME VARCHAR(20),
        PASSWORD VARCHAR(87)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS GAMES (
        GAME_ID SERIAL PRIMARY KEY,
        TITLE VARCHAR(100),
        GENRE VARCHAR(100),
        RATING NUMERIC(3, 1) DEFAULT 0,
        AGE_RESTRICTION INTEGER,
        PRICE NUMERIC(5, 2) DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ITEMS (
        ITEM_ID SERIAL PRIMARY KEY,
        GAME_ID INTEGER REFERENCES GAMES(GAME_ID),
        NAME VARCHAR(100),
        RARITY VARCHAR(50),
        LEVEL INTEGER DEFAULT 1
    ) 
    """,
    """
    CREATE TABLE IF NOT EXISTS GAMES_OF_USERS (
        USER_ID INTEGER PRIMARY KEY REFERENCES USERS(USER_ID),
        GAME_ID INTEGER PRIMARY KEY REFERENCES GAMES(GAME_ID),
        TIME_PLAYED INTEGER DEFAULT 0,
        TIME_PURCHASED DATE,
        EXPIRE_TIME DATE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS REVIEWS (
        REVIEW_ID SERIAL PRIMARY KEY
        USER_ID INTEGER REFERENCES USERS(USER_ID),
        GAME_ID INTEGER REFERENCES GAMES(GAME_ID),
        CONTENT VARCHAR(500),
        LIKES INTEGER DEFAULT 0,
        DISLIKES INTEGER DEFAULT 0,
        LABEL VARCHAR(50)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS SCREENSHOTS (
        SHOT_ID SERIAL PRIMARY KEY
        PHOTO VARCHAR(200),
        USER_ID INTEGER REFERENCES USERS(USER_ID),
        GAME_ID INTEGER REFERENCES GAMES(GAME_ID),
        CAPTION VARCHAR(200),
        DATE_ADDED DATE,
        LIKES INTEGER DEFAULT 0,
        DISLIKES INTEGER DEFAULT 0
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS MARKET (
        ITEM_ID SERIAL PRIMARY KEY REFERENCES ITEMS(ITEM_ID),
        USER_ID SERIAL PRIMARY KEY REFERENCES USERS(USER_ID),
        PRICE NUMERIC(5, 2),
        DATE_PURCHASED DATE,
        DESCRIPTION VARCHAR(500)
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
    """
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

    statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, 6, 60.00)"
    data = ("go go nippon my first trip to japan", "anime")
    cursor.execute(statement, data)
    statement = "INSERT INTO GAMES (TITLE, GENRE, AGE_RESTRICTION, PRICE) VALUES (%s, %s, 12, 0.00)"
    data = ("team fortress 2", "fps")
    cursor.execute(statement, data)

    connection.commit()
    cursor.close()

    connection.close();
