from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

id = "1"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def main():
    return redirect('/blog')


@app.route('/blog', methods=['GET'])
def blog():
    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('ind_post.html', blog=blog)
    else:
        blog_posts = Blog.query.all()
        return render_template('blog.html', posts="blog_posts")


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']
        post_new = Blog(blog_title, blog_body)
        title_error = ""
        body_error = ""

        if len(blog_title) < 1 and len(blog_body) < 1:
            title_error = "Please enter a text"
            body_error = "Please enter a text"
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
        if len(blog_title) < 1:
            title_error = "Please enter a text"
            return render_template('newpost.html', title_error=title_error, blog_body=blog_body)
        if len(blog_body) < 1:
            body_error = "Please enter a text"
            return render_template('newpost.html', body_error=body_error, blog_title=blog_title)
        else:
            if not title_error and not body_error:
                db.session.add(post_new)
                db.session.commit()
                blog_link = "/blog?id=" + str(post_new.id)
                return redirect(blog_link)
    else:
        return render_template('newpost.html')



if __name__ == '__main__':
    app.run()
