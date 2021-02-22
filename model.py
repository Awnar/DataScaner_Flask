from datetime import datetime

from sqlalchemy import ForeignKey, event, DDL

from api.common import validity_deltatime

projektDB = True


def SQLClass(db):
    class Logs(db.Model):
        ID = db.Column('ID', db.Integer, primary_key=True)
        user_id = db.Column('User ID', db.Integer, ForeignKey("users.ID"), nullable=False)
        tab = db.Column('Tabela', db.Text, nullable=False)
        comment = db.Column("comment", db.Text)
        time = db.Column('Time', db.DateTime)

        def __init__(self, user_id, tab, comment):
            self.user_id = user_id
            self.tab = tab
            self.comment = comment
            self.time = datetime.now()

    class Users(db.Model):
        ID = db.Column('ID', db.Integer, primary_key=True)
        name = db.Column('Name', db.VARCHAR(100), nullable=False, unique=True)
        password = db.Column('Password', db.VARCHAR(100), nullable=False)

        def __init__(self, name, password):
            self.name = name
            self.password = password

    class Token(db.Model):
        token = db.Column('Token', db.VARCHAR(200), primary_key=True)
        user_id = db.Column('User ID', db.Integer, ForeignKey("users.ID"), nullable=False)
        login_time = db.Column('Login Time', db.DateTime)
        validity_time = db.Column('Validity Time', db.DateTime)
        meta = db.Column("meta", db.JSON)

        def __init__(self, token, user_id, validity_time, login_time, meta):
            self.token = token
            self.user_id = user_id
            self.login_time = login_time
            self.validity_time = validity_time
            self.meta = meta

    class Data(db.Model):
        id = db.Column('ID', db.Integer, primary_key=True)
        user_id = db.Column('User ID', db.Integer, ForeignKey("users.ID"), nullable=False)
        module_name = db.Column('mod', db.Text, nullable=False)
        in_blob = db.Column('input', db.BLOB)
        in_typ = db.Column("in_type", db.Text)
        out_blob = db.Column('output', db.BLOB)
        out_typ = db.Column("out_type", db.Text)
        create = db.Column('Create Time', db.DateTime)
        update = db.Column('Update Time', db.DateTime)

        def __init__(self, module_name, user_id, in_blob, in_typ, out_blob, out_typ, create):
            self.user_id = user_id
            self.module_name = module_name
            self.in_blob = in_blob
            self.in_typ = in_typ
            self.out_blob = out_blob
            self.out_typ = out_typ
            self.create = self.update = create

        def toJSON(self):
            return {"server_ID": self.id,
                    "user_id": self.user_id,
                    "module_name": self.module_name,
                    "in_blob": self.in_blob.decode() if self.in_blob is not None else None,
                    "in_blob_type": self.in_typ,
                    "out_blob": self.out_blob.decode() if self.out_blob is not None else None,
                    "out_blob_type": self.out_typ,
                    "create": self.create,
                    "update": self.update}

    if (projektDB):
        log_token_insert = DDL("""
        CREATE TRIGGER `log_token_insert` AFTER INSERT ON `token`
        FOR EACH ROW INSERT INTO `logs` (`User ID`, `Tabela`, `comment`, `Time`)
        VALUES (NEW.`User ID`, "Token", CONCAT("Dodano token"), CURRENT_TIMESTAMP)
        """)
        event.listen(Token.__table__, 'after_create', log_token_insert, propagate=True)

        log_data_insert = DDL("""
        CREATE TRIGGER `log_data_insert` AFTER INSERT ON `data`
        FOR EACH ROW INSERT INTO `logs` (`User ID`, `Tabela`, `comment`, `Time`)
        VALUES (NEW.`User ID`, "Data", CONCAT("Dodano dane ",new.ID), CURRENT_TIMESTAMP)
        """)
        event.listen(Data.__table__, 'after_create', log_data_insert, propagate=True)

        log_Users_insert = DDL("""
        CREATE TRIGGER `log_users_insert` AFTER INSERT ON `users`
        FOR EACH ROW INSERT INTO `logs` (`User ID`, `Tabela`, `comment`, `Time`)
        VALUES (new.ID, "Users", CONCAT("Dodano użytkownika ",new.Name), CURRENT_TIMESTAMP)
        """)
        event.listen(Users.__table__, 'after_create', log_Users_insert, propagate=True)

        update_token = DDL("""
            CREATE PROCEDURE `updateToken`(IN `tok` VARCHAR(200), IN `validity_deltatime` TEXT)
                MODIFIES SQL DATA
            UPDATE token SET `Validity Time` = ADDTIME(CURRENT_TIMESTAMP, validity_deltatime) WHERE `Token` = tok;
        """)
        event.listen(Token.__table__, 'after_create', update_token, propagate=True)

        update_token = DDL("""
             CREATE FUNCTION `login`(`name` VARCHAR(100), `pass` VARCHAR(100), `token` VARCHAR(200), `validity_deltatime` TEXT, `meta` JSON) RETURNS int(11)
                MODIFIES SQL DATA
             BEGIN
                DECLARE idd INT;
                SELECT ID INTO idd FROM `users` WHERE `Name` = name AND `Password`= pass LIMIT 1;
                IF idd>0 THEN
                    INSERT INTO `token` (`Token`, `User ID`, `Login Time`, `Validity Time`, `meta`) VALUES (token, idd, CURRENT_TIMESTAMP, ADDTIME(CURRENT_TIMESTAMP, validity_deltatime), meta);
                END IF;
				return idd;
            END
        """)
        event.listen(Token.__table__, 'after_create', update_token, propagate=True)

    else:
        @event.listens_for(Token, "after_insert")
        def logout_old_token(mapper, connection, token):
            log = Logs(token.user_id, "Token", "Dodano token")
            db.session.add(log)
            db.session.commit()

        @event.listens_for(Data, "after_insert")
        def logout_old_token(mapper, connection, data):
            log = Logs(data.user_id, "Data", "Dodano dane " + data.id)
            db.session.add(log)
            db.session.commit()

        @event.listens_for(Users, "after_insert")
        def logout_old_token(mapper, connection, user):
            log = Logs(user.id, "Data", "Dodano użytkownika " + user.name)
            db.session.add(log)
            db.session.commit()

    # @event.listens_for(Token, "before_insert")
    # def logout_old_token(mapper, connection, token):
    #   Token.query.filter_by(user_id=token.user_id).filter(Token.validity_time > token.login_time).update({"validity_time": (token.login_time)})

    class exeClass:
        @staticmethod
        def getToken(token):
            return Token.query.filter_by(token=token).first()

        @staticmethod
        def setToken(token, user_id, meta):
            var = Token(token, user_id, datetime.now() + validity_deltatime, datetime.now(), meta)
            db.session.add(var)
            db.session.commit()

        @staticmethod
        def updateToken(token):
            if (projektDB):
                # CREATE PROCEDURE `updateToken`(IN `token` VARCHAR(200), IN `validity_deltatime` DATETIME)
                db.session.execute("CALL updateToken(:p1, :p2)", {'p1': token, 'p2': validity_deltatime})
            else:
                var = Token.query.filter_by(token=token).first()
                var.validity_time = datetime.now() + validity_deltatime
                db.session.commit()

        @staticmethod
        def Logout(token):
            var = Token.query.filter_by(token=token).first()
            var.validity_time = datetime.now()
            db.session.commit()

        @staticmethod
        def checkUser(name):
            return Users.query.filter_by(name=name).all()

        @staticmethod
        def Login(name, password, token, meta):
            if (projektDB):
                # CREATE FUNCTION `login`(`name` VARCHAR(100), `pass` VARCHAR(100), `token` VARCHAR(200), `validity_deltatime` DATETIME, `meta` JSON) RETURNS int(11)
                return db.session.execute("SELECT login (:p1, :p2, :p3, :p4, :p5)",
                                          {'p1': name, 'p2': password, 'p3': token, 'p4': validity_deltatime,
                                           'p5': str(meta).replace("\'", "\"")}).fetchone()[0]
            else:
                id = Users.query.filter_by(name=name, password=password).first()
                if id is not None:
                    exeClass.setToken(token, id.ID, meta)
                    return id.ID

        @staticmethod
        def Register(name, password):
            var = Users(name, password)
            db.session.add(var)
            db.session.commit()

        @staticmethod
        def RegisterAndLogin(name, password, token, meta):
            exeClass.Register(name, password)
            return exeClass.Login(name, password, token, meta)

        @staticmethod
        def setData(module_name, user_id, in_blob, in_des, out_blob, out_des, create):
            var = Data(module_name, user_id, in_blob, in_des, out_blob, out_des, create)
            db.session.add(var)
            db.session.commit()

        @staticmethod
        def getData(module_name, id, user_id):
            return Data.query.filter_by(id=id, user_id=user_id, module_name=module_name).first()

        @staticmethod
        def updateData(id, user_id, in_blob, in_des, out_blob, out_des):
            var = Data.query.filter_by(id=id, user_id=user_id).first()
            var.in_blob = in_blob
            var.in_des = in_des
            var.out_blob = out_blob
            var.out_des = out_des
            var.update = datetime.now()
            db.session.commit()

        @staticmethod
        def removeData(id, user_id):
            var = Data.query.filter_by(id=id, user_id=user_id).first()
            db.session.delete(var)
            db.session.commit()

        @staticmethod
        def getAllData(module_name, user_id, lastupdate=None):
            if lastupdate is None:
                return Data.query.filter_by(user_id=user_id, module_name=module_name).all()
            lastupdate = datetime.fromtimestamp(int(lastupdate))
            return Data.query.filter_by(user_id=user_id, module_name=module_name).filter(
                Data.update >= lastupdate).all()

    return exeClass
