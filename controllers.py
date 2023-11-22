from model import DbModel


class Controller:
    def __init__(self):
        self.model = DbModel()

    def get_currencies(self):
        data, error = self.model.get_data('currencies')
        if data:
            return 200, data
        else:
            return 500, {'message': error}

    def get_currency(self, path):
        cur_code = str(path.split('/')[-1])
        if not cur_code:
            return 400, {'message': "The currency code is missing in the address"}
        else:
            data, error = self.model.get_data('currency', cur_code)
            if error:
                return 500, {'message': error}
            elif data:
                return 200, data[0]
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
            data, error = self.model.post_data('currencies', code, fullname, sign)
        else:
            data, error = None, "The required form field is missing"
        return self.post_answer(data, error)

    def get_exchange_rates(self):
        data, error = self.model.get_data('exchange_rates')
        if data:
            return 200, data
        else:
            return 500, {'message': error}

    def get_exchange_rate(self, path):
        currencies = str(path.split('/')[-1])
        base_currency = currencies[0:3]
        target_currency = currencies[3:]
        if not base_currency or not target_currency:
            return 400, {'message': "Currency codes pair are missing in the address"}
        else:
            data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
            if data:
                return 200, data[0]
            elif error:
                return 500, {'message': error}
            else:
                return 404, {'message': "The exchange rate for the pair was not found"}

    def get_exchange(self, query):
        if not (query.get('from') and query.get('to') and query.get('amount')):
            return 400, {'message': "Currency codes pair or amount are missing in the address"}
        else:
            base_currency = query['from'][0]
            target_currency = query['to'][0]
            amount = float(query['amount'][0])
            data, error = self.model.get_data('exchange_rate', base_currency, target_currency)
            if data:
                data = data[0]
                converted_amount = amount * data['rate']
            else:
                invert_data, error = self.model.get_data('exchange_rate', target_currency, base_currency)
                if invert_data:
                    data = invert_data[0]
                    converted_amount = round(amount / data['rate'], 2)
                else:
                    bc_data, error = self.model.get_data('exchange_rate', 'USD', base_currency)
                    print(bc_data)
                    tc_data, error = self.model.get_data('exchange_rate', 'USD', target_currency)
                    if bc_data and tc_data:
                        data = tc_data[0]
                        data['rate'] = round(bc_data[0]['rate'] / tc_data[0]['rate'], 2)
                        converted_amount = round(amount * data['rate'], 2)
                        data['baseCurrency'] = bc_data[0]['targetCurrency']

            data['amount'] = amount
            data['convertedAmount'] = converted_amount
            if data:
                return 200, data
            elif error:
                return 500, {'message': error}
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
            data, error = self.model.post_data('exchange_rates', base_currency_code, target_currency_code, rate)
        else:
            data, error = None, {'message': "The required form field is missing"}

        return self.post_answer(data, error)

    def patch_exchange_rate(self, path, query):

        currencies = str(path.split('/')[-1])
        base_currency = currencies[0:3]
        target_currency = currencies[3:6]
        rate = query['rate']

        if (len(currencies) < 7
                or not base_currency or not target_currency or not rate):
            return 400, {'message': "The currency code or rate are missing in the address"}

        else:
            data, error = self.model.patch_rate(base_currency, target_currency, rate[0])
            if error == "The currency pair is missing in the database":
                return 404, {'message': error}
            elif data:
                return 200, data[0]
            else:
                return 500, {'message': error}

    @staticmethod
    def post_answer(data, error):
        if error and 'already exists' in error:
            return 409, data
        elif error == "The required form field is missing":
            return 400, {'message': error}
        elif data:
            return 200, data[0]
        else:
            return 500, {'message': error}
