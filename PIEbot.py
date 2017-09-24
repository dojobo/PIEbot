import json
import mysql.connector
import random
import twitter

CHAR_LIMIT = 140


class PIEbot(object):
    
    def __init__(self, config=None):
        """ intialize without config for testing """
        if config:
            self.db = mysql.connector.connect(**config['db'])
            self.cursor = self.db.cursor(dictionary=True)
            self.api = twitter.Api(**config['twitter'])


    def random_root_id(self):
        """ fetch the id of a random PIE root from the DB, return an int """
        self.cursor.execute('select root_id from pie_roots')
        ids = self.cursor.fetchall()
        return random.choice(ids)['root_id']

    def random_words_of_root_id(self, root_id, count=1):
        """ fetch a number of random words descended from root_id;
        ensure each is from a different language;
        return list of dicts """
        query = ("select root, root_pokorny, root_meaning, lang_name, lang_flag, mod_word, mod_pos, mod_meaning "
                 "from mod_words as W "
                 "join languages as L on W.lang_id = L.lang_id "
                 "join pie_roots as R on W.root_id = R.root_id "
                 "where W.root_id = %(root_id)s")
        self.cursor.execute(query, { 'root_id': root_id })
        words = self.cursor.fetchall()
        results = []
        while count > 0 and words:
            this_word = random.choice(words)
            results.append(this_word)
            words = [ word for word in words if word['lang_name'] != this_word['lang_name'] ]
            count -= 1
        return results

    def format_root(self, root, pokorny, meaning):
        """ format a root and its Pokorny formulation (which often doesn't match)
        for tweeting; return a str """
        if not pokorny or root == '*'+pokorny:
            root_phrase = "PIE {} ({})".format(root, meaning)
        else:
            root_phrase = "PIE {} or {} ({})".format(root, pokorny, meaning)
        return root_phrase

    def format_gloss(self, lang, mod_pos, mod_meaning):
        """ format the modern-language gloss and return a str """
        if lang == 'English':
            gloss = mod_pos
        else:
            gloss = "{}, \"{}\"".format(mod_pos, mod_meaning)
        return gloss


    def write_basic_tweet(self, row):
        """ format a simple tweet for one descendant, and return a str """
        lang = row['lang_name'].decode("utf-8")

        root = self.format_root(row['root'], row['root_pokorny'], row['root_meaning'])

        modern = "{} \"{}\"".format(lang, row['mod_word'])
        gloss = self.format_gloss(lang, row['mod_pos'], row['mod_meaning'])
        tweet = "{} > {} ({})".format(root, modern, gloss)

        return tweet

    def write_tweet_with_flags(self, rows):
        """ format a tweet for 3 langs and return a str """
        root = self.format_root(rows[0]['root'], rows[0]['root_pokorny'], rows[0]['root_meaning'])
        mod_strings = []
        for row in rows:
            lang = row['lang_name'].decode("utf-8")
            if row['lang_flag']:
                lang_display = row['lang_flag'].decode('utf-8')
            else:
                lang_display = lang
            gloss = self.format_gloss(lang, row['mod_pos'], row['mod_meaning'])
            mod_str = "{}: \"{}\" ({})".format(lang_display, row['mod_word'], gloss)
            mod_strings.append(mod_str)
        tweet = "{}:\n{}".format(root, "\n".join(mod_strings))

        # if too long, exclude Pokorny from the root... will probably need to be changed later
        if len(tweet) > CHAR_LIMIT:
            root = self.format_root(rows[0]['root'], None, rows[0]['root_meaning'])
            tweet = "{}:\n{}".format(root, "\n".join(mod_strings))

        return tweet


    def post_tweet(self, tweet):
        """ post a str as a tweet, and return a twitter.Status """
        return self.api.PostUpdate(tweet)


    def get_all_roots(self):
        """ return all roots as a list of dicts """
        query = ("select root_id, root, root_meaning, root_pokorny, source, date_added "
                 "from pie_roots")
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def close(self):
        """ close db connection """
        self.db.close()


if __name__ == '__main__':
    with open('config.json') as file:
        config = json.load(file)
    p = PIEbot(config)
    root_id = p.random_root_id()

    # simple tweet:    
    # word_entry = p.random_words_of_root_id(root_id)[0]
    # tweet = p.write_basic_tweet(word_entry)
    
    # or three langs:
    word_entries = p.random_words_of_root_id(root_id, 3)
    tweet = p.write_tweet_with_flags(word_entries)

    print(tweet)
    print("{} chars".format(len(tweet)))

    status = p.post_tweet(tweet)
    print("@{}: {}".format(status.user.screen_name, status.text))

    p.close()
