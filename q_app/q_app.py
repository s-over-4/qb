from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

bp = Blueprint('q_app', __name__)

# the web interface for the quote database
__version__ = '0.1'

# packages - must be installed
from flask import Flask
from markupsafe import escape
import sqlite3

# TODO: move these into a config file
# ===== quick config ===== #
#                          #

NICK = 'qb'                     # nick that the bot will send from and respond to (WILL APPEAR IN DATABASE)
MAINTAINER = 'c+1'              # the name of the person maintaining this bot (WILL APPEAR IN DATABASE)

LONG_HELP = (                   # long help message
    'a quote bot by @c+1\n'
    'commands:\n'
    '   !quote -parent:     quote the parent message\n'
    '   !quote -list:       list last 15 quotes\n'
    '   !quote:             alias for !quote -parent\n'
)
SHORT_HELP = 'a quote bot'      # short help message

DB_NAME = 'quotes.db'           # name of the file that the quote database will be written to/read from

#                              #
# ===== end quick config ===== #

# TODO: move this into a module
# ===== set up database ===== #
#                             #

queries = {
    'init_db': (
        'CREATE TABLE IF NOT EXISTS quotes ('

        # === quote parameters === #
        '   q_id INTEGER PRIMARY KEY AUTOINCREMENT,'    # the id of the quote in the database
        '   q_time INTEGER NOT NULL,'                   # the time at which the quoted message was posted; epoch timestamp
        '   q_content TEXT NOT NULL,'                   # the quote content
        '   q_author TEXT NOT NULL,'                    # the quote author

        # === euphoria-specific === #
        '   euph_room TEXT,'                            # the room on euphoria.io where the quote was recorded
        '   euph_id TEXT,'                              # the id of the message on euphoria.io in the specified room
        '   euph_bot TEXT,'                             # the name of the bot that recorded the quote on euphoria.io
        '   euph_maintainer TEXT,'                      # the name of the person maintaining the bot

        # === misc === #
        '   platform TEXT,'                             # the platform the quote was transcribed from
        '   edited NUMERIC'                             # whether any part of the quote has been edited after initial transcription
        ');'
    ),

    'add_quote': (
        'INSERT INTO quotes (q_time, q_content, q_author, euph_room, euph_id, euph_bot, euph_maintainer, platform, edited)'
        'VALUES (            ?,      ?,         ?,        ?,         ?,       ?,        ?,              \'euphoria.io\', 0 );'
    ),

    'list_15': (
        'SELECT * FROM quotes ORDER BY q_time DESC LIMIT 15'
    )
}

con = sqlite3.connect(DB_NAME, check_same_thread=False)
cur = con.cursor()

cur.execute(queries['init_db'])

#                                 #
# ===== end set up database ===== #



# ===== set up web server ===== #
app = Flask(__name__)


@bp.route('/')
def last_15():
    response = ''
    for row in cur.execute(queries['list_15']):
        response += f"\"{row[2]}\" - {row[3]}\n"
    
    return f'<pre>last 15 quotes:\n\n{escape(response)}</pre>'