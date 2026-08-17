from flask import Flask, request
import logging
import config_logging
import db_pool
import classifier
from publisher import publish_brief
import atexit
from per_key_executor import PerKeyExecutor

app = Flask(__name__)

# Global executor for per-ISIN sequential processing
executor = PerKeyExecutor(worker_idle_timeout=60.0)


@atexit.register
def shutdown_executor():
    executor.shutdown(wait=True)


def publication_background(data):
    headline = data['headline']
    text = data['text']
    isin = data['isin']
    test = data['test']
    provider = data['provider']
    link = data['link']
    origin = data['origin']
    if 'pubt_code' in data:
        pubt_code = data['pubt_code']
    else:
        pubt_code = ""
    return publish_brief(headline, text, isin, test, provider=provider, link=link, origin=origin, pubt_code=pubt_code)


@app.route("/classify", methods=['POST'])
def classify_request():
    try:
        data = request.get_json()
        text = data['text']
        details = data['details']
        result = classifier.classify(text, details)
        return result
    except Exception as e:
        logging.exception(e)
        return {"result": "an error occured"}


@app.route("/publish", methods=['POST'])
def submit_publication():
    try:
        data = request.get_json()
        isin = data['isin']
        submitted = executor.submit(isin, publication_background, data)
        if submitted:
            return "", 202
        else:
            return {"result": "queue full or shutdown in progress"}, 503
    except Exception as e:
        logging.exception(e)
        return {"result": "an error occured"}


if __name__ == '__main__':
    app.run()
