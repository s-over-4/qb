import basebot
import sqlite3



NICK = 'qb'             # nick that the bot will assume when connecting to a room

DB_NAME = 'quotes.db'   # name that the quote database will be read from

LONG_HELP = (           # long help message
    '/me preforms actions'
)

SHORT_HELP = (          # short help message
    '/me preforms actions'
)



# ===== setup database ===== #

con = sqlite3.connect(DB_NAME, check_same_thread=False)
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS quote (id, name, content, date)')



# ===== command functions ===== #

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
    r'^!test_the$': test_the
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