from flask import Flask, flash, render_template, request, session, redirect, jsonify
from sqlalchemy import create_engine, Column, Integer, String, LargeBinary, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
import os, base64

from sqlalchemy.sql.schema import ForeignKey

engine = create_engine("sqlite:///assignment.db", echo=True)
Base = declarative_base()
db_session = scoped_session(sessionmaker(bind = engine))

likePostsTable = Table("likePosts", Base.metadata,
    Column("username", Integer, ForeignKey("users.username")),
    Column("postID", Integer, ForeignKey("posts.id"))
)

followTable = Table(
    "follow", Base.metadata,
    Column("username", Integer, ForeignKey("users.username"), primary_key=True),
    Column("profile", Integer, ForeignKey("users.username"), primary_key=True)
)



class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key = True)
    password = Column(String)
    type = Column(String)
    posts = relationship("Post")
    likePosts = relationship("Post", secondary = likePostsTable, back_populates = "likes")
    following = relationship("User", lambda: followTable,
                              primaryjoin = lambda: User.username == followTable.c.username,
                              secondaryjoin = lambda: User.username == followTable.c.profile,
                              backref = "followers")

    def __init__(self, username, password, type, posts, likePosts, followers, following):
        self.username = username
        self.password = password
        self.type = type
        self.posts = posts
        self.likePosts = likePosts
        self.followers = followers
        self.following = following
    
    def getUserName(self):
        return self.username

    def getType(self):
        return self.type

    def getPosts(self):
        return self.posts
    
    def getLikePosts(self):
        return self.likePosts



class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String, ForeignKey("users.username"))
    image = Column(LargeBinary(length = (2**32) - 1))
    caption = Column(String)
    likes = relationship("User", secondary = likePostsTable, back_populates = "likePosts")
    comments = relationship("Comment")

    def __init__(self, username, image, caption, likes, comments):
        self.username = username
        self.image = image
        self.caption = caption
        self.likes = likes
        self.comments = comments
    
    def getID(self):
        return self.id

    def getUserName(self):
        return self.username

    def getImage(self):
        return base64.b64encode(self.image).decode("ascii")
    
    def getCaption(self):
        return self.caption

    def getLikes(self):
        return len(self.likes)
    
    def getComments(self):
        return self.comments



class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key = True, autoincrement = True)
    postid = Column(Integer, ForeignKey("posts.id"))
    username = Column(String)
    comment = Column(String)

    def __init__(self, postid, username, comment):
        self.postid = postid
        self.username = username
        self.comment = comment

    def getPostID(self):
        return self.postid

    def getUsername(self):
        return self.username
    
    def getComment(self):
        return self.comment



class Request(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key = True, autoincrement = True)
    username = Column(String)
    profile = Column(String)

    def __init__(self, username, profile):
        self.username = username
        self.profile = profile

    def getUsername(self):
        return self.username


Base.metadata.create_all(engine)

app = Flask(__name__)


def parseRequests(user):
    requests = db_session.query(Request).filter(Request.profile == user.getUserName()).all()
    usernames = []

    for request in requests:
        usernames.append(request.getUsername())
    print(user.getUserName())
    return usernames

@app.route("/")
def home():
    if not session.get("logged_in"):
        return render_template("login.html")
    else:
        user = db_session.query(User).filter(User.username == session.get("username")).first()
        usertype = user.getType()
        follow = user.following
        
        ids, images, captions, usernames, likes, likePosts, comments = [], [], [], [], [], user.getLikePosts(), []

        for user1 in follow:
            posts = user1.getPosts()

            for post in posts:
                commentsPerPost = []
                ids.append(post.getID())
                images.append(post.getImage())
                captions.append(post.getCaption())
                usernames.append(post.getUserName())
                likes.append(post.getLikes())

                for comment in post.getComments():
                    commentsPerPost.append(comment)
                comments.append(commentsPerPost)

        if usertype == "private":
            requests = parseRequests(user)
            print(requests)
        return render_template("index.html",
                                username = session.get("username"),
                                numPosts = len(ids),
                                data = zip(ids, images, captions, usernames, likes, comments),
                                likePosts = [post.id for post in likePosts],
                                requests = requests,
                                userType = usertype)



@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = str(request.form["username"])
        password = str(request.form["password"])
        reenter = str(request.form["reenter-password"])
        accountType = str(request.form["account-type"])
        exists = db_session.query(User).filter(User.username == str(request.form["username"])).first()
        
        if exists:
            flash("Username has been taken")
        elif password != reenter:
            flash("Passwords does not match")
        else:
            user = User(username, password, accountType, [], [], [], [])
            db_session.add(user)
            db_session.commit()
            flash("Account created")
        return home()



@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST" and request.form["username"] and request.form["password"]:
            POST_USERNAME = str(request.form["username"])
            POST_PASSWORD = str(request.form["password"])

            user = db_session.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD])).first()

            if user:
                session["logged_in"] = True
                session["username"] = POST_USERNAME
            else:
                flash("Incorrect username/password. Please try again")
    return redirect("/")



