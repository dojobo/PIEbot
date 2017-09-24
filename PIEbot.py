import json
import mysql.connector
import random
import twitter

with open('config.json') as file:
    config = json.load(file)

class PIEbot(object):
    
    def __init__(self):
        self.db = mysql.connector.connect(**config['db'])
        self.cursor = self.db.cursor(dictionary=True)
        self.api = twitter.Api(**config['twitter'])

    def random_root_id(self):
        self.cursor.execute('select root_id from pie_roots')
        ids = self.cursor.fetchall()
        return random.choice(ids)['root_id']

    def random_word_of_root_id(self, root_id):
        query = ("select root, root_pokorny, root_meaning, lang_name, mod_word, mod_pos, mod_meaning "
                 "from mod_words as W "
                 "join languages as L on W.lang_id = L.lang_id "
                 "join pie_roots as R on W.root_id = R.root_id "
                 "where W.root_id = %(root_id)s")
        self.cursor.execute(query, { 'root_id': root_id })
        words = self.cursor.fetchall()
        return random.choice(words)

    def write_tweet(self):
        root_id = self.random_root_id()
        w = self.random_word_of_root_id(root_id)
        lang = w['lang_name'].decode("utf-8")

        # newer root formulations often don't match Pokorny; show both:
        if w['root'] == '*'+w['root_pokorny']:
            root = "PIE {} ({})".format(w['root'], w['root_meaning'])
        else:
            root = "PIE {} or {} ({})".format(w['root'], w['root_pokorny'], w['root_meaning'])

        modern = "{} \"{}\"".format(lang, w['mod_word'])
        # don't give an gloss for English words
        if lang == 'English':
            gloss = w['mod_pos']
        else:
            gloss = "{}, \"{}\"".format(w['mod_pos'], w['mod_meaning'])
        tweet = "{} > {} ({})".format(root, modern, gloss)

        return tweet


    def post_tweet(self, tweet):
        return self.api.PostUpdate(tweet)


    def get_all_roots(self):
        query = ("select root_id, root, root_meaning, root_pokorny, source, date_added "
                 "from pie_roots")
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def close(self):
        self.db.close()


if __name__ == '__main__':
    p = PIEbot()
    tweet = p.write_tweet()
    print(tweet)
    print("{} chars".format(len(tweet)))
    status = p.post_tweet(tweet)
    print("@{}: {}".format(status.user.screen_name, status.text))
    p.close()
