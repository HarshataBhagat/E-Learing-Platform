from main import db, login
from flask_login import UserMixin, AnonymousUserMixin, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app



users = db.Table('users_courses', 
   db.Column('user_profile_id', db.Integer, db.ForeignKey('user_profile.id'), primary_key=True),
   db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)  

class Students(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(50))
   city = db.Column(db.String(50))  
   addr = db.Column(db.String(200))
   pin = db.Column(db.String(10))  


class User_Profile(UserMixin, db.Model):
   __tablename__ = 'user_profile'
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(100), nullable=False)
   firstname = db.Column(db.String(100))
   lastname = db.Column(db.String(100))
   email = db.Column(db.String(120), unique=True, nullable=False)
   img_file = db.Column(db.String(50), default = 'default_img.png')
   password_hash = db.Column(db.String(128))
   role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), default = 1)
   courses = db.relationship('Course', secondary=users, lazy='subquery', backref=db.backref('users_profile', lazy=True))
   course_instructor = db.relationship('Course', backref="user_profile_instructor", lazy=True)

   def __repr__(self):
      return '<User_Profile {}>'.format(self.username)

   def set_password(self, password):
      self.password_hash = generate_password_hash(password)

   def check_password(self, password):
      return check_password_hash(self.password_hash, password)

   def can(self, perm):
      return self.role is not None and self.role.has_permission(perm)

   def is_administrator(self):
      return self.can(Permission.ADMIN)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
        
login_manager.anonymous_user = AnonymousUser


@login.user_loader
def load_user(id):
    return User_Profile.query.get(int(id))



class Category(db.Model):
   __tablename__ = 'category'
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(200), nullable=False, unique=True )
   courses = db.relationship('Course', backref="category", lazy=True) 

   def __repr__(self) :
      return '<Category {}>'.format(self.name) 




class Course(db.Model):
   __tablename__ = 'course'
   id = db.Column(db.Integer, primary_key = True)
   course_name = db.Column(db.String(100), nullable= False)
   price = db.Column(db.Float)
   descripton = db.Column(db.Text)
   img_file = db.Column(db.String(50))
   category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
   instructor_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'))
   
   def __repr__(self) :
      return '<Course {}>'.format(self.course_name)  
 
class Role(db.Model):
   __tablename__ = 'roles'
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   permissions = db.Column(db.Integer, default=0)
   users =  db.relationship('User_Profile', backref="role", lazy='dynamic') 
      
   def add_permission(self, perm):
      if not self.has_permission(perm):
         self.permissions += perm

   def remove_permission(self, perm):
      if self.has_permission(perm):
         self.permissions -= perm

   def reset_permissions(self):
      self.permissions = 0

   def has_permission(self, perm):
      return self.permissions & perm == perm
  

class Permission:
   READ = 1
   ENROLL = 2
   MANAGE_COURSES = 4
   MANAGE_CATEGORY = 8
   MANAGE_INSTRUCTOR = 16
   ADMIN = 32
   

