from datetime import datetime

from sqlalchemy import ForeignKey

from api.common import validity_deltatime


def SQLClass(db):
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
        validity_time = db.Column('Validity Time', db.DateTime)
        meta = db.Column("meta", db.JSON)

        def __init__(self, token, user_id, validity_time, meta):
            self.token = token
            self.user_id = user_id
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

    class exeClass:
        @staticmethod
        def getToken(token):
            return Token.query.filter_by(token=token).first()

        @staticmethod
        def setToken(token, user_id, meta):
            var = Token(token, user_id, datetime.now() + validity_deltatime, meta)
            db.session.add(var)
            db.session.commit()

        @staticmethod
        def updateToken(token):
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
            return Data.query.filter_by(user_id=user_id, module_name=module_name).filter(Data.update >= lastupdate).all()

    return exeClass
