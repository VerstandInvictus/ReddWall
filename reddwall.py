import praw
import codecs
import unidecode
import os
import requests
import datetime
import regex as re
from collections import Counter

requests.packages.urllib3.disable_warnings()
subreddits = ["earthporn", "japanpics"]


class redditLogger:
    def __init__(self, logfile):
        self.logfile = logfile

    def logEntry(self, entry, level):
        with codecs.open(self.logfile, mode='a', encoding='utf-8') as log:
            log.write(entry + '\n')
        if 'progress' in level:
            print unidecode.unidecode(entry)


class reddit:
    def __init__(self, logobj):
        self.logger = logobj
        self.ua = "Python:ReddWall:v0.1 (by /u/verstandinvictus)"
        self.r = praw.Reddit(user_agent=self.ua)
        self.dest = os.path.join(os.getcwdu(), 'images')
        if not os.path.exists(self.dest):
            os.makedirs(self.dest)
        self.results = None
        self.resetResults()

    def resetResults(self):
        self.results = dict(
            count=0,
            skipped=0,
            failed=0,
            succeeded=0,
            nonexistent=0,
        )

    def getTopLinks(self, sub):
        atop = self.r.get_subreddit(sub).get_top_from_all(limit=None)
        submissions = set()
        for s in (atop,):
            for link in s:
                submissions.add(link)
        titles = list()
        for each in submissions:
            t = self.generateName(each)
            titles.append(re.split(' ', t))
        #self.upGoerFive(titles)

    def generateName(self, sub):
        rawtitle = unidecode.unidecode(sub.title.lower())
        spacesubs = ['\n', ur'\p{P}+']
        blanksubs = ['[\[\(].*[\)\]]', '/r/.*', '[0-9]']
        subdict = {
            "mt": "mount",
            "st helens": "saint_helens"
        }
        for pattern in spacesubs:
            rawtitle = re.sub(pattern, ' ', rawtitle)
        for pattern in blanksubs:
            rawtitle = re.sub(pattern, '', rawtitle)
        rawtitle = ' '.join(rawtitle.split())
        for pattern in subdict.iterkeys():
            rawtitle = re.sub(pattern, subdict[pattern], rawtitle)
        eatshorts = [x for x in re.split(' ', rawtitle) if len(x) > 1]
        try:
            ind = eatshorts.index('mount')
            print eatshorts[ind], eatshorts[ind+1], eatshorts[ind+2]
            #print rawtitle
        except:
            pass
        return rawtitle

    def upGoerFive(self, titles):
        c = Counter()
        for t in titles:
                c.update(t)
        for word, count in c.most_common(50):
            print "{0} :: {1}".format(count, word)

    def downloadImage(self, imgurl, imgname, dest=None):
        if not dest:
            rdest = self.dest
        else:
            rdest = dest
        try:
            imgwrite = os.path.join(rdest, imgname)
            if not os.path.exists(imgwrite):
                r = requests.get(imgurl)
                with open(imgwrite, "wb") as code:
                    code.write(r.content)
                self.logger.logEntry(('downloaded ' + imgname), 'progress')
                self.results['succeeded'] += 1
                return True
            else:
                self.logger.logEntry(('already have ' + imgname),
                                     'verbose')
                self.results['skipped'] += 1
                return True
        except:
            self.logger.logEntry('failed to get: {0} from {1}'.format(
                imgurl, imgname), 'verbose')
            self.results['failed'] += 1
            return None


if __name__ == "__main__":
    dt = datetime.date.today().strftime('%m-%d-%y')
    logfile = os.path.join('logs', str('reddwall ' + dt + '.log'))
    logger = redditLogger(logfile)
    site = reddit(logger)
    logfile = os.path.join('logs', )
    for target in subreddits:
        site.getTopLinks(target)
