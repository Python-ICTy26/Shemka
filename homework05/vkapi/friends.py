import dataclasses
import time
import typing as tp

from vkapi import session
from vkapi.config import VK_CONFIG

QueryParams = tp.Optional[tp.Dict[str, tp.Union[str, int]]]


@dataclasses.dataclass(frozen=True)
class FriendsResponse:
    count: int
    items: tp.List[tp.Dict[str, tp.Any]]


def get_friends(
    user_id: int,
    count: int = 5000,
    offset: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> FriendsResponse:
    """
    Получить список идентификаторов друзей пользователя или расширенную информацию
    о друзьях пользователя (при использовании параметра fields).

    :param user_id: Идентификатор пользователя, список друзей для которого нужно получить.
    :param count: Количество друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества друзей.
    :param fields: Список полей, которые нужно получить для каждого пользователя.
    :return: Список идентификаторов друзей пользователя или список пользователей.
    """
    fields = fields or []
    str_fields = ",".join(fields)
    params = dict(
        access_token=VK_CONFIG["access_token"],
        user_id=user_id,
        fields=str_fields,
        offset=offset,
        count=count,
        v=VK_CONFIG["version"],
    )
    response = session.get("friends.get", params=params).json()["response"]
    return FriendsResponse(count=response["count"], items=response["items"])


class MutualFriends(tp.TypedDict):
    id: int
    common_friends: tp.List[int]
    common_count: int


def get_mutual(
    source_uid: tp.Optional[int] = None,
    target_uid: tp.Optional[int] = None,
    target_uids: tp.Optional[tp.List[int]] = None,
    order: str = "",
    count: tp.Optional[int] = None,
    offset: int = 0,
    progress=None,
) -> tp.Union[tp.List[int], tp.List[MutualFriends], None]:
    """
    Получить список идентификаторов общих друзей между парой пользователей.

    :param source_uid: Идентификатор пользователя, чьи друзья пересекаются с друзьями пользователя с идентификатором target_uid.
    :param target_uid: Идентификатор пользователя, с которым необходимо искать общих друзей.
    :param target_uids: Cписок идентификаторов пользователей, с которыми необходимо искать общих друзей.
    :param order: Порядок, в котором нужно вернуть список общих друзей.
    :param count: Количество общих друзей, которое нужно вернуть.
    :param offset: Смещение, необходимое для выборки определенного подмножества общих друзей.
    :param progress: Callback для отображения прогресса.
    """
    params = dict(
        offset=offset,
        v=VK_CONFIG["version"],
        access_token=VK_CONFIG["access_token"],
    )

    if order != "":
        params["order"] = order
    if count is not None:
        params["count"] = count
    if source_uid is not None:
        params["source_uid"] = source_uid

    if target_uid is not None and target_uids is not None:
        raise ValueError("Either target_uid or target_uids must be specified")
    elif target_uid is None and target_uids is None:
        raise ValueError("target_uid or target_uids must be specified")

    if target_uid is not None:
        params["target_uid"] = target_uid
        mutual_ids = session.get("friends.getMutual", params=params).json()["response"]
        return mutual_ids
    elif target_uids is not None:
        offset_iterator = list(range(0, len(target_uids), 100))
        if progress is not None:
            offset_iterator = progress(offset_iterator)

        params["target_uids"] = ",".join(str(i) for i in target_uids)

        mutual_friends = []
        for offset in offset_iterator:
            params["offset"] = offset
            time_start = time.time()
            response = session.get("friends.getMutual", params=params).json()["response"]
            for r in response:
                r = MutualFriends(id=r["id"], common_friends=r["common_friends"], common_count=r["common_count"])
                if r["common_count"] > 0:
                    mutual_friends.append(r)

            delay = max(1 - (time.time() - time_start), 0)
            time.sleep(delay)
        return mutual_friends
    return None