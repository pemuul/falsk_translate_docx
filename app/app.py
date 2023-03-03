import json
from flask import Flask, request
from flask import render_template, make_response, redirect, url_for, send_file
import tasks
import os
from datetime import datetime


APP = Flask(__name__)
APP.config['UPLOAD_FOLDER'] = 'static'
file_id = 0


@APP.route('/',methods = ['GET'])
def index(): 
    ''' основная страница '''

    return render_template("index.html")


@APP.route('/',methods = ['POST'])
def save_img(): 
    ''' сохранение файла полученного с формы '''

    global file_id

    # получаем фото с формы
    file_doc = request.files['file_doc']

    file_type = file_doc.filename.split('.')[-1]

    if not file_type in ['docx']:
        return redirect(url_for('index'))
    
    file_name = f'{file_id}.{file_type}'
    file_id += 1
    
    file_doc.save(os.path.join(APP.config['UPLOAD_FOLDER'], file_name))

    file_doc_loc = APP.config['UPLOAD_FOLDER'] + '/' + file_name

    # создаём задачу 
    job = tasks.translate_docx_file.delay(file_doc_loc)
    
    # JOBID - id нашей задачи, в которой происходит обработка
    return render_template("download.html", JOBID=job.id)


@APP.route('/progress')
def progress():
    ''' проверяем, не выполнилась ли наша задача '''

    # получаем номер задачи из запроса
    jobid = request.values.get('jobid')

    if not jobid:
        return '{}'
    
    # получаем заму задачу по её номеру
    job = tasks.get_job(jobid)

    print(job.state, job.result)

    if job.state == 'PROGRESS':
        return json.dumps(dict(
            state=job.state,
            progress=job.result['current'],
        ))
    elif job.state == 'SUCCESS':
        return json.dumps(dict(
            state=job.state,
            progress=1.0,
        ))
        
    return '{}'


@APP.route('/result')
def result():
    jobid = request.values.get('jobid')
    if jobid:
        job = tasks.get_job(jobid)
        png_output = job.get()
        png_output="../"+png_output
        return png_output
    else:
        return 404


@APP.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = APP.config['UPLOAD_FOLDER'] + '/' + filename
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    APP.run(host='0.0.0.0')
