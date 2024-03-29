from app import login
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    bio = db.Column(db.String(248))
    passwd_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    admin = db.Column(db.Boolean)
    blesses = db.Column(db.Integer, default=0)
    curses = db.Column(db.Integer, default=0)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    replies = db.relationship('Reply', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<id {}, User {}>'.format(self.id, self.username)

    def set_password(self, password):
        self.passwd_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.passwd_hash, password)

    def hasBlessedReply(self, reply_id):
        r_bc = Reply_BC.query.filter_by(user_id=self.id, reply_id=reply_id).first() 
        if r_bc != None and r_bc.stance == True:
            return True
        return False 

    def blessReply(self, reply_id):
        reply = Reply.query.get(reply_id)
        if not self.hasBlessedReply(reply_id):
            if not self.hasCursedReply(reply_id):
                reply.blesses += 1
                R_BC = Reply_BC(user_id=self.id, reply_id=reply_id, stance=True)
                db.session.add(R_BC)
            else:
                reply.blesses += 1
                reply.curses -= 1
                Reply_BC.query.filter_by(user_id=self.id, reply_id=reply_id).first().stance = True 

    def hasCursedReply(self, reply_id):
        r_bc = Reply_BC.query.filter_by(user_id=self.id, reply_id=reply_id).first() 
        if r_bc != None and r_bc.stance == False:
            return True
        return False 
                 
    def curseReply(self, reply_id):
        reply = Reply.query.get(reply_id)
        if not self.hasCursedReply(reply_id):
            if not self.hasBlessedReply(reply_id):
                reply.curses += 1
                R_BC = Reply_BC(user_id=self.id, reply_id=reply_id, stance=False)
                db.session.add(R_BC)
            else:
                reply.blesses -= 1
                reply.curses += 1
                Reply_BC.query.filter_by(user_id=self.id, reply_id=reply_id).first().stance = False 


    def hasBlessedUser(self, user_id):
        u_bc = User_BC.query.filter_by(user_id=user_id, voter_id=self.id).first() 
        if u_bc != None and u_bc.stance == True:
            return True
        return False 

    def blessUser(self, user_id):
        user = User.query.get(user_id)
        if not self.hasBlessedUser(user_id):
            if not self.hasCursedUser(user_id):
                user.blesses += 1
                U_BC = User_BC(user_id=user_id, voter_id=self.id, stance=True)
                db.session.add(U_BC)
            else:
                user.blesses += 1
                user.curses -= 1
                User_BC.query.filter_by(user_id=user_id, voter_id=self.id).first().stance = True 


    def hasCursedUser(self, user_id):
        u_bc = User_BC.query.filter_by(user_id=user_id, voter_id=self.id).first() 
        if u_bc != None and u_bc.stance == False:
            return True
        return False 
                 

    def curseUser(self, user_id):
        user = User.query.get(user_id)
        if not self.hasCursedUser(user_id):
            if not self.hasBlessedUser(user_id):
                user.curses += 1
                U_BC = User_BC(user_id=user_id, voter_id=self.id, stance=False)
                db.session.add(U_BC)
            else:
                user.blesses -= 1
                user.curses += 1
                User_BC.query.filter_by(user_id=user_id, voter_id=self.id).first().stance = False 
    
    

class User_BC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    stance = db.Column(db.Boolean)

    def __repr__(self):
        return '<id {}, User_BC>'.format(self.id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    desc = db.Column(db.String(248))
    blesses = db.Column(db.Integer, default=0)
    curses = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    p_replies = db.relationship('Reply', backref='ogPost', lazy='dynamic')
    user_votes = db.relationship('Post_BC', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<id {}, Post {}>'.format(self.id, self.title)

    def blessedByUser(self, uid):
        if not self.isBlessedByUser(uid):
            if not self.isCursedByUser(uid):
                #hasn't voted yet
                self.blesses += 1
                p_bc = Post_BC(post_id=self.id, user_id=uid, stance=True)
                db.session.add(p_bc)
            else:
                # change from curse to bless
                self.blesses += 1
                self.curses -= 1
                Post_BC.query.filter_by(user_id=uid, post_id=self.id).first().stance = True;

    def cursedByUser(self, uid):
        if not self.isCursedByUser(uid):
            if not self.isBlessedByUser(uid):
                # hasn't voted yet
                self.curses += 1
                p_bc = Post_BC(post_id=self.id, user_id=uid, stance=False)
                db.session.add(p_bc)
            else:
                # change from bless to curse
                self.blesses -= 1
                self.curses += 1
                Post_BC.query.filter_by(user_id=uid, post_id=self.id).first().stance = False;

    def isBlessedByUser(self, uid):
        p_bc = Post_BC.query.filter_by(post_id=self.id, user_id=uid).first()
        if p_bc != None and p_bc.stance == True:
            return True
        return False
    
    def isCursedByUser(self, uid):
        p_bc = Post_BC.query.filter_by(post_id=self.id, user_id=uid).first()
        if p_bc != None and p_bc.stance == False:
            return True
        return False


class Post_BC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    stance = db.Column(db.Boolean)

    def __repr__(self):
        return '<id {}, Post_BC>'.format(self.id)

    
class Reply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
#     reply_id  = db.Column(db.Integer, db.ForeignKey('reply.id'))
    text = db.Column(db.String(248))
    blesses = db.Column(db.Integer, default=0)
    curses = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    stance = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # r_replies   = db.relationship('Reply', backref='ogPost', lazy='dynamic')
    user_votes = db.relationship('Reply_BC', backref='reply', lazy='dynamic')

    def __repr__(self):
        return '<id {}, Reply {}>'.format(self.id, self.text)


class Reply_BC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reply_id = db.Column(db.Integer, db.ForeignKey('reply.id'))
    stance = db.Column(db.Boolean)

    def __repr__(self):
        return '<id {}, Reply_BC>'.format(self.id)




# Old code from mega tutorial
'''
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
'''
