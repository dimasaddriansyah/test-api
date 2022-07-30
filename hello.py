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


factory = StemmerFactory()
stemmer = factory.create_stemmer()
stopwords_factory = StopWordRemoverFactory()
stopwords = stopwords_factory.get_stop_words()


def get_list_of_word(list_of_dokumen, stopwords):
    list_of_word = []
    for sentence in list_of_dokumen:
        for word in sentence.split(" "):
            stemmed_word = stemmer.stem(word)
            if word not in stopwords and stemmed_word not in list_of_word:
                list_of_word.append(stemmed_word)
    return list_of_word


def create_term_frequency(list_of_word, length_dokumen_with_kk):
    term_frequency = []
    for _ in range(length_dokumen_with_kk):
        term_frequency.append(
            dict(zip(list_of_word, [0 for _ in range(len(list_of_word))])))
    return term_frequency


def create_document_frequency(list_of_word):
    return dict(zip(list_of_word, [0 for _ in range(len(list_of_word))]))


def get_d_df(length_of_dokumen, document_frequency):
    d_df = {}
    for key, value in document_frequency.items():
        d_df[key] = length_of_dokumen / value
    return d_df


def get_idf(d_df):
    idf = {}
    for key, value in d_df.items():
        idf[key] = round(log10(value), 3)
    return idf


def get_w_q_t(term_frequency, idf):
    w_q_t = []
    for index, document in enumerate(term_frequency):
        w_q_t.append({})
        for key, value in document.items():
            w_q_t[index][key] = value * idf[key]
    return w_q_t


def get_bobot_kata_kunci(w_q_t, kata_kunci):
    bobot_kata_kunci = []
    for index, document in enumerate(w_q_t):
        if index > 0:
            bobot_kata_kunci.append({})
            for word in stemmer.stem(kata_kunci).split(" "):
                bobot_kata_kunci[index-1][word] = document[word]
    return bobot_kata_kunci


def get_qd(w_q_t):
    q_d = []
    for index, document in enumerate(w_q_t):
        q_d.append({})
        total = 0
        for key, value in document.items():
            q_d[index][key] = round(value ** 2, 3)
            total += q_d[index][key]
        q_d[index]["total"] = round(sqrt(total), 3)
    return q_d


def get_bobot_kata_kunci_qd(q_d, kata_kunci):
    bobot_kata_kunci_q_d = {}
    for word in stemmer.stem(kata_kunci).split(" "):
        bobot_kata_kunci_q_d[word] = q_d[0][word]
    return bobot_kata_kunci_q_d


def get_bobot_kk_dan_dokumen(q_d):
    bobot_kk_dan_dokumen = {}
    for index, document in enumerate(q_d):
        for key, value in document.items():
            if key == "total":
                if index == 0:
                    bobot_kk_dan_dokumen["bobot_kata_kunci"] = value
                else:
                    bobot_kk_dan_dokumen[f"bobot_dokumen_{index}"] = value
    return bobot_kk_dan_dokumen


def get_sum_of_tf_qd(term_frequency, bobot_kata_kunci_q_d):
    sum_of_tf_q_d = []
    for index, document in enumerate(term_frequency):
        if index > 0:
            sum_of_tf_q_d.append({})
            for key, value in document.items():
                if key in bobot_kata_kunci_q_d:
                    sum_of_tf_q_d[index-1][key] = value * \
                        bobot_kata_kunci_q_d[key]
    return sum_of_tf_q_d


def get_bobot_sum_of_tf_qd(sum_of_tf_q_d):
    bobot_sum_of_tf_qd = {}
    for index, document in enumerate(sum_of_tf_q_d):
        total = 0
        for _, value in document.items():
            total += value
        bobot_sum_of_tf_qd[f"bobot_sum_tf_qd_{index+1}"] = total
    return bobot_sum_of_tf_qd


def get_bobot_dokumen_result(bobot_sum_of_tf_qd, bobot_kata_kunci, bobot_dokumen):
    return round(sqrt(bobot_sum_of_tf_qd)/(bobot_kata_kunci/bobot_dokumen), 3)


@app.route('/cari/kata_kunci', methods=['POST'])
#! Pencarian Kata Kunci Sudah di Stemm
def filter_cari__kata_kunci():
    data = request.json["data"]
    hasil_stemm = stemmer.stem(data).split(" ")
    return make_response({
        'message': 'Hasil stemm pencarian berhasil',
        'data': hasil_stemm
    }, 200)


@app.route('/stemm/semua_produk', methods=['POST'])
#! Stemm Semua List Produk
def stemm__semua_produk():
    data = request.json["data"]
    hasil_stemm = get_list_of_word(data, stopwords)
    return make_response({
        'message': 'Hasil stemm semua produk berhasil',
        'data': hasil_stemm
    }, 200)


