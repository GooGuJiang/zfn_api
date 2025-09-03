from __future__ import annotations

import json
import traceback
from typing import Any
from urllib.parse import urljoin

from pyquery import PyQuery as pq
from requests import exceptions

from ..protocols import ClientProtocol


class InfoMixin(ClientProtocol):
    """Personal information APIs."""

    def get_info(self) -> dict[str, Any]:
        """获取个人信息"""
        url = urljoin(self.base_url, "xsxxxggl/xsxxwh_cxCkDgxsxx.html?gnmkdm=N100801")
        try:
            req_info = self.sess.get(
                url,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_info.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_info.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            info = req_info.json()
            if info is None:
                return self._get_info()
            result = {
                "sid": info.get("xh"),
                "name": info.get("xm"),
                "college_name": info.get("zsjg_id", info.get("jg_id")),
                "major_name": info.get("zszyh_id", info.get("zyh_id")),
                "class_name": info.get("bh_id", info.get("xjztdm")),
                "status": info.get("xjztdm"),
                "enrollment_date": info.get("rxrq"),
                "candidate_number": info.get("ksh"),
                "graduation_school": info.get("byzx"),
                "domicile": info.get("jg"),
                "postal_code": info.get("yzbm"),
                "politics_status": info.get("zzmmm"),
                "nationality": info.get("mzm"),
                "education": info.get("pyccdm"),
                "phone_number": info.get("sjhm"),
                "parents_number": info.get("gddh"),
                "email": info.get("dzyx"),
                "birthday": info.get("csrq"),
                "id_number": info.get("zjhm"),
            }
            return {"code": 1000, "msg": "获取个人信息成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取个人信息超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取个人信息时未记录的错误：" + str(e)}

    def _get_info(self) -> dict[str, Any]:
        """获取个人信息"""
        url = urljoin(self.base_url, "xsxxxggl/xsgrxxwh_cxXsgrxx.html?gnmkdm=N100801")
        try:
            req_info = self.sess.get(url, headers=self.headers, cookies=self.cookies, timeout=self.timeout)
            if req_info.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_info.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            pending_result = {}
            for ul_item in doc.find("div.col-sm-6").items():
                content = pq(ul_item).find("div.form-group")
                key = pq(content).find("label.col-sm-4.control-label").text()
                value = pq(content).find("div.col-sm-8 p.form-control-static").text()
                if key:
                    pending_result[key] = value
            for ul_item in doc.find("div.col-sm-4").items():
                content = pq(ul_item).find("div.form-group")
                key = pq(content).find("label.col-sm-4.control-label").text()
                value = pq(content).find("div.col-sm-8 p.form-control-static").text()
                if key:
                    pending_result[key] = value
            if pending_result.get("学号：") == "":
                return {
                    "code": 1014,
                    "msg": "当前学年学期无学生时盒数据，您可能已经毕业了。\n\n如果是专升本同学，请使用专升本后的新学号登录～",
                }
            result = {
                "sid": pending_result.get("学号：") or "无",
                "name": pending_result.get("姓名：") or "无",
                "domicile": pending_result.get("籍贯：") or "无",
                "phone_number": pending_result.get("手机号码：") or "无",
                "parents_number": "无",
                "email": pending_result.get("电子邮箱：") or "无",
                "political_status": pending_result.get("政治面貌：") or "无",
                "national": pending_result.get("民族：") or "无",
            }
            if pending_result.get("学院名称：") is not None:
                result.update(
                    {
                        "college_name": pending_result.get("学院名称：") or "无",
                        "major_name": pending_result.get("专业名称：") or "无",
                        "class_name": pending_result.get("班级名称：") or "无",
                    }
                )
            else:
                _url = urljoin(
                    self.base_url,
                    "xszbbgl/xszbbgl_cxXszbbsqIndex.html?doType=details&gnmkdm=N106005",
                )
                _req_info = self.sess.post(
                    _url,
                    headers=self.headers,
                    cookies=self.cookies,
                    timeout=self.timeout,
                    data={"offDetails": "1", "gnmkdm": "N106005", "czdmKey": "00"},
                )
                _doc = pq(_req_info.text)
                if _doc("p.error_title").text() != "无功能权限，":
                    for ul_item in _doc.find("div.col-sm-6").items():
                        content = pq(ul_item).find("div.form-group")
                        key = pq(content).find("label.col-sm-4.control-label").text() + "："
                        value = pq(content).find("div.col-sm-8 label.control-label").text()
                        if key:
                            pending_result[key] = value
                    result.update(
                        {
                            "college_name": pending_result.get("学院：") or "无",
                            "major_name": pending_result.get("专业：") or "无",
                            "class_name": pending_result.get("班级：") or "无",
                        }
                    )
            return {"code": 1000, "msg": "获取个人信息成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取个人信息超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {
                "code": 2333,
                "msg": "请重试，若多次失败可能是系统错误维护或需更新接口",
            }
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取个人信息时未记录的错误：" + str(e)}
