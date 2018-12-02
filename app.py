
from flask import Flask, render_template, request
import sqlite3, pandas as pd, json

we_texted_a_lot = Flask(__name__)


@we_texted_a_lot.route('/')
def show_handles():
    # Connect to chat.db
    conn = sqlite3.connect('/Users/Brienna/Library/Messages/chat.db')
    c = conn.cursor()

    # Show handles
    print(c.execute('select * from handle').description)
    cmd1 = 'SELECT ROWID, id, service FROM handle'
    c.execute(cmd1)
    deleted_msg = pd.DataFrame(c.fetchall(), columns=['ROWID', 'id', 'service']).sort_values(by='ROWID').set_index('ROWID')
    return render_template('view.html',tables=[deleted_msg.to_html(classes="handles")])

@we_texted_a_lot.route('/get_messages', methods=['POST'])
def get_messages():
    conn = sqlite3.connect('/Users/Brienna/Library/Messages/chat.db')
    c = conn.cursor()

    # Get handles from form
    handles = json.loads(request.form['selected_handles'])
    # Extract ids into where command
    where_specs = ""
    for idx, val in enumerate(handles):
        where_specs += "handle_id=" + val
        if idx != len(handles)-1:
            where_specs += " OR "
    
    cmd2 =  """SELECT ROWID, text, is_from_me, \
        datetime(date + strftime(\'%s\',\'2001-01-01\'), \'unixepoch\') as date_utc \
        FROM message WHERE """ + where_specs
    c.execute(cmd2)
    df_msg = pd.DataFrame(c.fetchall(), columns=['id', 'text', 'is_from_me', 'time']).sort_values(by='time')

if __name__ == '__main__':
    we_texted_a_lot.run(debug=True)
