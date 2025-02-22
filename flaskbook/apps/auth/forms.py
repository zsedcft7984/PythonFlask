from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
#아이디 생성 폼
class SignUpForm(FlaskForm):
    username = StringField(
        "사용자명",
        validators=[
            DataRequired(message="사용자명은 필수입니다."),
            Length(1,30, "15문자 이내로 입력해 주세요.")         
        ]
    )
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired(message="메일 주소는 필수입니다."),
            Email(message="메일 주소의 형식으로 입력해 주세요.")
        ]
    )
    password = PasswordField(
        "비밀번호",
        validators=[ 
            DataRequired(message="메일 주소는 필수입니다."),
            Length(min=6, message="한글+영문을 사용하여 최소6의 비밀번호를 작성해 주세요.")
        ]
    )
    password =PasswordField("비밀번호",
                            validators=[DataRequired("비밀번호는 필수입니다.")])
    submit = SubmitField("신규 등록")
#로그인 폼
class LoginForm(FlaskForm):
    email = StringField(
        "메일 주소",
        validators=[
            DataRequired(message="메일 주소는 필수입니다."),
            Email(message="메일 주소의 형식으로 입력해 주세요.")
        ]
    )
    password =PasswordField("비밀번호",
                            validators=[DataRequired("비밀번호는 필수입니다.")])
    submit = SubmitField("로그인")