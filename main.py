from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'password'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.before_request
def require_login():
    routes = ['login_user', 'show_blog', 'add_user', 'index', 'static']
    if request.endpoint not in routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def main():
    all_users = User.query.distinct()
    return render_template('index.html', list_all_users=all_users)


@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get("id")
    single_id = request.args.get('owner_id')
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('indpost.html', blog=blog)
    else:
        if single_id:
            ind_user_blogs = Blog.query.filter_by(owner_id=single_id)
            return render_template('singleUser.html', posts=ind_user_blogs)
        else:
            blog_posts = Blog.query.all()
            return render_template('blog.html', posts=blog_posts)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        owner = User.query.filter_by(username=session['username']).first()
        post_new = Blog(blog_title, blog_body, owner)
        title_error = ""
        body_error = ""

        if len(blog_title) < 1 and len(blog_body) < 1:
            flash("Please enter a title and blog entry", "error")
            return render_template('newpost.html', blog_title=blog_title, blog_body=blog_body)
        if len(blog_title) < 1:
            flash("Please enter a title", "error")
            return render_template('newpost.html', blog_body=blog_body)
        if len(blog_body) < 1:
            flash("Please enter a text", "error")
            return render_template('newpost.html', blog_title=blog_title)
        else:
            if not title_error and not body_error:
                db.session.add(post_new)
                db.session.commit()
                blog_link = "/blog?id=" + str(post_new.id)
                return redirect(blog_link)
    else:
        return render_template('newpost.html')


@app.route('/signup', methods=['POST', 'GET'])
def add_user():
    if request.method == 'POST':
        user_name = request.form['username']
        user_password = request.form['password']
        user_password_validate = request.form['password_validate']

        if len(user_name) < 1 and len(user_password) < 1 and len(user_password_validate) < 1:
            flash("All fields must be filled in", "error")
            return render_template('signup.html')
        if user_password != user_password_validate:
            flash("Passwords must match", "error")
            return render_template('signup.html')
        if len(user_name) < 3 and len(user_password) < 3:
            flash("Username and password must be at least three characters", "error")
            return render_template('signup.html')
        if len(user_password) < 3:
            flash("Username must be at least 3 characters", "error")
            return render_template('signup.html')
        if len(user_password) < 3:
            flash("Password must be at least 3 characters", "error")
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=user_name).first()

        if not existing_user:
            new_user = User(user_name, user_password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = user_name
            flash('New user created', 'success')
            return redirect('/newpost')
        else:
            flash('There is already a user with the same username', 'error')
            return render_template('signup.html')
    else:
        return render_template('signup.html')


@app.route('/login', methods=['POST', 'Get'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if not username and not password:
            flash("Username and password can't be empty", 'error')
            return render_template('login.html')
        if not username:
            flash("Username can't be empty", 'error')
            return render_template('login.html')
        if not password:
            flash("Password can't be empty", 'error')
            return render_template('login.html')


        if not user:
            flash('Username does not exit', 'error')
            return render_template('login.html')
        if user.password != password:
            flash('Password is incorrect', 'error')
            return render_template('login.html')
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('You are logged out', 'success')
    return redirect('/blog')



if __name__ == '__main__':
    app.run()
