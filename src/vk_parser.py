from random import shuffle, choice

import vk_api

from settings import VK_SERVICE_TOKEN


class VKParser:

    PUBLIC_IDS = [
        '-214419372',  # https://vk.com/today_russia
        '-137451337',  # https://vk.com/street_f1ght
    ]

    def __init__(self):
        vk_session = vk_api.VkApi(token=VK_SERVICE_TOKEN)
        self.vk = vk_session.get_api()

    def choose_post(self) -> str | None:
        post = None
        public_ids = self.PUBLIC_IDS.copy()
        shuffle(public_ids)

        for public_id in public_ids:
            post = self._try_to_pick_post(public_id)
            if post:
                break

        return post

    def _try_to_pick_post(self, public_id: str) -> str | None:
        posts = self._get_posts(public_id)
        if not posts:
            return None
        # no strategy for now, just pick random
        return choice(posts)

    def _get_posts(self, public_id: str) -> list[str]:
        posts = self.vk.wall.get(owner_id=public_id, count=40, filter='owner')['items']
        return [p.get('text') for p in posts if p.get('text').strip()]
