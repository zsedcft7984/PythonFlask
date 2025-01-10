import random, cv2, numpy as np, torch, torchvision
from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag

from flask import (
    Blueprint, 
    render_template,
    current_app, 
    send_from_directory,
    redirect,
    url_for,
    flash,
)
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError
import uuid
from pathlib import Path

#UploadImageForm을 import 한다
from apps.detector.forms import UploadImageForm, DetectorForm, DeleteForm
# redirect, url_for를 추가로 import한다
from flask_login import current_user, login_required

# template_folder를 지정한다(static은 지정하지 않는다.)
dt = Blueprint("detector", __name__, template_folder="templates")

# dt 애플리케이션을 사용하여 엔드포인트를 작성한다.
@dt.route("/")
def index():
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )
    # 태그 일람을 가져온다
    user_image_tag_dict = {}
    for user_image in user_images:
        #이미지에 연결할 태그 일람을 가져온다
        user_images_tag = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id ==
                    user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_images_tag
        #물체 감지 폼을 인스턴스화한다
        detector_form = DetectorForm()
        #삭제폼 인스턴스
        delete_form = DeleteForm()
        return render_template(
            "detector/index.html",
            user_images=user_images,
            #태그 일람을 탬플릿에 전달
            user_image_tag_dict=user_image_tag_dict,
            detector_form=detector_form,
            delete_form = delete_form
    
        )

@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@dt.route("/upload", methods=["GET", "POST"])
#로그인 필수로한다.
@login_required
def upload_image():
    #UploadImageForm을 이용해서 검증한다
    form = UploadImageForm()

    # post 요청들어오면 유효성 검사 결과에 따른 처리를 수행!
    if form.validate_on_submit():
        # 업로드된 이미지 파일을 취득한다.
        file = form.image.data
        # 파일의 파일명과 확장자를 취득하고, 파일명을 uuid로 변환한다
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        # 이미지를 저장한다
        image_path = Path(
            current_app.config["UPLOAD_FOLDER"], image_uuid_file_name
        )
        file.save(image_path)

        # DB에 저장한다
        user_image = UserImage(
            user_id = current_user.id, image_path = image_uuid_file_name
        )
        db.session.add(user_image)
        db.session.commit()

        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

@dt.route("/detect/<string:image_id>", methods=["POST"])
@login_required
def detect(image_id):
    user_image= db.session.query(UserImage).filter(
        UserImage.id == image_id).first()

    if user_image is None:
        flash("물체 감지 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.index"))
    #물체 감지 대상의 이미지 경로를 가져온다
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"], user_image.image_path
    )
    #물체 감질르 실행하여 태그와 변환 후의 이미지경로를 가져온다
    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        #데이터베이스에 태그 변환후의 이미지 경로 정보를 저장한다
        save_detected_image_tags(user_image, tags,
                                detected_image_file_name)
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생했습니다")
        #롤백
        db.session.rollback()
        #오류 로그 출력
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))
    return redirect(url_for("detector.index"))

@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        #user_image_tags 테이블로부터 레코드를 삭제한다
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        #user_images 테이블로부터 레코드를 삭제한다
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("이미지 삭제 처리에서 오류가 발생했습니다")
        #롤백
        db.session.rollback()
        #오류 로그 출력
        current_app.logger.error(e)
    return redirect(url_for("detector.index"))

def make_color(labels):
    #테두리 선의 색을 랜덤으로 설정
    colors = [[random.randint(0,255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color

def make_line(result_image):
    #테두리 선을 작성
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line

def draw_line(c1, c2, result_image, line, color):
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2

def draw_texts(result_image, line, c1, c2, color, labels, label):
    #감지한 텍스트 라벨을 이미지에 덧붙여 씀
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [225, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2

#exec_detext함수
def exec_detect(target_image_path):
    # 라벨 읽어 들이기
    labels = current_app.config["LABELS"]
    # 이미지 읽어 들이기
    image = Image.open(target_image_path)
    # 이미지 데이털르 텐서 타입의 수치 데이터로 변환
    image_tensor = torchvision.transforms.functional.to_tensor(image)
    #학습 완료 모델 읽어 들이기
    model = torch.load(Path(current_app.root_path, "detector", "model.pt"))
    #모델의 추론 모드로 전환
    model = model.eval()
    #추론 실행
    output = model([image_tensor])[0]

    tags = []
    result_image = np.array(image.copy())
    #학습 완료 모델이 감지한 각 물체만큼 이미지에 덧붙여 씀
    for box, label, score in zip(
        output["boxes"], output["labels"], output["scores"]
    ):
        print("감지 결과 raw 하게 확인 : ", box, label, score)
        if score > 0.5 and labels[label] not in tags:
            #테두리 선의 색 결정
            color = make_color(labels)
            #테두리 선의 결정
            line = make_line(result_image)
            #감지 이미지의 테ㅜ딜 선과 텍스트 라벨의 테두리 선의 외치 정보
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3]))
            #이미지에 테두리 선을 덧붙여씀
            cv2 = draw_line(c1, c2, result_image, line, color)
            #이미지에 텍스트 라벨을 벗붙여씀
            cv2 = draw_texts(result_image, line, c1, cv2, color, labels, label)
            tags.append(labels[label])
        #감지 후의 이미지 파일명 생성
        deteced_image_file_name = str(uuid.uuid4()) + ".jpg"
        #이미지 복사처 경로를 취득한다
        detected_image_file_path = str(
            Path(current_app.config["UPLOAD_FOLDER"],
                deteced_image_file_name)
        )
        cv2.imwrite(detected_image_file_path, cv2.cvtColor(
            result_image, cv2.COLOR_RGB2BGR)
        )
        return tags, deteced_image_file_name
    

# save_detected_image_tags 함수
def save_detected_image_tags(user_image, tags, detected_image_file_name):
    # 감지 후 이미지의 저장처 경로를 DB에 저장한다
    user_image.image_path = detected_image_file_name
    #감지 플러그를 True로 한다
    user_image.is_detected = True
    db.session.add(user_image)

    #user_images_tags 레코드를 작성한다
    for tag in tags:
        user_images_tags = UserImageTag(
            user_image_id = user_image.id, tag_name= tag)
        db.session.add(user_images_tags)

    db.session.commit()