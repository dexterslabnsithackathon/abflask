from flask import Flask, render_template, request, redirect, make_response, session, escape
from datetime import datetime
import os
# from flask.ext.wtf import Form
# from flask_wtforms import Form, BooleanField, TextField, PasswordField, validators
from pymongo import MongoClient

# class RegistrationForm(Form):
#     currurl = TextField('Current Url', [validators.Length(min=4)])
#     tarurl = TextField('Target Url', [validators.Length(min=4)])
#     novariants = IntegerField('No.of variants', [validators.Required()])
#     namevariant = TextField('Enter Variant',[validators.Required()])
#     accept_tos = BooleanField('I accept the TOS', [validators.Required()])

app = Flask("ABTest")
client=MongoClient('localhost',27017);
db = client['admin']

def export(x):
    file = x['route'] + '.txt'
    os.remove(file[1:])
    fo=open(file[1:],"w")
    for n in range(x['num']):
        fo.write(x['variant'][n])
        fo.write("\nTotal: ")
        fo.write('%d' % x['total'][n])
        fo.write("\tConverted: ")
        fo.write('%d' % x['conv'][n])
        fo.write("\tConvert Percentage: ")
        if(x['total'][n]==0 or x['conv'][n]==0):
            y= repr(0)
        else:
            y = repr(float(x['conv'][n])/float(x['total'][n])) 
        fo.write(y)
        fo.write("\n")

def framework(path):
    f = db.abtestdata.find();
    pathname = path[1:] + '.html'
    for x in f:
        if x['route']==request.path:
            #old user
            if request.path in session:
                flag=session[request.path]
                x['total'][flag] = x['total'][flag] + 1 
                db.abtestdata.update(
                    { 'route': request.path },
                    { '$set': 
                        {
                            'total':x['total']
                        }
                    }
                )
                export(x)
                pathname = x['variant'][flag]+'.html'
            else:    
            # new user
                flag=x['flag']
                x['total'][flag] = x['total'][flag] + 1
                flag = (flag+1)%x['num'] 
                session[request.path]=x['flag']
                db.abtestdata.update(
                    { 'route': request.path },
                    { '$set': 
                        {
                            'flag':flag,
                            'total':x['total']
                        }
                    }
                )
                export(x)
                pathname = x['variant'][x['flag']]+'.html'
        break
    return pathname



@app.route('/')
def slash():
    return redirect('/index');

@app.route('/index')
def index():
    path = framework(request.path)
    return render_template(path)

@app.route('/variantA')
def variantA():
    return render_template('variantA.html')

@app.route('/variantB')
def variantB():
    return render_template('variantB.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/success/<var>')
def successv(var):
    f = db.abtestdata.find();
    var = int(var)
    for x in f:
        x['conv'][var] = x['conv'][var] + 1 
        db.abtestdata.update(
            { 'route': '/index' },
            { '$set': 
                {
                    'conv':x['conv']
                }
            }
        )
        export(x)
        break

    return redirect('/success')

@app.route('/result')
def result():
    f = db.abtestdata.find();
    return render_template('result.html',f=f)
    
@app.route('/admin')
def admin():
    form = "Nothing Here!"
    return render_template('admin.html',form=form)

@app.route('/admin/submit' , methods=['GET', 'POST'])
def adminsub():
    tarurl = '/'+request.form['textinput']
    sucurl = request.form['textinput1']
    vara = request.form['var1']
    varb = request.form['var2']
    variant = [vara,varb]
    total = [0,0]
    conv= [0,0]
    success = ["url",sucurl]
    time = [2,6]
    endtime=datetime.now()
    flag=0

    result = db.abtestdata.insert_one(
    {
        "variant": variant,
        "route": tarurl,
        "success": success,
        "total": total,
        "conv": conv,
        "time": time,
        "endtime": endtime,
        "flag": flag,
        "num": 2,
        "deleted": 0
    }
)

    return render_template('admin.html')

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

if __name__ == "__main__":
    app.run(debug=True)
