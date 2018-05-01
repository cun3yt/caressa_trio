import pusher
import os

pusher_client = pusher.Pusher(
  app_id=os.environ.get('PUSHER_APP_ID'),
  key=os.environ.get('PUSHER_KEY'),
  secret=os.environ.get('PUSHER_SECRET'),
  cluster=os.environ.get('PUSHER_CLUSTER'),
  ssl=True
)


def run():
    print("pushing to pusher!")
    pusher_client.trigger('feeds', 'new-feed',
                          {
                              'feeds': [
                                  {
                                      'value': 'zooo',
                                  },
                                  {
                                      'value': 'moo',
                                  },
                                  {
                                      'value': 'boo',
                                  },
                              ]
                          })
