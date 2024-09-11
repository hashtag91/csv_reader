from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pandas as pd
import numpy as np
import os
import plotly.express as px


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.mkdir(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

current = 1

@app.route(f'/upload/', methods=['POST'])
def upload_file():
    page = request.args.get('page',1, type=int)
    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],file.filename)
    file.save(dst=file_path)
    return redirect(url_for('display',file_path=file_path, filename=file.filename, page=page))

@app.route("/display/<filename>/?page=<int:page>", methods=['GET'])
def display(filename,page):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    df = pd.read_csv(file_path)
    if not 'id' in df.columns:
        my_id = np.arange(1,df.shape[0]+1)
        df.insert(0,'id',my_id)
    shape = df.shape
    print(shape)
    rows_per_page = 100
    current_page = int(request.args.get('page',1))
    global current
    current = page
    total_rows = int(df.shape[0])
    number_of_page = (total_rows // rows_per_page)
    print(number_of_page)
    start = (page-1)*rows_per_page
    end = start + rows_per_page
    data = df[start:end]
    data_dict = data.to_dict('records')
    return render_template('csvread.html',filename=filename, data=data_dict, page_number=number_of_page, current_page=current_page, page=page, shape=shape)

@app.route('/describe/<filename>')
def describe(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    df = pd.read_csv(file_path)
    description = df.describe()
    indexes = description.index.values
    description.insert(0,'statistic',indexes)
    data = description.to_dict('records')
    shape = description.shape
    return render_template("describe.html",data=data,filename=filename, page=1, page_number=1, shape=shape)

def plots(col_count,method,dict,p_title,_x,_y=0):
    if col_count == "multiple":
        if method == "count":
            group = dict.groupby(_x)[_y].count()
            axe_x = group
            axe_y = group.index.values
            fig = px.bar(dict, x=axe_y, y=axe_x, color_discrete_sequence=['blue'],labels={'x':_x, 'y':_y})
            fig.update_layout(
                paper_bgcolor = "rgb(255,255,255)",
                plot_bgcolor = "rgb(155, 190, 199)",
                font_color = "rgb(0,0,0)",
                font_family = 'verdana',
                font_size = 20,
                title={
                    'text': "Custom Plot Title",  # Title text
                    'y':0.9,  # Position on the y-axis (0=bottom, 1=top)
                    'x':0.5,  # Position on the x-axis (center is 0.5)
                    'xanchor': 'center',  # Horizontal alignment
                    'yanchor': 'top'      # Vertical alignment
                },
                title_font=dict(
                    family="Arial, sans-serif",  # Font family
                    size=24,                    # Font size
                    color="RebeccaPurple"        # Font color
                )
            )
            fig.write_html('./static/pages/plot.html')
            return "generated"
        elif method == "sum":
            group = dict.groupby(_x)[_y].sum()
            axe_x = group
            axe_y = group.index.values
            fig = px.bar(dict, x=axe_y, y=axe_x, color_discrete_sequence=['blue'],labels={'x':_x, 'y':_y})
            fig.update_layout(
            paper_bgcolor = "rgb(255,255,255)",
            plot_bgcolor = "rgb(155, 190, 199)",
            font_color = "rgb(0,0,0)",
            font_family = 'verdana',
            font_size = 20
            )
            fig.write_html('./static/pages/plot.html')
            return "generated"
        else:
            return None
    else:
        group = dict.groupby(_x).count()
        print(group)
        axe_x = group['id']
        axe_y = group.index.values
        fig = px.bar(dict, x=axe_y, y=axe_x, color_discrete_sequence=['blue'],labels={'x':_x, 'y':'count'})
        fig.update_layout(
            paper_bgcolor = "rgb(255,255,255)",
            plot_bgcolor = "rgb(155, 190, 199)",
            font_color = "rgb(0,0,0)",
            font_family = 'verdana',
            font_size = 20
        )
        fig.write_html('./static/pages/plot.html')
        return "generated"

@app.route('/charts/<filename>')
def chart(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    df = pd.read_csv(file_path)
    describe = df.describe()
    num_col = describe.columns.to_list()
    non_num_col = df.columns.tolist()
    for x in num_col:
        non_num_col.remove(x)
    return render_template('chart.html',page=1, page_number=1, filename=filename, shape=df.shape, num_col=num_col, non_num_col=non_num_col, generation=None)

@app.route('/charts/<filename>', methods=['GET','POST'])
def plotchart(filename):
    if os.path.exists(url_for('static',filename='pages/plot.html')):
        os.remove(url_for('static',filename='pages/plot.html'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    df = pd.read_csv(file_path)
    describe = df.describe()
    num_col = describe.columns.to_list()
    non_num_col = df.columns.tolist()
    for x in num_col:
        non_num_col.remove(x)
    col = request.form.get('select')
    print(col)
    operat = request.form.get('operation')
    x = request.form.get('axis-x')
    y = request.form.get('axis-y')
    title = request.form.get('title')
    plots(col, operat, df, title, x,y)
    gen = 'generated'
    return render_template('chart.html',page=1, page_number=1, filename=filename, shape=df.shape, num_col=num_col, non_num_col=non_num_col, generation=gen)

if __name__ == ("__main__"):
    app.run(debug=True)