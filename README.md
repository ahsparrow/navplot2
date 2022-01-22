# NAVPLOT

Generates a PDF NOTAM briefing.

The app can be used standalone via the navplot.py script, or via a Heroku
scheduler to store files in Dropbox for use by the ASSelect app.

## Development

### Dropbox

1. Create a Dropbox app
2. Use dropbox/get\_refresh\_token.py to generate the OAuth2 refresh token

### Heroku

1. Install the Heroku CLI app from
https://devcenter.heroku.com/articles/heroku-cli and login to Heroku

        heroku login

2. Create a Heroku app called navplotuk
3. Set remote branch

        heroku git:remote -a navplotuk

4. Push to heroku

        git push heroku master

5. Add the Heroku-Scheduler addon
6. Create config vars:

        heroku config:set DROPBOX_APP_KEY=<Dropbox app key>
        heroku config:set DROPBOX_APP_SECRET=<Dropbox app secret>
        heroku config:set DROPBOX_REFRESH_TOKEN=<OAuth refresh token>

7. Create a Heroku scheduler job to run hourly at 10 minutes past:

        python heroku.py

### Dropbox

3. Generate shared links for the four PDF files

### ASSelect

8. Update the download links in the ASSelect app. The refs should end ...?dl=1
