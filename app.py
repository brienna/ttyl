
from flask import Flask, render_template, request
import sqlite3, pandas as pd, json, datetime

CHAT_DB_PATH = '/Users/Brienna/Library/Messages/chat.db'

we_texted_a_lot = Flask(__name__)



@we_texted_a_lot.route('/')
def show_handles():
    # Connect to chat.db
    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()

    # Get handles from db and show to user
    cmd1 = 'SELECT ROWID, id, service FROM handle'
    c.execute(cmd1)
    deleted_msg = pd.DataFrame(c.fetchall(), columns=['ROWID', 'id', 'service']).sort_values(by='ROWID').set_index('ROWID')
    return render_template('view.html',tables=[deleted_msg.to_html(classes="handles")])



@we_texted_a_lot.route('/get_messages', methods=['POST'])
def get_messages():
    # Connect to chat.db
    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()

    # Get handle ids that user selected
    handles = json.loads(request.form['selected_handles'])

    # Extract handle ids into WHERE clause
    where_specs = ""
    for idx, val in enumerate(handles):
        where_specs += "handle_id=" + val
        if idx != len(handles)-1:
            where_specs += " OR "
    
    # Query chat.db for messages that belong to these handle ids
    cmd2 =  """SELECT ROWID, text, is_from_me, \
        datetime(date + strftime(\'%s\',\'2001-01-01\'), \'unixepoch\') as date_utc \
        FROM message WHERE """ + where_specs
    c.execute(cmd2)
    df_msg = pd.DataFrame(c.fetchall(), columns=['id', 'text', 'is_from_me', 'time']).sort_values(by='time')

    # Convert messages' datetime into something useable
    df_msg['time'] = [datetime.datetime.strptime(str(t), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=-4) for t in df_msg['time']]
    df_msg['new_date'] = [d.date() for d in df_msg['time']]
    df_msg['new_time'] = [d.time() for d in df_msg['time']]
    df_msg['new_hours'] = [d.hour for d in df_msg['time']]

    # Get dates of conversation duration
    duration = get_conversation_length(df_msg)

    return render_template('result.html', duration=duration)


# Functions

def get_conversation_length(df_msg):
    start = df_msg['new_date'].iloc[0]
    start = start.strftime('%m.%d.%Y')
    end = df_msg['new_date'].iloc[-1]
    end = end.strftime('%m.%d.%Y')
    return [start, end]


if __name__ == '__main__':
    we_texted_a_lot.run(debug=True)





