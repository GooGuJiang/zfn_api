from __future__ import annotations

import json
import time
import traceback
from typing import Any
from urllib.parse import urljoin

from pyquery import PyQuery as pq
from requests import exceptions

from ..protocols import ClientProtocol


class GradeMixin(ClientProtocol):
    """Grade related APIs."""

    def get_grade(
        self, year: int, term: int = 0, use_personal_info: bool = False
    ) -> dict[str, Any]:
        """获取成绩"""
        url = urljoin(
            self.base_url,
            "cjcx/cjcx_cxDgXscj.html?doType=query&gnmkdm=N305005"
            if use_personal_info
            else "cjcx/cjcx_cxXsgrcj.html?doType=query&gnmkdm=N305005",
        )
        temp_term = term
        term_param = term**2 * 3
        term_str = "" if term_param == 0 else str(term_param)
        data = {
            "xnm": str(year),
            "xqm": term_str,
            "_search": "false",
            "nd": int(time.time() * 1000),
            "queryModel.showCount": "100",
            "queryModel.currentPage": "1",
            "queryModel.sortName": "",
            "queryModel.sortOrder": "asc",
            "time": "0",
        }
        try:
            req_grade = self.sess.post(
                url,
                headers=self.headers,
                data=data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_grade.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_grade.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            grade = req_grade.json()
            grade_items = grade.get("items")
            if not grade_items:
                return {"code": 1005, "msg": "获取内容为空"}
            result = {
                "sid": grade_items[0]["xh"],
                "name": grade_items[0]["xm"],
                "year": year,
                "term": temp_term,
                "count": len(grade_items),
                "courses": [
                    {
                        "course_id": i.get("kch_id"),
                        "title": i.get("kcmc"),
                        "teacher": i.get("jsxm"),
                        "class_name": i.get("jxbmc"),
                        "credit": self.align_floats(i.get("xf")),
                        "category": i.get("kclbmc"),
                        "nature": i.get("kcxzmc"),
                        "grade": self.parse_int(i.get("cj")),
                        "grade_point": self.align_floats(i.get("jd")),
                        "grade_nature": i.get("ksxz"),
                        "start_college": i.get("kkbmmc"),
                        "mark": i.get("kcbj"),
                    }
                    for i in grade_items
                ],
            }
            return {"code": 1000, "msg": "获取成绩成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取成绩超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取成绩时未记录的错误：" + str(e)}

    def get_gpa(self) -> float | str | dict[str, Any]:
        """获取GPA"""
        url = urljoin(
            self.base_url,
            "xsxy/xsxyqk_cxXsxyqkIndex.html?gnmkdm=N105515&layout=default",
        )
        req_gpa = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
        )
        doc = pq(req_gpa.text)
        if doc("h5").text() == "用户登录":
            return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
        allc_str = [allc.text() for allc in doc("font[size='2px']").items()]
        try:
            gpa_text = str(allc_str[2]) if len(allc_str) > 2 else ""
            gpa = float(gpa_text)
            return gpa
        except Exception:
            return "init"
