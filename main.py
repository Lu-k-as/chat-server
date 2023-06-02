from model_infosocial import *
import infosocial_db as db
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

hostName = "0.0.0.0"
serverPort = 8000


def login_page():
    return Path('templates/login.html').read_text()


def create_info(params, banners):
    infonaut = check_login(params)
    if not infonaut:
        return login_page()

    if 'info' in params:
        # something to save
        success = db.db_create_info(infonaut, urllib.parse.unquote(urllib.parse.unquote_plus(params['info'])))
        if not success:
            banners.append(f'<div class="big-error">Fehler beim Versuch die info zu speichern.</div>')
        else:
            banners.append(f'<div class="big-success">Die info wurde erfolgreich erstellt.</div>')
            return timeline(infonaut, banners)

    header = f'{user_box(infonaut)}\n' \
             '<h1>Was fuer ein "info" hast du fuer uns?</h1>' \
             '<div id="info-form">' \
             '<form action="create" method="get">' \
             '<p>' \
             'Dein Text:</p> <textarea name="info"></textarea>' \
             f'<p><input type="hidden" name="infonaut" value="{infonaut}"/>' \
             '<input type="submit" value="abschicken"/>' \
             '</p>' \
             '</form>' \
             '</div>'

    return '\n'.join(banners) + header


def delete_info(params, banners):
    infonaut = check_login(params)
    if not infonaut:
        return login_page()

    if 'info' not in params:
        return timeline(infonaut, banners)

    success = db.db_delete_info(infonaut, params['info'])
    if not success:
        banners.append(f'<div class="big-error">Fehler beim Versuch die info zu löschen.</div>')
    else:
        banners.append(f'<div class="big-success">Die info wurde erfolgreich gelöscht.</div>')
    return timeline(infonaut, banners)


def like_info(params, banners):
    infonaut = check_login(params)
    if not infonaut:
        return login_page()

    if 'info' not in params:
        return timeline(infonaut, banners)

    success = db.db_like(infonaut, params['info'])
    if not success:
        banners.append(f'<div class="big-error">Fehler beim Versuch die info zu liken.</div>')
    else:
        banners.append(f'<div class="big-success">Die info wurde erfolgreich geliked.</div>')
    return timeline(infonaut, banners)


def timeline(infonaut, banners):

    header = f'{user_box(infonaut)}\n' \
             f'<h1>Das sind die neuesten "infos" fuer dich:</h1>' \
             f'<div id="create-link"><a href="create?infonaut={infonaut}">Neue "info" erstellen</a></div>'
    try:
        infos = '\n'.join([info.html_block(infonaut) for info in db.db_load_all_infos(infonaut)])
        bans = '\n'.join(banners)
        return f'{bans}{header}<div id="infos-listing">\n{infos}\n</div>'
    except ItWasntMe as error:
        return f'<div class="big-error">Fehler beim Laden der Daten</div>'


def login(params):
    infonaut = check_login(params)
    if infonaut and db.db_logged_in(infonaut):
        return timeline(infonaut, [])
    else:
        return login_page()


def check_login(params):
    if 'infonaut' in params:
        return urllib.parse.unquote_plus(urllib.parse.unquote(params['infonaut']))

    return ''


class GDIServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(Path('templates/head.html').read_text(), "utf-8"))
        self.wfile.write(bytes(self.dispatch_action(), "utf-8"))
        self.wfile.write(bytes(Path('templates/foot.html').read_text(), "utf-8"))

    def dispatch_action(self):
        action, _, query = self.path.split('/')[-1].partition('?')

        parts = query.split('&')
        parsed = dict()
        for part in parts:
            key, _, value = part.partition('=')
            parsed[key] = value

        if action == 'login':
            return login(parsed)
        elif action == 'show':
            pass
        elif action == 'logout':
            return login_page()
        elif action == 'create':
            return create_info(parsed, [])
        elif action == 'delete':
            return delete_info(parsed, [])
        elif action == 'like':
            return like_info(parsed, [])

        return login_page()


def user_box(user):
    return f'<div id="infonaut-box">Hallo {user}! <span id="logout"><a href="logout">Logout</a></span></div>'


if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), GDIServer)
    print("Infosocial Client gestartet und erreichbar unter: http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print('Infosocial Client beendet. Auf Wiedersehen!')
