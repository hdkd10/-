from flask import Flask, request, render_template, send_file
import yt_dlp
import os
import uuid

app = Flask(name)

videos = {}

@app.route('/', methods=['GET', 'POST'])
def index():
if request.method == 'POST':
url = request.form['url']
uid = str(uuid.uuid4())

try:
ydl_opts = {
'quiet': True,
'skip_download': True,
'noplaylist': True,
}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
info = ydl.extract_info(url, download=False)
formats = []
for f in info.get('formats', []):
if f.get('url'):
label = ''
if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
label = '🎞️ فيديو + صوت'
elif f.get('vcodec') != 'none':
label = '🎥 فيديو فقط'
elif f.get('acodec') != 'none':
label = '🔊 صوت فقط'
f['label'] = f"{label} - {f.get('format_note', '')} - {f.get('ext', '')}"
formats.append(f)

best = next((f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none'), formats[0])

videos[uid] = {      
        'info': info,      
        'formats': formats,      
    }      

    return render_template('index.html', info=info, formats=formats, uid=uid, preview=best)

except Exception as e:
return render_template('index.html', msg=str(e))

return render_template('index.html')

@app.route('/download/<vid>')
def download(vid):
fmt = request.args.get('format')
if vid not in videos:
return "📛 الفيديو غير موجود"

info = videos[vid]['info']
filename = f"{vid}"

ydl_opts = {
'format': fmt,
'outtmpl': f"{filename}.%(ext)s",
}

try:
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
ydl.download([info['webpage_url']])

for ext in ['mp4', 'webm', 'mkv', 'mp3', 'm4a']:
path = f"{filename}.{ext}"
if os.path.exists(path):
return send_file(path, as_attachment=True)

return "❌ لم يتم العثور على الملف"

except Exception as e:
return f"⚠️ خطأ أثناء التحميل: {str(e)}"

if name == 'main':
app.run(host='0.0.0.0', port=8080)
