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


class NotificationMixin(ClientProtocol):
    """Notification related APIs."""

    def get_notifications(self) -> dict[str, Any]:
        """获取通知消息"""
        url = urljoin(self.base_url, "xtgl/index_cxDbsy.html?doType=query")
        data = {
            "sfyy": "0",
            "flag": "1",
            "_search": "false",
            "nd": int(time.time() * 1000),
            "queryModel.showCount": "1000",
            "queryModel.currentPage": "1",
            "queryModel.sortName": "cjsj",
            "queryModel.sortOrder": "desc",
            "time": "0",
        }
        try:
            req_notification = self.sess.post(
                url,
                headers=self.headers,
                data=data,
                cookies=self.cookies,
                timeout=self.timeout,
            )
            if req_notification.status_code != 200:
                return {"code": 2333, "msg": "教务系统挂了"}
            doc = pq(req_notification.text)
            if doc("h5").text() == "用户登录" or "错误" in doc("title").text():
                return {"code": 1006, "msg": "未登录或已过期，请重新登录"}
            notifications = req_notification.json()
            result = [
                {**self.split_notifications(i), "create_time": i.get("cjsj")}
                for i in notifications.get("items")
            ]
            return {"code": 1000, "msg": "获取消息成功", "data": result}
        except exceptions.Timeout:
            return {"code": 1003, "msg": "获取消息超时"}
        except (
            exceptions.RequestException,
            json.decoder.JSONDecodeError,
            AttributeError,
        ):
            traceback.print_exc()
            return {"code": 2333, "msg": "请重试，若多次失败可能是系统错误维护或需更新接口"}
        except Exception as e:
            traceback.print_exc()
            return {"code": 999, "msg": "获取消息时未记录的错误：" + str(e)}

    @classmethod
    def split_notifications(cls, item: dict[str, Any]) -> dict[str, Any]:
        if not item.get("xxnr"):
            return {"type": None, "content": None}
        content_list = re.findall(r"(.*):(.*)", item["xxnr"])
        if len(content_list) == 0:
            return {"type": None, "content": item["xxnr"]}
        return {"type": content_list[0][0], "content": content_list[0][1]}
