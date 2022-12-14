import typing as tp

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore
from vkapi.exceptions import APIError


class TimeoutHTTPAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.timeout = 5
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


class Session:
    """
    Сессия.

    :param base_url: Базовый адрес, на который будут выполняться запросы.
    :param timeout: Максимальное время ожидания ответа от сервера.
    :param max_retries: Максимальное число повторных запросов.
    :param backoff_factor: Коэффициент экспоненциального нарастания задержки.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
    ) -> None:
        self.base_url = base_url
        self._session = requests.Session()
        adapter = TimeoutHTTPAdapter(
            timeout=timeout,
            max_retries=Retry(
                total=max_retries,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["GET", "POST"],
                backoff_factor=backoff_factor,
            ),
        )
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
        self._session.hooks["response"] = [
            lambda response, *args, **kwargs: response.raise_for_status()
        ]

    def get(self, url: str, *args, **kwargs) -> requests.Response:
        return self._request(url, "get", *args, **kwargs)

    def post(self, url: str, *args, **kwargs) -> requests.Response:
        return self._request(url, "post", *args, **kwargs)

    def _request(self, url: str, method: str, *args, **kwargs) -> requests.Response:
        request_url = f"{self.base_url}/{url}"
        if method == "get":
            response = self._session.get(url=request_url, *args, **kwargs)
        elif method == "post":
            response = self._session.post(url=request_url, *args, **kwargs)
        else:
            raise APIError(f"{method} is not supported")

        return response