@app.route('/create_term_frequency', methods=['POST'])
#! Hasil Term Frequency
def fun_create_term_frequency():
    list_of_word = request.json["list_of_word"]
    length_of_dokumen_with_kk = request.json["length_of_dokumen_with_kk"]
    nama_dokumen_with_kk = request.json['nama_dokumen_with_kk']
    term_frequency = create_term_frequency(
        list_of_word, length_of_dokumen_with_kk)
    for index, sentence, in enumerate(nama_dokumen_with_kk):
        for word in stemmer.stem(sentence).split(" "):
            if word in term_frequency[index]:
                term_frequency[index][word] += 1
    return make_response({
        'message': 'Hasil term frequency berhasil',
        'data': term_frequency
    }, 200)


@app.route('/create_document_frequency', methods=['POST'])
#! Hasil Document Frequency
def fun_create_document_frequency():
    list_of_word = request.json["list_of_word"]
    term_frequency = request.json["term_frequency"]
    document_frequency = create_document_frequency(list_of_word)
    for index, sentence, in enumerate(term_frequency):
        if index > 0:
            for key, value in sentence.items():
                if value:
                    document_frequency[key] += 1
    return make_response({
        'message': 'Hasil document frequency berhasil',
        'data': document_frequency
    }, 200)


@app.route('/ddf', methods=['POST'])
#! Hasil DDF
def fun_ddf():
    length_of_dokumen = request.json["length_of_dokumen"]
    document_frequency = request.json["document_frequency"]
    ddf = get_d_df(length_of_dokumen, document_frequency)
    return make_response({
        'message': 'Hasil ddf berhasil',
        'data': ddf
    }, 200)


@app.route('/idf', methods=['POST'])
#! Hasil IDF
def fun_idf():
    ddf = request.json["ddf"]
    idf = get_idf(ddf)
    return make_response({
        'message': 'Hasil idf berhasil',
        'data': idf
    }, 200)


@app.route('/wqt', methods=['POST'])
#! Hasil WQT
def fun_wqt():
    term_frequency = request.json["term_frequency"]
    idf = request.json["idf"]
    wqt = get_w_q_t(term_frequency, idf)
    return make_response({
        'message': 'Hasil wqt berhasil',
        'data': wqt
    }, 200)


@app.route('/bobot_kata_kunci', methods=['POST'])
#! Hasil Bobot Kata Kunci
def fun_bobot_kata_kunci():
    wqt = request.json["wqt"]
    kata_kunci = request.json["kata_kunci"]
    bobot_kata_kunci = get_bobot_kata_kunci(wqt, kata_kunci)
    return make_response({
        'message': 'Hasil bobot kata kunci berhasil',
        'data': bobot_kata_kunci
    }, 200)


@app.route('/qd', methods=['POST'])
#! Hasil QD
def fun_qd():
    wqt = request.json["wqt"]
    qd = get_qd(wqt)
    return make_response({
        'message': 'Hasil qd berhasil',
        'data': qd
    }, 200)


@app.route('/bobot_kata_kunci_qd', methods=['POST'])
#! Hasil Bobot Kata Kunci QD
def fun_bobot_kata_kunci_qd():
    qd = request.json["qd"]
    kata_kunci = request.json["kata_kunci"]
    bobot_kata_kunci_qd = get_bobot_kata_kunci_qd(qd, kata_kunci)
    return make_response({
        'message': 'Hasil bobot kata kunci qd berhasil',
        'data': bobot_kata_kunci_qd
    }, 200)


@app.route('/bobot_kk_dan_dokumen', methods=['POST'])
#! Hasil Bobot Kata Kunci dan Dokumen
def bobot_kk_dan_dokumen():
    qd = request.json["qd"]
    bobot_kk_dan_dokumen = get_bobot_kk_dan_dokumen(qd)
    return make_response({
        'message': 'Hasil bobot kk dan dokumen berhasil',
        'data': bobot_kk_dan_dokumen
    }, 200)


@app.route('/sum_of_tf_qd', methods=['POST'])
#! Hasil Sum Of TF QD
def sum_of_tf_qd():
    term_frequency = request.json["term_frequency"]
    bobot_kata_kunci_qd = request.json["bobot_kata_kunci_qd"]
    sum_of_tf_qd = get_sum_of_tf_qd(term_frequency, bobot_kata_kunci_qd)
    return make_response({
        'message': 'Hasil sum of tf qd berhasil',
        'data': sum_of_tf_qd
    }, 200)


@app.route('/bobot_sum_of_tf_qd', methods=['POST'])
#! Hasil Bobot Sum Of TF QD
def bobot_sum_of_tf_qd():
    sum_of_tf_qd = request.json["sum_of_tf_qd"]
    bobot_sum_of_tf_qd = get_bobot_sum_of_tf_qd(sum_of_tf_qd)
    return make_response({
        'message': 'Hasil bobot sum of tf qd berhasil',
        'data': bobot_sum_of_tf_qd
    }, 200)
