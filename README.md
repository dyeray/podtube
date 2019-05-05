# podtube

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/dyeray/podtube)

Web application that creates a feed subscribable by a podcatcher from services that don't support feeds. Services currently supported:

* Youtube Channels
* iVoox Originals

Easy to deploy to App Engine Flexible Environment or Heroku. Just make sure you set environment variable youtube_developer_key on your server.

Subscribe to url [yourdomain]/?c=[channel-id]&s=[service-name] on your podcatcher to get the videos from your favourite channel.
