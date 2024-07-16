from core.utils.logging import Logging
from core.utils.functions import ExtensionsHandler
from flask import Flask, request, redirect, url_for
import importlib
import os
import json
from core.views import core


app = Flask(__name__)
app.secret_key = 'secret_key' # Change this for production
app.register_blueprint(core)
log = Logging()
extension_handler = ExtensionsHandler()

@app.errorhandler(404)
def page_not_found(e):
    if request.path == '/':
        
        return redirect(url_for('core.login'))
    return "Error 404: Page not found", 404


for extension in os.listdir('extensions'):
    if not os.path.isdir(f"extensions/{extension}"):
        log.log(f"{extension} is not a directory skipping this file", "warning")
        continue
    elif not os.path.isfile(f"extensions/{extension}/extension_config.json"):
        log.log(f"{extension} does not have a extension_config.json file skipping this file", "warning")
        continue
    else:
        extension_config = json.load(open(f"extensions/{extension}/extension_config.json"))
        if extension_config['enabled'] is False:
            log.log(f"{extension} is disabled skipping this file", "warning")
            continue
        else:
            path = f'extensions.{extension}.views'
            module = importlib.import_module(path, package='app')
            app.register_blueprint(getattr(module, extension_config['blueprint']), url_prefix=extension_config['url_prefix'])
            log.log(f"Registered {extension_config['url_prefix']} to {path}", "success")
            log.log(f"Registered {extension} static folder to {extension_config['static_url_path']}", "success")

if __name__ == '__main__':
    config = json.load(open('config.json'))
    app.run(debug=config['DEBUG'], port=config['PORT'], host=config['HOST'])
    