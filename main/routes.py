from main import app
from flask import render_template, redirect, jsonify, make_response, flash, request, url_for
from flask import  send_file
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from sqlalchemy.sql.expression import desc
from sqlalchemy import func
from main.decorators import admin_required, instructor_required, permission_required
from main.models import *
from flask_login import current_user, login_user, logout_user, login_required
from main.forms import LoginForm, Widgets,RegistrationForm
import os
import json

@app.route("/",methods=['GET','POST'])
def home():
    popular_courses_list_query = db.session.query(users.c.course_id,
                                func.count(users.c.course_id).label("value_occurrence")).group_by(
                                users.c.course_id).order_by( desc("value_occurrence")).limit(3).all()
                                    
    popular_courses_list = [Course.query.get(k._data[0]) for k in popular_courses_list_query ]

                                     
    return render_template('index.html',popular_courses_list=popular_courses_list)

    
@app.route('/login',methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User_Profile.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')  
            return redirect(url_for('login')) 
        login_user(user, remember=form.remember_me.data)   
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page) 
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User_Profile(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Register', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/courses")
def courses():
    courses_list = Course.query.all()
    return render_template('courses.html',courses_list=courses_list)

@app.route("/course_details/<int:id>", methods=['GET','POST'])
def course_details(id):  
    detail = Course.query.filter_by(id=id).first()
    return render_template('course-details.html',detail=detail)  


@app.route("/download_file")
def download_file():
    p = "static\pdf_document\info_doc.pdf"
    return send_file(p,as_attachment=True)


#================ Admin view ==================
@app.route('/admin')
@login_required
@admin_required
def admin():       
    return render_template('admin.html')




#================ Instructor view ==================
@app.route('/instructor')
@login_required
@instructor_required
def instructor():      
    return render_template('instructor_home.html') 


@app.route('/instructor/list_course')
@login_required
@instructor_required
def list_course():
    courses_list = Course.query.all()       
    return render_template('instructor_course_list.html',courses_list=courses_list) 



@app.route('/instructor/add_course/<int:id>', methods=['GET', 'POST'])
@login_required
@instructor_required
def add_course(id): 

    if request.method == 'POST':
        course_name = request.form.get('course_name')
        price = float(request.form.get('price'))
        descripton = request.form.get('descripton')
        img_file = request.form.get('img_file')  
        category = request.form.get('category')

        if id == 0:
            course = Course(course_name=course_name, price=price, descripton=descripton,
             img_file=img_file, category_id=category, instructor_id=current_user.id)
            c = course
            db.session.add(course)
            db.session.commit() 
            return redirect('/instructor/list_course')
        else:
            course = Course.query.filter_by(id=id).first()
            course.course_name = course_name
            course.price = price
            course.descripton = descripton
            course.img_file = img_file 
            course.category_id= int(category)
            db.session.commit()
            return redirect('/instructor/list_course')
    course = Course.query.filter_by(id=id).first()  
    category_list = Category.query.all()    
    return render_template('add_course.html',course=course, category_list=category_list, id=id) 

@app.route('/instructor/list_category')
@login_required
@instructor_required
def list_category():
    category_list = Category.query.all()       
    return render_template('instructor_category_list.html',category_list=category_list)   



@app.route('/instructor/add_category/<int:id>', methods=['GET', 'POST'])
@login_required
@instructor_required
def add_category(id): 

    if request.method == 'POST':
        name = request.form.get('name')
        if id == 0:
            category = Category(name=name)
            db.session.add(category)
            db.session.commit() 
            return redirect('/instructor/list_category')
    return render_template('add_category.html',id=id) 



@app.route('/delete_category/<int:id>', methods=['GET','POST'])
@login_required
@instructor_required
def delete_category(id):
    category = Category.query.filter_by(id=id).first()
    db.session.delete(category)
    db.session.commit()
    return redirect('/instructor/list_category')


@app.route('/delete_course/<int:id>', methods=['GET','POST'])
@login_required
@instructor_required
def delete_course(id):
    course = Course.query.filter_by(id=id).first()
    db.session.delete(course)
    db.session.commit()
    return redirect('/instructor/list_course')


#================ enroll view ==================

@app.route('/enroll/<int:id>', methods=['GET','POST'])
@login_required
def enroll(id):
    # f_course_id = id
    course = Course.query.filter_by(id=id).first()    
    user =  User_Profile.query.filter_by(id=current_user.id).first()
    # print(user)
    # print(course)
    user.courses.append(course)
    db.session.commit() 
    return render_template('enroll.html')


#================ contact view ==================
@app.route('/contact', methods=['GET','POST'])
def contact():
    form = Widgets()
    contact_info =[]
    if (request.method == 'POST'):
        first_name = request.form.get('first_name')        
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        message = request.form.get('message')
        quantity = request.form.get('quantity')
        contact_info.append({"first_name":first_name,'last_name':last_name,'email':email, 'message':message})
        print(contact_info)
        f = request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        try:
            print(quantity*quantity)
        except TypeError:
            print('Please enter a valid integer')
        return "Uploaded successfully!"
        # return redirect('/')
    return render_template('contact.html', form=form) 
   


# courses_list = Course.query.all()
# for courses in courses_list:
#     print(courses.course_name)

# ==================== CURD Operations ==================
#========= Show ===========
@app.route('/student_info', methods=['GET', 'POST'])
def student_form():
    students = Students.query.all()
    return render_template('student_form.html',students=students)


#=========Add and Edit ===========
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def add(id):

    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('city')
        addr = request.form.get('addr')
        pin = request.form.get('pin')
        

        if id == 0:
            student = Students(name=name, city=city, addr=addr, pin=pin)
            db.session.add(student)
            db.session.commit() 
            return redirect('/student_info')
        else:
            student = Students.query.filter_by(id=id).first()
            student.name = name
            student.city = city
            student.addr = addr
            student.pin = pin 
            db.session.commit()
            return redirect('/student_info')
    student = Students.query.filter_by(id=id).first()        
    return render_template('edit.html', student=student, id=id)


#========= Delete  ===========
@app.route('/delete/<string:id>', methods=['GET','POST'])
def delete(id):
    student = Students.query.filter_by(id=id).first()
    db.session.delete(student)
    db.session.commit()
    return redirect('/student_info')



#================ JSON Responce ==================
# @app.route('/get_data_json')
# def get_data_json():
#     return jsonify(courses_info)


#================ 404 error handeling ================== 
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404  


#================ Cookies handeling ================== 
@app.route('/cookies')
def cookies():
    res = make_response('Cookies', 200)
    cookies = request.cookies

    flavour = cookies.get('flavour')
    chocolate_type = cookies.get("chocolate type")
    chewy = cookies.get("chewy")

    # print(cookies)   

    res.set_cookie(
        "flavour", 
        value='chocolate chip', 
        max_age = None, 
        expires = None, 
        path = request.path, 
        domain=None, 
        secure=False, 
        httponly=False, 
        samesite=None
    )

    res.set_cookie("chocolate type", "dark")
    res.set_cookie("chewy", "yes")
    return res    
