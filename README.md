# CS9163 - Application Security 
## Assignment 3

Repo URL: https://github.com/joelbcastillo/flask_spell_check/tree/add-db

Student: Joel Castillo (jc5383)

Database Schema:

```sql
-- we don't know how to generate root <with-no-name> (class Root) :(
create table alembic_version
(
    version_num VARCHAR(32) not null
        constraint alembic_version_pkc
            primary key
);

create table users
(
    id INTEGER not null
        primary key,
    username VARCHAR(80) not null
        unique,
    password_hash VARCHAR(128) not null,
    two_factor VARCHAR(15),
    created_at DATETIME not null,
    is_admin BOOLEAN,
    check (is_admin IN (0, 1))
);

create table auth_history
(
    id INTEGER not null
        primary key,
    login_timestamp DATETIME,
    logout_timestamp DATETIME,
    user_id INTEGER
        references users
);

create table spell_check_query
(
    id INTEGER not null
        primary key,
    text TEXT,
    result TEXT,
    timestamp DATETIME,
    user_id INTEGER
        references users
);

```

The database for this flask application has 3 tables:

The `Users` table stores rows identifying all of the users in the application. Each row stores the identifying information (username, password, and two_factor_code) for each user. In addition, the application automatically captures and stores a timestamp when a user is created. Finally there is a boolean flag to determine if a user should have administrative access to the database or not.

Passwords are stored as a hash using the werkzeug generate_password_hash function. This means that the plaintext password cannot be accessed directly in the database. To authenticate a user, the password hash is checked against a generated password hash with the input from the password field on the login form. This allows us to still authenticate users without compromising the password security.

---

The auth_history table contains a log of each login/logout pair of authentication events for each user. Each pair is identified by a unique id. To tie the login events to a user, the table has a foreign key to the `Users` table with the id column. Each timestamp is a datetime. 

A better design would have had a single row for each login or logout that contains an ID, type (login / logout), timestamp, and user_id. 

---

The `SpellCheckQuery` table stores each query submitted for spell checking. Each query has a unique, numeric, id, the text that was submitted for checking, the returned mispelled words (result), the timestamp when the query was run, and a foreign key to the `Users` table via the `id` column. 

---

The database schema was defined using SQLAlchemy, a Python ORM to make it easier to interact with the database from the Python code. Each table is defined as a Python class and can be accessed directly as a class when returned via the ORM. The ORM also provides a security layer by automatically escaping input before executing queries. This allows us to handle most SQLi attacks.

In order to test the application for SQLi I used sqlmap. Due to the simplicity of the application and the aformentioned security benefits of the ORM, there were no vulnerabilities found, as expected.

[![asciicast](https://asciinema.org/a/46EdeZSZnN2haTQnvLyI5vyCq.png)](https://asciinema.org/a/46EdeZSZnN2haTQnvLyI5vyCq)

