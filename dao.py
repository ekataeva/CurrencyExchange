import sqlite3

from model import Model


class Dao:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.model = Model()
        self.get_querries = {'currencies': "SELECT id, fullname as name, code, sign from currencies",

                             'currency': """SELECT id, fullname as name, code, sign
                                                from currencies where code = ?""",

                             'exchange_rates': """select er.id, 
                                                bc.id as 'baseCurrency.id', 
                                                bc.fullname as 'baseCurrency.name', 
                                                bc.code as 'baseCurrency.code', 
                                                bc.sign as 'baseCurrency.sign',
                                                tc.id as 'targetCurrency.id', 
                                                tc.fullname as 'targetCurrency.name', 
                                                tc.code as 'targetCurrency.code', 
                                                tc.sign as 'targetCurrency.sign',
                                                er.rate as 'rate'
                                                from exchange_rates er
                                                join currencies bc on er.base_currency_id = bc.id
                                                join currencies tc on er.target_currency_id = tc.id""",

                             'exchange_rate': """select er.id, 
                                                bc.id as 'baseCurrency.id', 
                                                bc.fullname as 'baseCurrency.name', 
                                                bc.code as 'baseCurrency.code', 
                                                bc.sign as 'baseCurrency.sign',
                                                tc.id as 'targetCurrency.id', 
                                                tc.fullname as 'targetCurrency.name', 
                                                tc.code as 'targetCurrency.code', 
                                                tc.sign as 'targetCurrency.sign',
                                                er.rate as 'rate'
                                                from exchange_rates er
                                                join currencies bc on er.base_currency_id = bc.id
                                                join currencies tc on er.target_currency_id = tc.id
                                                WHERE bc.code = ? and tc.code = ?"""}

    def get_data(self, table_query, param1=None, param2=None):
        error = None

        try:
            if param1 and param2:
                self.cur.execute(self.get_querries[table_query], (param1, param2))
            elif param1:
                self.cur.execute(self.get_querries[table_query], (param1,))
            else:
                self.cur.execute(self.get_querries[table_query])
        except Exception as e:
            error = e
            print("Ошибка при получении данных:", str(e))

        results = []

        for row in self.cur.fetchall():
            item = {}
            for i, value in enumerate(row):
                column_name = self.cur.description[i][0]
                if '.' in column_name:
                    table_name, col_name = column_name.split('.')
                    if table_name not in item:
                        nested_dict = {}
                        item[table_name] = nested_dict
                    item[table_name][col_name] = value
                else:
                    item[column_name] = value
            results.append(item)

        self.model.data = results
        self.model.error = error

    def post_data(self, table_query, param1, param2, param3):

        if table_query == 'currencies':
            code = param1
            fullname = param2
            sign = param3
            try:
                self.cur.execute("PRAGMA FOREIGN_KEYS = ON")
                self.cur.execute('INSERT INTO currencies (code, fullname, sign) VALUES (?, ?, ?)',
                                 (code, fullname, sign))
                self.con.commit()
                self.get_data('currency', code)

            except sqlite3.IntegrityError:
                self.get_data('currency', code)
                self.model.error = 'A currency with this code already exists'
            except Exception as error:
                self.model.data = None
                self.model.error = error

        elif table_query == 'exchange_rates':
            base_currency_code = param1
            target_currency_code = param2
            rate = param3
            try:
                self.get_data('exchange_rate', base_currency_code, target_currency_code)
                if self.model.data:
                    self.model.error = 'An exchange rate with this codes already exists'
                else:
                    self.cur.execute("PRAGMA FOREIGN_KEYS = ON")
                    self.cur.execute("""INSERT INTO exchange_rates 
                                        (base_currency_id, target_currency_id, rate) 
                                        VALUES (
                                            (SELECT id from currencies WHERE code = ?), 
                                            (SELECT id from currencies WHERE code = ?), 
                                            ?)""",
                                        (base_currency_code, target_currency_code, rate))
                    self.con.commit()
                    self.get_data('exchange_rate', base_currency_code, target_currency_code)
            except Exception as error:
                print("Произошла ошибка:", str(error))
                self.model.data = None
                self.model.error = error

        else:
            self.model.data = None
            self.model.error = "The required form field is missing"

    def patch_rate(self, base_currency, target_currency, rate):
        try:
            self.get_data('exchange_rate', base_currency, target_currency)
            if not self.model.data:
                self.model.data = None
                self.model.error = "The currency pair is missing in the database"

            self.cur.execute("""UPDATE exchange_rates SET rate = ?
                            WHERE (base_currency_id  = (SELECT id from currencies WHERE code = ?) 
                                  and target_currency_id = (SELECT id from currencies WHERE code = ?))""",
                             (rate, base_currency, target_currency))
            self.con.commit()
            self.get_data('exchange_rate', base_currency, target_currency)
        except Exception as error:
            print("Произошла ошибка:", str(error))
            self.model.data = None
            self.model.error = error
