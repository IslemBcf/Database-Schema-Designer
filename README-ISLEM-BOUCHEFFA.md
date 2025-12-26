# Database Schema Designer – README

This document explains how to run and use the **Database Schema Designer** project step by step.

---

## 1. Open the Project

1. Open the project folder using **Visual Studio Code**.
2. Open the **Terminal** in VS Code.

---

## 2. Run the Application

In the terminal, type the following commands:

```bash
cd db-designer
python main.py
```

After pressing **Enter**, the application window will open.

---

## 3. Using the Interface

On the **left side panel**, you will find the following options:

- **Add Table**: Create a new table (example: `student`, `teacher`).
- **Add Attribute**: Add columns to a selected table (example: `id`, `name`).
- **Add Relationship**: Create relationships between tables (1-N or N-N).
- **Generate SQL**: Automatically generate SQL schema.
- **SQL Console**: Execute SQL queries manually.

---

## 4. Creating Tables and Attributes

1. Create tables such as `student` and `teacher`.
2. Add attributes to each table (for example: `id`, `name`).
3. Make sure to mark the `id` attribute as **PRIMARY KEY**.

---

## 5. Creating Relationships

- Use **Add Relationship** to define relationships between tables.
- You can choose:
  - **1-N (One-to-Many)**
  - **N-N (Many-to-Many)**

---

## 6. Using the SQL Console

Open the **SQL Console** and execute SQL commands such as:

```sql
INSERT INTO "student" ("id", "name") VALUES (1, 'Islem Boucheffa');
INSERT INTO "student" ("id", "name") VALUES (2, 'Mounib Riabi');
SELECT * FROM "student";
```

This allows you to insert data and test your database schema.

---

## 7. End

Once finished, the project allows you to visually design database schemas and test them using SQL.

