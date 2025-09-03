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


class CourseMixin(ClientProtocol):
    """Course selection related APIs."""

    def get_selected_courses(self, year: int, term: int) -> dict[str, Any]:
        """获取已选课程信息"""
        try:
            url = urljoin(
                self.base_url,
                "xsxk/zzxkyzb_cxZzxkYzbChoosedDisplay.html?gnmkdm=N253512",
            )
            temp_term = term
            term = term**2 * 3
            data = {"xkxnm": str(year), "xkxqm": str(term)}
            req_selected = self.sess.post(
                url,
                data=data,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_selected.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_selected.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            selected = req_selected.json()
            result = {
                "year": year,
                "term": temp_term,
                "count": len(selected),
                "courses": [
                    {
                        "course_id": i.get("kch"),
                        "class_id": i.get("jxb_id"),
                        "do_id": i.get("do_jxb_id"),
                        "title": i.get("kcmc"),
                        "teacher_id": (re.findall(r"(.*?\d+)/", i.get("jsxx")))[0],
                        "teacher": (re.findall(r"/(.*?)/", i.get("jsxx")))[0],
                        "credit": float(i.get("xf", 0)),
                        "category": i.get("kklxmc"),
                        "capacity": int(i.get("jxbrs", 0)),
                        "selected_number": int(i.get("yxzrs", 0)),
                        "place": self.get_place(i.get("jxdd")),
                        "time": self.get_course_time(i.get("sksj")),
                        "optional": int(i.get("zixf", 0)),
                        "waiting": i.get("sxbj"),
                    }
                    for i in selected
                ],
            }
            return {"code": 1000, "msg": "获取已选课程成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取已选课程超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": f"获取已选课程时未记录的错误：{str(e)}"}

    def get_selected_courses2(self, year: int = 0, term: int = 0) -> dict[str, Any]:
        """获取已选课程信息2"""
        try:
            url = urljoin(
                self.base_url,
                "/xsxxxggl/xsxxwh_cxXsxkxx.html?gnmkdm=N100801",
            )
            if year == 0 or term == 0:
                year_str = ""
                term_str = ""
                temp_term = 0
            else:
                temp_term = term
                term_param = term**2 * 3
                year_str = str(year)
                term_str = str(term_param)
            data = {
                "xnm": year_str,
                "xqm": term_str,
                "_search": "false",
                "queryModel.showCount": 5000,
                "queryModel.currentPage": 1,
                "queryModel.sortName": "",
                "queryModel.sortOrder": "asc",
                "time": 1,
            }
            req_selected = self.sess.post(
                url,
                data=data,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_selected.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_selected.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            selected = req_selected.json()
            result = {
                "year": year,
                "term": temp_term,
                "count": len(selected["items"]),
                "courses": [
                    {
                        "course_id": i.get("kch"),
                        "class_id": i.get("jxb_id"),
                        "title": i.get("kcmc"),
                        "credit": float(i.get("xf", 0)),
                        "teacher": i.get("jsxm"),
                        "category": i.get("kclbmc"),
                        "place": i.get("jxdd"),
                    }
                    for i in selected["items"]
                ],
            }
            return {"code": 1000, "msg": "获取已选课程2成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取已选课程2超时"}
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
            return {"code": 999, "msg": f"获取已选课程2时未记录的错误：{str(e)}"}

    def get_block_courses(self, year: int, term: int, block: int) -> dict[str, Any]:
        """获取板块课选课列表"""
        try:
            url_head = urljoin(
                self.base_url,
                "xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default",
            )
            req_head_data = self.sess.get(
                url_head,
                headers=self.headers,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_head_data.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_head_data.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            if str(doc("div.nodata")) != "":
                return {"code": 998, "msg": doc("div.nodata").text()}
            got_credit_list = [i for i in doc("font[color='red']").items()]
            if len(got_credit_list) == 0:
                return {"code": 1005, "msg": "板块课内容为空"}
            head_data = {"got_credit": got_credit_list[2].text()}
            kklxdm_list = []
            xkkz_id_list = []
            for tab_content in doc("a[role='tab']").items():
                onclick_content = tab_content.attr("onclick")
                r = re.findall(r"'(.*?)'", str(onclick_content))
                kklxdm_list.append(r[0].strip())
                xkkz_id_list.append(r[1].strip())
            head_data["bkk1_kklxdm"] = kklxdm_list[0]
            head_data["bkk2_kklxdm"] = kklxdm_list[1]
            head_data["bkk3_kklxdm"] = kklxdm_list[2]
            head_data["bkk1_xkkz_id"] = xkkz_id_list[0]
            head_data["bkk2_xkkz_id"] = xkkz_id_list[1]
            head_data["bkk3_xkkz_id"] = xkkz_id_list[2]
            for head_data_content in doc("input[type='hidden']"):
                name = head_data_content.attr("name")
                value = head_data_content.attr("value")
                head_data[str(name)] = str(value)
            url_display = urljoin(
                self.base_url, "xsxk/zzxkyzb_cxZzxkYzbDisplay.html?gnmkdm=N253512"
            )
            display_req_data = {
                "xkkz_id": head_data[f"bkk{block}_xkkz_id"],
                "xszxzt": "1",
                "kspage": "0",
            }
            req_display_data = self.sess.post(
                url_display,
                headers=self.headers,
                data=display_req_data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            doc_display = pq(req_display_data.text)
            display_data = {}
            for display_data_content in doc_display("input[type='hidden']").items():
                name = display_data_content.attr("name")
                value = display_data_content.attr("value")
                display_data[str(name)] = str(value)
            head_data.update(display_data)
            url_kch = urljoin(
                self.base_url, "xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512"
            )
            url_bkk = urljoin(
                self.base_url, "xsxk/zzxkyzb_cxJxbWithKchZzxkYzb.html?gnmkdm=N253512"
            )
            term = term**2 * 3
            kch_data = {
                "bklx_id": head_data["bklx_id"],
                "xqh_id": head_data["xqh_id"],
                "zyfx_id": head_data["zyfx_id"],
                "njdm_id": head_data["njdm_id"],
                "bh_id": head_data["bh_id"],
                "xbm": head_data["xbm"],
                "xslbdm": head_data["xslbdm"],
                "ccdm": head_data["ccdm"],
                "xsbj": head_data["xsbj"],
                "xkxnm": str(year),
                "xkxqm": str(term),
                "kklxdm": head_data[f"bkk{block}_kklxdm"],
                "kkbk": head_data["kkbk"],
                "rwlx": head_data["rwlx"],
                "kspage": "1",
                "jspage": "10",
            }
            kch_res = self.sess.post(
                url_kch,
                headers=self.headers,
                data=kch_data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            jkch_res = kch_res.json()
            bkk_data = {
                "bklx_id": head_data["bklx_id"],
                "xkxnm": str(year),
                "xkxqm": str(term),
                "xkkz_id": head_data[f"bkk{block}_xkkz_id"],
                "xqh_id": head_data["xqh_id"],
                "zyfx_id": head_data["zyfx_id"],
                "njdm_id": head_data["njdm_id"],
                "bh_id": head_data["bh_id"],
                "xbm": head_data["xbm"],
                "xslbdm": head_data["xslbdm"],
                "ccdm": head_data["ccdm"],
                "xsbj": head_data["xsbj"],
                "kklxdm": head_data[f"bkk{block}_kklxdm"],
                "kch_id": jkch_res["tmpList"][0]["kch_id"],
                "kkbk": head_data["kkbk"],
                "rwlx": head_data["rwlx"],
                "zyh_id": head_data["zyh_id"],
            }
            bkk_res = self.sess.post(
                url_bkk,
                headers=self.headers,
                data=bkk_data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            jbkk_res = bkk_res.json()
            if block != 3 and (len(jkch_res["tmpList"]) != len(jbkk_res)):
                return {"code": 999, "msg": "板块课编号及长度错误"}
            temp_list = jkch_res["tmpList"]
            block_list = jbkk_res
            for i in range(len(temp_list)):
                temp_list[i].update(block_list[i])
            result = {
                "count": len(temp_list),
                "courses": [
                    {
                        "course_id": j["kch_id"],
                        "class_id": j.get("jxb_id"),
                        "do_id": j.get("do_jxb_id"),
                        "title": j.get("kcmc"),
                        "teacher_id": (re.findall(r"(.*?\d+)/", j.get("jsxx")))[0],
                        "teacher": (re.findall(r"/(.*?)/", j.get("jsxx")))[0],
                        "credit": float(j.get("xf") or 0),
                        "kklxdm": head_data[f"bkk{block}_kklxdm"],
                        "capacity": int(j.get("jxbrl", 0)),
                        "selected_number": int(j.get("yxzrs", 0)),
                        "place": self.get_place(j.get("jxdd")),
                        "time": self.get_course_time(j.get("sksj")),
                    }
                    for j in temp_list
                ],
            }
            return {"code": 1000, "msg": "获取板块课信息成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取板块课信息超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": f"获取板块课信息时未记录的错误：{str(e)}"}

    def select_course(
        self,
        sid: str,
        course_id: str,
        do_id: str,
        kklxdm: str,
        year: int,
        term: int,
    ) -> dict[str, Any]:
        """选课"""
        try:
            url_select = urljoin(
                self.base_url, "xsxk/zzxkyzb_xkBcZyZzxkYzb.html?gnmkdm=N253512"
            )
            term = term**2 * 3
            select_data = {
                "jxb_ids": do_id,
                "kch_id": course_id,
                "qz": "0",
                "xkxnm": str(year),
                "xkxqm": str(term),
                "njdm_id": str(sid[0:2]),
                "zyh_id": str(sid[2:6]),
                "kklxdm": str(kklxdm),
            }
            req_select = self.sess.post(
                url_select,
                headers=self.headers,
                data=select_data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_select.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_select.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            result = req_select.json()
            return {"code": 1000, "msg": "选课成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "选课超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": f"选课时未记录的错误：{str(e)}"}

    def cancel_course(self, do_id: str, course_id: str, year: int, term: int) -> dict[str, Any]:
        """取消选课"""
        try:
            url_cancel = urljoin(
                self.base_url, "xsxk/zzxkyzb_tuikBcZzxkYzb.html?gnmkdm=N253512"
            )
            term = term**2 * 3
            cancel_data = {
                "jxb_ids": do_id,
                "kch_id": course_id,
                "xkxnm": str(year),
                "xkxqm": str(term),
            }
            req_cancel = self.sess.post(
                url_cancel,
                headers=self.headers,
                data=cancel_data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_cancel.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_cancel.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            result = {"status": re.findall(r"(\d+)", req_cancel.text)[0]}
            return {"code": 1000, "msg": "退课成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "选课超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": f"选课时未记录的错误：{str(e)}"}

    def get_course_category(self, type: str, item: dict[str, Any]) -> str | None:
        """根据课程号获取类别"""
        if type not in self.detail_category_type:
            return item.get("KCLBMC")
        if not item.get("KCH"):
            return None
        url = urljoin(self.base_url, f"jxjhgl/common_cxKcJbxx.html?id={item['KCH']}")
        req_category = self.sess.get(
            url,
            headers=self.headers,
            cookies=self.cookies,
            timeout=self.timeout,
        )
        doc = pq(req_category.text)
        ths = doc("th")
        try:
            data_list = [(th.text).strip() for th in ths]
            return data_list[6]
        except Exception:
            return None
