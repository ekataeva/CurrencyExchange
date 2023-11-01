import json
import sqlite3


class DbModel:
    def __init__(self):
        self.con = sqlite3.connect('database.db')
        self.cur = self.con.cursor()
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

        self.post_querries = {'currencies': 'INSERT INTO currencies (code, fullname, sign) '
                                            'VALUES (?, ?, ?)',
                              'exchange_rates': """INSERT INTO exchange_rates 
                                                (base_currency_id, target_currency_id, rate) 
                                                VALUES (
                                                    (SELECT id from currencies WHERE code = ?), 
                                                    (SELECT id from currencies WHERE code = ?), 
                                                    ?)"""}


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

    def post_data(self, table_query, param1, param2, param3):

        if (table_query == 'currencies'):
            code = param1
            fullname = param2
            sign = param3
            try:
                self.cur.execute('INSERT INTO currencies (code, fullname, sign) VALUES (?, ?, ?)',
                                 (code, fullname, sign))

                return self.get_data('currency', code), None
            except sqlite3.IntegrityError as e:
                return self.get_data('currency', code)[0], 'A currency with this code already exists'
            except Exception as e:
                return None, 'Server error'

        elif (table_query == 'exchange_rates'):
            base_currency_code = param1
            target_currency_code = param2
            rate = param3
            try:
                data = self.get_data('exchange_rate', base_currency_code, target_currency_code)
                if data:
                    return data[0], 'An exchange rate with this codes already exists'
                else:
                    self.cur.execute("""INSERT INTO exchange_rates 
                    (base_currency_id, target_currency_id, rate) 
                    VALUES (
                        (SELECT id from currencies WHERE code = ?), 
                        (SELECT id from currencies WHERE code = ?), 
                        ?)""",
                    (base_currency_code, target_currency_code, rate))
                    return self.get_data('exchange_rate', base_currency_code, target_currency_code), None
            except Exception as e:
                print("Произошла другая ошибка:", str(e))
                return None, 'Server error'

        else:
            return None, "The required form field is missing"

    def patch_rate(self, base_currency, target_currency, rate):
        try:
            data = self.get_data('exchange_rate', base_currency, target_currency)
            if not data:

                self.post_data()
            self.cur.execute('UPDATE currencies (code, fullname, sign) VALUES (?, ?, ?)',
                             (code, fullname, sign))

            return self.get_data('exchange_rate', base_currency, target_currency), None
        except sqlite3.IntegrityError as e:
            print("Ошибка при вставке данных:", str(e))
            return None, 'A currency with this code already exists'
        except Exception as e:
            print("Произошла другая ошибка:", str(e))
            return None, 'Server error'