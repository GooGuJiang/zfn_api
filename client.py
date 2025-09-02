import requests
from urllib.parse import urljoin

from .academia import AcademiaMixin
from .auth import AuthMixin
from .courses import CourseMixin
from .grades import GradeMixin
from .info import InfoMixin
from .notifications import NotificationMixin
from .schedule import ScheduleMixin
from .utils import UtilsMixin
from .constants import RASPIANIE


class Client(
    UtilsMixin,
    AuthMixin,
    InfoMixin,
    GradeMixin,
    ScheduleMixin,
    AcademiaMixin,
    NotificationMixin,
    CourseMixin,
):
    """Main client for interacting with the teaching system."""

    raspisanie = []
    ignore_type = []

    def __init__(self, cookies=None, **kwargs):
        if cookies is None:
            cookies = {}
        self.base_url = kwargs.get("base_url", "")
        self.raspisanie = kwargs.get("raspisanie", RASPIANIE)
        self.ignore_type = kwargs.get("ignore_type", [])
        self.detail_category_type = kwargs.get("detail_category_type", [])
        self.timeout = kwargs.get("timeout", 3)
        Client.raspisanie = self.raspisanie
        Client.ignore_type = self.ignore_type

        self.key_url = urljoin(self.base_url, "xtgl/login_getPublicKey.html")
        self.login_url = urljoin(self.base_url, "xtgl/login_slogin.html")
        self.kaptcha_url = urljoin(self.base_url, "kaptcha")
        self.headers = requests.utils.default_headers()
        self.headers["Referer"] = self.login_url
        self.headers[
            "User-Agent"
        ] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/56.0.2924.87 Safari/537.36"
        )
        self.headers[
            "Accept"
        ] = (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3"
        )
        self.sess = requests.Session()
        self.cookies = cookies
