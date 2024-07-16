import sqlite3
import bcrypt
import os
import zipfile
from functools import wraps
from flask import session, flash, redirect, url_for
import shutil
import random
import string
import json

class SiteConfigHandler:
    def __init__(self):
        self.site_config = json.load(open('config.json')) 

    def get_site_config(self):
        return self.site_config

    def edit_site_config(self, config: dict):
        self.site_config = config
        with open('config.json', 'w') as file:
            json.dump(config, file, indent=4)
        
        return True

class ExtensionsHandler:
    def __init__(self):
        self.connection = sqlite3.connect('db.sqlite3', check_same_thread=False)

    def show_temp(self) -> list:
        return os.listdir('temp')

    def change_extension_enabled(self, blueprint: str, is_enabled: bool = True) -> None:
        cursor = self.connection.cursor()
        cursor.execute("UPDATE extensions SET enabled = ? WHERE blueprint = ?", (is_enabled, blueprint))
        self.connection.commit()
        cursor.close()

    def get_blueprints(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute("SELECT blueprint FROM extensions")
        blueprints = cursor.fetchall()
        cursor.close()
        return [blueprint[0] for blueprint in blueprints]

    def add_tab_to_database(self, blueprint: str, navigation_name: str, redirect_to: str, forced: bool = False) -> None:
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO navigation (blueprint, navigation_name, redirect_to) VALUES (?, ?, ?)", (blueprint, navigation_name, redirect_to))
        self.connection.commit()
        cursor.close()

    def add_config_to_database(self, values: tuple, forced: bool = False) -> None:
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO extensions (enabled, name, version, description, url_prefix, blueprint, template_folder, static_folder, static_url_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
        self.connection.commit()
        cursor.close()

    def extract_zip(self, filename: str) -> bool:
        try:
            with zipfile.ZipFile('temp/' + filename, 'r') as zip_ref:
                zip_ref.extractall('temp/' + filename.rsplit('.', 1)[0])
            return True
        except zipfile.BadZipFile:
            return False
    
    def delete_extension_database(self, blueprint_name: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM extensions WHERE blueprint = ?", (blueprint_name,))
        cursor.execute("DELETE FROM navigation WHERE blueprint = ?", (blueprint_name,))
        self.connection.commit()
        cursor.close()

    def delete_extension_folder(self, blueprint_name: str) -> bool:
        if os.path.exists(f"extensions/{blueprint_name}"):
            shutil.rmtree(f"extensions/{blueprint_name}")
            return True
        return False

    def get_tabs(self) -> list:
        return_tabs = {}
        cursor = self.connection.cursor()
        # get all tabs and add the name from extensions table
        sql = "SELECT navigation.blueprint, navigation.navigation_name, navigation.redirect_to, extensions.name FROM navigation JOIN extensions ON navigation.blueprint = extensions.blueprint WHERE extensions.enabled = True"
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        for result in results:
            if result[3] not in return_tabs:
                return_tabs[result[3]] = []
            return_tabs[result[3]].append({
                'tab_name': result[1],
                'url_for': result[2]
            })
        return return_tabs

    def validate_extension(self, extension_name: str, is_installed: bool = False) -> dict:
        if is_installed:
            extension_path = f"extensions/{extension_name}"
        else:
            extension_path = f"temp/{extension_name}"
        if not os.path.exists(extension_path):
            return {
                'status': 'error',
                'message': 'Unable to find extracted folder'
            }
        if not os.path.exists(f"{extension_path}/extension_config.json"):
            return {
                'status': 'error',
                'message': 'Unable to find extension_config.json file'
            }
        return {
            'status': 'success',
            'message': 'Extension is valid'
        }

    def add_to_directory(self, extension_name: str) -> bool:
        if os.path.exists(f"extensions/{extension_name}"):
            shutil.rmtree(f"extensions/{extension_name}")
        shutil.move('temp/' + extension_name, 'extensions/' + extension_name)
        return True
    
    def get_extension_version(self, blueprint_name: str) -> str:
        cursor = self.connection.cursor()
        cursor.execute("SELECT version FROM extensions WHERE blueprint = ?", (blueprint_name,))
        version = cursor.fetchone()
        cursor.close()
        return version[0]

    def get_extension_config(self, blueprint_name: str) -> tuple:
        # load extension from sqlite3
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM extensions WHERE blueprint = ?", (blueprint_name,))
        extension = cursor.fetchone()
        cursor.close()
        return extension

    def list_extensions(self) -> list:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM extensions")
        extensions = cursor.fetchall()
        cursor.close()
        return list(extensions)


class UploadHandler:
    def validate_file_type(self, filename, allowed_extensions) -> bool:
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    def get_file_extension(self, filename: str) -> str:
        return filename.split('.')[-1]

    def generate_filename(self, length: int = 10):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(length))

    def delete_file(self, filename: str) -> None:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
class UserHandler:
    def __init__(self):
        self.connection = sqlite3.connect('db.sqlite3', check_same_thread=False)

    def login_required(self, login_page: str):
        def decorator(function):
            @wraps(function)
            def decorated_function(*args, **kwargs):
                # Start of wrapper
                login_id = session.get('login_id')
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM users WHERE login_id = ?", (login_id,))
                user = cursor.fetchone()
                cursor.close()
                if user:
                    return function(*args, **kwargs)
                else:
                    flash('You must be logged in to access this page.', 'error')
                    return redirect(url_for(login_page))
            return decorated_function
        return decorator

    def change_profile(self, login_id: str, firstname: str, lastname: str) -> dict:
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET firstname = ?, lastname = ? WHERE login_id = ?", (firstname, lastname, login_id))
        self.connection.commit()
        cursor.close()
        return {
            'status': 'success',
            'message': 'Profile has been updated'
        }

    def change_avatar(self, login_id: str, avatar_filename: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET avatar_file = ? WHERE login_id = ?", (avatar_filename, login_id))
        self.connection.commit()
        cursor.close()

    def change_password(self, login_id: str, current_password: str, new_password: str, confirm_password: str) -> dict:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE login_id = ?", (login_id,))
        user = cursor.fetchone()
        cursor.close()
        if not user:
            return {
                'status': 'error',
                'message': 'User not found'
            }
        
        if current_password == new_password:
            return {
                'status': 'error',
                'message': 'New password cannot be the same as the old password'
            }
        if new_password != confirm_password:
            return {
                'status': 'error',
                'message': 'New password must be equal to confirm password'
            }
        if not bcrypt.checkpw(current_password.encode('utf-8'), user[4].encode('utf-8')):
            return {
                'status': 'error',
                'message': 'Current password is incorrect.'
            }
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET password = ?, salt = ? WHERE login_id = ?", (hashed.decode(), salt.decode(), login_id))
        self.connection.commit()
        cursor.close()
        return {
            'status': 'success',
            'message': 'Password has been changed'
        }


        


    def create_user(self, username: str, password: str, firstname: str, lastname: str, user_type: str = 'user'):
        try:
            
            cursor = self.connection.cursor()
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            values = (username, hashed.decode(), salt.decode(), firstname, lastname, 'NONE', user_type)
            cursor.execute("INSERT INTO users (username, password, salt, firstname, lastname, login_id, user_type) VALUES (?, ?, ?, ?, ?, ?, ?)", values)
            self.connection.commit()
            cursor.close()
            return True
        except sqlite3.IntegrityError:
            return {
                'status': 'error',
                'message': 'User already exists'
            }
    
    def login(self, username: str, password: str):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
                login_id = bcrypt.gensalt().decode()
                cursor = self.connection.cursor()
                cursor.execute("UPDATE users SET login_id = ? WHERE username = ?", (login_id, username))
                self.connection.commit()
                cursor.close()
                return login_id
        return False

    def get_by_login_id(self, login_id:str, safe: bool = True):
        cursor = self.connection.cursor()
        if safe:
            cursor.execute("SELECT id, username, firstname, lastname, created_at, avatar_file, user_type FROM users WHERE login_id = ?", (login_id,))
        else:
            cursor.execute("SELECT * FROM users WHERE login_id = ?", (login_id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    def get_by_username(self, username: str, safe: bool = True):
        cursor = self.connection.cursor()
        if safe:
            cursor.execute("SELECT id, email, firstname, lastname, created_at, avatar_file, user_type FROM users WHERE username = ?", (username,))
        else:
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def get_by_id(self, id: int, safe: bool = True):
        cursor = self.connection.cursor()
        if safe:
            cursor.execute("SELECT id, username, firstname, lastname, created_at, avatar_file, user_type FROM users WHERE id = ?", (id,))
        else:
            cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        user = cursor.fetchone()
        cursor.close()
        return user

    

    def logout(self, login_id):
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET login_id = 'NONE' WHERE login_id = ?", (login_id,))
        self.connection.commit()
        cursor.close()