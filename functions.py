from flask import request, url_for, redirect


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