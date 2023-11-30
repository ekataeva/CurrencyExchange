from dao import Dao


missing_field_error = "The required form field is missing"


class Controller:
    def __init__(self):
        self.dao = Dao()

    def get_currencies(self):
        self.dao.get_data('currencies')
        if self.dao.model.data:
            return 200, self.dao.model.data
        else:
            return 500, {'message': self.dao.model.error}

    def get_currency(self, path):
        cur_code = str(path.split('/')[-1])
        if not cur_code:
            return 400, {'message': "The currency code is missing in the address"}
        else:
            self.dao.get_data('currency', cur_code)
            if self.dao.model.error:
                return 500, {'message': self.dao.model.error}
            elif self.dao.model.data:
                return 200, self.dao.model.data[0]
            else:
                return 404, {'message': "Currency not found"}

    def post_currencies(self, query):
        code = query['code']
        fullname = query['name']
        sign = query['sign']
        if code and fullname and sign:
            code = code[0]
            fullname = fullname[0]
            sign = sign[0]
            self.dao.post_data('currencies', code, fullname, sign)
        else:
            self.dao.model.data = None
            self.dao.model.error = missing_field_error

        return self.post_answer()

    def get_exchange_rates(self):
        self.dao.get_data('exchange_rates')
        if self.dao.model.data:
            return 200, self.dao.model.data
        else:
            return 500, {'message': self.dao.model.error}

    def get_exchange_rate(self, path):
        currencies = str(path.split('/')[-1])
        base_currency = currencies[0:3]
        target_currency = currencies[3:]
        if not base_currency or not target_currency:
            return 400, {'message': "Currency codes pair are missing in the address"}
        else:
            self.dao.get_data('exchange_rate', base_currency, target_currency)
            if self.dao.model.data:
                return 200, self.dao.model.data[0]
            elif self.dao.model.error:
                return 500, {'message': self.dao.model.error}
            else:
                return 404, {'message': "The exchange rate for the pair was not found"}

    def get_exchange(self, query):
        if not (query.get('from') and query.get('to') and query.get('amount')):
            return 400, {'message': "Currency codes pair or amount are missing in the address"}
        else:
            base_currency = query['from'][0]
            target_currency = query['to'][0]
            amount = float(query['amount'][0])
            converted_amount = None
            self.dao.get_data('exchange_rate', base_currency, target_currency)
            if self.dao.model.data:
                self.dao.model.data = self.dao.model.data[0]
                converted_amount = amount * self.dao.model.data['rate']
            else:
                self.dao.get_data('exchange_rate', target_currency, base_currency)
                if self.dao.model.data:
                    self.dao.model.data = self.dao.model.data[0]
                    converted_amount = round(amount / self.dao.model.data['rate'], 2)
                else:
                    self.dao.get_data('exchange_rate', 'USD', base_currency)
                    bc_data = self.dao.model.data
                    self.dao.get_data('exchange_rate', 'USD', target_currency)

                    if bc_data and self.dao.model.data:
                        self.dao.model.data = self.dao.model.data[0]
                        self.dao.model.data['rate'] = round(bc_data[0]['rate'] / self.dao.model.data['rate'], 2)
                        converted_amount = round(amount * self.dao.model.data['rate'], 2)
                        self.dao.model.data['baseCurrency'] = bc_data[0]['targetCurrency']

            self.dao.model.data['amount'] = amount
            self.dao.model.data['convertedAmount'] = converted_amount
            if self.dao.model.data:
                return 200, self.dao.model.data
            elif self.dao.model.error:
                return 500, {'message': self.dao.model.error}
            else:
                return 404, {'message': "The exchange rate for the pair was not found"}

    def post_exchange_rates(self, query):
        base_currency_code = query['baseCurrencyCode']
        target_currency_code = query['targetCurrencyCode']
        rate = query['rate']
        if base_currency_code and target_currency_code and rate:
            base_currency_code = base_currency_code[0]
            target_currency_code = target_currency_code[0]
            rate = rate[0]
            self.dao.post_data('exchange_rates', base_currency_code, target_currency_code, rate)
        else:
            self.dao.model.data = None
            self.dao.model.error = {'message': missing_field_error}

        return self.post_answer()

    def patch_exchange_rate(self, path, query):

        currencies = str(path.split('/')[-1])
        base_currency = currencies[0:3]
        target_currency = currencies[3:6]
        rate = query['rate']

        if (len(currencies) < 7
                or not base_currency or not target_currency or not rate):
            return 400, {'message': "The currency code or rate are missing in the address"}

        else:
            self.dao.patch_rate(base_currency, target_currency, rate[0])
            if self.dao.model.error == "The currency pair is missing in the database":
                return 404, {'message': self.dao.model.error}
            elif self.dao.model.data:
                return 200, self.dao.model.data[0]
            else:
                return 500, {'message': self.dao.model.error}

    def post_answer(self):
        if self.dao.model.error and 'already exists' in self.dao.model.error:
            return 409, self.dao.model.data
        elif self.dao.model.error == missing_field_error:
            return 400, {'message': self.dao.model.error}
        elif self.dao.model.data:
            return 200, self.dao.model.data[0]
        else:
            return 500, {'message': self.dao.model.error}
