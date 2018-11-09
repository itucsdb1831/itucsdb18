import psycopg2 as dbapi2
from user import User

dsn = """user=erfybxxvnizudu password=35d55b4417e736e6493eb90e4f674f8530afd4d6c071c675811fd7ee5240557c
host=ec2-204-236-230-19.compute-1.amazonaws.com port=5432 dbname=d7qite4opgg4jv"""

connection = dbapi2.connect(dsn)
cursor = connection.cursor()
cursor.execute("CREATE TABLE USERS (USER_ID SERIAL PRIMARY KEY, NAME VARCHAR(20), PASSWORD VARCHAR(87))")
connection.commit()
cursor.close()
connection.close()