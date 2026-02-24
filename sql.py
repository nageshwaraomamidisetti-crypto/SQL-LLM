import sqlite3

# Connect and create a cursor
connection = sqlite3.connect("data.db")
cursor = connection.cursor()

# Create the Table with proper schema
table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), 
SECTION VARCHAR(25), MARKS INT, COMPANY VARCHAR(25));
"""
cursor.execute(table_info)

# Insert Sample Records
records = [
    ('Sijo', 'BTech', 'A', 85, 'Infosys'),
    ('Lijo', 'MTech', 'B', 90, 'TCS'),
    ('Aarav', 'BTech', 'A', 78, 'Google'),
    ('Priya', 'Data Science', 'A', 92, 'Infosys'),
    ('Vikas', 'Web Development', 'B', 88, 'Microsoft'),
    ('Anjali', 'Data Science', 'B', 85, 'Amazon'),
    ('Rohan', 'BTech', 'A', 95, 'TCS'),
    ('Neha', 'Web Development', 'A', 91, 'Google'),
    ('Amit', 'Data Science', 'C', 80, 'Infosys'),
    ('Zara', 'MTech', 'A', 93, 'Microsoft'),
]

for record in records:
    cursor.execute(f"INSERT INTO STUDENT VALUES('{record[0]}', '{record[1]}', '{record[2]}', {record[3]}, '{record[4]}')")

connection.commit()
connection.close()

print("✅ Database initialized successfully with STUDENT table and sample data!")