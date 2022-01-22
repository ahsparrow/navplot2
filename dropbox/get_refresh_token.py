import argparse
import dropbox

def get_oauth(app_key, app_secret):
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
            app_key,
            consumer_secret=app_secret,
            token_access_type="offline",
            scope=[
                'account_info.read',
                'files.metadata.read',
                'files.content.write'])

    auth_url = auth_flow.start()
    print("Go to: " + auth_url)

    auth_code = input("Enter the authorization code: ").strip()

    oauth_result = auth_flow.finish(auth_code)
    return oauth_result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description="Get OAuth refresh key for a Dropbox app")
    parser.add_argument('app_key', help="The app key")
    parser.add_argument('app_secret', help="The app secret")
    args = parser.parse_args()

    oauth = get_oauth(args.app_key, args.app_secret)
    print("\n" + oauth.refresh_token)
