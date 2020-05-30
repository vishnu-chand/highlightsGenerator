import os
import pickle
from glob import glob
from wtforms import *
from flask_wtf import FlaskForm
from datetime import datetime as dt
from highlightsGenerator import getHighlights
from flask import Flask, flash, render_template, request
from youtube_dl import YoutubeDL

# for vid, (data, request) in pickle.load(open('audios/cache.pkl', 'rb')).items():
#     print(vid, request)
# print("12  app : ", );quit()

'''
https://www.youtube.com/watch?v=jPfeLG2fPeU
https://www.youtube.com/watch?v=i0RrKolSMgw&t=91s
https://www.youtube.com/watch?v=QD2hxpQd_b0&t=232s
https://www.youtube.com/watch?v=EgWqoWG5V80
'''

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'audios'
app.config['SECRET_KEY'] = 'asfasdmuju56uj6jn65mnb43r2cw#$$.2017' + str(dt.now().timestamp())  # time salted secret key


def downloadVideo(url, vid, vfmt):
    vdir = app.config['UPLOAD_FOLDER']
    timestamp = str(dt.now().timestamp()).replace('.', '')
    vpath = f'{vdir}/{vid}_{timestamp}'
    downloader = f"youtube-dl '{url}' -o '{vpath}.%(ext)s'"
    os.system(f"{downloader} -f {vfmt} --print-json --restrict-filenames -x")
    vpaths = glob(f'{vpath}.*')
    vpath = None
    if vpaths:
        vpath = vpaths[0]
    return vpath


def getMeta(url):
    with YoutubeDL() as ydl:
        try:
            vinfo = ydl.extract_info(url, download=False)
        except:
            vinfo = {}
    vid, isLongVideo, vfmt = vinfo.get("id"), False, None
    if vid:
        try:
            vfmt = vinfo['formats'][0]['format_id']
            isLongVideo = vinfo.get('duration') > 720
        except:
            pass
    return vid, isLongVideo, vfmt


class ArgsForm(FlaskForm):
    url = StringField("URL:", default='https://www.youtube.com/watch?v=jPfeLG2fPeU',
                      validators=[validators.DataRequired("Enter the url of the match video"),
                                  validators.URL("Enter valid url of the match video")])
    start = IntegerField("Start seconds: ", default=3, validators=[validators.DataRequired()])
    stop = IntegerField("Stop seconds: ", default=-25, validators=[validators.DataRequired()])
    submit = SubmitField("Submit")


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ArgsForm()
    if request.method == 'POST' and form.validate():
        clips, nRequest, url, cachePath = None, 0, request.form['url'], f"{app.config['UPLOAD_FOLDER']}/cache.pkl"
        try:
            start, stop = int(request.form['start']), int(request.form['stop'])
            with open(cachePath, 'rb') as book:
                jdata = pickle.load(book)
            vdata = getCache(url, start, stop, jdata, vid=None)
            if vdata:
                clips, nRequest = vdata
            else:
                vid, isLongVideo, vfmt = getMeta(url)
                vdata = getCache(url, start, stop, jdata, vid=vid)
                if vdata:
                    clips, nRequest = vdata
                else:                    
                    if isLongVideo:
                        flash('Pass video less than 10 min')
                        vfmt = None
                    if vfmt:
                        vpath = downloadVideo(url, vid, vfmt)
                        if vpath:
                            clips = getHighlights(vpath, vid, start, stop, 3)
                            os.remove(vpath)
                if clips is not None:
                    jdata[f'{vid}_{start}_{stop}'] = [clips, nRequest + 1]
                    with open(cachePath, 'wb') as book:
                        pickle.dump(jdata, book)
            if not clips:
                flash(f'Sorry!! process failed with "{url}". Try different url...')
        except:
            flash("Sorry!!, server busy not able to process your request now...")
        form.url.data = None
        return render_template("index.html", form=form, clips=clips or [])
    return render_template("index.html", form=form)


def getCache(url, start, stop, jdata, vid):
    try:
        if vid is None:
            vid = url.split('/')[-1].split('v=')[-1]
        vdata = jdata.get(f'{vid}_{start}_{stop}')
    except:
        vdata = None
    return vdata


if __name__ == '__main__':
    app.run(threaded=True, port=4378, host='127.23.0.1')
    # app.run(threaded=True, port=4378, debug=True)
    # from waitress import serve
    # serve(app, host='127.0.0.1', port=4378)
