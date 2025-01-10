from email_validator import validate_email, EmailNotValidError
from flask_debugtoolbar import DebugToolbarExtension
from flask_mail import Mail, Message
from flask import Flask, url_for, render_template,request,redirect,flash, make_response,session
import logging,os

app = Flask(__name__)
#SECRET_KEY 추가한다
app.config["SECRET_KEY"] = "7984"
#로그 레벨을 설정한다.
app.logger.setLevel(logging.DEBUG)
app.logger.critical("fatal error")
app.logger.error("error")
app.logger.warning("warning")
app.logger.info("info")
app.logger.debug("debug")
#리다이렉트를 중단하지 않도록 한다
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
#Mail 클래스의 config를 추가한다
app.config["MAIL_SERVER"] = "smtp.gmail.com"                  #이메일 서버 호스트명
app.config["MAIL_PORT"] = 587                      #이메일 서버의 포트
app.config["MAIL_USE_TLS"] = True                 #TLS를 유효로 하는가
app.config["MAIL_USERNAME"] = "phonecp7984@gmail.com"               #송신자 이메일 주소              
app.config["MAIL_PASSWORD"] = "qxxl hsoq ygol uefu"              #송신자 이메일 주소의 비밀번호
app.config["MAIL_DEFAULT_SENDER"] = "Flaskbook <phonecp7984@gmail.com>"  #이메일의 송신자명과 이메일 주소


#flask-mail 확장을 등록
mail =Mail(app)
# DebugToolbarExtension에 애플리케이션을 설정한다.
toolbar = DebugToolbarExtension(app)

@app.route("/")
def index():
    return "Hello, Flaskbook!"

@app.route("/contact")
def contact():
    #응답 객체를 취득한다
    response = make_response(render_template("contact.html"))
    # 쿠키를 설정한다
    response.set_cookie("flaskbook key","flaskbook value")
    #세션을 설정한다
    session["username"] = "AK"
    return response

    # return render_template("contact.html")

@app.route("/contact/complete", methods=["GET","POST"])
def contact_complete():
    if request.method == "POST":
        #form 속성을 사용해서 폼의 값을 취득한다
        username = request.form["username"]
        email = request.form["email"]
        description = request.form["description"]

        #입력 체크
        is_valid = True

        if not username:
            flash("사용자명은 필수입니다.")
            is_valid = False

        if not email:
            flash("메일 주소는 필수입니다.")
            is_valid = False
        
        try:
            validate_email(email)
        except EmailNotValidError:
            flash("메일 주소의 형식으로 입력해 주세요.")
            is_valid = False
        
        if not description:
            flash("문의 내용은 필수입니다.")
            is_valid = False

        if not is_valid:
            return redirect(url_for("contact"))
        
        #이메일을 보낸다
        send_email(
            email,
            "문의 감사합니다.",
            "contact_mail",
            username=username,
            description=description
            )
        
        #문의 완료 메시지
        flash("문의해 주셔서 감사합니다.")
        return redirect(url_for("contact_complete"))
    
    return render_template("contact_complete.html")

def send_email(to, subject, template, **kwargs):
    msg = Message(subject, recipients=[to])
    msg.body =render_template(template + ".txt", **kwargs)
    msg.html =render_template(template + ".html", **kwargs)
    mail.send(msg)