import base64
import binascii
import unicodedata
import rsa


class UtilsMixin:
    """Common utility helpers."""

    @staticmethod
    def encrypt_password(pwd, n, e):
        """Encode password using RSA and base64."""
        message = str(pwd).encode()
        rsa_n = binascii.b2a_hex(binascii.a2b_base64(n))
        rsa_e = binascii.b2a_hex(binascii.a2b_base64(e))
        key = rsa.PublicKey(int(rsa_n, 16), int(rsa_e, 16))
        encropy_pwd = rsa.encrypt(message, key)
        result = binascii.b2a_base64(encropy_pwd)
        return result

    @staticmethod
    def parse_int(digits):
        if not digits:
            return None
        if not digits.isdigit():
            return digits
        return int(digits)

    @staticmethod
    def align_floats(floats):
        if not floats:
            return None
        if floats == "无":
            return "0.0"
        return format(float(floats), ".1f")

    @staticmethod
    def get_place(place):
        return place.split("<br/>")[0] if "<br/>" in place else place

    @staticmethod
    def get_course_time(time):
        return "、".join(time.split("<br/>")) if "<br/>" in time else time

    @staticmethod
    def is_number(s):
        if s == "":
            return False
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            for i in s:
                unicodedata.numeric(i)
            return True
        except (TypeError, ValueError):
            pass
        return False
