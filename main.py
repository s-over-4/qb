import basebot
import sqlite3



NICK = 'qb'             # nick that the bot will assume when connecting to a room

DB_NAME = 'quotes.db'   # name that the quote database will be read from

LONG_HELP = (           # long help message
    'a quote bot by @c+1\n'
    'commands:\n'
    '   !quote - quote the parent message\n'
    '   !quote "message" @user - attribute a quote to a specified user\n'
    '   !list @qb - list quotes\n'
)

SHORT_HELP = (          # short help message
    'a quote bot'
)



# ===== setup database ===== #

queries = {
    'init_db': (
        'CREATE TABLE IF NOT EXISTS quotes('
        '   q_id INTEGER PRIMARY KEY,'          # the id of the quote in the database
        '   q_time INTEGER NOT NULL,'           # the time at which the quote was recorded; epoch timestamp
        '   q_content TEXT NOT NULL,'           # the quote content
        '   q_author TEXT NOT NULL,'            # the quote author
        '   euph_room TEXT,'                    # the room on euphoria.io where the quote was recorded
        '   euph_id TEXT,'                      # the id of the message on euphoria.io in the specified room
        '   platform TEXT,'                     # the platform the quote was transcribed from
        '   edited NUMERIC'                     # whether any part of the quote has been edited after initial transcription
        ')'
    )
}



con = sqlite3.connect(DB_NAME, check_same_thread=False)
cur = con.cursor()

cur.execute(queries['init_db'], )



# ===== command functions ===== #

# !quote - quote parent message
# regex: ^!quote$
def quote_parent(match, meta):
    # === get parent message id === #
    parent = meta['msg'].parent

    # ==+ api call for parent message === #
    packet = {'type': 'get-message', 'data': {'id': parent}}
    basebot.BaseBot.send_raw( self=meta['self'], obj=packet, retry=True )
    parent_data = basebot.BaseBot.recv_raw( self=meta['self'], retry=True )
    
    # === check if there is a parent message === #
    if 'error' in parent_data: meta['reply']('error: ' + parent_data['error']); return
    content = parent_data['data']['content']
    meta['reply'](content)

    # === create query === #
    # q_id, date, room, msg_content, msg_id, usr_nick, usr_id, edited
    q_id = (cur.execute('SELECT MAX(q_id) FROM quotes').fetchall())[0]
    meta['reply']('q_id:' + str(q_id))
    


# !list - list quotes
# regex: ^!list\s+@(\S+)$
def list(match, meta):
    res = cur.execute('SELECT q_content FROM quotes')
    meta['reply'](str(res.fetchall()))


# !test_the
# regex: ^!test_the$
def test_the(match, meta):
    meta['reply']('testing...')
    res = cur.execute('SELECT name FROM sqlite_master')
    meta['reply'](str(res.fetchone()))


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
    r'^!test_the$': test_the,
    r'^!list\s+@(\S+)$': list,
    r'^!quote$': quote_parent
}



def main():
    # === run bot === #
    basebot.run_minibot(
        botname=NICK,
        nickname=NICK,
        short_help=SHORT_HELP,
        long_help=LONG_HELP,
        regexes=regexes
    )



if __name__ == '__main__': main()