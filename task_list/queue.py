from psycopg2 import connect
from pq import PQ


conn = connect('host={host} dbname={dbname} user={user}'.format(host='localhost', dbname='caressa_django', user='cuneyt'))
pq = PQ(conn, table='alexa_conversation_queue')


def get_alexa_user_communication_queue(alexa_user_id):
    return pq['alexa_u_{}/pickle'.format(alexa_user_id)]
