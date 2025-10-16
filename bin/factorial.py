#!/usr/bin/env python3

import contextlib
import datetime
import enum
import pathlib
import random
import shelve
import sys
from typing import Any, Callable, Dict, List, Optional

import bs4
import requests


def main():
    with Client.new() as client:
        with Cache.open() as cache:
            login(client, cache)

        if len(sys.argv) > 1:
            date = datetime.date.fromisoformat(sys.argv[1])
        else:
            date = datetime.date.today()

        delete_shifts(client, date)

        config = ShiftsConfig(
            start_at=datetime.time(8, 30),
            start_at_variance=lambda: datetime.timedelta(
                minutes=random.randrange(-15, 15)
            ),
            shift_duration=datetime.timedelta(hours=4, minutes=5),
            shift_duration_variance=lambda: datetime.timedelta(
                minutes=random.randrange(-15, 15)
            ),
            break_duration=datetime.timedelta(minutes=55),
            break_duration_variance=lambda: datetime.timedelta(
                minutes=random.randrange(-10, 10)
            ),
            break_type=BreakType.OneHourBreak,
        )

        create_shifts(client, date, config)


def login(client: "Client", cache: "Cache"):
    default_email = cache.last_used_email()
    if default_email is not None:
        prompt = f'enter e-mail (default="{default_email}"): '
    else:
        prompt = "enter e-mail: "
    email = input(prompt) or default_email
    if not email:
        raise ValueError("no email provided")
    cache.set_last_used_email(email)

    cookie = cache.session_cookie(email)
    if cookie is None or cookie.has_expired():
        password = input("enter password: ")
        if not password:
            raise ValueError("no password provided")
        client.login(email, password)
        cache.set_session_cookie(email, client.session_cookie())
    else:
        client.set_session_cookie(cookie)


def delete_shifts(client: "Client", date: datetime.date):
    me = client.get_me()
    for shift in client.list_shifts(date=date, employee_ids=[me["employee_id"]]):
        client.delete_shift(shift_id=shift["id"])


def create_shifts(client: "Client", date: datetime.date, config: "ShiftsConfig"):
    first_shift_started_at = (
        datetime.datetime.combine(date, config.start_at) + config.start_at_variance()
    )
    first_shift_ended_at = (
        first_shift_started_at
        + config.shift_duration
        + config.shift_duration_variance()
    )
    client.create_shift(
        date=date,
        clock_in=first_shift_started_at.time(),
        clock_out=first_shift_ended_at.time(),
    )
    print(
        f"first_shift: {first_shift_started_at.time()}-{first_shift_ended_at.time()} ({first_shift_ended_at - first_shift_started_at})",
    )

    break_started_at = first_shift_ended_at
    break_ended_at = (
        break_started_at + config.break_duration + config.break_duration_variance()
    )
    client.create_shift(
        date=date,
        clock_in=break_started_at.time(),
        clock_out=break_ended_at.time(),
        workable=False,
        time_settings_break_configuration_id=config.break_type.value,
    )
    print(
        f"break: {break_started_at.time()}-{break_ended_at.time()} ({break_ended_at - break_started_at})"
    )

    second_shift_started_at = break_ended_at
    second_shift_ended_at = (
        second_shift_started_at
        + config.shift_duration
        + config.shift_duration_variance()
    )
    client.create_shift(
        date=date,
        clock_in=second_shift_started_at.time(),
        clock_out=second_shift_ended_at.time(),
    )
    print(
        f"second_shift: {second_shift_started_at.time()}-{second_shift_ended_at.time()} ({second_shift_ended_at - second_shift_started_at})",
    )

    print(
        f"worked_total: {(second_shift_ended_at - first_shift_started_at) - (break_ended_at - break_started_at)}"
    )


class ShiftsConfig:
    def __init__(
        self,
        start_at: datetime.time,
        start_at_variance: Callable[[], datetime.timedelta],
        shift_duration: datetime.timedelta,
        shift_duration_variance: Callable[[], datetime.timedelta],
        break_duration: datetime.timedelta,
        break_duration_variance: Callable[[], datetime.timedelta],
        break_type: "BreakType",
    ):
        self.start_at = start_at
        self.start_at_variance = start_at_variance
        self.shift_duration = shift_duration
        self.shift_duration_variance = shift_duration_variance
        self.break_duration = break_duration
        self.break_duration_variance = break_duration_variance
        self.break_type = break_type


class BreakType(enum.Enum):

    ThirtyMinuteBreak = 4793
    FourtyFiveMinuteLunchBreak = 4797
    OneHourBreak = 4794


