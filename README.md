# Проект “Обмен валют”

REST API для описания валют и обменных курсов. Позволяет просматривать и редактировать списки валют и обменных курсов, и совершать расчёт конвертации произвольных сумм из одной валюты в другую.
Веб-интерфейс для проекта отсутствует.

### [ТЗ проекта](https://zhukovsd.github.io/python-backend-learning-course/Projects/CurrencyExchange/#деплой)

## Валюты

### Получение списка валют

- **Метод:** `GET`
- **Путь:** `/currencies`

#### Пример ответа:
```json
[
    {
        "id": 0,
        "name": "United States dollar",
        "code": "USD",
        "sign": "$"
    },
    {
        "id": 1,
        "name": "Euro",
        "code": "EUR",
        "sign": "€"
    }
]
```
#### HTTP коды ответов:
- Успех - 200
- Ошибка (например, база данных недоступна) - 500

### Получение конкретной валюты

- **Метод:** `GET`
- **Путь:** `/currency/{currencyCode}`

#### Пример ответа:
```json
{
    "id": 0,
    "name": "Euro",
    "code": "EUR",
    "sign": "€"
}
```
#### HTTP коды ответов:
- Успех - 200
- Код валюты отсутствует в адресе - 400
- Валюта не найдена - 404
- Ошибка (например, база данных недоступна) - 500

### Добавление новой валюты
- **Метод:** `POST`
- **Путь:** `/currencies`
- **Тело запроса:** Поля формы (`x-www-form-urlencoded`) - `name`, `code`, `sign`

#### Пример ответа:
```json
{
    "id": 0,
    "name": "Euro",
    "code": "EUR",
    "sign": "€"
}
```
#### HTTP коды ответов:
- Успех - 200
- Отсутствует нужное поле формы - 400
- Валюта с таким кодом уже существует - 409
- Ошибка (например, база данных недоступна) - 500

## Обменные курсы
### Получение списка всех обменных курсов
- **Метод:** `GET`
- **Путь:** `/exchangeRates`

#### Пример ответа:
```json
[
    {
        "id": 0,
        "baseCurrency": {
            "id": 0,
            "name": "United States dollar",
            "code": "USD",
            "sign": "$"
        },
        "targetCurrency": {
            "id": 1,
            "name": "Euro",
            "code": "EUR",
            "sign": "€"
        },
        "rate": 0.99
    }
]
```
#### HTTP коды ответов:
- Успех - 200
- Ошибка (например, база данных недоступна) - 500

### Получение конкретного обменного курса
- **Метод:** `GET`
- **Путь:** `/exchangeRate/{baseCurrencyCode}{targetCurrencyCode}`

#### Пример ответа:
```json
{
    "id": 0,
    "baseCurrency": {
        "id": 0,
        "name": "United States dollar",
        "code": "USD",
        "sign": "$"
    },
    "targetCurrency": {
        "id": 1,
        "name": "Euro",
        "code": "EUR",
        "sign": "€"
    },
    "rate": 0.99
}
```
#### HTTP коды ответов:
- Успех - 200
- Коды валют пары отсутствуют в адресе - 400
- Обменный курс для пары не найден - 404
- Ошибка (например, база данных недоступна) - 500

### Добавление нового обменного курса
- **Метод:** `POST`
- **Путь:** `/exchangeRates`
- **Тело запроса:** Поля формы (`x-www-form-urlencoded`) - `baseCurrencyCode`, `targetCurrencyCode`, `rate`

#### Пример ответа:
```json
{
    "id": 0,
    "baseCurrency": {
        "id": 0,
        "name": "United States dollar",
        "code": "USD",
        "sign": "$"
    },
    "targetCurrency": {
        "id": 1,
        "name": "Euro",
        "code": "EUR",
        "sign": "€"
    },
    "rate": 0.99
}
```

#### HTTP коды ответов:
- Успех - 200
- Отсутствует нужное поле формы - 400
- Валютная пара с таким кодом уже существует - 409
- Ошибка (например, база данных недоступна) - 500

### Обновление существующего обменного курса
- **Метод:** `PATCH`
- **Путь:** `/exchangeRate/{baseCurrencyCode}{targetCurrencyCode}`
- **Тело запроса:** Поля формы (`x-www-form-urlencoded`) - `rate`

#### Пример ответа:
```json
{
    "id": 0,
    "baseCurrency": {
        "id": 0,
        "name": "United States dollar",
        "code": "USD",
        "sign": "$"
    },
    "targetCurrency": {
        "id": 1,
        "name": "Euro",
        "code": "EUR",
        "sign": "€"
    },
    "rate": 0.99
}
```

#### HTTP коды ответов:
- Успех - 200
- Отсутствует нужное поле формы - 400
- Валютная пара отсутствует в базе данных - 404
- Ошибка (например, база данных недоступна) - 500

## Обмен валюты
### Расчёт перевода
- **Метод:** `GET`
- **Путь:** `/exchange?from={BASE_CURRENCY_CODE}&to={TARGET_CURRENCY_CODE}&amount=${AMOUNT}`
#### Пример запроса:
```http
GET /exchange?from=USD&to=AUD&amount=10
```
#### Пример ответа:
```json
{
    "baseCurrency": {
        "id": 0,
        "name": "United States dollar",
        "code": "USD",
        "sign": "$"
    },
    "targetCurrency": {
        "id": 1,
        "name": "Australian dollar",
        "code": "AUD",
        "sign": "A€"
    },
    "rate": 1.45,
    "amount": 10.00,
    "convertedAmount": 14.50
}
```
Примечание: Все HTTP коды ответов будут соответствовать стандартам, указанным выше.
