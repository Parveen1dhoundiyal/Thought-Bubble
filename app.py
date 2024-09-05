from flask import Flask, render_template, request, redirect, url_for, session ,flash
import mysql.connector
from mysql.connector import Error
import re
app = Flask(__name__)
app.secret_key = 'your_secret_key'  

# Database connection function
def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='thought bubble',
        user='root',
        password=''
    )
    print("Connected to database")
    return connection


def strip_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def get_trending_posts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    query = """
        SELECT p.id, p.title, p.excerpt, p.created_at AS date, p.category, u.username, 
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count
        FROM posts p
        JOIN user u ON p.user_id = u.id
        ORDER BY (SELECT COUNT(*) FROM comments WHERE post_id = p.id) + 
                 (SELECT COUNT(*) FROM likes WHERE post_id = p.id) DESC
        LIMIT 5
    """
    cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return posts

def get_all_posts(category=None):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    if category:
        query = """
            SELECT p.id, p.title, p.excerpt, p.created_at AS date, p.category, u.username
            FROM posts p
            JOIN user u ON p.user_id = u.id
            WHERE p.category = %s
            ORDER BY p.created_at DESC
        """
        cursor.execute(query, (category,))
    else:
        query = """
            SELECT p.id, p.title, p.excerpt, p.created_at AS date, p.category, u.username
            FROM posts p
            JOIN user u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """
        cursor.execute(query)
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return posts

@app.route('/')


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    trending_posts = get_trending_posts()
    return render_template('index.html', trending_posts=trending_posts)

@app.route('/all-posts')
def all_posts():
    category = request.args.get('category')  
    
    all_posts = get_all_posts(category)  
    categories = ['Poems', 'Quotes', 'Fiction', 'Biography', 'Motivation', 'Inspiration', 'Life Lessons', 'Science', 'Story', 'Politics', 'Tech']

    return render_template('all_posts.html', categories=categories,posts=all_posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form.get('username')
        userid = request.form.get('userid')
        password = request.form.get('password')

        connection = get_db_connection()
        cursor = connection.cursor()
        query = """SELECT id, username FROM user WHERE username = %s AND id = %s AND password = %s"""
        cursor.execute(query, (username, userid, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session['username'] = username
            session['user_id'] = userid
            return redirect(url_for('index', username=username))
        else:
            message = "Invalid credentials. Please Register or try again."

    return render_template('login.html', message=message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = """INSERT INTO user (username, email, password) 
                       VALUES (%s, %s, %s)"""
            cursor.execute(query, (username, email, password))
            connection.commit()

            user_id = cursor.lastrowid  
            cursor.close()
            connection.close()
            message = f"Registration successful! Your user ID is {user_id}."

        except Error as e:
            message = f"Failed to register: {e}"

    return render_template('register.html', message=message)

@app.route('/dashboard')
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Fetch user details
    cursor.execute("SELECT username, id, email, password FROM user WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    # Fetch all posts related to this user, joining with the user table to get the username
    query = """
        SELECT p.id, p.title, u.username
        FROM posts p
        JOIN user u ON p.user_id = u.id
        WHERE p.user_id=%s
    """
    cursor.execute(query, (session['user_id'],))
    posts = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return render_template('dashboard.html', user=user, posts=posts)

@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        category = request.form['category']

        cursor.execute("UPDATE posts SET title=%s, body=%s, category=%s WHERE id=%s", 
                       (title, body, category, post_id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('dashboard'))

    cursor.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_post.html', post=post)


@app.route('/delete-post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("DELETE FROM comments WHERE post_id = %s", (post_id,))


        cursor.execute("DELETE FROM likes WHERE post_id = %s", (post_id,))


        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))


        connection.commit()

    except Exception as e:

        connection.rollback()
        print(f"Error: {e}")

    finally:

        cursor.close()
        connection.close()


    return redirect(url_for('dashboard'))



@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    if request.method == 'POST':
        # Handle the update
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        connection = get_db_connection()
        cursor = connection.cursor()
        query = """UPDATE user SET username=%s, email=%s, password=%s WHERE id=%s"""
        cursor.execute(query, (username, email, password, user_id))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('dashboard'))

    else:
        # Display the form with current user details
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT username, id, email, password FROM user WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template('update.html', user=user)

@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        username = session.get('username')
        title = request.form.get('title')
        body = request.form.get('body')
        category = request.form.get('category')

        # Strip HTML tags from body
        body = strip_html_tags(body)

        excerpt = ' '.join(body.split()[:30])

        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = """INSERT INTO posts (user_id, title, body, excerpt, category) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (session['user_id'], title, body, excerpt, category))
            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('index'))

        except Error as e:
            return f"An error occurred: {e}"

    return render_template('createpost.html')




@app.route('/post/<int:post_id>', methods=['GET'])
def show_post(post_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Query to get the post details along with comments and likes
    query = """
        SELECT p.id, p.title, p.body, p.category, p.created_at AS date, 
               (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count,
               (SELECT COUNT(*) FROM likes WHERE post_id = p.id) AS like_count,
               u.username
        FROM posts p
        JOIN user u ON p.user_id = u.id
        WHERE p.id = %s
    """
    cursor.execute(query, (post_id,))
    post = cursor.fetchone()

    if post is None:
        cursor.close()
        connection.close()
        abort(404)

    # Query to get comments
    cursor.execute("SELECT * FROM comments WHERE post_id = %s", (post_id,))
    post['comments'] = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('single.html', post=post)

@app.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check if the user has already liked the post
    cursor.execute("SELECT * FROM likes WHERE post_id = %s AND username = %s", (post_id, session['username']))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return redirect(url_for('show_post', post_id=post_id))

    # Add a new like
    cursor.execute("INSERT INTO likes (post_id, username) VALUES (%s, %s)", (post_id, session['username']))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('show_post', post_id=post_id))

@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    comment_text = request.form['comment_text']
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("INSERT INTO comments (post_id, username, comment_text) VALUES (%s, %s, %s)", 
                   (post_id, session['username'], comment_text))
    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('show_post', post_id=post_id))




@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)
