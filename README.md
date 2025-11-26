# download plex posters
python script that helps you automatically download plex movie posters. (tested on python 3.8 so should work on anything basically)
alternative to 2miles' plex poster downloader to make it even easier

To get your plex token:
1. open plex in browser
2. click f12 for developer tools
3. click network on developer tools tab, then on plex click the movies tab then the recommended tab
4. on developer tools tab click on the get requests and under headers, find X-Plex-Token then you will find your plex token there to paste into the python script

For library id:
1. open plex in browser
2. click library
3. look at the url in the browser for ?source=X&pivot=library where X is the number for the source, usually 1.
4. replace it in the python script
