from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from flask import Flask, request, make_response
from math import log10, sqrt
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World! Deploy nich...</p>"


@app.route("/works")
def it_works():
    return "IT Works! nyehehe"


