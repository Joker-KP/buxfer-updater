import datetime
import os
import re
import string
import subprocess
import time


def download_statement(account_folder, account_id, config):
    ui_result = play_and_wait(f'accounts/{account_id}', timeout_seconds=config.ui_vision_account_timeout,
                              use_file_storage=config.ui_vision_file_storage,
                              path_download_dir=config.ff_download_dir,
                              path_autorun_html=config.ui_vision_init_html,
                              browser_path=config.ff_bin)
    if 'file' not in ui_result:
        print("Problem with UI.Vision result:", ui_result['status'])
        return

    # move to the right place for upload
    downloaded = ui_result['file']
    basename = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '__' + os.path.basename(downloaded)
    target = os.path.join(account_folder, basename)
    os.rename(downloaded, target)


def play_and_wait(macro, timeout_seconds=10, use_file_storage=True,
                  path_download_dir=None, path_autorun_html=None, browser_path=None):
    assert os.path.exists(path_download_dir)
    assert os.path.exists(path_autorun_html)
    assert os.path.exists(browser_path)

    log = 'log_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
    log_full_path = os.path.join(path_download_dir, log)
    # print("Log file will show up at " + log_full_path)

    storage = "xfile" if use_file_storage else "browser"
    args = f'file:///{path_autorun_html}?macro={macro}' + \
           f'&closeRPA=1&closeBrowser=1&direct=1&storage={storage}&savelog={log}'
    ff_stdout = open(os.path.join(path_download_dir, 'ff_stdout.txt'), 'wt')
    ff_stderr = open(os.path.join(path_download_dir, 'ff_stderr.txt'), 'wt')
    proc = subprocess.Popen([browser_path, args], stdout=ff_stdout, stderr=ff_stderr)

    runtime_seconds = 0
    print("-- Statement downloading...")
    print("-- .", end='')
    while not os.path.exists(log_full_path) and runtime_seconds < timeout_seconds:
        # print(f"Waiting for macro to finish, ({runtime_seconds} of {timeout_seconds} seconds)")
        print(".", end='')
        time.sleep(1)
        runtime_seconds += 1
    print(f" ({runtime_seconds} secs)")

    result = {}
    if runtime_seconds < timeout_seconds:
        time.sleep(1)  # additional time for saving log
        with open(log_full_path) as f:
            lines = f.read().splitlines()
            if len(lines) < 1:
                status_text = "Empty log file"
            else:
                status_text = lines[0]

        if 'Status=OK' in status_text:
            for line in lines:
                matches = re.match(r'\[echo] File downloaded: (.*)', line)
                if matches:
                    full_path = os.path.join(path_download_dir, matches[1])
                    if os.path.exists(full_path):
                        result['file'] = full_path
                        # TODO: all is fine so we may remove the log file from downloads
                    else:
                        result["warning"] = f"Downloaded file {full_path} not found."

    else:
        status_text = f"Macro did not complete withing the time given: {timeout_seconds} secs"
        proc.kill()

    result["status"] = re.sub(f'[^{re.escape(string.printable)}]', '', status_text)
    return result
