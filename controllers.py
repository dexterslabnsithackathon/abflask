from flask import Flask, render_template, request, redirect, make_response, session, escape
from datetime import datetime
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
                            'total':x['total']
                        }
                    }
                )
                return render_template(x['variant'][flag]+'.html',c=flag)
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
                return render_template(x['variant'][x['flag']]+'.html',c=flag)
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
def success():
    return render_template('success.html')

@app.route('/success/<var>')
def successv(var):
    f = db.abtestdata.find();
    var = int(var)
    for x in f:
        x['conv'][var] = x['conv'][var] + 1 
        db.abtestdata.update(
            { 'route': 'index' },
            { '$set': 
                {
                    'conv':x['conv']
                }
            }
        )
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
    tarurl = request.form['textinput']
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
