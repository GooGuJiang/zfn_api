import base64
import json
import time
import traceback
from pyquery import PyQuery as pq
from requests import exceptions


class AuthMixin:
    """Authentication related APIs."""

    def login(self, sid, password):
        """登录教务系统"""
        need_verify = False
        try:
            req_csrf = self.sess.get(self.login_url, headers=self.headers, timeout=self.timeout)
            if req_csrf.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_csrf.text)
            csrf_token = doc("#csrftoken").attr("value")
            pre_cookies = self.sess.cookies.get_dict()
            req_pubkey = self.sess.get(self.key_url, headers=self.headers, timeout=self.timeout).json()
            modulus = req_pubkey["modulus"]
            exponent = req_pubkey["exponent"]
            if str(doc("input#yzm")) == "":
                encrypt_password = self.encrypt_password(password, modulus, exponent)
                login_data = {"csrftoken": csrf_token, "yhm": sid, "mm": encrypt_password}
                req_login = self.sess.post(
                    self.login_url, headers=self.headers, data=login_data, timeout=self.timeout
                )
                doc = pq(req_login.text)
                tips = doc("p#tips")
                if str(tips) != "":
                    if "用户名或密码" in tips.text():
                        return {"code": 1002, "msg": "用户名或密码不正确"}
                    return {"code": 998, "msg": tips.text()}
                self.cookies = self.sess.cookies.get_dict()
                return {"code": 1000, "msg": "登录成功", "data": {"cookies": self.cookies}}
            need_verify = True
            req_kaptcha = self.sess.get(self.kaptcha_url, headers=self.headers, timeout=self.timeout)
            kaptcha_pic = base64.b64encode(req_kaptcha.content).decode()
            return {
                "code": 1001,
                "msg": "获取验证码成功",
                "data": {
                    "sid": sid,
                    "csrf_token": csrf_token,
                    "cookies": pre_cookies,
                    "password": password,
                    "modulus": modulus,
                    "exponent": exponent,
                    "kaptcha_pic": kaptcha_pic,
                    "timestamp": time.time(),
                },
            }
        except exceptions.Timeout:
            msg = "获取验证码超时" if need_verify else "登录超时"
            return {"code": 1003, "msg": msg}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            msg = "获取验证码时未记录的错误" if need_verify else "登录时未记录的错误"
            return {"code": 999, "msg": f"{msg}：{str(e)}"}

    def login_with_kaptcha(
        self, sid, csrf_token, cookies, password, modulus, exponent, kaptcha, **kwargs
    ):
        """需要验证码的登陆"""
        try:
            encrypt_password = self.encrypt_password(password, modulus, exponent)
            login_data = {"csrftoken": csrf_token, "yhm": sid, "mm": encrypt_password, "yzm": kaptcha}
            req_login = self.sess.post(
                self.login_url,
                headers=self.headers,
                cookies=cookies,
                data=login_data,
                timeout=self.timeout,
            )
            if req_login.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_login.text)
            tips = doc("p#tips")
            if str(tips) != "":
                if "验证码" in tips.text():
                    return {"code": 1004, "msg": "验证码输入错误"}
                if "用户名或密码" in tips.text():
                    return {"code": 1002, "msg": "用户名或密码不正确"}
                return {"code": 998, "msg": tips.text()}
            self.cookies = self.sess.cookies.get_dict()
            if not self.cookies.get("route") and cookies.get("route"):
                route_cookies = {"JSESSIONID": self.cookies["JSESSIONID"], "route": cookies["route"]}
                self.cookies = route_cookies
            else:
                return {"code": 1000, "msg": "登录成功", "data": {"cookies": self.cookies}}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "登录超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "验证码登录时未记录的错误：" + str(e)}
