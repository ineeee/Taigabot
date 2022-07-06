# tiktok plugin
# updated 07/2022
# i'm sorry

import re
from util import hook
from utilities import request


class Wrangler:  # i love you 4chan
    def __init__(self, text: str, eat: bool = False):
        self.eat = eat
        self.text = text

    def get_text(self):
        """will return self.text but wipe it"""
        temp = self.text
        self.text = ''
        return temp

    def cut_left(self, search: str):
        """
            cut self.text up to $search from the left to the right, inclusive.
            using the text "hello world",

            if self.eat is set to false, then:
            cut_left("llo") -> "llo world"
                      ^^^       ^^^
        """
        if self.text.find(search) == -1:
            return None

        if not self.eat:
            self.text = self.text[self.text.index(search):]
        else:
            self.text = self.text[self.text.index(search) + len(search):]

        return self

    def cut_right(self, search: str):
        """
            cut self.text up to $search from the right to the left.
            consider the text "hello world"

            if self.eat is set to false, then:
            cut_right("llo") -> "hello"
                       ^^^         ^^^
        """
        if self.text.find(search) == -1:
            return None

        if not self.eat:
            self.text = self.text[:self.text.index(search) + len(search)]
        else:
            self.text = self.text[:self.text.index(search)]

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

    desc = Wrangler(html, True).cut_left('videoData') \
                               .cut_left('{').cut_right('}') \
                               .cut_left('text":"').cut_right('","stitchEnabled') \
                               .get_text()

    likes = Wrangler(likes_json, True).cut_left(':').cut_right(',').get_text()
    shares = Wrangler(shares_json, True).cut_left(':').cut_right(',').get_text()
    plays = Wrangler(plays_json, True).cut_left(':').cut_right(',').get_text()
    comments = Wrangler(comments_json, True).cut_left(':').cut_right(',').get_text()

    username = Wrangler(username_json, True).cut_left('":"').cut_right('",').get_text()
    nickname = Wrangler(nickname_json, True).cut_left('":"').cut_right('",').get_text()

    return f'[TikTok] \x02{nickname} (@{username})\x02 - {desc} - {likes} likes, {shares} shares, {plays} plays, {comments} comments'
