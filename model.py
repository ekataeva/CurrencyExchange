import json
import sqlite3


class DbModel:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
        self.get_querries = {'currencies': "SELECT * from currencies",

                             'currency': "SELECT * from currencies where code = ?",

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
                print("Query done")
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

        self.con.commit()
        return results, error

    def post_data(self, query_parameters):
        code = query_parameters.get('code', [])  # [0]
        fullname = query_parameters.get('fullname', [])  # [0]
        sign = query_parameters.get('sign', [])  # [0]

        if code and fullname and sign:
            code = code[0]
            fullname = fullname[0]
            sign = sign[0]

            try:
                self.cur.execute('INSERT INTO currencies (code, fullname, sign) VALUES (?, ?, ?)',
                                 (code, fullname, sign))
                self.con.commit()
                return 200  # Успех
            except sqlite3.IntegrityError as e:
                print("Ошибка при вставке данных:", str(e))
                return 409  # Валюта с таким кодом уже существует
            except Exception as e:
                print("Произошла другая ошибка:", str(e))
                return 500  # Ошибка (например, база данных недоступна)
        else:
            return 400  # Отсутствует нужное поле формы
