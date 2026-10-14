Daily Cash Closing API for a convenience store. This is a REST API made with FastAPI, SQLAlchemy and SQLite for a local convenience store. It lets you manage the product catalog, register sales and expenses, and see how the day closed. How much came in, how much went out and what is left.

Authentication. Every endpoint needs an API key sent in the request header called X-API-Key. The key for testing is clave-de-prueba-2026. If the key is missing or wrong the API answers with a 401 Unauthorized error. If you are using Swagger UI at /docs, press the Authorize button at the top right and paste the key there.

How to run it locally. First create and activate a virtual environment with python3 -m venv venv and then source venv/bin/activate. On Windows you activate it with venv\Scripts\activate. Then install the dependencies with pip install -r requirements.txt. After that load the sample data into the database with python seed.py. Finally start the server with uvicorn main:app --reload
Endpoints.

GET /products returns every product in the catalog. You can filter by category, for example /products?category=beverages.

GET /sales/{id} returns the details of one sale using its ID.

GET /products/{id}/sales returns all the sales linked to a given product.

GET /expenses returns all the recorded expenses. To see only one day add a date, for example /expenses?date=2026-09-10.

GET /cash-closing takes a date, for example date=2026-09-10, and calculates the total sales, the breakdown by payment method, the total expenses and the net balance for that day. For that date the response gives total sales of 12500, split into 5500 in cash, 4600 in debit and 2400 by transfer. Total expenses are 6500 and the daily balance is 6000.

POST /expenses creates a new expense. The body needs a date, a concept and an amount. For example date 2026-09-10, concept Cleaning supplies and amount 3000.

About the use of AI. As the course guidelines allow, we used AI tools (nootboklm,claude and ChatGPT) as coding assistants. We used them mainly to help structure the code, translate the documentation into English and sort out the JSON validation syntax. The business logic, the database relationships and the endpoints were checked, tested and understood by the whole team.