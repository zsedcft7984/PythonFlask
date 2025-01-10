from flask import Flask
from pathlib import Path
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect   # 보안관련
from apps.config import config

from flask_login import LoginManager

# SQLAlchemy 를 인스턴스화 한다
db = SQLAlchemy()
csrf = CSRFProtect() 


# loginmanger 인스턴스화 한다.
login_manager = LoginManager()

# login_view 속성에 미로그인시 리다이렉트하는 엔드포인트를 지정한다.
login_manager.login_view = "auth.signup"
# login_message 속성에 로그인 후에 표시할 메시지를 지정한다.
# 여기에는 아무것도 표시하지 않도록 공백을 지정하도록 한다.
login_manager.login_message = ""


# create_app 함수를 작성한다.
def create_app(config_key):
    # 플라스크 인스턴스(객체)생성
    app = Flask(__name__)

    # 앱의 config을 설정을 한다
    # app.config.from_mapping(
    #     SECRET_KEY = "1234",
    #     SQLALCHEMY_DATABASE_URI= "sqlite:///"
    #     + str(Path(Path(__file__).parent.parent, 'local.sqlite')),
    #     SQLAlCHEMY_TRACK_MODIFICATIONS = False,
    #     ## SQL을 콘솔 로그에 출력하는 설정
    #     SQLALCHEMY_ECHO = True,
    #     WTF_CSRF_SECRET_KEY = "1234"
    # )

    app.config.from_object(config[config_key])

    # 함수를 사용해서 앱과 연계한다.
    csrf.init_app(app) 

    # SQLALchemy와 앱을 연계한다
    db.init_app(app)

    # Migrate와 앱을 연계한다.
    Migrate(app, db)

    # login_manager를 애플리케이션과 연계한다.
    login_manager.init_app(app)

    # crud패키지로부터 views를 import 한다
    from apps.crud import views as crud_views


    # 이제부터 작성하는 auth(회원인증관련) views를 import한다
    from apps.auth import views as auth_views

    app.register_blueprint(auth_views.auth, url_prefix="/auth")

    # register_blueprint 를 사용하 views의 crud를 앱에 등록한다.
    app.register_blueprint(crud_views.crud, url_prefix="/crud")

    # 이제부터 작성하는 detector 패키지로부터  views를 import한다
    from apps.detector import views as dt_views

    app.register_blueprint(dt_views.dt)

    return app