@app.route("/addPost", methods=["POST", "GET"])
def addPost():
    if request.method == "GET":
        return render_template("addPost.html")
    elif request.method == "POST":
        username = session.get("username")
        image = request.files["image"]
        caption = request.form["caption"]

        newPost = Post(username, image.read(), caption, [], [])
        db_session.add(newPost)
        db_session.commit()

    return redirect("/",)



@app.route("/addLike", methods=["POST", "GET"])
def addLike():
    if request.method == "POST": 
        postid = request.form.get("id") 
        user = db_session.query(User).filter(User.username == str(session.get("username"))).first()
        post = db_session.query(Post).filter(Post.id == postid).first()
        post.likes.append(user)
        db_session.commit()

        return "success"



@app.route("/removeLike", methods=["POST", "GET"])
def removeLike():
    if request.method == "POST": 
        postid = request.form.get("id") 
        user = db_session.query(User).filter(User.username == str(session.get("username"))).first()
        post = db_session.query(Post).filter(Post.id == postid).first()
        post.likes.remove(user)
        db_session.commit()

        return "success"



@app.route("/addComment", methods=["POST", "GET"])
def addComment():
    if request.method == "POST":
        postid = request.form.get("id")
        newComment = Comment(postid, session.get("username"), request.form.get("comment"))        
        db_session.add(newComment)
        db_session.commit()
        
    return "<div class = 'comment'><label class = 'postUsername'>" + newComment.getUsername() + "</label><label class = 'comment'> " + newComment.getComment() + "</label></div>"



@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        users = db_session.query(User).filter(User.username.like("%" + request.form.get("username") + "%")).all()

        return jsonify([user.username for user in users])



@app.route("/follow", methods=["POST", "GET"])
def follow():
    if request.method == "POST":
        user = db_session.query(User).filter(User.username == request.form.get("username")).first()
        profile = db_session.query(User).filter(User.username == request.form.get("profileName")).first()

        if profile.getType() == "public":
            profile.followers.append(user)
            user.following.append(profile)
            db_session.commit()
            return "Unfollow"
        else:
            db_session.add(Request(user.getUserName(), profile.getUserName()))
            db_session.commit()
            return "Request Sent"



@app.route("/unfollow", methods=["POST", "GET"])
def unfollow():
    if request.method == "POST":
        user = db_session.query(User).filter(User.username == request.form.get("username")).first()
        profile = db_session.query(User).filter(User.username == request.form.get("profileName")).first()

        profile.followers.remove(user)

        db_session.commit()
    return "Follow"



@app.route("/removeRequest", methods=["POST", "GET"])
def removeRequest():
    if request.method == "POST":
        followRequest = db_session.query(Request).filter(Request.username.in_([request.form.get("username")]), Request.profile.in_([request.form.get("profileName")])).first()

        db_session.delete(followRequest)
        db_session.commit()

        return "Follow"



@app.route("/displayProfile", methods=["POST", "GET"])
def displayProfile():
    user = db_session.query(User).filter(User.username == session.get("username")).first()
    userToDisplay = None

    if request.method == "POST":
        userToDisplay = db_session.query(User).filter(User.username == request.form.get("username")).first()        
    elif request.method == "GET":
        userToDisplay = user

    if userToDisplay.getType() == "public" or user in userToDisplay.followers or userToDisplay.getUserName() == user.getUserName():
        posts = userToDisplay.getPosts()

        ids, images, captions, usernames, likes, likePosts, comments = [], [], [], [], [], user.getLikePosts(), []

        for post in posts:
            commentsPerPost = []
            ids.append(post.getID())
            images.append(post.getImage())
            captions.append(post.getCaption())
            usernames.append(post.getUserName())
            likes.append(post.getLikes())

            for comment in post.getComments():
                commentsPerPost.append(comment)
            comments.append(commentsPerPost)

        if user.getType() == "private":
            requests = parseRequests(user)

        return render_template("displayProfile.html",
                                username = session.get("username"),
                                usernameDisplay = userToDisplay.getUserName(),
                                numPosts = len(ids),
                                data = zip(ids, images, captions, usernames, likes, comments),
                                likePosts = [post.id for post in likePosts],
                                numFollowers = len(userToDisplay.followers),
                                numFollowing = len(userToDisplay.following),
                                ifFollowed = userToDisplay in user.following,
                                requests = requests,
                                userType = user.getType())
    else :
        requestexists = db_session.query(Request).filter(Request.username == user.getUserName(), Request.profile == userToDisplay.getUserName()).first()
        
        return render_template("displayProfile.html",
                                username = session.get("username"),
                                usernameDisplay = userToDisplay.getUserName(),
                                numPosts = len(userToDisplay.getPosts()),
                                numFollowers = len(userToDisplay.followers),
                                numFollowing = len(userToDisplay.following),
                                requestSent = requestexists is not None,
                                userType = user.getType())



@app.route("/logout")
def logout():
    session["logged_in"] = False
    return home()



@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



@app.errorhandler(Exception)
def handle_bad_request(e):
    return redirect("/")



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host="0.0.0.0", port=5000, debug=True)
