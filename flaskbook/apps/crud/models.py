from datetime import datetime

from apps.app import db, login_manager       #  flaskbook/apps/app.py 으로부터 db를 import합니다.
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# db.Model을 상속한 User 클래스를 작성한다 모델정의하기
class User(db.Model, UserMixin):
    # 테이블명을 지정한다.
    __tablename__ = "users"

    # 컬럼을 정의한다.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default = datetime.now, onupdate = datetime.now)
    
    # backref를 이용하여 relation 정보를 설정한다.
    user_images = db.relationship(
                    "UserImage", backref="user", order_by = "desc(UserImage.id)"
                    )
    

    # 비밀번호를 설정하기 위한 프로퍼티
    ## 사용자가 패스워드 라는 속성명을 갱신하려고 할떄 , 나는 그값을 받아서 암호화 generate_password_hash)를 한차례 수행 한다음에 password_hash 속성에 이를 저장할래!
    @property
    def password(self):
            raise ArithmeticError("읽어 들일 수 없음")
        
    # 비밀번호 설정하기 위해 setter 함수로 해시화한 비밀번호를 설정한다.
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    

    # 비밀번호를 체크한다.
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # 이메일 주소 중복을 체크한다.
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None
    
# 로그인하고 있는 사용자 정보를 취득하는 함수를 정의한다.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)