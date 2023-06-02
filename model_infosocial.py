import datetime


class Info:

    def __init__(self, iid, creator_name, text, creation_date, likes, liked):
        self.id = iid
        self.creator_name = creator_name
        self.text = text
        self.creation_date = creation_date
        self.likes = likes
        self.liked = liked

    def html_block(self, infonaut):
        return f'<div class="info-div">' \
               f'<p class="info-date">{self.creation_date.strftime("am %d.%m.%Y um %H:%M Uhr")}</p>' \
               f'<p class="author-head">von <span class="author-name">{self.creator_name}</span>' \
               f'{self.delete_button(infonaut)}</p>' \
               f'<p class="info-text">{self.text}</p>' \
               f'<p class="info-likes">{self.likes} likes{self.like_button(infonaut)}</p>' \
               f'</div>'

    def like_button(self, infonaut):
        if infonaut == self.creator_name or self.liked:
            return ''
        return f' [<a href="like?info={self.id}&infonaut={infonaut}">like</a>] '

    def delete_button(self, infonaut):
        if infonaut != self.creator_name:
            return ''
        return f' <span class="delete-span">[<a href="delete?info={self.id}&infonaut={infonaut}">' \
               f'info löschen</a>]</span> '


def format_date(date_str):
    print(date_str)
    print(type(date_str))
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.f').strftime('%d.%m.%Y um %H:%M Uhr')


class ItWasntMe(Exception):

    def __init__(self):
        super().__init__("Ich wars nicht!")
