from database import get_connection

def check_login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    # Check Admin
    cursor.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (username, password)
    )
    admin = cursor.fetchone()

    if admin:
        conn.close()
        return ("admin", username)

    # Check User
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (username, password)
    )
    user = cursor.fetchone()

    if user:
        conn.close()
        return ("user", user[1])   # user name

    conn.close()
    return None