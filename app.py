from flask import Flask, render_template, request, send_file
import xml.etree.ElementTree as ET
import yaml
import io

app = Flask(__name__)

def xml_to_dict(element):
    result = {}
    for child in element:
        if len(child) == 0:
            result[child.tag] = child.text
        else:
            result[child.tag] = xml_to_dict(child)
    return result

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='ファイルがアップロードされていません。')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='ファイルが選択されていません。')
        
        if not file.filename.endswith('.xml'):
            return render_template('index.html', error='XMLファイルのみアップロード可能です。')
        
        try:
            xml_content = file.read()
            root = ET.fromstring(xml_content)
            data = xml_to_dict(root)
            
            yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
            
            return send_file(
                io.BytesIO(yaml_content.encode('utf-8')),
                mimetype='application/x-yaml',
                as_attachment=True,
                attachment_filename='converted.yaml'
            )
        except ET.ParseError:
            return render_template('index.html', error='XMLの解析エラーが発生しました。')
        except Exception as e:
            return render_template('index.html', error=f'エラーが発生しました: {str(e)}')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)