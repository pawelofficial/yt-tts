import mysql.connector

# Set up the connection to the MySQL server
cnx = mysql.connector.connect(user='admin', password='password',
                              host='91.185.185.41',
                              database='db')

# Create a cursor object to interact with the server
cursor = cnx.cursor()

# Execute a simple query
query = 'SHOW DATABASES'
cursor.execute(query)

# Fetch the results and print them out
for result in cursor:
    print(result)

# Clean up the cursor and connection objects
cursor.close()
cnx.close()
