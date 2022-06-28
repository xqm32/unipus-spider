from itertools import count
import json
import re
from time import sleep

import httpx
from lxml.etree import HTML
from _log import log


class Unipus:
    def __init__(self):
        self.client = httpx.Client()
        with open("config.json", "r") as f:
            self.config = json.load(f)
        self.baseURL = self.config["baseURL"]

    def login(self):
        index = self.client.get(f"{self.baseURL}/index.php", follow_redirects=True)
        # 这里需要更新 Referer 否则无法登录
        self.client.headers.update({"Referer": str(index.url)})
        html = HTML(index.text)

        hidden = html.xpath('//input[@type="hidden"]')
        data = {i.get("name"): i.get("value") for i in hidden}
        data.update(self.config)

        self.client.post(f"{self.baseURL}/index.php", data=data)
        # 验证登录是否成功
        hpindex_student = self.client.get(f"{self.baseURL}/login/hpindex_student.php")
        if hpindex_student.text.find(self.config["username"]) != -1:
            log.info("登陆成功")

    def book(self, bookID, classID):
        # 需要进入书籍才能进行学习
        self.client.get(
            f"{self.baseURL}/book/index.php",
            params={"BookID": bookID, "ClassID": classID, "Quiz": "N"},
        )

    def initPage(self, unitID, sectionID, sisterID):
        data = {
            "UnitID": unitID,
            "SectionID": sectionID,
            "SisterID": sisterID,
        }

        initPagePHP = self.client.post(
            f"{self.baseURL}/book/book184/initPage.php", data=data
        )
        key = json.loads(initPagePHP.text)
        # log.info(key)
        return key

    def answer(self, unitID, sectionID, sisterID):
        key = self.initPage(unitID, sectionID, sisterID)
        if not key["ItemID"]:
            log.info("题目不存在")
            return False
        elif not key["key"]:
            log.info("无需作答")
            return True

        answer = key["key"].split("^")
        answer = list(i.split("|")[0] if "|" in i else i for i in answer)

        data = {
            "ItemID": key["ItemID"],
            "answer[]": answer[0:4],
        }
        # log.info(data)

        post = self.client.post(
            "http://172.31.241.173/book/book184/postDrag.php", data=data
        )
        # log.info(post.text)

        data = {
            "UnitID": unitID,
            "SectionID": sectionID,
            "SisterID": sisterID,
        }
        done = self.client.post(
            "http://172.31.241.173/book/book184/done.php", data=data
        )
        log.info("".join(re.findall(r"Your score: (.*)%", done.text)))
        return True
    
    # def get


unipus = Unipus()
unipus.login()
unipus.book(184, 791)
unipus.answer(7,3,6)
# unipus.answer(7,5,5)

# for i in range(1, 9):
#     for j in count(1):
#         log.info(f"{i}-{j}-{1}")
#         if not unipus.answer(i, j, 1):
#             break
#         for k in count(1):
#             log.info(f"{i}-{j}-{k}")
#             if not unipus.answer(i, j, k):
#                 break
#             sleep(1)

# for i in range(1, 9):
#     for j in range(3,4):
#         log.info(f"{i}-{j}-{1}")
#         if not unipus.answer(i, j, 1):
#             break
#         for k in count(6):
#             log.info(f"{i}-{j}-{k}")
#             if not unipus.answer(i, j, k):
#                 break
#             sleep(1)