# download plex posters
python script that helps you automatically download plex movie posters. (tested on python 3.8 so should work on anything basically)
alternative to <a href = "https://github.com/2miles/plex-poster-downloader"> 2miles' plex poster downloader</a> to make it super convenient for people who don't want to deal with too much troubleshooting.

How to run:
1. open command prompt (Win+R and typing cmd)
2. drag the python script file onto the command prompt (be sure to configure it with the plex token and library id as stated below first!)
3. click enter and let the poster files download

remember to keep the '' when pasting in the values eg. PLEX_TOKEN = 'pasted_value' 

To get your plex token:
1. open plex in browser
2. click f12 for developer tools
3. click network on developer tools tab, then on plex click the movies tab then the recommended tab
4. on developer tools tab click on the get requests and under headers, find X-Plex-Token then you will find your plex token there to paste into the python script by opening it with notepad and pasting in the values

For library id:
1. open plex in browser
2. click library
3. look at the url in the browser for ?source=X&pivot=library where X is the number for the source, usually 1.
4. replace it in the python script by opening it with notepad and replacing id with the value
