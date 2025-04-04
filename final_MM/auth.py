import psycopg2
from flask import session
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

# ----------------------- User Registration ------------------------

def register_user(name, email, password, twitter_username):
    """Registers a new user into the database."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "Email already registered."

        # ✅ Hash password securely
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # ✅ Insert user into the database
        cursor.execute(
            "INSERT INTO users (name, email, password, twitter_username) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, twitter_username)
        )
        conn.commit()
        return "success"

    except Exception as e:
        print(f"Error registering user: {e}")
        return "Registration failed. Please try again."

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ----------------------- User Login ------------------------

def login_user(email, password):
    """Authenticates user and retrieves their id, twitter_username, and name."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Fetch id, hashed password, twitter_username, and name
        query = "SELECT id, password, twitter_username, name FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()

        if result:
            user_id, hashed_password, twitter_username, name = result

            # ✅ Check if password matches
            if check_password_hash(hashed_password, password):
                return (user_id, twitter_username, name)  # Return tuple (id, twitter_username, name)
            else:
                return "Invalid email or password."
        else:
            return "Invalid email or password."

    except Exception as e:
        print(f"Error during login: {e}")
        return "An error occurred. Please try again."

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ----------------------- Get Current Logged-in User ------------------------

def get_current_user():
    """Fetches current logged-in user from session, including email."""
    if "twitter_username" in session:  # ✅ Using 'twitter_username' stored in session
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # ✅ Fetch user details based on twitter_username stored in session
            cursor.execute(
                "SELECT name, email, twitter_username FROM users WHERE twitter_username = %s",
                (session["twitter_username"],)
            )
            user = cursor.fetchone()

            if user:
                return {
                    "name": user[0],
                    "email": user[1],
                    "twitter_username": user[2]
                }
            else:
                return None

        except Exception as e:
            print(f"Error fetching user: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return None
