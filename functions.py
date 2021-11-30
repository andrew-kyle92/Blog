from flask import request, url_for, redirect
import os

ALLOWED_EXTENSIONS = {"jpg", "png"}


def catch_redirect(url, *args):
    requested_url = url
    for key in args:
        print(key)
    if requested_url == "edit_post":
        my_dict = {
            "next_url": requested_url,
            "post_id": args[1]
        }
        print(my_dict.values())
        return my_dict


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def create_folder_struct(username):
    user_root_path = f"static/uploads/users/{username.replace(' ', '_').lower()}"
    os.mkdir(user_root_path)
    os.mkdir(f"{user_root_path}/data")
    os.mkdir(f"{user_root_path}/data/profile-picture")
    os.mkdir(f"{user_root_path}/data/music")


def add_music(user, song_data):
    user_root_path = f"static/uploads/users/{user.name.replace(' ', '_').lower()}/data/music"
    artist_dir = f"{song_data['artist'].replace(' ', '_')}"
    artist_exists = os.path.isdir(f"{user_root_path}/{artist_dir}")
    album_dir = f"{song_data['album'].replace(' ', '_')}"
    album_exists = os.path.isdir(f"{user_root_path}/{artist_dir}/{album_dir}")
    song_name = f"{song_data['song']}"
    song_exists = os.path.isfile(f"{user_root_path}/{artist_dir}/{album_dir}/{song_name}")
    if artist_exists:
        if album_exists:
            if song_exists:
                return False
            else:
                return True
        else:
            os.mkdir(f"{user_root_path}/{artist_dir}/{album_dir}")
            return True
    else:
        os.mkdir(f"{user_root_path}/{artist_dir}")
        os.mkdir(f"{user_root_path}/{artist_dir}/{album_dir}")
        return True