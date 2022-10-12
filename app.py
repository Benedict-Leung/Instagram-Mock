from enum import unique
from flask import Flask, flash, render_template, request, redirect, jsonify, url_for
from sqlalchemy import Boolean, create_engine, Column, Integer, String, LargeBinary, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.sql.schema import ForeignKey
import os, base64
from flask_login import current_user, LoginManager, login_user, logout_user, login_required, UserMixin

engine = create_engine("postgresql+psycopg2://qjgpyesi:WA2GGQvNYXuR1gLn8_ri9btHbxFVNh_8@otto.db.elephantsql.com/qjgpyesi", echo=True)
Base = declarative_base()
db_session = scoped_session(sessionmaker(bind = engine))

likePostsTable = Table("likePosts", Base.metadata,
    Column("username", String, ForeignKey("users.username")),
    Column("postID", Integer, ForeignKey("posts.id"))
)

followTable = Table(
    "follow", Base.metadata,
    Column("username", String, ForeignKey("users.username"), primary_key=True),
    Column("profile", String, ForeignKey("users.username"), primary_key=True)
)



'''
+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
|   Username    |   Password    |     Type      |     Posts     |   LikePosts   |   Following   |   Followers   |
+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
|     userA     |     userA     |     public    |       []      |       []      |       []      |       []      |
+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
|     userB     |     userB     |    private    |       []      |       []      |       []      |       []      |
+---------------+---------------+---------------+---------------+---------------+---------------+---------------+
'''
class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key = True, unique=True)
    password = Column(String)
    type = Column(String)
    posts = relationship("Post")
    likePosts = relationship("Post", secondary = likePostsTable, back_populates = "likes")
    following = relationship("User", lambda: followTable,
                              primaryjoin = lambda: User.username == followTable.c.username,
                              secondaryjoin = lambda: User.username == followTable.c.profile,
                              backref = "followers")
    is_authenticated = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_anonymous = Column(Boolean, default=False)

    def __init__(self, username, password, type, posts, likePosts, followers, following):
        self.username = username
        self.password = password
        self.type = type
        self.posts = posts
        self.likePosts = likePosts
        self.followers = followers
        self.following = following
        self.is_authenticated = False
        self.is_active = True
        self.is_anonymous = False
    
    def getUserName(self):
        return self.username

    def getType(self):
        return self.type

    def getPosts(self):
        return self.posts
    
    def getLikePosts(self):
        return self.likePosts
    
    def getFollowers(self):
        return self.followers
    
    def getFollowing(self):
        return self.following
    
    def is_active(self):
        return True

    def is_authenticated(self):
        return self.is_authenticated

    def is_anonymous(self):
        return False
    
    def follow(self, user):
        self.following.append(user)
    
    def unFollow(self, user):
        self.getFollowing().remove(user)

    def get_id(self):
        return self.username




'''
+---------------+---------------+---------------+---------------+---------------+---------------+
|       ID      |    Username   |     Image     |     Caption   |     Likes     |    Comments   |
+---------------+---------------+---------------+---------------+---------------+---------------+
|       1       |     userA     |      ...      |   "Foo bar"   |       []      |       []      |
+---------------+---------------+---------------+---------------+---------------+---------------+
|       2       |     userB     |      ...      | "Hello World" |       []      |       []      |
+---------------+---------------+---------------+---------------+---------------+---------------+
|       3       |     userB     |      ...      |       ""      |       []      |       []      |
+---------------+---------------+---------------+---------------+---------------+---------------+
'''
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
    
    def addLike(self, user):
        return self.likes.append(user)
    
    def removeLike(self, user):
        return self.likes.remove(user)



'''
+---------------+---------------+---------------+---------------+
|       ID      |     postID    |    Username   |    Comment    |
+---------------+---------------+---------------+---------------+
|       1       |       3       |     userA     |      "Hi"     |
+---------------+---------------+---------------+---------------+
|       2       |       3       |     userB     |     "Nice"    |
+---------------+---------------+---------------+---------------+
|       3       |       1       |     userB     |     "Wow!"    |
+---------------+---------------+---------------+---------------+
'''
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



'''
+---------------+---------------+---------------+
|       ID      |    Username   |     Profile   |
+---------------+---------------+---------------+
|       1       |     userA     |     userB     |
+---------------+---------------+---------------+
'''
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



# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.config['SESSION_TYPE'] = 'filesystem'

from flask import send_from_directory
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ontariotech.png', mimetype='image/vnd.microsoft.icon')


def parseRequests(user):
    requests = db_session.query(Request).filter(Request.profile == user.getUserName()).all()
    usernames = []

    for request in requests:
        usernames.append(request.getUsername())
    return usernames


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(username):
    print("Load user.......................", username)
    return db_session.query(User).filter(User.username == username).first()

@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
@login_required
def home():
    print("----------------------home------------------------------")
    print(current_user.username)
    user = current_user
    usertype = user.getType()
    requests = None
    follow = user.getFollowing()

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
    return render_template("index.html",
                            username = user.getUserName(),
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
        return redirect("/home")



@app.route("/login", methods=["POST", "GET"])
def login():
    # print(current_user.is_authenticated)
    # if current_user.is_authenticated:
    #     return redirect("/home")

    if request.method == "POST" and request.form["username"] and request.form["password"]:
            POST_USERNAME = str(request.form["username"])
            POST_PASSWORD = str(request.form["password"])

            user = db_session.query(User).filter(User.username.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD])).first()
            
            if user:
                # session["logged_in"] = True
                # session["username"] = POST_USERNAME
                
                login_user(user)
                print(current_user.is_authenticated)
                print("index-----------------------------")
                return redirect("/")
            else:
                flash("Incorrect username/password. Please try again")
    elif request.method == "GET":
        return render_template("login.html")
    return redirect("/")



