# python-threading-exemplar

This is a project to do some simple prototyping with some targeted multithreading situations in python.

As I'm relatively new to python, and have rarely had a need in the past to go hardcore multithreaded with other languages (C# etc),
this is really just for me to try out a few things, learn the 'pythonic' ways to do things, but also use slightly different techniques along the way.

The actual problem I'm trying to solve (the reason for doing this), is the following (I'll keep it generic):

* A 3rd party API provides an endpoint, that returns data - potentially a lot of data.
* The API limits output, by providing a pagination facility - supplying a 'next page' token, which you supply in the next request
* The API also allows data to be requested in either json/csv format.  Csv is more convenient/portable for large requests - however the API does not provide pagination on csv responses
* Csv requests 'do' accept 'next page' tokens
* We don't know how many pages will be returned (we know the last page when there's no 'next page' token)

So the need here is to (in the most performant way)...

1. Call the API (json) and get response (we only 'want' the 'next page' token)
2. For each 'page' in the list - call the API to get corresponding (csv) 
3. Return the 'combined' csv, and make sure any errors/threads are neatly handled

# Options

## Daemon Thread

The first example will go eu natural, and utilise standard python threading features.  

This utilises the excellent information here...
https://superfastpython.com/thread-triggered-background-task/

## Celery

The next example will be an excuse to learn about Celery, and figure out if it's useful in this context