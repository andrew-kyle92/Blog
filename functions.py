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
                fields_updated.append(field)
        elif field == "email":
            if user_dict[field]["updated"]:
                user_data.email = user_dict[field]["value"]
                fields_updated.append(field)
        elif field == "name":
            if user_dict[field]["updated"]:
                user_data.name = user_dict[field]["value"]
                fields_updated.append(field)
        elif field == "password":
            if user_dict[field]["updated"]:
                user_data.password = user_dict[field]["value"]
                fields_updated.append(field)
    return fields_updated