class Client:

    @classmethod
    @contextlib.contextmanager
    def new(cls, **kwargs):
        with requests.Session() as session:
            yield cls(session=session, **kwargs)

    def __init__(
        self,
        session: requests.Session,
        user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        base_url: str = "https://api.factorialhr.com",
    ):
        self._session = session
        self._session.headers["User-Agent"] = user_agent
        self._base_url = base_url

    def session_cookie(self) -> Optional["SessionCookie"]:
        try:
            return SessionCookie.from_cookie_jar(self._session.cookies)
        except StopIteration:
            return None

    def set_session_cookie(self, cookie: "SessionCookie"):
        self._session.cookies.set(cookie.NAME, cookie.value)

    def get_me(self):
        response = self._session.get(self._url_api_resources_api_public_credentials())
        if not response.ok:
            raise RuntimeError(response.json())
        return response.json()["data"][0]

    def create_shift(
        self,
        date: datetime.date,
        clock_in: datetime.time,
        clock_out: datetime.time,
        workable: Optional[bool] = None,
        time_settings_break_configuration_id: Optional[int] = None,
    ):
        payload: Dict[str, Any] = {
            "date": date.isoformat(),
            "clock_in": f"{date.isoformat()}T{clock_in.isoformat()}",
            "clock_out": f"{date.isoformat()}T{clock_out.isoformat()}",
        }
        if workable is not None:
            payload["workable"] = workable
        if time_settings_break_configuration_id is not None:
            payload["time_settings_break_configuration_id"] = (
                time_settings_break_configuration_id
            )
        response = self._session.post(
            self._url_api_resources_attendance_shifts(), json=payload
        )
        if not response.ok:
            raise RuntimeError(response.content)
        return response.json()

    def list_shifts(
        self, date: datetime.date, employee_ids: Optional[List[int]] = None
    ):
        params: Dict[str, Any] = {
            "start_on": date.isoformat(),
            "end_on": date.isoformat(),
        }
        if employee_ids is not None:
            params["employee_ids[]"] = employee_ids
        response = self._session.get(
            self._url_api_resources_attendance_shifts(), params=params
        )
        if not response.ok:
            raise RuntimeError(response.content)
        return response.json()["data"]

    def delete_shift(self, shift_id):
        response = self._session.delete(
            f"{self._url_api_resources_attendance_shifts()}/{shift_id}"
        )
        if not response.ok:
            raise RuntimeError(response.content)
        return response.json()

    def login(self, email: str, password: str):
        self._login(email, password)
        me = self.get_me()
        if me["email"] != email:
            raise RuntimeError("unexpected login email")

    def _login(self, email: str, password: str):
        payload = {
            "authenticity_token": self._generate_authenticity_token(),
            "user[email]": email,
            "user[password]": password,
            "user[remember_me]": "0",
        }
        response = self._session.post(self._url_users_sign_in(), data=payload)
        response.raise_for_status()

    def _generate_authenticity_token(self):
        response = self._session.get(self._url_users_sign_in())
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        try:
            return soup.find("input", attrs={"name": "authenticity_token"})["value"]
        except KeyError as e:
            raise RuntimeError("token not found") from e

    def _url_users_sign_in(self) -> str:
        return f"{self._base_url}/de/users/sign_in"

    def _url_api_resources_api_public_credentials(self) -> str:
        return f"{self._base_url}/api/resources/api_public/credentials"

    def _url_api_resources_attendance_shifts(self) -> str:
        return f"{self._base_url}/api/resources/attendance/shifts"


class Cache:

    DEFAULT_PATH = pathlib.Path.home() / ".cache" / pathlib.Path(__file__).name

    def __init__(self, shelf: shelve.DbfilenameShelf):
        self._shelf = shelf

    def last_used_email(self) -> Optional[str]:
        return self._shelf.get("last_used_email")

    def set_last_used_email(self, email):
        self._shelf["last_used_email"] = email

    def session_cookie(self, email: str) -> Optional["SessionCookie"]:
        cookies = self._shelf.get("session_cookies", {})
        return cookies.get(email)

    def set_session_cookie(self, email: str, cookie: "SessionCookie"):
        cookies = self._shelf.get("session_cookies", {})
        cookies[email] = cookie
        self._shelf["session_cookies"] = cookies

    @classmethod
    @contextlib.contextmanager
    def open(cls, path: pathlib.Path = DEFAULT_PATH):
        with shelve.open(path) as shelf:
            yield cls(shelf=shelf)


class SessionCookie:

    NAME = "_factorial_session_v2"

    def __init__(self, value: str, expires_at: datetime.datetime):
        self.value = value
        self.expires_at = expires_at

    def has_expired(self) -> bool:
        return self.expires_at < datetime.datetime.now()

    @classmethod
    def from_cookie_jar(cls, cookie_jar: requests.cookies.RequestsCookieJar):
        cookie = next(c for c in cookie_jar if c.name == cls.NAME)
        expires_at = datetime.datetime.fromtimestamp(cookie.expires)
        return cls(value=cookie.value, expires_at=expires_at)


if __name__ == "__main__":
    main()
