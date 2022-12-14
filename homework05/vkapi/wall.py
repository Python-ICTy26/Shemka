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

    if count == 0:
        code = f'return API.wall.get({{"owner_id": "{owner_id}", "domain":"{domain}", "count": "1"}});'
        params = {
            "code": code,
            "access_token": VK_CONFIG["access_token"],
            "v": VK_CONFIG["version"],
        }
        count = session.post("execute", data=params).json()["response"]["count"]

    offsets_iterator = [
        [q for q in range(i, i + max_count, max_count // 25) if q < count]
        for i in range(0, count, max_count)
    ]
    if progress is not None:
        offsets_iterator = progress(offsets_iterator)

    posts = list()

    for offsets in offsets_iterator:
        code = f"""
        var posts = [];
        var count = 0;
        var i = 0;
        var offsets = {offsets};
        
        while ((i < 25) && (i < offsets.length)) {{
            var new_posts = API.wall.get({{
                "owner_id": "{owner_id}",
                "domain": "{domain}",
                "offset": offsets[i],
                "count": "{max_count // 25}",
                "filter": "{filter}",
                "extended": {extended},
                "fields": "{','.join(fields) if fields is not None else ''}",
                "v": "{VK_CONFIG['version']}"
            }})["items"];
            posts = posts + new_posts;
            
            i = i + 1;
        }}
        
        return {{"count": count, "items": posts}};
        """

        params = {
            "code": code,
            "access_token": VK_CONFIG["access_token"],
            "v": VK_CONFIG["version"],
        }
        ts = time.time()
        new_posts = session.post("execute", params=params).json()["response"]
        delay = max([0, 1 - (time.time() - ts)])
        time.sleep(delay)
        posts.extend(new_posts["items"])
        posts = [p for p in posts if p is not None]

    return json_normalize(posts)
