from __future__ import annotations

import json
import re
import time
import traceback
from typing import Any
from urllib.parse import urljoin

from pyquery import PyQuery as pq
from requests import exceptions

from ..protocols import ClientProtocol


class AcademiaMixin(ClientProtocol):
    """Academia related APIs."""

    def get_academia(self) -> dict[str, Any]:
        """获取学业生涯情况"""
        url_main = urljoin(
            self.base_url,
            "xsxy/xsxyqk_cxXsxyqkIndex.html?gnmkdm=N105515&layout=default",
        )
        url_info = urljoin(
            self.base_url, "xsxy/xsxyqk_cxJxzxjhxfyqKcxx.html?gnmkdm=N105515"
        )
        try:
            req_main = self.sess.get(
                url_main,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
                stream=True,
            )
            if req_main.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc_main = pq(req_main.text)
            if doc_main("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            if str(doc_main("div.alert-danger")) != "":
                return {"code": 998, "msg": doc_main("div.alert-danger").text()}
            sid_attr = doc_main("input#xh_id").attr("value")
            sid = str(sid_attr or "")
            display_statistics = (
                str(doc_main("div#alertBox").text()).replace(" ", "").replace("\n", "")
            )
            statistics = self.get_academia_statistics(display_statistics)
            type_statistics = self.get_academia_type_statistics(req_main.text)
            details = {}
            for type in type_statistics.keys():
                details[type] = self.sess.post(
                    url_info,
                    headers=self.headers,
                    data={"xfyqjd_id": type_statistics[type]["id"]},
                    cookies=self.cookies,
                    timeout=self.timeout,
                    stream=True,
                ).json()
            result = {
                "sid": sid,
                "statistics": statistics,
                "details": [
                    {
                        "type": type,
                        "credits": type_statistics[type]["credits"],
                        "courses": [
                            {
                                "course_id": i.get("KCH"),
                                "title": i.get("KCMC"),
                                "situation": self.parse_int(i.get("XDZT")),
                                "display_term": self.get_display_term(
                                    sid, i.get("JYXDXNM"), i.get("JYXDXQMC")
                                ),
                                "credit": self.align_floats(i.get("XF")),
                                "category": self.get_course_category(type, i),
                                "nature": i.get("KCXZMC"),
                                "max_grade": self.parse_int(i.get("MAXCJ")),
                                "grade_point": self.align_floats(i.get("JD")),
                            }
                            for i in details[type]
                        ],
                    }
                    for type in type_statistics.keys()
                    if len(details[type]) > 0
                ],
            }
            return {"code": 1000, "msg": "获取学业情况成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取学业情况超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取学业情况时未记录的错误：" + str(e)}

    def get_academia_pdf(self) -> dict[str, Any]:
        """获取学业生涯（学生成绩总表）pdf"""
        url_view = urljoin(self.base_url, "bysxxcx/xscjzbdy_dyXscjzbView.html")
        url_window = urljoin(self.base_url, "bysxxcx/xscjzbdy_dyCjdyszxView.html")
        url_policy = urljoin(self.base_url, "xtgl/bysxxcx/xscjzbdy_cxXsCount.html")
        url_filetype = urljoin(self.base_url, "bysxxcx/xscjzbdy_cxGswjlx.html")
        url_common = urljoin(self.base_url, "common/common_cxJwxtxx.html")
        url_file = urljoin(self.base_url, "bysxxcx/xscjzbdy_dyList.html")
        url_progress = urljoin(self.base_url, "xtgl/progress_cxProgressStatus.html")
        data = {
            "gsdygx": "10628-zw-mrgs",
            "ids": "",
            "bdykcxzDms": "",
            "cytjkcxzDms": "",
            "cytjkclbDms": "",
            "cytjkcgsDms": "",
            "bjgbdykcxzDms": "",
            "bjgbdyxxkcxzDms": "",
            "djksxmDms": "",
            "cjbzmcDms": "",
            "cjdySzxs": "",
            "wjlx": "pdf",
        }
        try:
            data_view = {"time": str(round(time.time() * 1000)), "gnmkdm": "N558020"}
            data_params = data_view
            del data_params["time"]
            req_view = self.sess.post(
                url_view,
                headers=self.headers,
                data=data_view,
                params=data_view,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_view.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_view.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            data_window = {"xh": ""}
            self.sess.post(
                url_window,
                headers=self.headers,
                data=data_window,
                params=data_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            data_policy = data
            del data_policy["wjlx"]
            self.sess.post(
                url_policy,
                headers=self.headers,
                data=data_policy,
                params=data_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            data_filetype = data_policy
            self.sess.post(
                url_filetype,
                headers=self.headers,
                data=data_filetype,
                params=data_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            self.sess.post(
                url_common,
                headers=self.headers,
                data=data_params,
                params=data_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            req_file = self.sess.post(
                url_file,
                headers=self.headers,
                data=data,
                params=data_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            doc = pq(req_file.text)
            if "错误" in doc("title").text():
                error = doc("p.error_title").text()
                return {"code": 998, "msg": error}
            data_progress = {"key": "score_print_processed", "gnmkdm": "N558020"}
            self.sess.post(
                url_progress,
                headers=self.headers,
                data=data_progress,
                params=data_progress,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            pdf = (
                req_file.text.replace("#成功", "")
                .replace('"', "")
                .replace("/", "\\")
                .replace("\\\\", "/")
            )
            req_pdf = self.sess.get(
                urljoin(self.base_url, pdf),
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout + 2,
            )
            result = req_pdf.content
            return {"code": 1000, "msg": "获取学生成绩总表pdf成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取成绩总表pdf超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取成绩总表pdf时未记录的错误：" + str(e)}

    @classmethod
    def get_academia_statistics(cls, display_statistics: str) -> dict:
        display_statistics = "".join(display_statistics.split())
        gpa_list = re.findall(r"([0-9]{1,}[.][0-9]*)", display_statistics)
        if len(gpa_list) == 0 or not cls.is_number(gpa_list[0]):
            gpa = None
        else:
            gpa = float(gpa_list[0])
        plan_list = re.findall(
            r"计划总课程(\d+)门通过(\d+)门?.*未通过(\d+)门?.*未修(\d+)?.*在读(\d+)门?.*计划外?.*通过(\d+)门?.*未通过(\d+)门",
            display_statistics,
        )
        if len(plan_list) == 0 or len(plan_list[0]) < 7:
            return {"gpa": gpa}
        plan_list = plan_list[0]
        return {
            "gpa": gpa,
            "planed_courses": {
                "total": int(plan_list[0]),
                "passed": int(plan_list[1]),
                "failed": int(plan_list[2]),
                "missed": int(plan_list[3]),
                "in": int(plan_list[4]),
            },
            "unplaned_courses": {
                "passed": int(plan_list[5]),
                "failed": int(plan_list[6]),
            },
        }

    @classmethod
    def get_academia_type_statistics(cls, content: str) -> dict[str, dict[str, Any]]:
        finder = re.findall(
            r"\"(.*)&nbsp.*要求学分.*:([0-9]{1,}[.][0-9]*|0|&nbsp;).*获得学分.*:([0-9]{1,}[.][0-9]*|0|&nbsp;).*未获得学分.*:([0-9]{1,}[.][0-9]*|0|&nbsp;)[\s\S]*?<span id='showKc(.*)'></span>",
            content,
        )
        finder_list = list({}.fromkeys(finder).keys())
        academia_list = [
            list(i)
            for i in finder_list
            if i[0] != ""
            and len(i[0]) <= 20
            and "span" not in i[-1]
            and i[0] not in cls.ignore_type
        ]
        result = {
            i[0]: {
                "id": i[-1],
                "credits": {
                    "required": i[1] if cls.is_number(i[1]) and i[1] != "0" else None,
                    "earned": i[2] if cls.is_number(i[2]) and i[2] != "0" else None,
                    "missed": i[3] if cls.is_number(i[3]) and i[3] != "0" else None,
                },
            }
            for i in academia_list
        }
        return result
