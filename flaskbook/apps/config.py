from pathlib import Path

basedir = Path(__file__).parent.parent

# BaseConfig 클래스 작성하기

class BaseConfig :
    SECRET_KEY = '123'
    WTF_CSRF_SECRET_KEY = '122'
    # 이미지 업로드 경로에 apps/images 를 지정한다
    UPLOAD_FOLDER = str(Path(basedir, "apps", "images"))

    # 물체 감지에 이용하는 라벨
    LABELS = [
        "unlabeled",
        "person",
        "bicycle",
        "car",
        "motorcycle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
        "traffic light",
        "fire hydrant",
        "street sign",
        "stop sign",
        "parking meter",
        "bench",
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
        "hat",
        "backpack",
        "umbrella",
        "shoe",
        "eye glasses",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis"
    ]

# BaseConfig 클래스를 상속하여 LocalConfig 클래스를 작성한다.
class LocalConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'local.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

# BaseConfig 클래스를 상속하여 TestingConfig 클래스를 작성한다.
class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'testing.sqlite'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

# config 사전에 매핑한다
config = {
    "testing" : TestingConfig,
    "local" : LocalConfig,
}