@app.route("/addPost", methods=["POST", "GET"])
@login_required
def addPost():
    if request.method == "GET":
        user = db_session.query(User).filter(User.username == current_user.getUserName()).first()
        usertype = user.getType()
        requests = None

        if usertype == "private":
            requests = parseRequests(user)

        return render_template("addPost.html", username = user.getUserName(), userType = usertype, requests = requests)
    elif request.method == "POST":
        username = current_user.getUserName()
        image = request.files["image"]
        caption = request.form["caption"]

        newPost = Post(username, image.read(), caption, [], [])
        db_session.add(newPost)
        db_session.commit()

    return redirect("/displayProfile")



@app.route("/addLike", methods=["POST", "GET"])
@login_required
def addLike():
    if request.method == "POST": 
        postid = request.form.get("id") 
        user = db_session.query(User).filter(User.username == current_user.getUserName()).first()
        post = db_session.query(Post).filter(Post.id == postid).first()
        post.addLike(user)
        db_session.commit()

        return "success"



@app.route("/removeLike", methods=["POST", "GET"])
@login_required
def removeLike():
    if request.method == "POST": 
        postid = request.form.get("id") 
        user = db_session.query(User).filter(User.username == current_user.getUserName()).first()
        post = db_session.query(Post).filter(Post.id == postid).first()
        post.removeLike(user)
        db_session.commit()

        return "success"



@app.route("/addComment", methods=["POST", "GET"])
@login_required
def addComment():
    if request.method == "POST":
        postid = request.form.get("id")
        newComment = Comment(postid, current_user.getUserName(), request.form.get("comment"))        
        db_session.add(newComment)
        db_session.commit()
        
    return "<div class = 'comment'><label class = 'postUsername'>" + newComment.getUsername() + "</label><label class = 'comment'> " + newComment.getComment() + "</label></div>"



@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    if request.method == "POST":
        users = db_session.query(User).filter(User.username.like("%" + request.form.get("username") + "%")).all()

        return jsonify([user.username for user in users])



@app.route("/follow", methods=["POST", "GET"])
@login_required
def follow():
    if request.method == "POST":
        user = db_session.query(User).filter(User.username == request.form.get("username")).first()
        profile = db_session.query(User).filter(User.username == request.form.get("profileName")).first()

        if profile.getType() == "public":
            user.follow(profile)
            db_session.commit()
            return "Unfollow"
        else:
            db_session.add(Request(user.getUserName(), profile.getUserName()))
            db_session.commit()
            return "Request Sent"



@app.route("/unfollow", methods=["POST", "GET"])
@login_required
def unfollow():
    if request.method == "POST":
        user = db_session.query(User).filter(User.username == request.form.get("username")).first()
        profile = db_session.query(User).filter(User.username == request.form.get("profileName")).first()

        user.unFollow(profile)

        db_session.commit()
    return "Follow"



@app.route("/removeRequest", methods=["POST", "GET"])
@login_required
def removeRequest():
    if request.method == "POST":
        followRequest = db_session.query(Request).filter(Request.username.in_([request.form.get("username")]), Request.profile.in_([request.form.get("profileName")])).first()

        db_session.delete(followRequest)
        db_session.commit()

        return "Follow"



@app.route("/displayProfile", methods=["POST", "GET"])
@login_required
def displayProfile():
    user = db_session.query(User).filter(User.username == current_user.getUserName()).first()
    userToDisplay = None
    requests = None

    if request.method == "POST":
        userToDisplay = db_session.query(User).filter(User.username == request.form.get("username")).first()        
    elif request.method == "GET":
        userToDisplay = user

    if userToDisplay.getType() == "public" or user in userToDisplay.getFollowers() or userToDisplay.getUserName() == user.getUserName():
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
                                username = current_user.getUserName(),
                                usernameDisplay = userToDisplay.getUserName(),
                                numPosts = len(ids),
                                data = zip(ids, images, captions, usernames, likes, comments),
                                likePosts = [post.id for post in likePosts],
                                numFollowers = len(userToDisplay.getFollowers()),
                                numFollowing = len(userToDisplay.getFollowing()),
                                ifFollowed = userToDisplay in user.getFollowing(),
                                requests = requests,
                                userType = user.getType())
    else :
        requestexists = db_session.query(Request).filter(Request.username == user.getUserName(), Request.profile == userToDisplay.getUserName()).first()
        
        return render_template("displayProfile.html",
                                username = current_user.getUserName(),
                                usernameDisplay = userToDisplay.getUserName(),
                                numPosts = len(userToDisplay.getPosts()),
                                numFollowers = len(userToDisplay.getFollowers()),
                                numFollowing = len(userToDisplay.getFollowing()),
                                requestSent = requestexists is not None,
                                userType = user.getType())



@app.route("/acceptRequest", methods=["POST", "GET"])
@login_required
def acceptRequest():
    if request.method == "POST":
        profileName = request.form.get("profileName")
        username = request.form.get("username")
        profileRequest = db_session.query(Request).filter(Request.profile == profileName, Request.username == username).first()
        
        if profileRequest:
            user = db_session.query(User).filter(User.username == username).first()
            profile = db_session.query(User).filter(User.username == profileName).first()

            db_session.delete(profileRequest)
            user.follow(profile)

            db_session.commit()

            return "Success"
    return ""


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")



@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()



@app.errorhandler(Exception)
def handle_bad_request(e):
    print(e)
    # return redirect("/")



if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5000, debug=True)
