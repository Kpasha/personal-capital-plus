import re
import os
import json
import logging
import getpass
import requests
from os import path

from .exceptions import (
    RequireTwoFactorException,
    LoginFailedException
)

from .constants import (
    BASE_URL,
    API_ENDPOINT
)


class AuthLevelEnum(object):
    USER_REMEMBERED = "USER_REMEMBERED"


class TwoFactorVerificationModeEnum(object):
    SMS = 0
    # PHONE = 1
    EMAIL = 2


class Connector(object):

    # cross-site request forgery token params
    CSRF_KEY = "csrf"
    CSRF_TOKEN_REGEXP = re.compile(r"globals.csrf='([a-f0-9-]+)'")

    AUTH_LEVEL_KEY = "authLevel"
    SUCCESS_KEY = "success"
    SP_HEADER_KEY = "spHeader"
    ERRORS_KEY = "errors"

    def __init__(self):
        self.__session = CookieSession(API_ENDPOINT)

    def login(self, username, password):
        initial_csrf = self.__get_csrf_from_home_page(BASE_URL)
        csrf, auth_level = self.__identify_user(username, initial_csrf)

        if csrf and auth_level:
            self.session.csrf = csrf
            if auth_level != AuthLevelEnum.USER_REMEMBERED:
                raise RequireTwoFactorException()

            result = self.__authenticate_password(password).json()
            if self.__get_header_value(result, Connector.SUCCESS_KEY) is False:
                raise LoginFailedException(self.__get_error_value(result))
        else:
            raise LoginFailedException("Did not acquire CSRF token and auth level.")

    def authenticate_password(self, password):
        return self.__authenticate_password(password)

    def two_factor_authenticate(self, mode, code):
        if mode == TwoFactorVerificationModeEnum.SMS:
            return self.__authenticate_sms(code)
        elif mode == TwoFactorVerificationModeEnum.EMAIL:
            return self.__authenticate_email(code)

    def two_factor_challenge(self, mode):
        if mode == TwoFactorVerificationModeEnum.SMS:
            return self.__challenge_sms()
        elif mode == TwoFactorVerificationModeEnum.EMAIL:
            return self.__challenge_email()

    @property
    def csrf(self):
        return self.session.csrf

    @csrf.setter
    def csrf(self, csrf):
        self.session.csrf = csrf

    @property
    def session(self):
        return self.__session

    @classmethod
    def connect(cls):
        pc = cls()
        user, pw = cls.get_user_credentials()

        try:
            pc.login(user, pw)
        except RequireTwoFactorException:
            pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
            pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('SMS code: '))
            pc.authenticate_password(pw)

        pc.session.csrf = pc.csrf

        return pc.session

    @staticmethod
    def get_user_credentials():
        email = os.getenv('PEW_EMAIL')
        password = os.getenv('PEW_PASSWORD')

        if not email:
            print("You can set the environment variables for PEW_EMAIL and PEW_PASSWORD so "
                  "the prompts don't come up every time")
            return input('Enter email:')

        if not password:
            return getpass.getpass('Enter password:')

        return email, password

    @classmethod
    def __get_header_value(cls, result, valueKey):
        if (cls.SP_HEADER_KEY in result) and (valueKey in result[cls.SP_HEADER_KEY]):
            return result[cls.SP_HEADER_KEY][valueKey]
        return None

    @classmethod
    def __get_error_value(cls, result):
        try:
            return cls.__get_header_value(result, cls.ERRORS_KEY)[0]['message']
        except (ValueError, IndexError):
            return None

    def __get_csrf_from_home_page(self, url):
        r = self.__session.session.get(url)
        found_csrf = Connector.CSRF_TOKEN_REGEXP.search(r.text)

        if found_csrf:
            return found_csrf.group(1)
        return None

    def __identify_user(self, username, csrf):
        """
        Returns reusable CSRF code and the auth level as a 2-tuple
        """
        data = {
            "username": username,
            "csrf": csrf,
            "apiClient": "WEB",
            "bindDevice": "false",
            "skipLinkAccount": "false",
            "redirectTo": "",
            "skipFirstUse": "",
            "referrerId": "",
        }

        r = self.session.post("/login/identifyUser", data)

        if r.status_code == requests.codes.ok:
            result = r.json()
            new_csrf = self.__get_header_value(result, Connector.CSRF_KEY)
            auth_level = self.__get_header_value(result, Connector.AUTH_LEVEL_KEY)
            return (new_csrf, auth_level)

        return (None, None)

    def __generate_challenge_payload(self, challenge_type):
        return {
            "challengeReason": "DEVICE_AUTH",
            "challengeMethod": "OP",
            "challengeType": challenge_type,
            "apiClient": "WEB",
            "bindDevice": "false",
            "csrf": self.csrf
        }

    def __generate_authentication_payload(self, code):
        return {
            "challengeReason": "DEVICE_AUTH",
            "challengeMethod": "OP",
            "apiClient": "WEB",
            "bindDevice": "false",
            "code": code,
            "csrf": self.csrf
        }

    def __challenge_email(self):
        data = self.__generate_challenge_payload("challengeEmail")
        return self.session.post("/credential/challengeEmail", data)

    def __authenticate_email(self, code):
        data = self.__generate_authentication_payload(code)
        return self.session.post("/credential/authenticateEmail", data)

    def __challenge_sms(self):
        data = self.__generate_challenge_payload("challengeSMS")
        return self.session.post("/credential/challengeSms", data)

    def __authenticate_sms(self, code):
        data = self.__generate_authentication_payload(code)
        return self.session.post("/credential/authenticateSms", data)

    def __authenticate_password(self, passwd):
        data = {
            "bindDevice": "true",
            "deviceName": "",
            "redirectTo": "",
            "skipFirstUse": "",
            "skipLinkAccount": "false",
            "referrerId": "",
            "passwd": passwd,
            "apiClient": "WEB",
            "csrf": self.csrf
        }
        return self.session.post("/credential/authenticatePassword", data)


