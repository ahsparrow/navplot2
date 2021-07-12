# NAVPLOT

Generates a PDF NOTAM breifing.

The app can be used standalone via the navplot.py script, or via a Heroku
scheduler to store data in MongoDB Atlas database for use by the ASSelect
app.

## Development

### MongoDB

1. Create a database "notam" with a collection "notams"
2. Add user "navplot"
3. Create a Realm app "Navplot" with function getnotam

        exports = function(name) {
            var collection = context.services.get("mongodb-atlas").db("notam").collection("notams");
            return collection.findOne({ name: name}).then((doc) => {
              return doc;
            });
        };

4. Set API Key authentication for the Realm app
5. Update the ASSelect app with both the App ID and the API Key

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

        heroku config:set MONGODB_PASSWORD=<mongodb_password>

7. Create a Heroku scheduler job to run hourly at 10 minutes past:

        python heroku.py
