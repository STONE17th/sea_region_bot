import psycopg2

import os


class DataBase:
    _instance = None
    _ip_address = os.getenv('IP_ADDRESS')
    _db_name = os.getenv('DB_NAME')
    _user_name = os.getenv('USER_NAME')
    _password = os.getenv('PASSWORD')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def execute(self, sql: str, parameters: tuple = tuple(),
                fetchone=False, fetchall=False, commit=False):
        connection = psycopg2.connect(
            user=self._user_name,
            password=self._password,
            dbname=self._db_name,
            host=self._ip_address,
        )
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)
        if commit:
            connection.commit()
        if fetchone:
            data = cursor.fetchone()
        if fetchall:
            data = cursor.fetchall()
        connection.close()
        return data

    @staticmethod
    def extract_kwargs(sql: str, parameters: dict, _and: bool = True) -> tuple:
        sql += (' AND ' if _and else ', ').join([f'{key} = ?' for key in parameters])
        return sql, tuple(parameters.values())

    def create_tables(self):
        sqls = [
            '''CREATE TABLE IF NOT EXISTS admins(
            admin_tg_id         INTEGER PRIMARY KEY,
            name                CHARACTER VARYING(100),
            phone               CHARACTER VARYING(100),
            email               CHARACTER VARYING(100)
            )''',
            '''CREATE TABLE IF NOT EXISTS cargo_types(
            cargo_type_id       SERIAL PRIMARY KEY,
            type                CHARACTER VARYING(200)
            )''',
            '''CREATE TABLE IF NOT EXISTS drivers(
            driver_tg_id        INTEGER PRIMARY KEY,
            full_name           CHARACTER VARYING(500),
            passport            CHARACTER VARYING(200),
            phone               CHARACTER VARYING(200),
            status              INTEGER DEFAULT 0
            )''',
            '''CREATE TABLE IF NOT EXISTS trucks(
            truck_id            SERIAL PRIMARY KEY,
            driver_tg_id        INTEGER,
            cargo_type_id       INTEGER,
            cargo_weight        INTEGER,
            truck_brand         CHARACTER VARYING(200),
            truck_model         CHARACTER VARYING(200),
            truck_number        CHARACTER VARYING(200),
            FOREIGN KEY (driver_tg_id) REFERENCES drivers (driver_tg_id),
            FOREIGN KEY (cargo_type_id) REFERENCES cargo_types (cargo_type_id)
            )''',
            '''CREATE TABLE IF NOT EXISTS orders(
            order_id            SERIAL PRIMARY KEY,
            description         CHARACTER VARYING(500),
            cargo_weight        INTEGER,
            cargo_type_id       INTEGER,
            phone               INTEGER,
            status              INTEGER,
            FOREIGN KEY (cargo_type_id) REFERENCES cargo_types (cargo_type_id)
            )''',
            '''CREATE TABLE IF NOT EXISTS orders_in_progress(
            entry_id            SERIAL PRIMARY KEY,
            order_id            INTEGER,
            driver_tg_id        INTEGER,
            date_start          TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (driver_tg_id) REFERENCES drivers (driver_tg_id)
            )''',
            '''CREATE TABLE IF NOT EXISTS finished_orders(
            entry_id            SERIAL PRIMARY KEY,
            order_id            INTEGER,
            driver_tg_id        INTEGER,
            date_finish         TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (order_id),
            FOREIGN KEY (driver_tg_id) REFERENCES drivers (driver_tg_id)
            )''',
        ]
        for sql in sqls:
            self.execute(sql, commit=True)

    @property
    def admins(self) -> tuple:
        sql = 'SELECT admin_tg_id FROM admins'
        response = self.execute(sql, fetchall=True)
        if response:
            return tuple([user_admin[0] for user_admin in response])
        return (None,)

    @property
    def drivers(self) -> tuple:
        sql = 'SELECT driver_tg_id FROM drivers'
        response = self.execute(sql, fetchall=True)
        if response:
            return tuple([user_admin[0] for user_admin in response])
        return (None,)

    def add_admin(self, admin_tg_id: int, email: str, phone: str):
        sql = 'INSERT INTO admins (admin_tg_id, phone, email) VALUES (%s, %s, %s)'
        self.execute(sql, (admin_tg_id, email, phone), commit=True)

    def add_driver(self, driver_tg_id: int, name: str, passport: str, phone: str):
        sql = 'INSERT INTO drivers (driver_tg_id, full_name, passport, phone) VALUES (%s, %s, %s, %s)'
        self.execute(sql, (driver_tg_id, name, passport, phone), commit=True)

    # def add_task(self, user_tg_id: int, year: int, month: int, day: int, time: str, desc: str):
    #     sql = f'INSERT INTO table_{user_tg_id} (year, month, day, time, description) VALUES (%s, %s, %s, %s, %s)'
    #     self.execute(sql, (year, month, day, time, desc), commit=True)
    #
    # def get_day(self, user_tg_id: int, year: int, month: int, day: int):
    #     sql = f'SELECT * FROM table_{user_tg_id} WHERE year=%s AND month=%s AND day=%s'
    #     return self.execute(sql, (year, month, day), fetchall=True)
    #
    # def get_month(self, user_tg_id: int, year: int, month: int):
    #     sql = f'SELECT day FROM table_{user_tg_id} WHERE year=%s AND month=%s'
    #     return self.execute(sql, (year, month), fetchall=True)
    #
    # def del_task(self, user_tg_id: int, task_id: int):
    #     sql = f'DELETE FROM table_{user_tg_id} WHERE task_id=%s'
    #     self.execute(sql, (task_id,), commit=True)
    #
    # def add_scheduler(self, user_tg_id: int, scheduler_tg_id: int, scheduler_title: str):
    #     sql = f'''INSERT INTO table_admins (user_tg_id, scheduler_tg_id, scheduler_title) VALUES
    #         (%s, %s, %s) ON CONFLICT (user_tg_id, scheduler_tg_id) DO NOTHING'''
    #     return self.execute(sql, (user_tg_id, scheduler_tg_id, scheduler_title), commit=True)
    #
    # def load_schedulers(self, user_tg_id: int):
    #     sql = f'SELECT scheduler_tg_id, scheduler_title FROM table_admins WHERE user_tg_id=%s'
    #     return self.execute(sql, (user_tg_id,), fetchall=True)
    #
    # def del_scheduler(self, user_tg_id: int, scheduler_tg_id: int):
    #     sql = f'DELETE FROM table_admins WHERE user_tg_id=%s AND scheduler_tg_id=%s'
    #     self.execute(sql, (user_tg_id, scheduler_tg_id), commit=True)
    #
    # def count_tasks(self, user_tg_id: int, year: int, month: int):
    #     sql = f'SELECT * FROM table_{user_tg_id} WHERE year=%s AND month=%s'
    #     return self.execute(sql, (year, month), fetchall=True)
