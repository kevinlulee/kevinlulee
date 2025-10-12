import os
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup


def format_date_range(messages):
    """Generate a human-readable date range from messages."""
    if not messages:
        return None
    
    timestamps = [msg['timestamp'] for msg in messages if msg['timestamp']]
    if not timestamps:
        return None
    
    start_ts = min(timestamps)
    end_ts = max(timestamps)
    
    start_dt = datetime.fromtimestamp(start_ts)
    end_dt = datetime.fromtimestamp(end_ts)
    
    # Format as "Month Year to Month Year"
    start_str = start_dt.strftime("%B %Y")
    end_str = end_dt.strftime("%B %Y")
    
    if start_str == end_str:
        return start_str
    
    return f"{start_str} to {end_str}"


def format_phone_number(phone_int):
    """Format phone number as (XXX) XXX-XXXX."""
    if not phone_int:
        return None
    
    phone_str = str(phone_int)
    
    # Remove leading 1 if present and not 1800/1888/etc
    if phone_str.startswith('1') and len(phone_str) == 11 and not phone_str.startswith('1800') and not phone_str.startswith('1888') and not phone_str.startswith('1877') and not phone_str.startswith('1866'):
        phone_str = phone_str[1:]
    
    # Format as (XXX) XXX-XXXX
    if len(phone_str) == 10:
        return f"({phone_str[:3]}) {phone_str[3:6]}-{phone_str[6:]}"
    
    return phone_str


def parse_phone_number(phone_str):
    """Extract phone number as integer, removing +, -, and spaces."""
    if not phone_str:
        return None
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone_str)
    return int(digits) if digits else None


def parse_timestamp(dt_str):
    """Convert ISO 8601 timestamp to Unix timestamp (integer)."""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except Exception as e:
        return None


def parse_html_file(filepath):
    """Parse a single HTML file and extract messages."""
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    messages = []
    contact_name = None
    contact_phone = None

    # Find all message divs
    for msg_div in soup.find_all('div', class_='message'):
        # Extract timestamp
        abbr_tag = msg_div.find('abbr', class_='dt')
        timestamp = None
        if abbr_tag and abbr_tag.get('title'):
            timestamp = parse_timestamp(abbr_tag['title'])

        # Extract sender info
        cite_tag = msg_div.find('cite', class_='sender')
        phone = None
        name = None
        is_me = False

        if cite_tag:
            # Get phone number
            tel_link = cite_tag.find('a', class_='tel')
            if tel_link and tel_link.get('href'):
                phone_str = tel_link['href'].replace('tel:', '')
                if phone_str:  # Non-empty phone
                    phone = parse_phone_number(phone_str)

            # Get name - check both <span class="fn"> and <abbr class="fn">
            fn_tag = cite_tag.find('span', class_='fn')
            if not fn_tag:
                fn_tag = cite_tag.find('abbr', class_='fn')
            
            if fn_tag:
                name = fn_tag.get_text(strip=True)
                if name == 'Me':
                    is_me = True
                    name = 'Me'
                elif not is_me and phone:
                    # This is the contact - save their info
                    contact_name = name
                    contact_phone = phone

        # Extract message content
        q_tag = msg_div.find('q')
        message_text = q_tag.get_text(strip=True) if q_tag else ""

        messages.append({
            'timestamp': timestamp,
            'phone': phone,
            'name': name,
            'is_me': is_me,
            'message': message_text
        })

    # Return messages along with contact info
    return {
        'contact_name': contact_name,
        'contact_phone': contact_phone,
        'messages': messages
    }


