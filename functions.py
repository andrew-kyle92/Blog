import os
import shutil

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


def create_folder_struct(user_data):
    """ Creates the basic folder structure for new user profiles """
    user_root_path = f"static/uploads/users/{user_data.id}-{user_data.name.replace(' ', '_').lower()}"
    os.mkdir(user_root_path)
    os.mkdir(f"{user_root_path}/data")
    os.mkdir(f"{user_root_path}/data/profile-picture")
    os.mkdir(f"{user_root_path}/data/music")


def add_music(user, song_data):
    """ Adds directories for the uploaded content.
    Also checks whether the song already exists or not. """
    user_root_path = f"static/uploads/users/{user.id}-{user.name.replace(' ', '_').lower()}/data/music"
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


def update_account(user_data, user_dict):
    """ Finds the updated columns to submit to the DB """
    fields_updated = []
    for field in user_dict.keys():
        if field == "account_type":
            if user_dict[field]["updated"]:
                user_data.account_type = user_dict[field]["value"]
                fields_updated.append("Account Type")
        elif field == "email":
            if user_dict[field]["updated"]:
                user_data.email = user_dict[field]["value"]
                fields_updated.append("Email")
        elif field == "name":
            if user_dict[field]["updated"]:
                user_data.name = user_dict[field]["value"]
                fields_updated.append("Name")
        elif field == "password":
            if user_dict[field]["updated"]:
                user_data.password = user_dict[field]["value"]
                fields_updated.append("Password")
    return fields_updated


def check_music_dir(user_data, song_data):
    """ Checks an album after a song has been deleted.
     Will delete the album directory if there are no more songs.
     Then, delete the artist directory if there are no more albums. """

    user_path = f"static/uploads/users/{user_data['id']}-{user_data['name'].lower().replace(' ', '_')}"
    music_path = f"{user_path}/data/music"
    artist_dir = f"{music_path}/{song_data['artist'].replace(' ', '_')}"
    album_dir = f"{artist_dir}/{song_data['album'].replace(' ', '_')}"
    user = user_data
    song_path = song_data["song_file"]

    # Deleting the song file at its path
    os.remove(song_path)

    # checking if the song was deleted or not
    if os.path.isfile(song_path):
        return False
    else:
        # checking if there are any more songs in the album directory
        album_files = os.listdir(f"{album_dir}")
        if len(album_files) > 1:
            return True, song_data["song_name"], 0
        else:
            shutil.rmtree(album_dir, ignore_errors=False)
            return True, song_data["song_name"], 1


def upload_tab_file(data):
    tab_root = "static/uploads/tab-files"
    artist_path = f"{data['artist']}"
    album_path = f"{data['album']}"
    file_path = f"{data['tab_file']}"
    full_path = f"/{tab_root}/{artist_path}/{album_path}/{file_path}"

    if os.path.exists(f"{tab_root}/{artist_path}"):
        if os.path.exists(f"{tab_root}/{artist_path}/{album_path}"):
            if os.path.exists(f"{tab_root}/{artist_path}/{album_path}/{file_path}"):
                return False
            else:
                return True, full_path
        else:
            os.mkdir(os.path.join(f"{tab_root}/{artist_path}/{album_path}"))
            return True, full_path
    else:
        os.mkdir(f"{tab_root}/{artist_path}")
        os.mkdir(f"{tab_root}/{artist_path}/{album_path}")
        return True, full_path
