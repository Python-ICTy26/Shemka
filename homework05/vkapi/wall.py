import math
import time
import typing as tp

import pandas as pd
from pandas import json_normalize
from vkapi import session
from vkapi.config import VK_CONFIG


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    *args,
    **kwargs,
) -> tp.Dict[str, tp.Any]:
    params = {
        "access_token": VK_CONFIG["access_token"],
        "v": VK_CONFIG["version"],
        "owner_id": owner_id,
        "domain": domain,
        "offset": offset,
        "count": max_count,
        "filter": filter,
        "extended": extended,
    }
    if fields:
        params["fields"] = ",".join(fields)
    return session.get("wall.get", params=params).json()["response"]


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """

    code = """return API.wall.get({
         "owner_id": "%s",
         "domain": "%s",
         "offset": %d,
         "count": "%d",
         "filter": "%s",
         "extended": %d,
         "fields": "%s",
         "v": "%s"
    });"""

    answer = []
    for i in range(math.ceil(count / 100)):
        code_for_request = code % (
            owner_id,
            domain,
            100 * i,
            100 * (i + 1) if count > 100 else count,
            filter,
            extended,
            fields,
            VK_CONFIG["version"],
        )
        response = session.post(
            url="execute",
            data={
                "code": code_for_request,
                "access_token": VK_CONFIG["access_token"],
                "v": VK_CONFIG["version"],
            },
        )
        answer += response.json()["response"]["items"]
        if i % 2 == 0:
            time.sleep(1)
    return json_normalize(answer)
