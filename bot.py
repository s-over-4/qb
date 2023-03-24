# the euphoria bot that collects quotes for the database
__version__ = '2.0'

# packages - must be installed
import basebot
import sqlite3
from time import time
from string import Template


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





# ===== helper functions ===== #
#                              #

# get_parent: Dict meta -> Object
# get the parent message details
def get_parent(meta):
    parent_id = meta['msg'].parent

    # === api call for parent message === #
    packet = { 'type': 'get-message', 'data': {'id': parent_id} }
    basebot.BaseBot.send_raw( self=meta['self'], obj=packet, retry=True )
    parent_data = basebot.BaseBot.recv_raw( self=meta['self'], retry=True )

    return parent_data

#                                  #
# ===== end helper functions ===== #





# ===== command functions ===== #
#                               #

# !quote - quote parent message
# regex: ^!quote$
def quote_parent(match, meta):
    parent_data = get_parent(meta)
    
    # === check if there's a parent message at all === #
    if 'error' in parent_data: meta['reply']('API error: ' + parent_data['error']); return

    # === prepare quote details === #
    q_time = parent_data['data']['time']
    q_content = parent_data['data']['content']
    q_author = parent_data['data']['sender']['name']

    euph_room = meta['msg_meta']['self'].roomname
    euph_id = parent_data['data']['id']

    cur.execute(
        queries['add_quote'], (
            # for the most part, these mach their field names
            q_time,
            q_content,
            q_author,
            euph_room,
            euph_id,
            NICK,       # euph_bot
            MAINTAINER  # maintainer
        )
    )

    con.commit()

    meta['reply']("added successfully")
    

# !list - list last 15 quotes
# regex: ^!list\s+@(\S+)$
def list(match, meta):
    response = ''
    for row in cur.execute(queries['list_15']):
        response += f"\"{row[2]}\" - {row[3]}\n"
    
    meta['reply'](response)



# !kill command
# regex: ^!kill\s+@(\S+)\s*$
def maybe_die(match, meta):
    # ignore !kills towards others
    nick = match.group(1)
    if not meta['self'].nick_matches(nick):
        return

    # otherwise, respond and exit
    meta['reply']('/me exits')
    meta['self'].manager.shutdown()



# regexes to which the bot will respond
regexes = {
    r'^!kill\s+@(\S+)\s*$': maybe_die,
    r'^!quote\s+-list$': list,
    r'^!quote$': quote_parent,
    r'^!quote\s+-parent$': quote_parent
}

#                                   #
# ===== end command functions ===== #





def main():
    # === run the bot! === #
    basebot.run_minibot(
        botname=NICK,
        nickname=NICK,
        short_help=SHORT_HELP,
        long_help=LONG_HELP,
        regexes=regexes
    )



if __name__ == '__main__': main()