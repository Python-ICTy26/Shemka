import datetime as dt
import typing as tp

from vkapi.friends import get_friends


def age_predict(user_id: int) -> tp.Optional[float]:
    """
    Наивный прогноз возраста пользователя по возрасту его друзей.
    Возраст считается как медиана среди возраста всех друзей пользователя
    :param user_id: Идентификатор пользователя.
    :return: Медианный возраст пользователя.
    """
    friends = get_friends(user_id, fields=["bdate"])
    _, friends_list = friends.count, friends.items
    year = dt.datetime.now().year
    ages = []
    for i in friends_list:
        try:
            if i["bdate"] and len(i["bdate"].split(".")) == 3:
                ages.append(year - int(i["bdate"].split(".")[2]))
        except KeyError:
            pass
    if ages and len(ages) % 2 == 0:
        srt_ages = sorted(ages)
        return (srt_ages[len(ages) // 2] + srt_ages[len(ages) // 2 - 1]) / 2.0
    elif ages and len(ages) % 2 == 1:
        srt_ages = sorted(ages)
        return srt_ages[len(ages) // 2]
    return None
