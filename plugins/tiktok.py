# tiktok plugin
# updated 07/2022
# i'm sorry

import re
from util import hook
from utilities import request


class Wrangler(str):
    def __init__(self, text: str):
        self.text = text

    def get_text(self):
        """will return and wipe self.text"""
        temp = self.text
        self.text = ''
        return temp

    def cut_left(self, search: str):
        """
            cut self.text up to $search from the left to the right, inclusive.
            given the text "hello world",
            cut_left("llo") -> "llo world"
                      ^^^       ^^^
        """
        if self.text.find(search) == -1:
            return None
        else:
            self.text = self.text[self.text.index(search):]
            return self

    def cut_right(self, search: str):
        """
            cut self.text up to $search from the right to the left, inclusive.
            given the text "hello world",
            cut_right("llo") -> "hello"
                       ^^^         ^^^
        """
        if self.text.find(search) == -1:
            return None
        else:
            self.text = self.text[:self.text.index(search) + len(search)]
            return self


@hook.command
def tiktok(id: str):
    """tiktok <id> -- return info on some tiktok video by unique id"""
    if re.match(r'^[0-9]{8,}$', id) is None:
        return 'invalid id'

    html = request.get(f'https://www.tiktok.com/embed/v2/{id}?lang=en-US')

    likes_json = Wrangler(html).cut_left('"diggCount"').cut_right(',').get_text()
    shares_json = Wrangler(html).cut_left('"shareCount"').cut_right(',').get_text()
    plays_json = Wrangler(html).cut_left('"playCount"').cut_right(',').get_text()
    comments_json = Wrangler(html).cut_left('"commentCount"').cut_right(',').get_text()

    username_json = Wrangler(html).cut_left('"uniqueId"').cut_right(',').get_text()
    nickname_json = Wrangler(html).cut_left('"nickName"').cut_right(',').get_text()

    return f'{likes_json}, {shares_json}, {plays_json}, {comments_json}' \
           f'{username_json}, {nickname_json}'
