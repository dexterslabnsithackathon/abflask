from flask import Flask, render_template, request, redirect, make_response, session, escape
import os
from pymongo import MongoClient
# from pymongo import mongo
app = Flask("ABTest")
client=MongoClient('localhost',27017);
db = client['admin']

@app.route('/')
@app.route('/index')
def index():
    f = db.abtestdata.find();
    for x in f:
        if x['route']=='index':
            #old user
            if 'index' in session:
                flag=session['index']
                x['total'][flag] = x['total'][flag] + 1 
                db.abtestdata.update(
                    { 'route': 'index' },
                    { '$set': 
                        {
                            'flag':flag,
                            'total':x['total']
                        }
                    }
                )
                return render_template(x['variant'][x['flag']]+'.html')
            else:    
            # new user
                flag=x['flag']
                x['total'][flag] = x['total'][flag] + 1
                flag = (flag+1)%x['num'] 
                session['index']=x['flag']
                db.abtestdata.update(
                    { 'route': 'index' },
                    { '$set': 
                        {
                            'flag':flag,
                            'total':x['total']
                        }
                    }
                )
                return render_template(x['variant'][x['flag']]+'.html')
        break
    # return "How did I get here? 404"
    return "Old Index Page without Variants!"

@app.route('/variantA')
def variantA():
    return render_template('variantA.html')

@app.route('/variantB')
def variantB():
    return render_template('variantB.html')

@app.route('/success')
@app.route('/success/<var>')
def success(var):
    f = db.abtestdata.find();
    var = int(var)
    for x in f:
        x['conv'][var] = x['conv'][var] + 1 
        #create cookie
        db.abtestdata.update(
            { 'route': 'index' },
            { '$set': 
                {
                    'conv':x['conv']
                }
            }
        )
        break

    return render_template('success.html')

@app.route('/result')
def result():
    f = db.abtestdata.find();
    return render_template('result.html',f=f)

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
    app.run(debug=True)