class CookieSession(object):

    SESSION_FN = path.join(path.expanduser("~"), ".personalcapital", "session.json")

    def __init__(self, api_endpoint):
        self.__session = requests.Session()
        self.__session_file = CookieSession.SESSION_FN
        self.__api_endpoint = api_endpoint
        self.__csrf = ""
        self.load()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.save()

    @property
    def api_endpoint(self):
        return self.__api_endpoint

    @api_endpoint.setter
    def api_endpoint(self, new_endpoint):
        self.__api_endpoint = new_endpoint

    @property
    def session(self):
        return self.__session

    @session.setter
    def session(self, new_session):
        raise NotImplementedError("Re-assigning internal session not supported.")

    @property
    def cookies(self):
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    @cookies.setter
    def cookies(self, cookies):
        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)

    @property
    def csrf(self):
        return self.__csrf

    @csrf.setter
    def csrf(self, csrf):
        self.__csrf = csrf

    def fetch(self, endpoint, data=None):
        """
        for getting data after logged in
        """
        payload = {
            "lastServerChangeId": "-1",
            "csrf": self.csrf,
            "apiClient": "WEB"
        }
        if data is not None:
            payload.update(data)

        return self.post(endpoint, payload)

    def post(self, endpoint, data):
        return self.session.post(self.api_endpoint + endpoint, data)

    def load(self, session_file=None):
        fn = session_file or self.SESSION_FN
        if path.isfile(fn):
            with open(fn) as data_file:
                cookies = {}
                try:
                    cookies = json.load(data_file)
                except ValueError as err:
                    logging.error(err)
                self.cookies = cookies
        return self

    def save(self):
        with open(self.__session_file, 'w') as data_file:
            data_file.write(json.dumps(self.cookies))

    def make_request(self, endpoint):
        response = self.fetch(endpoint)

        # throw error if bad, parse json if good
        if response.status_code != 200:
            raise ValueError("Request failed with code {}.".format(response.status_code))
        return response.json()['spData']
