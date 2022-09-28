import mysql.connector


class DB(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DB, cls).__new__(cls)
            cls.instance.connection = None
            cls.instance.cursor = None
        return cls.instance

    def connect(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = mysql.connector.connect(
            host='localhost',
            user='RQ',
            passwd='4RQFour'
        )
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection is None:
            return
        self.connection.close()

    def init_database(self):
        self.check()
        self.cursor.execute('DROP DATABASE IF EXISTS Messenger')
        self.cursor.execute('CREATE DATABASE Messenger')

        self.cursor.execute('USE Messenger')
        self.cursor.execute("""
        CREATE TABLE user(
            firstname VARCHAR(255) NOT NULL CHECK (user.firstname <> ''),
            lastname VARCHAR(255) NOT NULL CHECK (user.lastname <> ''),
            phone VARCHAR(11) UNIQUE NOT NULL CHECK (user.phone <> ''),
            email VARCHAR(255) UNIQUE NOT NULL CHECK (user.email <> ''),
            username varchar(255) PRIMARY KEY CHECK (user.username <> ''),
            password varchar(255) NOT NULL CHECK (user.password <> ''),
            security_answer varchar(255) NOT NULL CHECK (user.security_answer <> ''),
            logged_in bit NOT NULL DEFAULT 0,
            CONSTRAINT CHK_phone_format CHECK (LENGTH(phone) = 11 AND phone REGEXP('^[0-9]+$')),
            CONSTRAINT CHK_email_format CHECK (email REGEXP('^[a-zA-Z0-9.!#$%&’*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$')),
            CONSTRAINT CHK_firstname_format CHECK (firstname REGEXP '^[a-zA-Z]+$'),
            CONSTRAINT CHK_lastname_format CHECK (lastname REGEXP '^[a-zA-Z]+$'),
            CONSTRAINT CHK_username_format CHECK (LENGTH(username) >= 5 AND username REGEXP '^[a-zA-Z][a-zA-Z0-9]+$'),
            CONSTRAINT CHK_password_format CHECK (LENGTH(password) >= 5 AND password REGEXP '^[a-zA-Z0-9]+$' AND NOT password REGEXP '^[0-9]+$')
        )""")
        self.cursor.execute("""
        CREATE TABLE friendship(
            user1 VARCHAR(255) NOT NULL,
            user2 VARCHAR(255) NOT NULL,
            FOREIGN KEY (user1) REFERENCES user(username),
            FOREIGN KEY (user2) REFERENCES user(username)
        )""")
        self.cursor.execute("""
        CREATE TABLE blocked(
            user1 VARCHAR(255) NOT NULL,
            user2 VARCHAR(255) NOT NULL,
            FOREIGN KEY (user1) REFERENCES user(username),
            FOREIGN KEY (user2) REFERENCES user(username)
        )""")
        self.cursor.execute("""
        CREATE TABLE friend_request(
                sender VARCHAR(255) NOT NULL,
                receiver VARCHAR(255) NOT NULL,
                FOREIGN KEY (sender) REFERENCES user(username),
                FOREIGN KEY (receiver) REFERENCES user(username)
        )""")
        self.cursor.execute("""
        CREATE FUNCTION isBlocked(user1 VARCHAR(255), user2 VARCHAR(255))
                RETURNS INT
                DETERMINISTIC
                BEGIN
                    DECLARE blocked INT;
                    IF (EXISTS (SELECT * FROM blocked WHERE blocked.user1 = user1 AND blocked.user2 = user2)) THEN
                        RETURN 1;
                    ELSE
                        RETURN 0;
                    END IF;            
                END
        """)
        self.cursor.execute("""
        CREATE TRIGGER check_friend_req_insert BEFORE INSERT ON friend_request
        FOR EACH ROW
        BEGIN
            IF isBlocked(NEW.receiver, NEW.sender) = 1 THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'user is blocked';
            ELSEIF NEW.sender = NEW.receiver THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'cannot request itself';
            ELSEIF EXISTS (SELECT * FROM friendship WHERE user1 = NEW.sender AND user2 = NEW.receiver) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'already friend';
            ELSEIF EXISTS (SELECT * FROM friendship WHERE user2 = NEW.sender AND user1 = NEW.receiver) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'already friend';
            ELSEIF EXISTS (SELECT * FROM friend_request WHERE sender = NEW.sender AND receiver = NEW.receiver) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'already requested';
            END IF;    
        END
        """)
        self.cursor.execute("""
        CREATE TRIGGER check_blocked_insert BEFORE INSERT ON blocked
        FOR EACH ROW
        BEGIN
            IF isBlocked(NEW.user1, NEW.user2) = 1 THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'user is already blocked';
            ELSEIF NEW.user1 = NEW.user2 THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'cannot block itself';
            END IF;
        END
        """)
        self.cursor.execute("""
        CREATE TRIGGER check_friendship BEFORE INSERT ON friendship
        FOR EACH ROW
        BEGIN
            IF EXISTS (SELECT * FROM friend_request WHERE sender = NEW.user1 AND receiver = NEW.user2) THEN
                DELETE FROM friend_request WHERE sender = NEW.user1 AND receiver = NEW.user2;
                DELETE FROM friend_request WHERE sender = NEW.user2 AND receiver = NEW.user1;
            ELSEIF EXISTS (SELECT * FROM friend_request WHERE sender = NEW.user2 AND receiver = NEW.user1) THEN
                DELETE FROM friend_request WHERE sender = NEW.user2 AND receiver = NEW.user1;
            ELSE
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'there is no pending request';
            END IF;
        END
        """)
        self.cursor.execute("""
       CREATE TABLE message(
           id INTEGER PRIMARY KEY AUTO_INCREMENT ,
           sender VARCHAR(255) NOT NULL CHECK (message.sender <> ''),
           receiver VARCHAR(255) NOT NULL CHECK (message.receiver <> ''),
           text VARCHAR(255) NOT NULL CHECK (message.text <> ''),
           time DATETIME NOT NULL,
           liked BIT NOT NULL DEFAULT 0,
           seen BIT NOT NULL DEFAULT 0
       )""")
        self.cursor.execute("""
        CREATE TRIGGER insert_message BEFORE INSERT ON message
        FOR EACH ROW  
        BEGIN  
            IF NOT EXISTS (SELECT * FROM user WHERE user.username = NEW.sender) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'invalid sender';
            ELSEIF NOT EXISTS (SELECT * FROM user WHERE user.username = NEW.receiver) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'invalid receiver';
            END IF;
        END
        """)
        self.cursor.execute("""
        CREATE TABLE user_status (
            username varchar(255) UNIQUE,
            time DATETIME DEFAULT NULL,
            pass_tries INT DEFAULT 0,
            forget_tries INT DEFAULT 0,
            FOREIGN KEY (username) REFERENCES user(username)
        )""")
        self.cursor.execute("""
        CREATE TABLE log (
            id INT PRIMARY KEY AUTO_INCREMENT,
            time DATETIME DEFAULT NULL,
            text VARCHAR(255) NOT NULL
        )""")
        self.cursor.execute("""
        CREATE TRIGGER check_message BEFORE INSERT ON message
        FOR EACH ROW
        BEGIN
            IF isBlocked(NEW.receiver, NEW.sender) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'user is blocked';
            ELSEIF NOT EXISTS (SELECT * FROM friendship WHERE (user1 = NEW.sender AND user2 = NEW.receiver) OR (user2 = NEW.sender AND user1 = NEW.receiver)) THEN
                SIGNAL SQLSTATE '12345' SET MESSAGE_TEXT = 'user is not friend';
            END IF;
        END
        """)
        self.cursor.execute("""
        CREATE PROCEDURE login (IN username VARCHAR(255), IN password VARCHAR(255), OUT logged_in INT)  
        BEGIN  
            DECLARE ban_time DATETIME;
            DECLARE failed INT;
            SELECT time INTO ban_time FROM user_status WHERE user_status.username = username;
            IF ban_time > NOW() THEN
                SELECT 0 INTO logged_in;
            ELSEIF EXISTS (SELECT * FROM user WHERE (user.username = username AND user.password = password AND user.logged_in = 0)) THEN
                UPDATE user SET user.logged_in = 1 WHERE user.username = username;
                UPDATE user_status SET user_status.pass_tries = 0 WHERE user_status.username = username;
                INSERT INTO log (time, text) VALUES (NOW(), CONCAT(username, " logged in!"));
                SELECT 1 INTO logged_in;
            ELSE
                SELECT pass_tries INTO failed FROM user_status WHERE user_status.username = username;
                INSERT INTO log (time, text) VALUES (NOW(), CONCAT(username, " used a wrong password!"));
                IF failed = 2 THEN
                    UPDATE user_status SET user_status.time = (NOW() + INTERVAL 1 DAY) WHERE user_status.username = username;
                    INSERT INTO log (time, text) VALUES (NOW(), CONCAT(username, " banned for a day!"));
                END IF;
                UPDATE user_status SET user_status.pass_tries = failed + 1 WHERE user_status.username = username;
                SELECT 0 INTO logged_in;
            END IF;  
        END
        """)
        self.cursor.execute("""
        CREATE PROCEDURE security_answer (IN username VARCHAR(255), IN answer VARCHAR(255), OUT pass VARCHAR(255))  
        BEGIN
            DECLARE failed INT;
            SELECT forget_tries INTO failed FROM user_status WHERE user_status.username = username;
            IF failed = 5 THEN
                 SELECT NULL INTO pass;
            ELSEIF EXISTS (SELECT * FROM user WHERE (user.username = username AND user.security_answer = answer)) THEN
                SELECT password INTO pass FROM user WHERE user.username = username;
                UPDATE user_status SET user_status.forget_tries = 0 WHERE user_status.username = username;
            ELSE
                UPDATE user_status SET user_status.forget_tries = failed + 1 WHERE user_status.username = username;
                SELECT NULL INTO pass;
            END IF;  
        END
        """)
        self.cursor.execute("""
        CREATE PROCEDURE pass_recovery (IN user VARCHAR(255), IN email VARCHAR(255), IN phone VARCHAR(11), OUT pass VARCHAR(255))  
        BEGIN  
            IF EXISTS (SELECT * FROM user WHERE (user.username = username AND user.phone = phone AND user.email = email)) THEN
                SELECT password INTO pass FROM user WHERE user.username = username;
                UPDATE user_status SET user_status.forget_tries = 0 WHERE user_status.username = username;
            ELSE
                SELECT NULL INTO pass;
            END IF;  
        END
        """)
        self.cursor.execute("""
        CREATE TRIGGER add_status AFTER INSERT ON user
        FOR EACH ROW  
        BEGIN  
          INSERT INTO user_status (username) VALUES (NEW.username);
        END
        """)
        self.cursor.execute("""
        CREATE TRIGGER delete_user BEFORE DELETE ON user
        FOR EACH ROW  
        BEGIN  
            DELETE FROM user_status WHERE user_status.username = OLD.username;
            DELETE FROM friendship WHERE (friendship.user1 = OLD.username OR friendship.user2 = OLD.username);
            DELETE FROM message WHERE (message.receiver = OLD.username);
            UPDATE message SET message.sender = "deleted" WHERE message.sender = OLD.username;
        END
        """)

        self.fakeData()
        self.connection.commit()

    def fakeData(self):
        query = "INSERT INTO user (firstname, lastname, phone, email, username, password, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = [
            ("fname", "lname", "00000000006", "a@email.com", "user1", "user1", "ans1"),
            ("fname", "lname", "00000000001", "aa@email.com", "user2", "user2", "ans1"),
            ("fname", "lname", "00000000002", "aaa@email.com", "user3", "user3", "ans1"),
            ("fname", "lname", "00000000003", "aaaa@email.com", "user4", "user4", "ans1"),
            ("fname", "lname", "00000000004", "aaaaa@email.com", "user5", "user5", "ans1"),
            ("fname", "lname", "00000000005", "aaaaaa@email.com", "user6", "user6", "ans1")
        ]
        self.cursor.executemany(query, values)

    def check(self):
        if self.cursor is not None:
            self.connection.close()
        self.connect()
        self.cursor.execute("USE Messenger")

    def register(self, values):
        self.check()
        query = "INSERT INTO user (firstname, lastname, phone, email, username, password, security_answer) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (values['firstname'], values['lastname'], values['phone'], values['email'], values['username'],
                  values['password'], values['security'])
        self.cursor.execute(query, values)
        self.connection.commit()

    def login(self, values):
        self.check()
        values = (values['username'], values['password'])
        self.cursor.execute(f"CALL login(\"{values[0]}\", \"{values[1]}\", @V)")
        self.cursor.execute("SELECT @V")
        result = self.cursor.fetchall()
        self.connection.commit()
        if result[0][0] == 0:
            return None

        return values[0]

    def friends(self, user):
        self.check()
        query = f"SELECT * FROM friendship WHERE (user1 = \"{user}\" OR user2 = \"{user}\")"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def is_blocked_by(self, user1, user2):
        self.check()
        query = f"SELECT * FROM blocked WHERE user1 = \"{user1}\" AND user2 = \"{user2}\""
        self.cursor.execute(query)
        return len(self.cursor.fetchall()) > 0

    def remove_friend(self, user, friend):
        self.check()
        query = f"DELETE FROM friendship WHERE user1 = \"{user}\" AND user2 = \"{friend}\""
        self.cursor.execute(query)
        query = f"DELETE FROM friendship WHERE user1 = \"{friend}\" AND user2 = \"{user}\""
        self.cursor.execute(query)
        self.connection.commit()

    def search_users(self, str):
        self.check()
        query = f"SELECT username FROM user WHERE username LIKE \"%{str}%\""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def send_request(self, sender, receiver):
        self.check()
        query = f"INSERT INTO friend_request (sender, receiver) VALUES (%s, %s)"
        values = (sender, receiver)
        self.cursor.execute(query, values)
        self.connection.commit()

    def block(self, user1, user2):
        self.check()
        query = f"INSERT INTO blocked (user1, user2) VALUES (%s, %s)"
        values = (user1, user2)
        self.cursor.execute(query, values)
        self.connection.commit()

    def requests(self, user):
        self.check()
        query = f"SELECT sender FROM friend_request WHERE  receiver = \"{user}\""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def accept_request(self, user1, user2):
        self.check()
        query = f"INSERT INTO friendship (user1, user2) VALUES (%s, %s)"
        values = (user1, user2)
        self.cursor.execute(query, values)
        self.connection.commit()

    def logout(self, user):
        self.check()
        query = f"UPDATE user SET logged_in = 0 WHERE username = \"{user}\""
        self.cursor.execute(query)
        self.connection.commit()

    def blocked_users(self, user):
        self.check()
        query = f"SELECT user2 FROM blocked WHERE user1 = \"{user}\""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def unblock(self, user1, user2):
        self.check()
        query = f"DELETE FROM blocked WHERE user1 = \"{user1}\" AND user2 = \"{user2}\""
        self.cursor.execute(query)
        self.connection.commit()

    def send_msg(self, sender, receiver, text, time):
        self.check()
        query = f"INSERT INTO message (sender, receiver, text, time) VALUES (%s, %s, %s, %s)"
        values = (sender, receiver, text, time)
        self.cursor.execute(query, values)
        self.connection.commit()

    def messages(self, user):
        self.check()
        query = f"SELECT * FROM message WHERE receiver = \"{user}\" ORDER BY message.time desc"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def like(self, id):
        self.check()
        query = f"UPDATE message SET liked = 1 WHERE id = \"{id}\""
        self.cursor.execute(query)
        self.connection.commit()

    def seen(self, id):
        self.check()
        query = f"UPDATE message SET seen = 1 WHERE id = \"{id}\""
        self.cursor.execute(query)
        self.connection.commit()

    def pass_recovery(self, user, email, phone):
        self.check()
        self.cursor.execute(f"CALL pass_recovery(\"{user}\", \"{email}\", \"{phone}\", @V)")
        self.cursor.execute("SELECT @V")
        result = self.cursor.fetchall()[0][0]
        self.connection.commit()
        return result

    def security_answer(self, user, answer):
        self.check()
        self.cursor.execute(f"CALL security_answer(\"{user}\", \"{answer}\", @V)")
        self.cursor.execute("SELECT @V")
        result = self.cursor.fetchall()[0][0]
        self.connection.commit()
        return result

    def delete_user(self, user):
        self.check()
        self.cursor.execute(f"DELETE FROM user WHERE username = \"{user}\"")
        self.connection.commit()
