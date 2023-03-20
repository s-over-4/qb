import basebot



HELP = """

/me preforms actions

"""



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
    r'^!kill\s+@(\S+)\s*$': maybe_die
}



def main():
    basebot.run_minibot(
        botname='test_bot',
        nickname='test_bot',
        long_help=HELP,
        regexes=regexes
    )



if __name__ == '__main__': main()