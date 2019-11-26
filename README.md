# ChatRoom
 "AWAY": away_handler,
            "JOIN": join_handler, //join a channel
            "LIST": list_handler,  //list all channels
            "MOTD": motd_handler, //extra (message of the day)
            "NAMES": names_handler, //list all name of people in a certain channel
            "NICK": nick_handler,   //changes nickname
            "NOTICE": notice_and_privmsg_handler,  //bot doesnt reply if used instead of priv message
            "PART": part_handler, //removed from channels specified
            "PING": ping_handler, //test if user is still there
            "PONG": pong_handler, //reply to ping
            "PRIVMSG": notice_and_privmsg_handler, //private message, then usernames
            "QUIT": quit_handler,  //disconnect from server
            "TOPIC": topic_handler, //changes topic of channel
            "WALLOPS": wallops_handler, //send message to everyone on the server
            "WHO": who_handler,  //returns lists of user which matches ""5
