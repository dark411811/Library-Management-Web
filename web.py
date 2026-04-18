from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

web = Flask(__name__)
web.secret_key = 'gdgp_hisar_final_secret_key'

# --- Database Configuration ---
web.config['MYSQL_HOST'] = 'localhost'
web.config['MYSQL_USER'] = 'root'
web.config['MYSQL_PASSWORD'] = '' 
web.config['MYSQL_DB'] = 'library_db'
web.config['MYSQL_PORT'] = 3307 

mysql = MySQL(web)

# 1. Login System
@web.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        team = {'Manpreet': '008', 'Sakshi': '106', 'Pinku': '083'}
        
        if user in team and team[user] == pw:
            session['logged_in'] = True
            session['user'] = user
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid Username or Password!")
    return render_template('login.html')

@web.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 2. Dashboard with Fixed Search
@web.route('/')
def index():
    if not session.get('logged_in'): 
        return redirect(url_for('login'))
    
    search_query = request.args.get('search', '').strip()
    cur = mysql.connection.cursor()
    
    if search_query:
        # Search logic fixed with wildcards
        cur.execute("SELECT title, author, COUNT(*) FROM books WHERE title LIKE %s GROUP BY title, author", ('%' + search_query + '%',))
    else:
        cur.execute("SELECT title, author, COUNT(*) FROM books GROUP BY title, author")
    
    books_data = cur.fetchall()
    
    # Stats for Cards
    cur.execute("SELECT COUNT(*) FROM books"); t_books = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM issued_books"); t_issued = cur.fetchone()[0]
    cur.close()
    
    return render_template('index.html', books=books_data, t_books=t_books, t_issued=t_issued)

# 3. Add Book
@web.route('/add_page')
def add_page():
    return render_template('add_books.html')

@web.route('/add_book_action', methods=['POST'])
def add_book_action():
    title = request.form.get('title')
    author = request.form.get('author')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@web.route('/add_one/<title>/<author>')
def add_one(title, author):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# 4. Issue Book & History
@web.route('/issue_page')
def issue_page():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, title FROM books")
    all_books = cur.fetchall()
    cur.close()
    return render_template('issue_book.html', books=all_books)

@web.route('/issue_action', methods=['POST'])
def issue_action():
    b_id = request.form.get('book_id')
    s_name = request.form.get('student_name')
    r_no = request.form.get('roll_no')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO issued_books (book_id, student_name, roll_no) VALUES (%s, %s, %s)", (b_id, s_name, r_no))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('issued_details'))

@web.route('/issued_details')
def issued_details():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT books.id, books.title, issued_books.student_name, issued_books.roll_no, issued_books.issue_date 
        FROM issued_books 
        JOIN books ON issued_books.book_id = books.id
    """)
    data = cur.fetchall()
    cur.close()
    return render_template('issued_info.html', issues=data)

# 5. Remove & About
@web.route('/remove_quantity', methods=['POST'])
def remove_quantity():
    title = request.form.get('title')
    qty = int(request.form.get('qty_to_remove'))
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM books WHERE title = %s LIMIT %s", (title, qty))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@web.route('/about')
def about():
    return render_template('about_page.html')

if __name__ == '__main__':
    web.run(debug=True)