import unittest
import os
import shutil
import re
import HTMLTestRunner
import requests

from bs4 import BeautifulSoup


class TestCustomBlog(unittest.TestCase):
    def setUp(self):
        try:
            os.remove("C:\\MyWork\\myGitHub\\custom-blog\\app.db.bk")
        except:
            pass;
        shutil.copy("C:\\MyWork\\myGitHub\\custom-blog\\app.db","C:\\MyWork\\myGitHub\\custom-blog\\app.db.bk")

    def tearDown(self):
        shutil.copy("C:\\MyWork\\myGitHub\\custom-blog\\app.db.bk", "C:\\MyWork\\myGitHub\\custom-blog\\app.db")

    def testRegistShouldSuccessGivenNormalInput(self):#注册界面，邮箱合法，两次密码相同，预期结果为注册成功
        result = self.getResultByUserPasswd("test2@163.com", "111111")
        self.assertEqual(200, result.status_code, "status_code should be 200",f'期望返回code=200，实际返回{result.status_code}')
        soup = BeautifulSoup(result.text, "html.parser")
        returnStr = soup.find_all("li")[0].get_text()
        self.assertRegex(returnStr, "Registered successfully")

    def testRegistShouldFailGivenDuplicateUserAgain(self):#注册界面，邮箱合法，两次密码相同，但邮箱已经注册过了，预期结果为注册失败
        result = self.getResultByUserPasswd("test@163.com", "111111")
        self.assertEqual(200, result.status_code, "status_code should be 200",f'期望返回code=200，实际返回{result.status_code}')
        soup = BeautifulSoup(result.text, "html.parser")
        returnStr = soup.find_all("li")[0].get_text()
        self.assertRegex(returnStr, "Such user already is avalable")

    def testRegistShouldFailGivenDifferentPassword(self):#注册界面，邮箱合法，但两次密码不同，预期结果为注册失败
        result = self.getResultByUserPasswd("test@163.com", "111111", "222222")
        self.assertEqual(200, result.status_code, "status_code should be 200",f'期望返回code=200，实际返回{result.status_code}')
        soup = BeautifulSoup(result.text, "html.parser")
        returnStr = soup.find_all("span", attrs={"class": "error"})[0].get_text()
        self.assertRegex(returnStr, "Passwords must match")

    def testLoginShouldSuccessGivenNormalUserAndPassword(self):#登录界面，邮箱合法，密码正确，预期结果为注册成功
        result = self.getLoginResultByUserPasswd("a_kui@163.com", "111111")
        self.assertEqual(200, result.status_code)
        soup = BeautifulSoup(result.text, "html.parser")
        resultStr = soup.find("li").get_text()
        self.assertRegex(resultStr, "Logged in successfully")

    def testLoginShouldFailedGivenBadPassword(self):#登录界面，邮箱合法，密码错误，预期结果为注册失败
        result = self.getLoginResultByUserPasswd("a_kui@163.com", "222222")
        self.assertEqual(200, result.status_code)
        soup = BeautifulSoup(result.text, "html.parser")
        resultStr = soup.find("li").get_text()
        self.assertRegex(resultStr, "Wrong credentials")

    def testLoginShouldFailedGivenBadUserEmail(self):#登录界面，邮箱不合法，密码错误，预期结果为注册失败
        result = self.getLoginResultByUserPasswd("abcd", "111111")
        self.assertEqual(200, result.status_code)
        soup = BeautifulSoup(result.text, "html.parser")
        resultStr = soup.find("span", attrs={"class": "error"}).get_text()
        self.assertRegex(resultStr, "Invalid email address.")

    def getResultByUserPasswd(self, username, password, cpassword=""):
        if (len(cpassword) == 0):
            cpassword = password
        session = requests.session()
        result = session.get("http://127.0.0.1:5000/register")
        soup = BeautifulSoup(result.text, "html.parser")
        csrf_token = soup.find_all("input", id="csrf_token")[0].attrs["value"]
        data = {"csrf_token": csrf_token, "email": username, "password": password, "cpassword": cpassword}
        result = session.post("http://127.0.0.1:5000/register", data=data)
        return result

    def getLoginResultByUserPasswd(self, username, password):
        session = requests.session()
        result = session.get("http://127.0.0.1:5000/login")
        soup = BeautifulSoup(result.text, "html.parser")
        csrf_token = soup.find_all("input", id="csrf_token")[0].attrs["value"]
        data = {"csrf_token": csrf_token, "email": username, "password": password}
        result = session.post("http://127.0.0.1:5000/login", data=data)
        return result


if __name__ == "__main__":
    test = unittest.TestSuite()
    methodList = unittest.TestLoader().getTestCaseNames(TestCustomBlog())
    for methodname in methodList:
        if (re.match("test", methodname)):
            test.addTest(TestCustomBlog(methodName=methodname))
    file_path = "result.html"
    file_result = open(file_path, 'w', encoding="utf-8")
    runner = HTMLTestRunner.HTMLTestRunner(stream=file_result, title="测试", description="用例执行情况")
    unittest.main(testRunner=runner)
    file_result.close()
