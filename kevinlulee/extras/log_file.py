from datetime import datetime

def log_file(file, type="edit", dst_path = None):

    dst_path = dst_path or "/home/kdog3682/data/everything.log"
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file = file.replace("/home/kdog3682", "~")

    keys = [timestamp, file, type]
    log_entry = ' | '.join(keys) + "\n"
    with open(dst_path, 'a') as file:
        file.write(log_entry)
