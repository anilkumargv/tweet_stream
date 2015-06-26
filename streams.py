import tweepy
import json
import time
from datetime import datetime
from collections import Counter
from threading import Timer

consumer_key = 'U8gXzQYoQYNf2ghJ5hA9hIayA'
consumer_secret = 'nuJGk0OArFUCpN48kInSOXO9zTWo4bBmJt8ZO5qZyCreFTQwdv'
access_token = '551108705-WisOnqL21cTgggfXnrJjSvJRznPaBXtnn4SDU5yt'
access_token_secret = 'XcgqlS3NrmXdCTbfgroGut382gLFcYxXtC98c8vQZ51sW'

dict = {}
time_then = datetime.now()
total_links = 0
domains = []
unique_words = []

class StdOutListener(tweepy.StreamListener):

   def on_data(self, data):
      
      global time_then
      
      # loading the json data into 'decoded' variable
      decoded = json.loads(data)
      
      if not decoded.get('user'):
         return True

      time_now = datetime.now()
      
      user = str(decoded['user']['screen_name'])
      text = str(decoded['text'].encode('ascii','ignore'))
      urls = decoded['entities']['urls']
      
      #print '@%s: %s' % (user, text)
      #print ''
      
      url_exp_list = []
      
      # all words in the tweet text
      text_words = [word.lower() for word in text.split() if not word.startswith(('@','RT','http'))]
      
      # getting common words by comaparing with already given words list in 'words.txt'
      common_words = []
      for word in text_words:      
         with open('words.txt') as f:
            for line in f:
               if word in line:
                  common_words.append(word)
                  break
      
      # removing the common words
      words = [w for w in text_words if w not in common_words]

      for url in urls:
         url_exp = self.expander(url['expanded_url'])
         url_exp_list.append(url_exp)
      
      #update the user details if already exists or create new dictionary item 
      try:
         dict[user][0] += 1
         dict[user][1] = time_now
         if url_exp_list :
            for u in url_exp_list:
               dict[user][2].append(u)
         if words :
            for word in words:
               dict[user][3].append(word)
      
      except KeyError:
         dict[user] = [1,time_now,url_exp_list,words]

      except:
         print "not possible"

      return True

   
   def on_error(self, status):
      print status
      
   
   # function to get the domain names by stripping the unncessary data in the url
   def expander(self,url):
      parts = url.split('//',1)
      if parts[1].startswith('www'):
         parts[1] = parts[1].split('www.',1)[1]
      return parts[1].split('/',1)[0]

if __name__ == '__main__':
   try:
      word = raw_input("Enter the word you want to search : ")
      time_then = datetime.now()

      l = StdOutListener()
      auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
      auth.set_access_token(access_token, access_token_secret)

      print "\nShowing all new tweets for '" + word + "'\n"   
      
      threads = []

      # Separate thread to print the data every 60 seconds
      def print_every_min():
         try:
            timer = Timer(60,print_every_min)
            timer.daemon = True
            timer.start()
            threads.append(timer)

            global total_links
            global domains
            global unique_words
            
            ti_now = datetime.now()
            for entry in dict.keys():
               diff = divmod((ti_now - (dict[entry][1])).total_seconds(),60)
               td = (diff[0]*60)+ diff[1]
               #print td
               if td <= 300:
                  print entry, dict[entry][0]
                  total_links += len(dict[entry][2])
                  for u in dict[entry][2]:
                     domains.append(u)
                  for w in dict[entry][3]:
                     unique_words.append(w)

               else:
                  del dict[entry]

            print "\n"
            print "total number of links posted by the same users in the last 5 minutes is : {0}".format(total_links)
            print "\n"
            print "Top 10 domains are : {0}".format([str(name) for name,frequency in Counter(domains).most_common(10)])
            print "\n"
            print "Total number of unique words in the last 5 minutes is : {0} ".format(len(set(unique_words)))

            print "\n"
            print "Top 10 most common words are : {0}".format([str(word) for word,frequency in Counter(unique_words).most_common(10)])

            print "\nNext data will be displayed in a minute\n"
            total_links = 0
            domains = []
            unique_words = []
                  
         except TypeError:
            print "\n\n **** Bye **** \n\n"
         
      print_every_min()
      while True:
         try:   
            stream = tweepy.Stream(auth, l)
            stream.filter(track=[word])

         except KeyboardInterrupt:
            break
         
         except :
            print "Reconnecting..."
            time.sleep(2)
         
   except KeyboardInterrupt:
         
         for thread in threads:
            print thread

         stream.disconnect()
         print "\n\n*** Bye ***\n\n"

