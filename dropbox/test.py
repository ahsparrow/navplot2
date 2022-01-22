import argparse
import datetime
import dropbox

def test_dropbox(app_key, app_secret, refresh_token):
    dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token,
            app_key=app_key,
            app_secret=app_secret)

    """
    res = dbx.users_get_current_account()
    print(res)
    print("")

    res = dbx.files_list_folder("")
    for entry in res.entries:
        print(entry.name)
    """

    dbx.files_upload(
            datetime.datetime.now().isoformat().encode(),
            "/test.txt",
            dropbox.files.WriteMode.overwrite)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Test Dropbox access")
    parser.add_argument('app_key')
    parser.add_argument('app_secret')
    parser.add_argument('refresh_token')
    args = parser.parse_args()

    test_dropbox(args.app_key, args.app_secret, args.refresh_token)
