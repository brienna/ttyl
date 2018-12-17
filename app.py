
from flask import Flask, render_template, request
import sqlite3, pandas as pd, json, datetime, matplotlib.pyplot as plt, math
import matplotlib.patches as mpatches

CHAT_DB_PATH = '/Users/Brienna/Library/Messages/chat.db'
# IMAGES
SPIDER_PLOT_PATH = '/Users/Brienna/Documents/GitHub repositories/we-text-a-lot/static/img/spider_plot.png'

we_texted_a_lot = Flask(__name__)



@we_texted_a_lot.route('/')
def show_handles():
    # Connect to chat.db
    conn = sqlite3.connect(CHAT_DB_PATH)
    c = conn.cursor()

    # Get handles from db and show to user
    cmd1 = 'SELECT ROWID, id, service FROM handle'
    c.execute(cmd1)
    deleted_msg = pd.DataFrame(c.fetchall(), columns=['ROWID', 'id', 'service']).sort_values(by='id').rename(columns={"ROWID": "ID", "id": "CONTACT", "service": "SERVICE"})
    return render_template('view.html',tables=[deleted_msg.to_html(classes="handles table table-dark", index=False)])



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
    duration = get_duration(df_msg)
    # Get total number of messages sent
    num_messages = get_num_messages(df_msg)
    # Get most active day and activity on that day
    most_active_day = get_most_active_day(df_msg)
    # Show spider plot of average day activity
    get_spider_plot(df_msg)

    return render_template('result.html', 
        duration=duration, 
        num_messages=num_messages,
        most_active_day=most_active_day,
        spider_plot_url = '/static/img/spider_plot.png') # change relative/dir paths later


# Functions

def get_duration(df_msg):
    '''
    Gets the time duration of the conversation.
    Returns [start date, end date]
    '''
    start = df_msg['new_date'].iloc[0]
    end = df_msg['new_date'].iloc[-1]
    return [start.strftime('%m.%d.%Y'), end.strftime('%m.%d.%Y')]


def get_num_messages(df_msg):
    '''
    Gets the number of messages sent in total, by me, by them.
    Returns [total, me, other person]
    '''
    total = len(df_msg)
    by_me = len(df_msg[df_msg['is_from_me'] == 1])
    by_them = total - by_me
    return [str(total), str(by_me), str(by_them)]

def get_most_active_day(df_msg):
    '''
    Gets the date with the most text messages.
    Returns [date, total number of messages, number of messages from me, number of messages from them]
    '''
    # LATER: Account for more than 1 day in the mode
    day = df_msg['new_date'].mode()[0]
    df_temp = df_msg[df_msg['new_date'] == day]
    num_msgs = len(df_temp)
    num_msgs_me = len(df_temp[df_temp['is_from_me'] == 1])
    num_msgs_them = num_msgs - num_msgs_me
    return [day.strftime('%m.%d.%Y'), num_msgs, num_msgs_me, num_msgs_them]

def get_spider_plot(df_msg):
    # Format data frames
    df_24hrs_me = df_msg[df_msg['is_from_me'] == 1]['new_hours']
    df_24hrs_them = df_msg[df_msg['is_from_me'] == 0]['new_hours']
    values_me = df_24hrs_me.value_counts().sort_index().values.flatten().tolist() # IMPORTANT TO SORT HOURS
    values_them = df_24hrs_them.value_counts().sort_index().values.flatten().tolist() # IMPORTANT TO SORT HOURS

    # We need to repeat the first value to close the circular graph:
    values_me += values_me[:1]
    values_them += values_them[:1]

    # Get number of variables
    categories = set(list(df_msg['new_hours'])[1:]) # set() reduces to distinct values
    N = len(categories)

    # Set angle of each axis in the plot (again repeating first value to close the circular graph)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    # Initialize spider plot
    ax = plt.subplot(111, polar=True)
    ax.set_facecolor((38/255, 38/255, 38/255)) # divide rgb value by 255

    ## If you want the first axis to be on top
    ax.set_theta_offset(math.pi/2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels 
    plt.xticks(angles[:-1], categories, color='grey', size=8);

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks([1000,2000,3000,4000,5000,6000], ["1k", "2k", "3k","4k","5k","6k"], color='grey', size=8)
    plt.ylim(0,max(values_me))

    ## ----------- Plot Individual 1 :: me
    ax.plot(angles, values_me, linewidth=1, linestyle='solid')
    ax.fill(angles, values_me, color=(136/255, 204/255, 92/255), alpha=0.9);
     
    ## ----------- Plot Individual 2 :: himher
    ax.plot(angles, values_them, linewidth=1, linestyle='solid')
    ax.fill(angles, values_them, color=(222/255, 97/255, 75/255), alpha=0.1)

    red_patch = mpatches.Patch(color=(222/255, 97/255, 75/255), label='Him',alpha=0.4)
    blue_patch = mpatches.Patch(color=(255/255, 254/255, 123/255), label='Me',alpha=0.4)
    plt.legend(handles=[red_patch, blue_patch],loc='upper right', bbox_to_anchor=(0.1,0.1))
    plt.savefig(SPIDER_PLOT_PATH)

if __name__ == '__main__':
    we_texted_a_lot.run(debug=True)





