import json
import re
import time
import traceback
from urllib.parse import urljoin
from pyquery import PyQuery as pq
from requests import exceptions


class ScheduleMixin:
    """Schedule related APIs."""

    def get_exam_schedule(self, year: int, term: int = 0):
        """获取考试信息"""
        url = urljoin(
            self.base_url,
            "kwgl/kscx_cxXsksxxIndex.html?doType=query&gnmkdm=N358105",
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
                        "course_id": i.get("kch"),
                        "title": i.get("kcmc"),
                        "time": i.get("kssj"),
                        "location": i.get("cdmc"),
                        "xq": i.get("cdxqmc"),
                        "zwh": i.get("zwh"),
                        "cxbj": i.get("cxbj", ""),
                        "exam_name": i.get("ksmc"),
                        "teacher": i.get("jsxx"),
                        "class_name": i.get("jxbmc"),
                        "kkxy": i.get("kkxy"),
                        "credit": self.align_floats(i.get("xf")),
                        "ksfs": i.get("ksfs"),
                        "sjbh": i.get("sjbh"),
                        "bz": i.get("bz1", ""),
                    }
                    for i in grade_items
                ],
            }
            return {"code": 1000, "msg": "获取考试信息成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取考试信息超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取考试信息时未记录的错误：" + str(e)}

    def get_schedule(self, year: int, term: int):
        """获取课程表信息"""
        url = urljoin(self.base_url, "kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151")
        temp_term = term
        term = term**2 * 3
        data = {"xnm": str(year), "xqm": str(term)}
        try:
            req_schedule = self.sess.post(
                url,
                headers=self.headers,
                data=data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_schedule.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_schedule.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            schedule = req_schedule.json()
            if not schedule.get("kbList"):
                return {"code": 1005, "msg": "获取内容为空"}
            result = {
                "sid": schedule["xsxx"].get("XH"),
                "name": schedule["xsxx"].get("XM"),
                "year": year,
                "term": temp_term,
                "count": len(schedule["kbList"]),
                "courses": [
                    {
                        "course_id": i.get("kch_id"),
                        "title": i.get("kcmc"),
                        "teacher": i.get("xm"),
                        "class_name": i.get("jxbmc"),
                        "credit": self.align_floats(i.get("xf")),
                        "weekday": self.parse_int(i.get("xqj")),
                        "time": self.display_course_time(i.get("jc")),
                        "sessions": i.get("jc"),
                        "list_sessions": self.list_sessions(i.get("jc")),
                        "weeks": i.get("zcd"),
                        "list_weeks": self.list_weeks(i.get("zcd")),
                        "evaluation_mode": i.get("khfsmc"),
                        "campus": i.get("xqmc"),
                        "place": i.get("cdmc"),
                        "hours_composition": i.get("kcxszc"),
                        "weekly_hours": self.parse_int(i.get("zhxs")),
                        "total_hours": self.parse_int(i.get("zxs")),
                    }
                    for i in schedule["kbList"]
                ],
                "extra_courses": [i.get("qtkcgs") for i in schedule.get("sjkList")],
            }
            result = self.split_merge_display(result)
            return {"code": 1000, "msg": "获取课表成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取课表超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取课表时未记录的错误：" + str(e)}

    def get_schedule_pdf(self, year: int, term: int, name: str = "导出"):
        """获取课表pdf"""
        url_policy = urljoin(self.base_url, "kbdy/bjkbdy_cxXnxqsfkz.html")
        url_file = urljoin(self.base_url, "kbcx/xskbcx_cxXsShcPdf.html")
        origin_term = term
        term = term**2 * 3
        data = {
            "xm": name,
            "xnm": str(year),
            "xqm": str(term),
            "xnmc": f"{year}-{year + 1}",
            "xqmmc": str(origin_term),
            "jgmc": "undefined",
            "xxdm": "",
            "xszd.sj": "true",
            "xszd.cd": "true",
            "xszd.js": "true",
            "xszd.jszc": "false",
            "xszd.jxb": "true",
            "xszd.xkbz": "true",
            "xszd.kcxszc": "true",
            "xszd.zhxs": "true",
            "xszd.zxs": "true",
            "xszd.khfs": "true",
            "xszd.xf": "true",
            "xszd.skfsmc": "false",
            "kzlx": "dy",
        }
        try:
            pilicy_params = {"gnmkdm": "N2151"}
            req_policy = self.sess.post(
                url_policy,
                headers=self.headers,
                data=data,
                params=pilicy_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_policy.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_policy.text)
            if doc("h5").text() == "用户登录":
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            file_params = {"doType": "table"}
            req_file = self.sess.post(
                url_file,
                headers=self.headers,
                data=data,
                params=file_params,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            doc = pq(req_file.text)
            if "错误" in doc("title").text():
                error = doc("p.error_title").text()
                return {"code": 998, "msg": error}
            result = req_file.content
            return {"code": 1000, "msg": "获取课程表pdf成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取课程表pdf超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取课程表pdf时未记录的错误：" + str(e)}

    @classmethod
    def display_course_time(cls, sessions):
        if not sessions:
            return None
        args = re.findall(r"(\d+)", sessions)
        start_time = cls.raspisanie[int(args[0]) + 1][0]
        end_time = cls.raspisanie[int(args[0]) + 1][1]
        return f"{start_time}~{end_time}"

    @classmethod
    def list_sessions(cls, sessions):
        if not sessions:
            return None
        args = re.findall(r"(\d+)", sessions)
        return [n for n in range(int(args[0]), int(args[1]) + 1)]

    @classmethod
    def list_weeks(cls, weeks):
        """返回课程所含周列表"""
        if not weeks:
            return None
        args = re.findall(r"[^,]+", weeks)
        week_list = []
        for item in args:
            if "-" in item:
                weeks_pair = re.findall(r"(\d+)", item)
                if len(weeks_pair) != 2:
                    continue
                if "单" in item:
                    for i in range(int(weeks_pair[0]), int(weeks_pair[1]) + 1):
                        if i % 2 == 1:
                            week_list.append(i)
                elif "双" in item:
                    for i in range(int(weeks_pair[0]), int(weeks_pair[1]) + 1):
                        if i % 2 == 0:
                            week_list.append(i)
                else:
                    for i in range(int(weeks_pair[0]), int(weeks_pair[1]) + 1):
                        week_list.append(i)
            else:
                week_num = re.findall(r"(\d+)", item)
                if len(week_num) == 1:
                    week_list.append(int(week_num[0]))
        return week_list

    @classmethod
    def get_display_term(cls, sid, year, term):
        if (sid and year and term) is None:
            return None
        grade = int(sid[0:2])
        year = int(year[2:4])
        term = int(term)
        mapping = {
            grade: "大一上" if term == 1 else "大一下",
            grade + 1: "大二上" if term == 1 else "大二下",
            grade + 2: "大三上" if term == 1 else "大三下",
            grade + 3: "大四上" if term == 1 else "大四下",
        }
        return mapping.get(year)

    @classmethod
    def split_merge_display(cls, schedule):
        repetIndex = []
        count = 0
        for items in schedule["courses"]:
            for index in range(len(schedule["courses"])):
                if (schedule["courses"]).index(items) == count:
                    continue
                elif (
                    items["course_id"] == schedule["courses"][index]["course_id"]
                    and items["weekday"] == schedule["courses"][index]["weekday"]
                    and items["weeks"] == schedule["courses"][index]["weeks"]
                ):
                    repetIndex.append(index)
            count += 1
        if len(repetIndex) % 2 != 0:
            return schedule
        for r in range(0, len(repetIndex), 2):
            fir = repetIndex[r]
            sec = repetIndex[r + 1]
            if len(re.findall(r"(\d+)", schedule["courses"][fir]["sessions"])) == 4:
                schedule["courses"][fir]["sessions"] = (
                    re.findall(r"(\d+)", schedule["courses"][fir]["sessions"])[0]
                    + "-"
                    + re.findall(r"(\d+)", schedule["courses"][fir]["sessions"])[1]
                    + "节"
                )
                schedule["courses"][fir]["list_sessions"] = cls.list_sessions(
                    schedule["courses"][fir]["sessions"]
                )
                schedule["courses"][fir]["time"] = cls.display_course_time(
                    schedule["courses"][fir]["sessions"]
                )
                schedule["courses"][sec]["sessions"] = (
                    re.findall(r"(\d+)", schedule["courses"][sec]["sessions"])[2]
                    + "-"
                    + re.findall(r"(\d+)", schedule["courses"][sec]["sessions"])[3]
                    + "节"
                )
                schedule["courses"][sec]["list_sessions"] = cls.list_sessions(
                    schedule["courses"][sec]["sessions"]
                )
                schedule["courses"][sec]["time"] = cls.display_course_time(
                    schedule["courses"][sec]["sessions"]
                )
        return schedule
