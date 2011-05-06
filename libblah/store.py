import json
import os
from log import logger
from libblah.consts import get_user_config_path

osp = os.path


def get_account_basic_info_by_account_no(account_no):
    accs = get_accounts_basic_info_list()
    for acc in accs:
        if account_no == acc["mobile_no"] or account_no == acc["sid"]:
            return acc

    return None

def get_account_by_sid(sid):
    return get_data_from_local_json(sid, "account.json")

def get_accounts_basic_info_list():
    config_path = get_user_config_path()
    sids = [i for i in os.listdir(config_path) if (i < 'a') and (not i.startswith('.'))]
    account_list = []

    for sid in sids:
        account = get_data_from_local_json(sid, "account.json")
        if not account:
            continue
        account_list.append(account)

    return account_list

def set_last_login_sid(sid):
    config_path = get_user_config_path()
    last_login_log = os.path.join(config_path, ".last_login_log")
    with open(last_login_log, 'w') as f:
        f.write(sid)

def get_last_login_sid():
    config_path = get_user_config_path()
    last_login_log = os.path.join(config_path, ".last_login_log")
    if os.path.exists(last_login_log):
        with open(last_login_log) as f:
            return f.read()
    return None

def save_data_to_local_json(d, file_name):
    config_path = get_user_config_path()
    sid = str(d["sid"])
    path = osp.join(config_path, sid, file_name)
    with open(path, "w") as f:
        f.write(json.dumps(d))

def get_data_from_local_json(sid, file_name):
    config_path = get_user_config_path()
    path = osp.join(config_path, sid, file_name)
    if not osp.exists(path):
        return None
    with open(path) as f:
        content = f.read()

    js_obj = None
    try:
        js_obj = json.loads(content)
    except ValueError: # content is ""
        logger.error("%s content: `%s`" % (file_name, content))
        
    return js_obj

def delete_config_from_local_json(sid, file_name):
    config_path = get_user_config_path()
    path = osp.join(config_path, sid, file_name)
    if osp.exists(path):
        os.remove(path)

def main():
#    from pprint import pprint as pp
    accs = get_accounts_basic_info_list()
    print accs

if __name__ == "__main__":
    main()