def write_log(log_dir, successful_files, skipped_files, error_files, conversations):
    """Write processing log to file."""
    log_dir = Path(log_dir).expanduser()
    log_dir.mkdir(exist_ok=True, parents=True)
    
    log_path = log_dir / "log.txt"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("Google Voice Message Processing Log\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"SUMMARY\n")
        f.write(f"-------\n")
        f.write(f"Successful files: {len(successful_files)}\n")
        f.write(f"Skipped files: {len(skipped_files)}\n")
        f.write(f"Error files: {len(error_files)}\n")
        f.write(f"Total conversations: {len(conversations)}\n\n")
        
        f.write(f"SUCCESSFUL FILES ({len(successful_files)})\n")
        f.write(f"-" * 40 + "\n")
        for fname in successful_files:
            f.write(f"  ✓ {fname}\n")
        f.write("\n")
        
        f.write(f"SKIPPED FILES ({len(skipped_files)})\n")
        f.write(f"-" * 40 + "\n")
        for fname, reason in skipped_files:
            f.write(f"  ⊘ {fname}\n")
            f.write(f"    Reason: {reason}\n")
        f.write("\n")
        
        f.write(f"ERROR FILES ({len(error_files)})\n")
        f.write(f"-" * 40 + "\n")
        for fname, error in error_files:
            f.write(f"  ✗ {fname}\n")
            f.write(f"    Error: {error}\n")
        f.write("\n")
    
    return log_path


def process_directory(directory_path, output_dir, log_dir):
    """Process all HTML files in directory and create JSON outputs."""
    directory_path = Path(directory_path).expanduser()
    output_dir = Path(output_dir).expanduser()
    
    output_dir.mkdir(exist_ok=True, parents=True)

    # Tracking
    skipped_files = []
    successful_files = []
    error_files = []

    # Dictionary to hold conversations: (name, phone) -> list of messages
    conversations = defaultdict(list)

    # Process all files
    for filepath in directory_path.glob('*.html'):
        filename = filepath.name
        
        # Only process files with "Text" in the name
        if 'Text' not in filename:
            continue

        try:
            result = parse_html_file(filepath)
            messages = result['messages']
            contact_name = result['contact_name']
            contact_phone = result['contact_phone']

            # Use "Me" as contact if no other contact found (talking to self)
            if not contact_name:
                contact_name = "Me"
                contact_phone = None

            # Group messages by contact
            key = (contact_name.lower(), contact_phone)
            
            for msg in messages:
                conversations[key].append({
                    'timestamp': msg['timestamp'],
                    'sender': msg['name'],
                    'message': msg['message']
                })
            
            successful_files.append(filename)

        except Exception as e:
            error_msg = f"Error processing {filename}: {e}"
            error_files.append((filename, str(e)))

    # Sort messages within each conversation by timestamp
    for key in conversations:
        conversations[key].sort(key=lambda x: x['timestamp'] or 0)

    # Write output files
    name_counts = defaultdict(list)
    for (name, phone) in conversations.keys():
        name_counts[name].append(phone)

    for (name, phone), messages in conversations.items():
        # Sanitize filename
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_').lower()

        # If multiple contacts with same name, add phone suffix
        if len(name_counts[name]) > 1:
            filename = f"{safe_name}_{phone}.json"
        else:
            filename = f"{safe_name}.json"

        output_path = output_dir / filename

        # Format phone number for display
        formatted_phone = format_phone_number(phone)
        
        # Get time range
        time_range = format_date_range(messages)

        # Create output data
        output_data = {
            'contact': name,
            'phone': formatted_phone,
            'time_range': time_range,
            'num_messages': len(messages),
            'messages': messages
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)


    # Write log file
    log_path = write_log(log_dir, successful_files, skipped_files, error_files, conversations)

    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"{'='*60}")
    print(f"Successful: {len(successful_files)}")
    print(f"Skipped: {len(skipped_files)}")
    print(f"Errors: {len(error_files)}")
    print(f"Total conversations: {len(conversations)}")
    print(f"\nOutput written to: {output_dir}")
    print(f"Log written to: {log_path}")


if __name__ == "__main__":
    html_directory = '/mnt/chromeos/MyFiles/Downloads/Takeout/Voice/Calls-sample'

    html_directory = '/mnt/chromeos/MyFiles/Downloads/Takeout/Voice/Calls'
    output_directory = "~/data/google-voice/conversations"
    log_directory = "~/data/google-voice/logs"
    # log_path = "~/data/google-voice/logs/log.txt"
    
    raise Exception("the files have successfully been collected. aborting")

    process_directory(html_directory, output_directory, log_directory)
