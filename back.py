import psycopg2
from psycopg2 import sql
import pandas as pd

# Database connection details
hostname = "localhost"
username = "postgres"
password = "Admin"
port_id = 5432
database_origin = "postgres"  # Start by connecting to the 'postgres' database to create {name_of_new_database}
name_of_new_database = "Movie_database"

is_database_there = True

connection = None
cursor = None
len_movie_entries = 0

my_list = []


# Connect to the PostgreSQL server using the default 'postgres' database
def create_connection_to_Origin():
    global hostname, username, password, database_origin, port_id, connection, cursor
    try:
        # Connect to the 'postgres' database to create the {name_of_new_database}
        connection = psycopg2.connect(
            dbname=database_origin,
            user=username,
            password=password,
            host=hostname,
            port=port_id,
        )
        connection.autocommit = True  # Enable autocommit for database creation
        cursor = connection.cursor()

        # Terminate any active sessions that are connected to the 'template1' database
        cursor.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'template1' AND pg_stat_activity.pid <> pg_backend_pid();
        """
        )
        connection.commit()

        # Check if the name_of_new_database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;", (name_of_new_database,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"Database {name_of_new_database} already exists.")
        else:
            # Create the {name_of_new_database} if it doesn't exist
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier("Movie_database"))
            )
            print(f"Database {name_of_new_database} created successfully!")

    except Exception as e:
        print(f"Error: {e}")


def close_connection_to_database():
    """Close the connection to PostgreSQL"""
    global connection, cursor
    if cursor:
        cursor.close()
    if connection:
        connection.close()
    print("Database connection closed.")


def create_table():
    global hostname, username, password, port_id, connection, cursor
    try:

        create_connection_to_Origin()
        # Establish connection to the the new database
        connection = psycopg2.connect(
            dbname=name_of_new_database,
            user=username,
            password=password,
            host=hostname,
            port=port_id,
        )
        cursor = connection.cursor()

        # Create the table named 'movies'
        create_table_query = """
            CREATE TABLE IF NOT EXISTS movies (
                id SERIAL PRIMARY KEY,
                title TEXT,
                us_gross NUMERIC,
                worldwide_gross NUMERIC,
                production_budget NUMERIC,
                release_date TEXT,
                distributor TEXT,
                source TEXT,
                major_genre TEXT,
                creative_type TEXT,
                director TEXT,
                rotten_tomatoes_rating NUMERIC,
                imdb_rating NUMERIC,
                imdb_votes NUMERIC
            );
        """

        # Execute the create table query
        cursor.execute(create_table_query)

        connection.commit()
        print("Movie table already exists or movies table created successfully.")

    except Exception as e:
        print("Line 56")
        print(f"Error: {e}")

    finally:
        close_connection_to_database()


def insert_multiple_movies():
    global hostname, username, password, port_id, connection, cursor, my_list, len_movie_entries

    read_file_into_DataFrame()
    try:
        # Establish connection to the Movies database
        connection = psycopg2.connect(
            dbname=name_of_new_database,
            user=username,
            password=password,
            host=hostname,
            port=port_id,
        )
        cursor = connection.cursor()

        # Check if the table is empty by running a simple count query
        cursor.execute("SELECT COUNT(*) FROM Movies;")
        row_count = cursor.fetchone()[0]  # Fetch the count of rows

        if row_count != 0:
            print("Table already has entries.")
            len_movie_entries = 0
            return

        # Prepare the SQL insert query

        insert_query2 = """
            INSERT INTO movies (
                title, us_gross, worldwide_gross, production_budget, release_date, distributor, 
                source, major_genre, creative_type, director, rotten_tomatoes_rating, imdb_rating, imdb_votes
            )
            VALUES (
                COALESCE(NULLIF(%s, 'nan'), ''),  -- Replace 'nan' with empty string for title
                COALESCE(NULLIF(%s, 'nan'), 0),  -- Replace 'nan' with 0 for us_gross
                COALESCE(NULLIF(%s, 'nan'), 0),  -- Replace 'nan' with 0 for worldwide_gross
                COALESCE(NULLIF(%s, 'nan'), 0),  -- Replace 'nan' with 0 for production_budget
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for release_date
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for distributor
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for source
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for major_genre
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for creative_type
                COALESCE(NULLIF(%s, 'nan'), ''), -- Replace 'nan' with empty string for director
                COALESCE(NULLIF(%s, 'nan'), 0),  -- Replace 'nan' with 0 for rotten_tomatoes_rating
                COALESCE(NULLIF(%s, 'nan'), 0),  -- Replace 'nan' with 0 for imdb_rating
                COALESCE(NULLIF(%s, 'nan'), 0)   -- Replace 'nan' with 0 for imdb_votes
            );
        """

        insert_query = """
            INSERT INTO movies (
                title,
                us_gross,
                worldwide_gross,
                production_budget,
                release_date,
                distributor,
                source,
                major_genre,
                creative_type,
                director,
                rotten_tomatoes_rating,
                imdb_rating,
                imdb_votes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Convert the list of dictionaries into a list of tuples
        movie_entries = [
            (
                movie["Title"],
                str(movie["US Gross"]),
                str(movie["Worldwide Gross"]),
                str(movie["Production Budget"]),
                movie["Release Date"],
                movie["Distributor"],
                movie["Source"],
                movie["Major Genre"],
                movie["Creative Type"],
                movie["Director"],
                str(movie["Rotten Tomatoes Rating"]),
                str(movie["IMDB Rating"]),
                str(movie["IMDB Votes"]),
            )
            for movie in my_list
        ]

        # Use executemany to insert all rows at once
        cursor.executemany(insert_query, movie_entries)
        connection.commit()
        len_movie_entries = len(movie_entries)
        print(f"Inserted {len_movie_entries} movies into the database successfully.")

    except Exception as e:
        print("Error during bulk insert:", e)

    finally:
        close_connection_to_database()


def delete_database():
    global is_database_there
    is_database_there = False

    """Terminate any active connections to all databases and delete all databases"""
    create_connection_to_Origin()

    global cursor
    try:
        cursor.execute(
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'Movie_database' AND pg_stat_activity.pid <> pg_backend_pid();
            """
        )
        connection.commit()

        # Drop the 'Movie_database'
        cursor.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier("Movie_database")
            )
        )
        connection.commit()
        print("Database 'Movie_database' deleted successfully!")

    except Exception as e:
        print(f"Error deleting database: {e}")

    finally:
        close_connection_to_database()


def read_file_into_DataFrame():
    """Read file into dataframe"""
    file_path = "movies.xlsx"
    global my_list
    try:
        df = pd.read_excel(file_path)
        if "Release Date" in df.columns:
            df["Release Date"] = df["Release Date"].astype(str)
        df = df.where(pd.notnull(df), 0)
        numeric_columns = [
            "US Gross",
            "Worldwide Gross",
            "Production Budget",
            "Rotten Tomatoes Rating",
            "IMDB Rating",
            "IMDB Votes",
        ]
        for column in numeric_columns:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
        my_list = df.to_dict(orient="records")
        print(f"Data read and cleaned successfully from {file_path}.")
        for item in my_list:
            if 0:
                print(item)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin  # Import CORS

app = Flask(__name__, template_folder="../frontEnd")
CORS(app)  # Enable CORS for all routes


@app.route("/")
def index():
    return render_template(
        "main.html"
    )  # This renders main.html at http://localhost:8000


@cross_origin(
    origins=["http://localhost:3000"]
)  # Allow only this origin # Example route with this specific CORS policy
@app.route("/api/create_database", methods=["GET"])
def create_database_endpoint():
    global is_database_there
    is_database_there = True
    create_table()
    insert_multiple_movies()
    if len_movie_entries > 0:
        return jsonify(
            f"Created database and inserted {len_movie_entries} movies into the database."
        )
    return jsonify(f"Database already present.")


@cross_origin(
    origins=["http://localhost:3000"]
)  # Allow only this origin # Example route with this specific CORS policy
@app.route("/api/delete_database", methods=["GET"])
def delete_database_endpoint():
    delete_database()
    return jsonify("Database deleted!")


@cross_origin(
    origins=["http://localhost:3000"]
)  # Allow only this origin # Example route with this specific CORS policy
@app.route("/api/filters_endpoint", methods=["POST"])
def receive_data4():
    global is_database_there
    if not is_database_there:
        return jsonify(
            "Create the database before searching."
        )  # Status code 400 Bad Request

    create_connection_to_Origin()
    create_database_endpoint()

    data = request.get_json()
    title = data.get("title")  # Could be None
    major_genre = data.get("major_genre")  # Could be None
    alphabet_sort = data.get("alphabetSort")  # Could be None
    release_date = data.get("releaseDate")  # Could be None
    number_of_items = data.get("Number_of_Items")  # Could be None
    rotten_tomatoes_rating = data.get("rotten_tomatoes_rating")  # Could be None

    if 0:
        print("|", title)
        print("|", major_genre)
        print("|", alphabet_sort)
        print("|", release_date)
        print("|", number_of_items)
        print("|", rotten_tomatoes_rating)

    to_return = filter_by_entry4(
        title,
        major_genre,
        alphabet_sort,
        release_date,
        number_of_items,
        rotten_tomatoes_rating,
    )
    if len(to_return) == 0:
        return jsonify("No entries found.")
    return jsonify(
        {"message": "Data received successfully", "received_data": to_return}
    )


def filter_by_entry4(
    title,
    major_genre="",
    alphabet_sort="",
    release_date="",
    number_of_items="",
    rotten_tomatoes_rating=0,
):
    global connection, cursor, name_of_new_database, hostname, username, password, port_id
    # Connect to the database
    try:
        connection = psycopg2.connect(
            dbname=name_of_new_database,
            user=username,
            password=password,
            host=hostname,
            port=port_id,
        )
        cursor = connection.cursor()

        # Base query
        query = "SELECT * FROM movies"
        filters = []
        params = []

        # Add filters based on the provided arguments
        if title:  # Filter by title only if title is not empty
            filters.append("LOWER(title) LIKE %s")
            params.append(f"%{title}%")  # Add wildcard for partial match

        if major_genre:  # Filter by genre only if major_genre is provided
            filters.append("LOWER(major_genre) LIKE %s")
            params.append(f"%{major_genre}%")  # Add wildcard for partial match

        if release_date:  # Filter by release date (starts with "####-##-##")
            filters.append("release_date LIKE %s")
            params.append(
                f"{release_date}%"
            )  # Match the beginning of the release_date (e.g., '2025-01-')

        if (
            rotten_tomatoes_rating > 0
        ):  # Filter by Rotten Tomatoes rating greater than or equal to the input value
            filters.append("rotten_tomatoes_rating > %s")
            params.append(rotten_tomatoes_rating)  # Add rating threshold

        # Append filters to the query
        if filters:
            query += " WHERE " + " AND ".join(filters)

        # Add sorting based on `alphabet_sort`
        if alphabet_sort == "ascending":
            query += " ORDER BY title ASC"
        elif alphabet_sort == "descending":
            query += " ORDER BY title DESC"

        # Limit the number of items
        if number_of_items:
            query += " LIMIT %s"
            params.append(int(number_of_items))

        # Execute the query
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        # Convert results to a list of dictionaries
        dictionary = []
        columns = [desc[0] for desc in cursor.description]
        for row in results:
            dictionary.append(dict(zip(columns, row)))

        return dictionary

    except Exception as e:
        print(f"Error: {e}")
        return []

    finally:
        close_connection_to_database()


if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)  # Port for the back-end server
