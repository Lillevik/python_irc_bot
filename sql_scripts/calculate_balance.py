from sqlite3 import connect

print("Starting...")
server_query = "SELECT id FROM Server;"

user_query = "SELECT User.id, User.nick FROM User " \
             "JOIN Server ON Server.id = ?";

graph_query = "SELECT Graph_data.user_id, User.id, Graph_data.streak " \
              "FROM Graph_data " \
              "JOIN User on User.id = Graph_data.user_id " \
              "WHERE Graph_data.server_id = ? AND Graph_data.user_id = ?"

update_query = "UPDATE Score SET cash = ? WHERE user_id = ? and server_id = ?;"

conn = connect("../leet.db")
cursor = conn.cursor()

server_results = cursor.execute(server_query).fetchall()

for server in server_results:
    user_results = cursor.execute(user_query, server).fetchall()
    results = []
    for user in user_results:
        graph_results = cursor.execute(graph_query, (server[0], user[0])).fetchall()
        cash = 0
        for day in graph_results:
            streak = day[2]
            if streak > 0:
                if streak > 10:
                    streak = 10
                cash += streak * 10
        cursor.execute(update_query, (cash, user[0], server[0]))
        conn.commit()
print("Done.")
