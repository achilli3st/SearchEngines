from flask import Flask, render_template, request
from requests.auth import HTTPBasicAuth
from collections import OrderedDict
import operator
import requests
import json

app = Flask(__name__)  # __Main__

#renders main page
@app.route('/')  # www.website.com/
def hellWorld():
    return render_template('index.html')



@app.route('/tables',methods=['POST'])
def tables():

    global table
    table = request.form['table'];
    #fetch the options from the table
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Cache-Control': 'no-store'}
    option_response = requests.get('https://99fcbc7e2b652690507a3e7780829743.us-east-1.aws.found.io:9243/'+table+'/_mapping?pretty',
                 auth=HTTPBasicAuth('elastic', 'OZctrgMjXAVc9uNRHO9ERr6a'), headers=headers)
    data = json.loads(option_response.content)
    DictionaryOfOptions=data[table]['mappings']['data']['properties']
    option_list = DictionaryOfOptions.keys()
    return render_template('base.html',option_list=option_list)


#reads all the options and query sent by the user
@app.route('/search', methods=['Post'])  # www.website.com/search
def getUserInput():
    searchquery = request.form['searchtext']
    option = request.form['optionsfromtables']

    ExactMatch = request.form.get('ExactMatch')
    FuzzyMatchingFields = request.form.get('FuzzyMatchingFields')
    FuzzyMatchingMultipleFieldsbyWeight = request.form.get('FuzzyMatchingMultipleFieldsbyWeight')

    print ExactMatch
    print FuzzyMatchingFields
    print FuzzyMatchingMultipleFieldsbyWeight

    #headers remain the same across all the options
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Cache-Control': 'no-store'}

    MultiMatchdict = {}
    #run FuzzyMatch Multifield only when it is set
    if FuzzyMatchingMultipleFieldsbyWeight == "on":
        #multifield Options
        multifieldOptions = {}
        NumberofMultiOptions = request.form.get('NumberofMultiOptions')
        for x in range(0, int(NumberofMultiOptions)):
            multifieldOptions["MultiOptions"+str(x)] = request.form.get('MultiOptions'+str(x))
            multifieldOptions["WeightOptions"+str(x)] = request.form.get("WeightOptions"+str(x))
            #multifieldOptions["MultiWeightText"+str(x)] = request.form.get("MultiWeightText"+str(x))
        print multifieldOptions

        extendedQuery = ""
        for x in range(0, int(NumberofMultiOptions)):
            extendedQuery = extendedQuery+"\""+multifieldOptions["MultiOptions"+str(x)]+"^"+multifieldOptions["WeightOptions"+str(x)]+"\""+","

        extendedQuery = extendedQuery[1:-2]
        print extendedQuery

        # get Fuzzy Matching Multiple Fields by weight
        data = '{"query": {"multi_match": {"query": "' + searchquery + '", "fields": ["' + option + '", "' + extendedQuery + '"], "fuzziness": "AUTO","operator":  "and"}}}'

        responseFuzzyMultiMatch = requests.get(
            "https://99fcbc7e2b652690507a3e7780829743.us-east-1.aws.found.io:9243/"+table+"/data/_search",
            auth=HTTPBasicAuth('elastic', 'OZctrgMjXAVc9uNRHO9ERr6a'), headers=headers, data=data)

        #json parsing
        MultiMatchContent = json.loads(responseFuzzyMultiMatch.content)

        #output sorting

        counter1 = 0
        for doc in MultiMatchContent['hits']['hits']:
            MultiMatchdict[counter1] = doc
            counter1 += 1
        print MultiMatchdict



    ExactMatchdict = {}
    try:
        #get the exact match
        data = '{"query":{"match_phrase":{"'+option+'":"'+searchquery+'"}}}'
        responseExactMatch = requests.get(
            "https://99fcbc7e2b652690507a3e7780829743.us-east-1.aws.found.io:9243/"+table+"/data/_search",
            auth=HTTPBasicAuth('elastic', 'OZctrgMjXAVc9uNRHO9ERr6a'), headers=headers, data=data)

        #json Parsing
        ExactMatchContent =  json.loads(responseExactMatch.content)

        #output sorting

        counter2 = 0
        for doc in ExactMatchContent['hits']['hits']:
            ExactMatchdict[counter2] = doc
            counter2 += 1
        print ExactMatchdict

    except KeyError:
        print "error in Exact Match"

    FuzzyMatchdict = {}
    try:
        #get Fuzzy matching fields match
        data = '{ "query": {"match": {"'+option+'": {"query":"'+searchquery+'","fuzziness": "AUTO" ,"operator":  "and" }}}}'
        responseFuzzyMatch = requests.get(
            "https://99fcbc7e2b652690507a3e7780829743.us-east-1.aws.found.io:9243/"+table+"/data/_search",
            auth=HTTPBasicAuth('elastic', 'OZctrgMjXAVc9uNRHO9ERr6a'), headers=headers, data=data)

        #json Parsing
        FuzzyMatchContent = json.loads(responseFuzzyMatch.content)
        #output sorting

        counter3 = 0
        for doc in FuzzyMatchContent['hits']['hits']:
            FuzzyMatchdict[counter3] = doc
            counter3 += 1
        print FuzzyMatchdict

    except KeyError:
        print "Error in Fuzzy Match"





    #combMNZ
    #NumberofSets = Number of Sets
    #Dc = Normalized score of document d in result set C
    #Sd = Score of Document D in the rank list C before normalization
    #DcMin = Minimum document score in the ranked list
    #DcMax = Maximum document score in the ranked list
    print ExactMatchdict
    print FuzzyMatchdict
    print MultiMatchdict

    if ExactMatch == None and FuzzyMatchingFields == None and FuzzyMatchingMultipleFieldsbyWeight == None:
        print "All three are empty"
        # combMNZ
        # For Fuzzy Match List
        Finalcollection = {}

        DcListFM = {}
        for element in FuzzyMatchdict:
            DcListFM[FuzzyMatchdict[element]['_id']] = FuzzyMatchdict[element]['_score']
        print DcListFM
        DcMinFM = min(DcListFM.values())
        DcMaxFM = max(DcListFM.values())
        print DcMinFM
        print DcMaxFM

        if DcMaxFM == DcMinFM:
            DcMaxFM += 0.000001

        NormalizedDcMF = {}
        for key, value in DcListFM.items():
            DcFM = (value - DcMinFM) / (DcMaxFM - DcMinFM)
            Finalcollection[key] = ''
            NormalizedDcMF[key] = DcFM
            print key, DcFM

        # for exact Match
        DcListEM = {}
        for element in ExactMatchdict:
            DcListEM[ExactMatchdict[element]['_id']] = ExactMatchdict[element]['_score']
        print DcListEM
        DcMinEM = min(DcListEM.values())
        DcMaxEM = max(DcListEM.values())
        print DcMinEM
        print DcMaxEM


        if DcMaxEM == DcMinEM:
            DcMaxEM += 0.000001


        NormalizedDcEM = {}
        for key, value in DcListEM.items():
            DcEM = (value - DcMinEM) / (DcMaxEM - DcMinEM)
            Finalcollection[key] = ''
            NormalizedDcEM[key] = DcEM
            print key, DcEM

        DcListMM = {}
        NormalizedDcMM = {}
        try:
            # for Multi Match List
            for element in MultiMatchdict:
                DcListMM[MultiMatchdict[element]['_id']] = MultiMatchdict[element]['_score']
            print DcListMM
            DcMinMM = min(DcListMM.values())
            DcMaxMM = max(DcListMM.values())
            print DcMinMM
            print DcMaxMM

            if DcMaxMM == DcMinMM:
                DcMaxMM += 0.000001


            for key, value in DcListMM.items():
                DcMM = (value - DcMinMM) / (DcMaxMM - DcMinMM)
                Finalcollection[key] = ''
                NormalizedDcMM[key] = DcMM
                print key, DcMM

        except ValueError:
            pass

        # final Scoring and combining

        print Finalcollection

        CombMNZ = {}
        for key in Finalcollection:
            Dcgreater0 = 0
            CombMNZd = 0

            if key in NormalizedDcEM.keys():
                if NormalizedDcEM[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMF.keys():
                if NormalizedDcMF[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMM.keys():
                if NormalizedDcMM[key] is 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcEM.keys():
                CombMNZd = NormalizedDcEM[key] * Dcgreater0

            if key in NormalizedDcMF.keys():
                CombMNZd += NormalizedDcMF[key] * Dcgreater0

            if key in NormalizedDcMM.keys():
                CombMNZd += NormalizedDcMM[key] * Dcgreater0

            CombMNZ[key] = CombMNZd

        print CombMNZ

    elif FuzzyMatchingFields == None and FuzzyMatchingMultipleFieldsbyWeight == None:
        # return the list as it is
        print "Exact Match is set"
        CombMNZ = {}
        for element in ExactMatchdict.items():
            CombMNZ[element[1]['_id']] = element[1]['_score']
        print CombMNZ

    elif ExactMatch == None and FuzzyMatchingMultipleFieldsbyWeight == None:
        # return the list as it is
        print "Fuzzy Match is set"
        CombMNZ = {}
        for element in FuzzyMatchdict.items():
            CombMNZ[element[1]['_id']] = element[1]['_score']
        print CombMNZ

    elif ExactMatch == None and FuzzyMatchingFields == None:
        # return the list as it is
        print "Multi Match is set"
        CombMNZ = {}
        for element in MultiMatchdict.items():
            CombMNZ[element[1]['_id']] = element[1]['_score']
        print CombMNZ

    elif ExactMatch == None:
        print "fuzzy match and Multi Match is set"
        # combMNZ
        # For Fuzzy Match List
        NumberofSets = 2
        DcListFM = {}
        Finalcollection = {}
        for element in FuzzyMatchdict:
            DcListFM[FuzzyMatchdict[element]['_id']] = FuzzyMatchdict[element]['_score']
        print DcListFM
        DcMinFM = min(DcListFM.values())
        DcMaxFM = max(DcListFM.values())
        print DcMinFM
        print DcMaxFM


        if DcMaxFM == DcMinFM:
            DcMaxFM += 0.000001


        NormalizedDcMF = {}
        for key, value in DcListFM.items():
            DcFM = (value - DcMinFM) / (DcMaxFM - DcMinFM)
            Finalcollection[key] = ''
            NormalizedDcMF[key] = DcFM
            print key, DcFM

            # for Multi Match List
        DcListMM = {}
        NormalizedDcMM = {}

        try:
            for element in MultiMatchdict:
                DcListMM[MultiMatchdict[element]['_id']] = MultiMatchdict[element]['_score']
            print DcListMM
            DcMinMM = min(DcListMM.values())
            DcMaxMM = max(DcListMM.values())
            print DcMinMM
            print DcMaxMM

            if DcMaxMM == DcMinMM:
                DcMaxMM += 0.000001

            for key, value in DcListMM.items():
                DcMM = (value - DcMinMM) / (DcMaxMM - DcMinMM)
                Finalcollection[key] = ''
                NormalizedDcMM[key] = DcMM
                print key, DcMM

        except ValueError:
            pass

        # final Scoring and combining

        print Finalcollection

        CombMNZ = {}
        for key in Finalcollection:
            Dcgreater0 = 0
            CombMNZd = 0
            if key in NormalizedDcMF.keys():
                if NormalizedDcMF[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMM.keys():
                if NormalizedDcMM[key] is 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass
            if key in NormalizedDcMF.keys():
                CombMNZd = NormalizedDcMF[key] * Dcgreater0

            if key in NormalizedDcMM.keys():
                CombMNZd += NormalizedDcMM[key] * Dcgreater0

            CombMNZ[key] = CombMNZd
        print "CombMNZ is : "
        print CombMNZ

    elif FuzzyMatchingFields == None:
        print 'Exact Match and Multi Match is set'
        # combMNZ
        # For Exact Match List
        NumberofSets = 2
        DcListEM = {}
        Finalcollection = {}
        for element in ExactMatchdict:
            DcListEM[ExactMatchdict[element]['_id']] = ExactMatchdict[element]['_score']
        print DcListEM
        DcMinEM = min(DcListEM.values())
        DcMaxEM = max(DcListEM.values())
        print DcMinEM
        print DcMaxEM


        if DcMaxEM == DcMinEM:
            DcMaxEM += 0.000001


        NormalizedDcEM = {}
        for key, value in DcListEM.items():
            DcEM = (value - DcMinEM) / (DcMaxEM - DcMinEM)
            Finalcollection[key] = ''
            NormalizedDcEM[key] = DcEM
            print key, DcEM

            # for Multi Match List
        DcListMM = {}
        NormalizedDcMM = {}
        try:
            for element in MultiMatchdict:
                DcListMM[MultiMatchdict[element]['_id']] = MultiMatchdict[element]['_score']
            print DcListMM
            DcMinMM = min(DcListMM.values())
            DcMaxMM = max(DcListMM.values())
            print DcMinMM
            print DcMaxMM


            if DcMaxMM == DcMinMM:
                DcMaxMM += 0.000001


            for key, value in DcListMM.items():
                DcMM = (value - DcMinMM) / (DcMaxMM - DcMinMM)
                Finalcollection[key] = ''
                NormalizedDcMM[key] = DcMM
                print key, DcMM

        except ValueError:
            pass

        # final Scoring and combining

        print Finalcollection

        CombMNZ = {}
        for key in Finalcollection:
            Dcgreater0 = 0
            CombMNZd = 0
            if key in NormalizedDcEM.keys():
                if NormalizedDcEM[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMM.keys():
                if NormalizedDcMM[key] is 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass
            if key in NormalizedDcEM.keys():
                CombMNZd = NormalizedDcEM[key] * Dcgreater0

            if key in NormalizedDcMM.keys():
                CombMNZd += NormalizedDcMM[key] * Dcgreater0

            CombMNZ[key] = CombMNZd

        print CombMNZ

    elif FuzzyMatchingMultipleFieldsbyWeight == None:
        print 'Exact match and fuzzy match is set'
        # combMNZ
        # For Exact Match List
        DcListEM = {}
        Finalcollection = {}
        for element in ExactMatchdict:
            DcListEM[ExactMatchdict[element]['_id']] = ExactMatchdict[element]['_score']
        print DcListEM
        DcMinEM = min(DcListEM.values())
        DcMaxEM = max(DcListEM.values())
        print DcMinEM
        print DcMaxEM

        if DcMaxEM == DcMinEM:
            DcMaxEM += 0.000001

        NormalizedDcEM = {}
        for key, value in DcListEM.items():
            DcEM = (value - DcMinEM) / (DcMaxEM - DcMinEM)
            Finalcollection[key] = ''
            NormalizedDcEM[key] = DcEM
            print key, DcEM

        # for Fuzzy Match List
        DcListFM = {}
        for element in FuzzyMatchdict:
            DcListFM[FuzzyMatchdict[element]['_id']] = FuzzyMatchdict[element]['_score']
        print DcListFM
        DcMinFM = min(DcListFM.values())
        DcMaxFM = max(DcListFM.values())
        print DcMinFM
        print DcMaxFM

        if DcMaxFM == DcMinFM:
            DcMaxFM += 0.000001

        NormalizedDcFM = {}
        for key, value in DcListFM.items():
            DcFM = (value - DcMinFM) / (DcMaxFM - DcMinFM)
            Finalcollection[key] = ''
            NormalizedDcFM[key] = DcFM
            print key, DcFM

        # final Scoring and combining

        print Finalcollection

        CombMNZ = {}
        for key in Finalcollection:
            CombMNZd = 0
            Dcgreater0 = 0
            if key in NormalizedDcEM.keys():
                if NormalizedDcEM[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcFM.keys():
                if NormalizedDcFM[key] is 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass
            if key in NormalizedDcEM.keys():
                CombMNZd = NormalizedDcEM[key] * Dcgreater0

            if key in NormalizedDcFM.keys():
                CombMNZd += NormalizedDcFM[key] * Dcgreater0

            CombMNZ[key] = CombMNZd

        print CombMNZ

    else:
        print "Everything is set"
        # combMNZ
        # For Fuzzy Match List
        Finalcollection = {}

        DcListFM = {}
        for element in FuzzyMatchdict:
            DcListFM[FuzzyMatchdict[element]['_id']] = FuzzyMatchdict[element]['_score']
        print DcListFM
        DcMinFM = min(DcListFM.values())
        DcMaxFM = max(DcListFM.values())
        print DcMinFM
        print DcMaxFM

        if DcMaxFM == DcMinFM:
            DcMaxFM += 0.000001

        NormalizedDcMF = {}
        for key, value in DcListFM.items():
            DcFM = (value - DcMinFM) / (DcMaxFM - DcMinFM)
            Finalcollection[key] = ''
            NormalizedDcMF[key] = DcFM
            print key, DcFM

        # for exact Match
        DcListEM = {}
        for element in ExactMatchdict:
            DcListEM[ExactMatchdict[element]['_id']] = ExactMatchdict[element]['_score']
        print DcListEM
        DcMinEM = min(DcListEM.values())
        DcMaxEM = max(DcListEM.values())
        print DcMinEM
        print DcMaxEM

        if DcMaxEM == DcMinEM:
            DcMaxEM += 0.000001


        NormalizedDcEM = {}
        for key, value in DcListEM.items():
            DcEM = (value - DcMinEM) / (DcMaxEM - DcMinEM)
            Finalcollection[key] = ''
            NormalizedDcEM[key] = DcEM
            print key, DcEM

        # for Multi Match List
        DcListMM = {}
        NormalizedDcMM = {}
        try:
            for element in MultiMatchdict:
                DcListMM[MultiMatchdict[element]['_id']] = MultiMatchdict[element]['_score']
            print DcListMM
            DcMinMM = min(DcListMM.values())
            DcMaxMM = max(DcListMM.values())
            print DcMinMM
            print DcMaxMM


            if DcMaxMM == DcMinMM:
                DcMaxMM += 0.000001



            for key, value in DcListMM.items():
                DcMM = (value - DcMinMM) / (DcMaxMM - DcMinMM)
                Finalcollection[key] = ''
                NormalizedDcMM[key] = DcMM
                print key, DcMM
        except ValueError:
            pass

        # final Scoring and combining

        print Finalcollection

        CombMNZ = {}
        for key in Finalcollection:
            CombMNZd = 0
            Dcgreater0 = 0

            if key in NormalizedDcEM.keys():
                if NormalizedDcEM[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMF.keys():
                if NormalizedDcMF[key] == 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcMM.keys():
                if NormalizedDcMM[key] is 0.0:
                    pass
                else:
                    Dcgreater0 += 1
            else:
                pass

            if key in NormalizedDcEM.keys():
                CombMNZd = NormalizedDcEM[key] * Dcgreater0

            if key in NormalizedDcMF.keys():
                CombMNZd += NormalizedDcMF[key] * Dcgreater0

            if key in NormalizedDcMM.keys():
                CombMNZd += NormalizedDcMM[key] * Dcgreater0

            CombMNZ[key] = CombMNZd

        print CombMNZ

    # sort the dictionary
    CombMNZ1 = sorted(CombMNZ.items(), key=operator.itemgetter(1), reverse=True)
    SortedCombMNZ = OrderedDict()
    for element in CombMNZ1:
        SortedCombMNZ[element[0]] = element[1]

    print SortedCombMNZ

    FinalDocSet = OrderedDict()
    for element in SortedCombMNZ.items():
        for element1 in FuzzyMatchdict:
            if element[0] == FuzzyMatchdict[element1]['_id']:
                FinalDocSet[element[0]] = FuzzyMatchdict[element1]['_source']
                # FinalDocSet[element][key] = 1

        for element1 in ExactMatchdict:
            if element[0] == ExactMatchdict[element1]['_id']:
                FinalDocSet[element[0]] = ExactMatchdict[element1]['_source']
                # FinalDocSet[element][key] = 1

        for element1 in MultiMatchdict:
            if element[0] == MultiMatchdict[element1]['_id']:
                FinalDocSet[element[0]] = MultiMatchdict[element1]['_source']
                # FinalDocSet[element][key] = 1

    print FinalDocSet


    #NumberofSets = 3
    return render_template('search.html', FinalDocSet=FinalDocSet, table=table)
    #return responseExactMatch.text

if __name__ == '__main__':
    app.run()
