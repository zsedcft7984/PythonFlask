# db를 import 한다
from apps.app import db

from apps.crud.forms import UserForm
from apps.crud.models import User
from flask import Blueprint, render_template, redirect, url_for

from flask_login import login_required

# Bluepring로 crud앱을 생성한다
crud = Blueprint("crud", __name__, template_folder = "templates", static_folder = "static")

# index 엔드포인트를 작성하고 index.html을 반환한다
@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")

@crud.route("/sql")
@login_required
def sql():
    db.session.query(User).all()
    return "콘솔 로그를 확인해 주세요"


# methods에 GET과 POST 를 지정합니다.
@crud.route("/users/<user_id>", methods=["GET" , "POST"])
@login_required
def edit_user(user_id):
    form = UserForm()

    # User 모델을 이용하여 사용자를 취득한다.
    user = User.query.filter_by(id=user_id).first()

    # form으로부터 제출된 경우는 사용자를 갱신하여 사용자의 일람 화면으로 리다이렉트한다.

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))

    # GET의 경우는 html을 반환한다
    return render_template("crud/edit.html", user=user, form=form)

@crud.route("/users/<user_id>/delete", methods =["post"])
@login_required
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("crud.users"))


# 사용자의 일람 화면의 엔드포인트 만들기
@crud.route("/users")
@login_required
def users():
    """사용자의 일람을 취득한다"""
    users =User.query.all()
    return render_template("crud/index.html", users=users)

@crud.route("/users/new", methods=["GET" , "POST"])
@login_required
def create_user():
    #UserForm 을 인스턴스화 한다.
    form = UserForm()

    # 폼의 값을 검증한다.
    if form.validate_on_submit():
        # 사용자를 작성한다.
        user = User(
            username= form.username.data,
            email = form.email.data,
            password = form.password.data,
        )
        
        # 사용자를 추가하고 커밋한다.
        db.session.add(user)
        db.session.commit()

        #사용자의 일람화면으로 리다이렉트한다.
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)






