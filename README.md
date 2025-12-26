Database Schema Designer

This project is a visual database modeling tool that allows you to design database schemas step by step. You can create tables, define attributes, and establish relationships using an intuitive graphical interface.

1. Prerequisites & Installation

To run this application, Python must be installed on your system.

Requirements

The project uses only standard Python libraries (as listed in requirements.txt):

# tkinter
# sqlite3


Note: These libraries are included with most Python installations, so no additional pip install steps are usually required unless you replace the database connector.

2. How to Run the Application

Open the project folder in Visual Studio Code.

Open the Terminal in VS Code.

Navigate to the project directory and run the main script:

cd db-designer
python main.py

3. Using the Interface

The left-side panel provides the main design tools:

Add Table – Create a new table (e.g., student, teacher)

Add Attribute – Add columns to a selected table (e.g., id, name)

Add Relationship – Define relationships between tables:

One-to-Many (1–N)

Many-to-Many (N–N)

Generate SQL – Automatically generate the SQL schema

SQL Console – Execute SQL queries manually

4. Workflow & Testing

Create Entities
Create tables such as student and add attributes.

Primary Keys
Mark the id attribute as the PRIMARY KEY.

Relationships
Use the Add Relationship tool to define how tables are connected.

SQL Console Testing
Test your schema by inserting data and running queries:

INSERT INTO "student" ("id", "name") VALUES (1, 'Student one');
INSERT INTO "student" ("id", "name") VALUES (2, 'Student two');
SELECT * FROM "student";
