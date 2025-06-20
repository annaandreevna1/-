import os
from flask import render_template, request, redirect, url_for, jsonify, flash, send_file, make_response
from . import db
from .models import User, Parent, Event
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

def init_routes(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        return render_template('index.html', current="index")
    
    @app.route('/users')
    @login_required
    def users():
        users = User.query.all()
        return render_template('users.html', current="users", users=users)

    @app.route('/user/add', methods=["GET", "POST"])
    @login_required
    def user_add():
        if request.method == "GET":
            return render_template('user/add.html', current="users")
        if request.method == "POST":
            user = User()
            user.username = request.form["username"]
            user.password = request.form["password"]
            db.session.add(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/user/edit/<id>', methods=["GET", "POST"])
    @login_required
    def user_edit(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/edit.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            user.username = request.form["username"]
            user.password = request.form["password"]
            db.session.commit()
            return redirect("/users")

    @app.route('/user/del/<id>', methods=["GET", "POST"])
    @login_required
    def user_del(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/del.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            db.session.delete(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/parents')
    @login_required
    def parents():
        parents = Parent.query.all()
        return render_template('parents.html', current="parents", parents=parents)

    @app.route('/parent/add', methods=["GET", "POST"])
    @login_required
    def parent_add():
        if request.method == "GET":
            return render_template('parent/add.html', current="parents")
        if request.method == "POST":
            parent = Parent()
            parent.first_name = request.form["first-name"]
            parent.last_name = request.form["last-name"]
            parent.patronymic = request.form["patronymic"]
            parent.name_children = request.form["name_children"]
            db.session.add(parent)
            db.session.commit()
            return redirect("/parents")

    @app.route('/parent/edit/<id>', methods=["GET", "POST"])
    @login_required
    def parent_edit(id):
        if request.method == "GET":
            parent = db.get_or_404(Parent, id)
            return render_template('parent/edit.html', current="parents", parent=parent)
        if request.method == "POST":
            parent = db.get_or_404(Parent, request.form["id"])
            parent.first_name = request.form["first-name"]
            parent.last_name = request.form["last-name"]
            parent.patronymic = request.form["patronymic"]
            parent.name_children = request.form["name_children"]
            db.session.commit()
            return redirect("/parents")

    @app.route('/parent/del/<id>', methods=["GET", "POST"])
    @login_required
    def parent_del(id):
        if request.method == "GET":
            parent = db.get_or_404(Parent, id)
            return render_template('parent/del.html', current="parents", parent=parent)
        if request.method == "POST":
            parent = db.get_or_404(Parent, request.form["id"])
            db.session.delete(parent)
            db.session.commit()
            return redirect("/parents")
        
    @app.route('/parent/photo-edit/<id>', methods=["GET", "POST"])
    def parent_photo_edit(id):
        if request.method == "GET":
            parent = db.get_or_404(Parent, id)
            return render_template('parent/add_photo.html', current="parents", parent=parent)
        if request.method == "POST":
            # Проверяем, есть ли файл в запросе
            if 'photo' not in request.files:
                flash('No file part')
                return redirect("/parents")
        
            file = request.files['photo']
        
            # Если пользователь не выбрал файл
            if file.filename == '':
                flash('No selected file')
                return redirect("/parents")
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jpg"}
            
            # Если файл разрешен и корректен
            if file and allowed_file(file.filename):
                if not os.path.exists(app.config['IMGS']):
                    os.makedirs(app.config['IMGS'])
                file.save(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")))
                return redirect("/parents")
    
        return redirect("/parents")

    @app.route('/parent/photo/<id>', methods=["GET", "POST"])
    def parent_photo(id):
        if request.method == "GET":
            parent = db.get_or_404(Parent, id)
            if os.path.isfile(os.path.join(app.config['IMGS'], f"{id}.jpg")):
                return send_file(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")), as_attachment=True)
            else:
                return make_response(f"File '{id}' not found.", 404)
    
    @app.route('/parents/json')
    def parents_all():
        parents = Parent.query.all()
        result = []
        for parent in parents:
            parent_dict = parent.__dict__
            parent_dict.pop('_sa_instance_state', None)  # Удаляем служебное поле SQLAlchemy
            result.append(parent_dict)
        return jsonify(result)

    @app.route('/events')
    @login_required
    def events():
        events = Event.query.all()
        
        return render_template('events.html', current="events", events=events)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
    
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
        
            user = User.query.filter_by(username=username, password=password).first()
            
            if user:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/")
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
    
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")