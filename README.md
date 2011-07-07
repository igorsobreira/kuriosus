Kuriosus
========

You probably read a lot of documents online (articles, pdfs, blog posts, etc) every 
day, just like me. Kuriosus helps to remember those interesting ones and keep track
of a "To Read" list, right there in your g-talk.

Kuriosus works as a g-talk bot, just add the contact and start talking to it.

Example:

  me: read http://igorsobreira.com/blog/2011/2/6/adding-methods-dynamically-in-python/ Adding methods dynamically in python
  me: read
    ... show all your read documents from today ...
  me: read yesterday
    ... show all your read documents from yesterday ...

  me: toread http://igorsobreira.com/blog/2011/2/6/adding-methods-dynamically-in-python/

  me: unread http://igorsobreira.com/blog/2011/2/6/adding-methods-dynamically-in-python/

Kuriosus in under development. At the moment you can run it yourself, soon I'll provide
a public g-talk contact that you can add.

Installing
----------

Your need a MongoDB server running.

  $ pip install -r requirements.txt
  $ cp kuriosus/settings.py.EXAMPLE kuriosus/settings.py

create a g-talk account (@gmail.com or whatever) and fill the settings

  $ scripts/start

To run tests:

  $ scripts/runtests