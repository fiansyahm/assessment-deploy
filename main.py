import json
import base64
import time
from flask import Flask, request,Response
from flask_cors import CORS
from tabulate import tabulate
from term_graph import getData, getArticleIdAuthorReferencesAndAuthor, author_matrixs, getTable2Data, makeTable2, addTable2TotalRowAndColoumn, makeNewAdjMatrix, rank, makeTermGraph

application = Flask(__name__)
CORS(application)

@application.route('/data/<type>/<name>', methods=['GET', 'POST'])
def data(type, name):
    if request.method == 'POST' or request.method == 'GET':
        start_time = time.time()
        if request.method == 'POST':
            table = getData(request.get_json()["data"])
        elif request.method == 'GET':
            table = getData()

        print("Tabel 1")
        title = ['Article-ID', 'Terms in Title and Keywords',
                 'Terms Found in Abstracts', 'Publication Year', 'Authors', 'References']
        print(title)
        # print(tabulate(table))

    # pair ArticleId,Author,& References & author
        pairs, authors, articles,initial_articles_pair ,title_articles_pair,initial_author_pair,nation_author_pair = getArticleIdAuthorReferencesAndAuthor(table)

        # for i in pairs:
        #     print(i)
        #     print("\n")
        # for y in authors:
        #     print(y)
        #     print("\n")

        # pasangan yang memungkinkan antara 2 penulis
        if type == "article":
            input_author_article = articles
        elif type == "author":
            input_author_article = authors
        author_matrix = author_matrixs(input_author_article)

    # ambil data untuk tabel 2(step 1)
        author_matrix_and_relation = getTable2Data(pairs, author_matrix, type)

        # for x in author_matrix_and_relation:
        #     print(x)
        # return author_matrix_and_relation

    # errornyadisini
        table2, raw_table2 = makeTable2(author_matrix_and_relation, input_author_article)
        # add total coloum & row in table 2
        raw_table2WithRowCol = addTable2TotalRowAndColoumn(raw_table2, input_author_article)
        # makeNewAdjMatrix
        newAdjMatrixs = makeNewAdjMatrix(raw_table2WithRowCol, len(input_author_article))
        # rank author
        table, author_rank,last_author_rank = rank(newAdjMatrixs, input_author_article, name)

        try:
            outer_author = request.get_json()["outer"]
            top_author_rank = request.get_json()["author-rank"]
        except:
            outer_author = 0
            top_author_rank = 20

        initial_articles_pair_search={}
        count=0
        for j in initial_articles_pair:
            initial_articles_pair_search[j]=count
            count+=1

        initial_author_pair_search={}
        count=0
        for j in initial_author_pair:
            initial_author_pair_search[j]=count
            count+=1

        if name == "graph":
            # Make Term Graph
            output = makeTermGraph(
                input_author_article, author_matrix_and_relation, last_author_rank, outer_author, top_author_rank)
            output.seek(0)
            my_base64_jpgData = base64.b64encode(output.read())
            if request.method == 'GET':
                end_time = time.time()
                total_time = end_time - start_time
                print(
                    "Waktu eksekusi program: {:.2f} detik".format(total_time))
                return Response(output.getvalue(), mimetype='image/png')
            else:
                end_time = time.time()
                total_time = end_time - start_time
                print(
                    "Waktu eksekusi program: {:.2f} detik".format(total_time))
                return my_base64_jpgData
        elif name == "rank":
            title_nation_of_the_article = []
            for i in input_author_article:
                if type == "article":
                    if i in initial_articles_pair:
                        title_nation_of_the_article.append(title_articles_pair[initial_articles_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")
                elif type == "author":
                    if i in initial_author_pair:
                        title_nation_of_the_article.append(nation_author_pair[initial_author_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")
            tmp = [input_author_article, [table, author_rank]]
            if type == "article" or type == "author":
                tmp.append(title_nation_of_the_article)
            end_time = time.time()
            total_time = end_time - start_time
            print("Waktu eksekusi program: {:.2f} detik".format(total_time))
            return tmp
        
        elif name == "rankgraph":
            title_nation_of_the_article = []
            for i in input_author_article:
                if type == "article":
                    if i in initial_articles_pair:
                        title_nation_of_the_article.append(title_articles_pair[initial_articles_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")
                elif type == "author":
                    if i in initial_author_pair:
                        title_nation_of_the_article.append(nation_author_pair[initial_author_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")

            tmp = {'authors':input_author_article, 'ranks':author_rank,'title':title_nation_of_the_article,'nodes_strength':last_author_rank}
            tmp=json.dumps(tmp)
            tmp_dict = json.loads(tmp)
            end_time = time.time()
            total_time = end_time - start_time
            print("Waktu eksekusi program: {:.2f} detik".format(total_time))
            return tmp_dict
        elif name == "rankgraphimage":
            title_nation_of_the_article = []
            for i in input_author_article:
                if type == "article":
                    if i in initial_articles_pair:
                        title_nation_of_the_article.append(title_articles_pair[initial_articles_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")
                elif type == "author":
                    if i in initial_author_pair:
                        title_nation_of_the_article.append(nation_author_pair[initial_author_pair_search[i]])
                    else:
                        # bukan penulis pertama
                        title_nation_of_the_article.append("None")

            tmp = {'authors':input_author_article, 'ranks':author_rank,'title':title_nation_of_the_article,'nodes_strength':last_author_rank}
            tmp=json.dumps(tmp)
            # Make Term Graph
            output = makeTermGraph(input_author_article, author_matrix_and_relation, last_author_rank, outer_author, top_author_rank)
            output.seek(0)
            my_base64_jpgData = base64.b64encode(output.read())
            my_base64_jpgData=my_base64_jpgData.decode("utf-8")
            tmp_dict = json.loads(tmp)
            tmp_dict['graph']=my_base64_jpgData

            end_time = time.time()
            total_time = end_time - start_time
            print("Waktu eksekusi program: {:.2f} detik".format(total_time))
            return tmp_dict

if __name__ == "__main__":
    application.run(host='0.0.0.0')
