from flask import Blueprint, render_template, redirect, request, session, url_for, flash, abort
from .utils.forms import *
from .utils.functions import *
from werkzeug.utils import secure_filename
import json

route_config = json.load(open('core/route_config.json'))
core = Blueprint('core', __name__, template_folder=route_config['template_folder'], static_folder=route_config['static_folder'], static_url_path=route_config['static_url_path'])
user_handler = UserHandler()
upload_handler = UploadHandler()
extension_handler = ExtensionsHandler()
site_config = SiteConfigHandler()

@core.route('/dashboard/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        login_result = user_handler.login(form.username.data, form.password.data)
        if login_result != False:
            session['login_id'] = login_result
            return redirect(url_for('core.home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html', form=form, site_config = site_config.get_site_config())

@core.route('/dashboard/register', methods=['GET', 'POST'])
def register():

    if site_config.get_site_config()['ALLOW_REGISTER'] == False:
        abort(404)

    form = RegisterForm()

    if form.validate_on_submit():
        result = user_handler.create_user(form.username.data, form.password.data, form.firstname.data, form.lastname.data)
        if result == True:
            return redirect(url_for('core.login'))
        else:
            flash(result, 'error')
    return render_template('register.html', form = form, site_config = site_config.get_site_config())

@core.route('/dashboard')
@user_handler.login_required('core.login')
def home():
    return render_template('home.html', site_config = site_config.get_site_config(), user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())

@core.route('/dashboard/settings', methods = ['GET', 'POST'])
@user_handler.login_required('core.login')
def settings():
    profile_form = UserProfile()
    password_form = ChangePassword()
    avatar_form = AvatarUpload()
    site_config_form = SiteConfigForm()
    if site_config_form.validate_on_submit():
        config = site_config.get_site_config()
        config['SITE_NAME'] = site_config_form.site_name.data
        config['ALLOW_REGISTER'] = site_config_form.site_allow_registration.data
        site_config.edit_site_config(config)
        flash('Site configuration updated successfully.', 'site_config')

    if avatar_form.validate_on_submit():
        file = avatar_form.avatar_upload.data
        if file:
            if file.filename == '':
                flash('No file selected. Please select a file to upload.', 'avatar_error')
            elif not upload_handler.validate_file_type(file.filename, ['png', 'jpg', 'jpeg', 'gif', 'svg']):
                flash('Invalid file type. Please upload an image file.', 'avatar_error')
            else:
                filename = secure_filename(file.filename)
                user_id = user_handler.get_by_login_id(session.get('login_id'), safe=True)[0]
                save_filename = f"{user_id}.{upload_handler.get_file_extension(filename)}"
                file.save(f'core/static/images/avatars/{save_filename}')
                user_handler.change_avatar(session.get('login_id'), save_filename)
                flash('Avatar updated successfully.', 'avatar_success')
                
    if profile_form.validate_on_submit():
        result = user_handler.change_profile(session.get('login_id'), profile_form.firstname.data, profile_form.lastname.data)
        if result['status'] == 'success':
            flash('Profile updated successfully.', 'profile')
            
    if password_form.validate_on_submit():
        result = user_handler.change_password(session.get('login_id'), password_form.current_password.data, password_form.new_password.data, password_form.confirm_password.data)
        if result['status'] == 'success':
            flash('Password changed successfully.', 'password_form_success')
        else:
            flash(result['message'], 'password_form_error')
    return render_template('settings.html',  site_config = site_config.get_site_config(), site_config_form = site_config_form, avatar_form = avatar_form, password_form = password_form, profile_form = profile_form,user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_tabs = extension_handler.get_tabs())

@core.route('/dashboard/extensions', methods=['GET', 'POST'])
@user_handler.login_required('core.login')
def extensions():
    extension_upload_form = ExtensionUploadForm()
    prefs = ExtensionsCRUD(extension_handler.get_blueprints())
    extension_checkboxes = prefs(request.form)

    if request.method == 'POST' and extension_checkboxes.validate():
        data = dict(extension_checkboxes.data)
        data.pop('submit')
        selected_blueprints = [selected_blueprints for selected_blueprints in data if data[selected_blueprints] == True ]
        action = extension_checkboxes.action_field.data
        if action == 'enable':
            for blueprint in selected_blueprints:
                extension_handler.change_extension_enabled(blueprint, True)
        elif action == 'disable':
            for blueprint in selected_blueprints:
                extension_handler.change_extension_enabled(blueprint, False)
        elif action == 'delete':
            for blueprint in selected_blueprints:
                extension_handler.delete_extension_database(blueprint)
                extension_handler.delete_extension_folder(blueprint)

    if extension_upload_form.validate_on_submit():
        
        file = extension_upload_form.extension.data
        if file.filename == '':
            flash('No file selected. Please select a file to upload.', 'error')
        elif not upload_handler.validate_file_type(file.filename, ['zip']):
            flash('Invalid file type. Please upload a .zip file.', 'error')
        else:
            filename = secure_filename(file.filename)
            file.save('temp/' + filename)
            if extension_handler.extract_zip(filename):
                folder_name = filename.rsplit('.', 1)[0]
                is_extension_valid = extension_handler.validate_extension(folder_name)
                if is_extension_valid['status'] == 'error':
                    flash(is_extension_valid['message'], 'error')
                else:
                    extension_handler.add_to_directory(folder_name)

                    flash('Extension added successfully. Please restart to activate the extension.', 'success')
            else:
                flash('Invalid file type. Please upload a .zip file.', 'error')
    return render_template('extensions.html', site_config = site_config.get_site_config(), extension_upload_form = extension_upload_form, user_data=user_handler.get_by_login_id(session.get('login_id'), safe=True), extension_checkboxes = extension_checkboxes, extensions_list = extension_handler.list_extensions(), extension_tabs = extension_handler.get_tabs())

@core.route('/logout')
@user_handler.login_required('core.login')
def logout():
    user_handler.logout(session.get('login_id'))
    return redirect(url_for('core.login'))


