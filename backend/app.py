from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import zipfile
import json
import shutil
from datetime import datetime
from collections import Counter
import emoji
from pathlib import Path
import tempfile
import gc
import psutil

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # Reduced to 50MB max file size
# MAX_MESSAGES_PER_FRIEND = 1000  # Limit messages per friend to prevent memory issues

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store session data (in production, use Redis or database)
sessions = {}
# Cache for analyzed friend data
friend_cache = {}

def get_cached_analysis(friend_id, session_id):
    """Get cached analysis for a friend."""
    cache_key = f"{session_id}_{friend_id}"
    return friend_cache.get(cache_key)

def cache_analysis(friend_id, session_id, analysis):
    """Cache analysis for a friend."""
    cache_key = f"{session_id}_{friend_id}"
    friend_cache[cache_key] = analysis

def log_memory_usage(stage):
    """Log memory usage for debugging."""
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage at {stage}: {memory_mb:.2f} MB")

def extract_messages_from_zip(zip_path, session_id, user_name):
    """Process ZIP file directly without extracting - ULTRA FAST VERSION."""
    try:
        log_memory_usage("start of direct ZIP processing")
        
        # Process ZIP directly without extracting
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get list of all files in the ZIP
            file_list = zip_ref.namelist()
            
            # Find inbox folders
            inbox_files = [f for f in file_list if 'messages/inbox/' in f or 'inbox/' in f]
            
            if not inbox_files:
                return None, "Could not find messages inbox folder. Please ensure you're uploading the messages folder from your Instagram data."
            
            # Extract friend list from folder structure
            friends = []
            added_names = set()
            
            # Group files by chat folder
            chat_folders = {}
            for file_path in inbox_files:
                # Extract folder name from path
                parts = file_path.split('/')
                if len(parts) >= 3:
                    # Find the inbox folder and the chat folder after it
                    try:
                        inbox_index = parts.index('inbox')
                        if inbox_index + 1 < len(parts):
                            chat_folder = parts[inbox_index + 1]
                            if chat_folder not in chat_folders:
                                chat_folders[chat_folder] = []
                            chat_folders[chat_folder].append(file_path)
                    except ValueError:
                        continue
            
            print(f"Found {len(chat_folders)} chat folders")
            
            # Process each chat folder
            for folder_name, files in chat_folders.items():
                message_files = [f for f in files if f.endswith('message_1.json')]
                
                if message_files:
                    # Try to read the first message file to get participant info
                    try:
                        with zip_ref.open(message_files[0]) as f:
                            chat_data = json.load(f)
                        
                        # Only include one-to-one chats
                        if 'participants' in chat_data and len(chat_data['participants']) == 2:
                            for participant in chat_data['participants']:
                                if 'name' in participant:
                                    friend_name = participant['name']
                                    if friend_name != user_name and friend_name not in added_names:
                                        friends.append({
                                            'id': len(friends),
                                            'name': friend_name,
                                            'chat_folder': folder_name,
                                            'message_files': len([f for f in files if 'message_' in f]),
                                            'total_messages': 'Unknown',
                                            'analyzed': False,
                                            'zip_path': zip_path  # Store ZIP path for later access
                                        })
                                        added_names.add(friend_name)
                                        break  # Only take the first friend
                    except Exception as e:
                        print(f"Error reading {message_files[0]}: {e}")
                        # Fallback: use folder name
                        friend_name = folder_name.replace('_', ' ').title()
                        if friend_name not in added_names:
                            friends.append({
                                'id': len(friends),
                                'name': friend_name,
                                'chat_folder': folder_name,
                                'message_files': len([f for f in files if 'message_' in f]),
                                'total_messages': 'Unknown',
                                'analyzed': False,
                                'zip_path': zip_path
                            })
                            added_names.add(friend_name)
        
        log_memory_usage("end of direct ZIP processing")
        print(f"Extracted {len(friends)} friends from ZIP without extraction")
        return friends, None
        
    except Exception as e:
        return None, str(e)

def get_friend_details(friend_id, session_id, user_name):
    """Get real friend details on-demand."""
    try:
        session_data = sessions.get(session_id)
        if not session_data:
            return None, "Session not found"
        
        friends = session_data['friends']
        friend = next((f for f in friends if f['id'] == int(friend_id)), None)
        if not friend:
            return None, "Friend not found"
        
        # Read directly from ZIP file
        zip_path = friend.get('zip_path')
        if not zip_path or not os.path.exists(zip_path):
            return None, "ZIP file not found"
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Find all message files for this friend
                chat_folder_prefix = f"messages/inbox/{friend['chat_folder']}/"
                message_files = [f for f in zip_ref.namelist() if f.startswith(chat_folder_prefix) and 'message_' in f]
                
                if not message_files:
                    return None, "No message files found"
                
                # Read first message file to get real participant names
                message_files.sort()
                first_file = message_files[0]
                
                with zip_ref.open(first_file) as f:
                    chat_data = json.load(f)
                
                # Get real participant names
                real_friend_name = friend['name']  # Default to folder name
                total_messages = 0
                
                if 'participants' in chat_data and len(chat_data['participants']) == 2:
                    for participant in chat_data['participants']:
                        if 'name' in participant:
                            participant_name = participant['name']
                            if participant_name != user_name:
                                real_friend_name = participant_name
                                break
                
                # Count total messages across all files
                for msg_file in message_files:
                    try:
                        with zip_ref.open(msg_file) as f:
                            file_data = json.load(f)
                        if 'messages' in file_data:
                            total_messages += len(file_data['messages'])
                    except Exception as e:
                        print(f"Error reading {msg_file}: {e}")
                        continue
            
            return {
                'real_name': real_friend_name,
                'total_messages': total_messages,
                'message_files': len(message_files)
            }, None
            
        except Exception as e:
            return None, f"Error reading message file: {str(e)}"
            
    except Exception as e:
        return None, str(e)

def extract_from_json_files(file, session_id, user_name):
    """Extract data from individual JSON files uploaded directly."""
    try:
        log_memory_usage("start of JSON file processing")
        
        # Create session directory
        session_path = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_path, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(session_path, file.filename)
        file.save(file_path)
        
        # Try to parse the JSON file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
        except Exception as e:
            return None, f"Invalid JSON file: {str(e)}"
        
        # Extract friend information
        friends = []
        if 'participants' in chat_data and len(chat_data['participants']) == 2:
            for participant in chat_data['participants']:
                if 'name' in participant:
                    friend_name = participant['name']
                    if friend_name != user_name:
                        friends.append({
                            'id': 0,
                            'name': friend_name,
                            'chat_folder': 'direct_upload',
                            'file_path': file_path
                        })
                        break  # Only take the first friend
        
        if not friends:
            return None, "No valid friend found in the uploaded file"
        
        log_memory_usage("end of JSON file processing")
        return friends, None
        
    except Exception as e:
        return None, str(e)

def analyze_friend_data(friend_id, session_id, user_name):
    """Analyze data for a specific friend with detailed insights."""
    try:
        session_data = sessions.get(session_id)
        if not session_data:
            return None, "Session not found"
        
        friends = session_data['friends']
        friend = next((f for f in friends if f['id'] == int(friend_id)), None)
        if not friend:
            return None, "Friend not found"
        
        # Check if this is client-side processed data
        if session_data.get('client_processed'):
            print(f"Processing client-side data for friend {friend['name']} (ID: {friend_id})")
            messages = friend.get('messages', [])
            print(f"Found {len(messages)} messages for {friend['name']}")
            print(f"User name: {user_name}")
            print(f"Friend name: {friend['name']}")
            if not messages:
                return None, "No messages found for this friend"
            messages.sort(key=lambda x: x.get('timestamp_ms', 0))
            total_messages = len(messages)
            your_messages = sum(1 for msg in messages if msg.get('sender_name') == user_name)
            their_messages = total_messages - your_messages
            timestamps = [msg.get('timestamp_ms', 0) for msg in messages if msg.get('timestamp_ms', 0)]
            first_timestamp = min(timestamps) if timestamps else None
            last_timestamp = max(timestamps) if timestamps else None
            friendship_duration_days = 0
            if first_timestamp and last_timestamp and last_timestamp > first_timestamp:
                duration_seconds = (last_timestamp - first_timestamp) / 1000
                friendship_duration_days = duration_seconds / 86400
            else:
                friendship_duration_days = 0
            messages_per_day = total_messages / friendship_duration_days if friendship_duration_days > 0 else 0
            your_content = [msg.get('content', '') for msg in messages if msg.get('sender_name') == user_name and msg.get('content')]
            their_content = [msg.get('content', '') for msg in messages if msg.get('sender_name') == friend['name'] and msg.get('content')]
            # --- Robust stopword filtering ---
            stopwords = set([
                'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
                'oh', 'yeah', 'yes', 'no', 'ok', 'okay', 'haha', 'lol', 'omg', 'wow', 'hey', 'hi', 'hello', 'bye', 'goodbye', 'thanks', 'thank',
                'sent', 'used', 'am', 'as', 'were', 'was', 'is', 'are', 'did', 'had', 'has', 'u', 'im', 'dont', 'cant', 'wont', 'didnt', 'doesnt', 'should', 'shouldnt', 'couldnt', 'wouldnt', 'instagram', 'photo', 'video', 'reel', 'story', 'message', 'messages', 'chat', 'call', 'missed', 'unsent', 'attachment', 'replied', 'reply', 'link', 'shared', 'sticker', 'gif', 'voice', 'media', 'group', 'sent a photo', 'sent a video', 'sent a reel', 'sent an attachment', 'unsent a message', 'reacted to', 'video call', 'missed video call', 'you sent an attachment', 'you unsent a message', 'this message is no longer available', 'sent a voice message', 'sent a sticker', 'sent a gif', 'sent a story reply', 'replied to your story', 'replied to story', 'sent a story reply'
            ])
            # Add user name and variants to stopwords for your words
            your_stopwords = set(stopwords)
            if user_name:
                your_stopwords.add(user_name.lower())
                for part in user_name.lower().split():
                    your_stopwords.add(part)
                your_stopwords.add(user_name)
            # Add friend's name and variants to stopwords for their words
            their_stopwords = set(stopwords)
            if friend['name']:
                their_stopwords.add(friend['name'].lower())
                for part in friend['name'].lower().split():
                    their_stopwords.add(part)
                their_stopwords.add(friend['name'])
            import re
            def analyze_words(content_list, stopwords_set):
                words = []
                for content in content_list:
                    clean_words = re.findall(r'\b[a-zA-Z]+\b', content.lower())
                    filtered_words = [word for word in clean_words if word not in stopwords_set and len(word) > 2]
                    words.extend(filtered_words)
                return Counter(words).most_common(15)
            your_words = analyze_words(your_content, your_stopwords)
            their_words = analyze_words(their_content, their_stopwords)
            from datetime import datetime
            your_timestamps = [msg.get('timestamp_ms', 0) for msg in messages if msg.get('sender_name') == user_name and msg.get('timestamp_ms', 0)]
            their_timestamps = [msg.get('timestamp_ms', 0) for msg in messages if msg.get('sender_name') == friend['name'] and msg.get('timestamp_ms', 0)]
            your_hours = [datetime.fromtimestamp(ts / 1000).hour for ts in your_timestamps]
            your_days = [datetime.fromtimestamp(ts / 1000).strftime('%A') for ts in your_timestamps]
            their_hours = [datetime.fromtimestamp(ts / 1000).hour for ts in their_timestamps]
            their_days = [datetime.fromtimestamp(ts / 1000).strftime('%A') for ts in their_timestamps]
            hour_counts = Counter(your_hours)
            day_counts = Counter(your_days)
            their_hour_counts = Counter(their_hours)
            their_day_counts = Counter(their_days)
            your_timing = {
                'peak_hour': hour_counts.most_common(1)[0][0] if hour_counts else 12,
                'peak_day': day_counts.most_common(1)[0][0] if day_counts else 'Monday',
                'hourly': [{'hour': hour, 'count': count} for hour, count in sorted(hour_counts.items())],
                'daily': [{'day': day, 'count': count} for day, count in day_counts.items()]
            }
            their_timing = {
                'peak_hour': their_hour_counts.most_common(1)[0][0] if their_hour_counts else 12,
                'peak_day': their_day_counts.most_common(1)[0][0] if their_day_counts else 'Monday',
                'hourly': [{'hour': hour, 'count': count} for hour, count in sorted(their_hour_counts.items())],
                'daily': [{'day': day, 'count': count} for day, count in their_day_counts.items()]
            }
            # --- Response time analysis ---
            response_times = []
            conversation_gaps = []
            for i in range(len(messages) - 1):
                current_msg = messages[i]
                next_msg = messages[i + 1]
                current_sender = current_msg.get('sender_name', '')
                next_sender = next_msg.get('sender_name', '')
                current_time = current_msg.get('timestamp_ms', 0)
                next_time = next_msg.get('timestamp_ms', 0)
                if current_time > 0 and next_time > 0:
                    time_diff_seconds = (next_time - current_time) / 1000
                    time_diff_hours = time_diff_seconds / 3600
                    if time_diff_hours > 24:
                        gap_start = datetime.fromtimestamp(current_time / 1000)
                        gap_end = datetime.fromtimestamp(next_time / 1000)
                        conversation_gaps.append({
                            'start': gap_start.isoformat(),
                            'end': gap_end.isoformat(),
                            'duration_hours': time_diff_hours,
                            'duration_days': time_diff_hours / 24
                        })
                    if time_diff_hours <= 24 and current_sender != next_sender:
                        response_times.append({
                            'from': current_sender,
                            'to': next_sender,
                            'time': time_diff_seconds
                        })
            your_response_times = [rt['time'] for rt in response_times if rt['to'] == user_name]
            their_response_times = [rt['time'] for rt in response_times if rt['to'] == friend['name']]
            def categorize_response_times(response_times):
                if not response_times:
                    return {}
                instant = sum(1 for t in response_times if t < 60)
                quick = sum(1 for t in response_times if 60 <= t < 300)
                normal = sum(1 for t in response_times if 300 <= t < 3600)
                slow = sum(1 for t in response_times if 3600 <= t < 86400)
                very_slow = sum(1 for t in response_times if t >= 86400)
                total = len(response_times)
                return {
                    'instant': {'count': instant, 'percentage': (instant/total)*100 if total > 0 else 0},
                    'quick': {'count': quick, 'percentage': (quick/total)*100 if total > 0 else 0},
                    'normal': {'count': normal, 'percentage': (normal/total)*100 if total > 0 else 0},
                    'slow': {'count': slow, 'percentage': (slow/total)*100 if total > 0 else 0},
                    'very_slow': {'count': very_slow, 'percentage': (very_slow/total)*100 if total > 0 else 0}
                }
            your_response_categories = categorize_response_times(your_response_times)
            their_response_categories = categorize_response_times(their_response_times)
            # --- Shared content analysis ---
            def analyze_shared_content(message_list):
                instagram_posts = 0
                instagram_reels = 0
                instagram_stories = 0
                other_links = 0
                story_replies = 0
                for msg in message_list:
                    content = msg.get('content', '') or ''
                    content_lower = content.lower()
                    is_story_reply = False
                    if 'replied to your story' in content_lower or 'sent a story reply' in content_lower or 'replied to story' in content_lower:
                        is_story_reply = True
                    elif (('photos' in msg or 'videos' in msg) and (len(content.strip()) <= 10 or (len(content.strip()) == 1 and emoji.is_emoji(content.strip())))):
                        is_story_reply = True
                    if is_story_reply:
                        story_replies += 1
                        continue
                    share = msg.get('share')
                    if share and 'link' in share:
                        link = share['link']
                        if 'instagram.com/p/' in link or 'ig.me/p/' in link:
                            instagram_posts += 1
                        elif 'instagram.com/reel/' in link or 'ig.me/reel/' in link:
                            instagram_reels += 1
                        elif 'instagram.com/stories/' in link:
                            instagram_stories += 1
                        else:
                            other_links += 1
                    elif content.startswith('http'):
                        other_links += 1
                return {
                    'instagram_posts': instagram_posts,
                    'instagram_reels': instagram_reels,
                    'instagram_stories': instagram_stories,
                    'story_replies': story_replies,
                    'other_links': other_links,
                    'total_shared': instagram_posts + instagram_reels + instagram_stories + story_replies + other_links
                }
            your_shared_content = analyze_shared_content([msg for msg in messages if msg.get('sender_name') == user_name])
            their_shared_content = analyze_shared_content([msg for msg in messages if msg.get('sender_name') != user_name])
            your_avg_length = sum(len(content) for content in your_content) / len(your_content) if your_content else 0
            their_avg_length = sum(len(content) for content in their_content) / len(their_content) if their_content else 0
            # --- Friendship intensity (improved version) ---
            score = 0
            # Message volume (0-30 points)
            if total_messages >= 1000:
                score += 30
            elif total_messages >= 500:
                score += 20
            elif total_messages >= 200:
                score += 15
            elif total_messages >= 100:
                score += 10
            elif total_messages >= 50:
                score += 5
            # Response speed (0-25 points)
            # Use both your and their response times
            avg_your_response = sum(your_response_times) / len(your_response_times) if your_response_times else None
            avg_their_response = sum(their_response_times) / len(their_response_times) if their_response_times else None
            if avg_your_response is not None and avg_their_response is not None:
                avg_response = (avg_your_response + avg_their_response) / 2
            elif avg_your_response is not None:
                avg_response = avg_your_response
            elif avg_their_response is not None:
                avg_response = avg_their_response
            else:
                avg_response = None
            if avg_response is not None:
                if avg_response < 300:  # <5 min
                    score += 25
                elif avg_response < 1800:  # <30 min
                    score += 20
                elif avg_response < 3600:  # <1 hour
                    score += 15
                elif avg_response < 86400:  # <1 day
                    score += 10
            # Conversation gaps (0-25 points)
            if len(conversation_gaps) == 0:
                score += 25
            elif len(conversation_gaps) <= 3:
                score += 20
            elif len(conversation_gaps) <= 10:
                score += 15
            elif len(conversation_gaps) <= 20:
                score += 10
            # Balance (0-20 points)
            if total_messages > 0:
                balance = abs(50 - (your_messages / total_messages * 100))
                if balance <= 10:
                    score += 20
                elif balance <= 20:
                    score += 15
                elif balance <= 30:
                    score += 10
            friendship_intensity = min(score, 100)
            friendship_rating = 'Very High' if friendship_intensity >= 80 else 'High' if friendship_intensity >= 60 else 'Moderate' if friendship_intensity >= 40 else 'Low'
            analysis = {
            'friend': friend,
            'total_messages': total_messages,
            'your_messages': your_messages,
            'their_messages': their_messages,
            'your_percentage': (your_messages / total_messages * 100) if total_messages > 0 else 0,
            'their_percentage': (their_messages / total_messages * 100) if total_messages > 0 else 0,
            'first_message': datetime.fromtimestamp(first_timestamp / 1000).isoformat() if first_timestamp else None,
            'last_message': datetime.fromtimestamp(last_timestamp / 1000).isoformat() if last_timestamp else None,
            'friendship_duration_days': friendship_duration_days,
            'messages_per_day': messages_per_day,
            'your_words': your_words,
            'their_words': their_words,
                'your_lengths': {'avg_length': your_avg_length, 'longest': max([len(c) for c in your_content], default=0)},
                'their_lengths': {'avg_length': their_avg_length, 'longest': max([len(c) for c in their_content], default=0)},
            'your_timing': your_timing,
            'their_timing': their_timing,
            'your_avg_response': sum(your_response_times) / len(your_response_times) if your_response_times else 0,
            'their_avg_response': sum(their_response_times) / len(their_response_times) if their_response_times else 0,
            'your_response_categories': your_response_categories,
            'their_response_categories': their_response_categories,
            'your_response_count': len(your_response_times),
            'their_response_count': len(their_response_times),
            'your_shared_content': your_shared_content,
            'their_shared_content': their_shared_content,
            'conversation_gaps': conversation_gaps,
            'gap_count': len(conversation_gaps),
            'friendship_intensity': friendship_intensity,
                'friendship_rating': friendship_rating
        }
            cache_analysis(friend_id, session_id, analysis)
            return analysis, None
    except Exception as e:
        print(f"Error in analyze_friend_data for friend_id {friend_id}: {e}")
        return None, f"Error analyzing friend: {e}"

def analyze_network_data(session_id, user_name):
    """Analyze social network data."""
    session_data = sessions.get(session_id)
    if not session_data:
        return None, "Session not found"
    friends = session_data['friends']
    # Check if this is client-side processed data
    if session_data.get('client_processed'):
        network_data = []
        for friend in friends:
            analysis, error = analyze_friend_data(friend['id'], session_id, user_name)
            if analysis:
                network_data.append(analysis)
        if not network_data:
            return None, "No network data available from client-side processing"
        most_messages = sorted(network_data, key=lambda x: x['total_messages'], reverse=True)[:10]
        most_balanced = sorted(network_data, key=lambda x: abs(50 - x['your_percentage']))[:10]
        longest_friendships = sorted(network_data, key=lambda x: x['friendship_duration_days'], reverse=True)[:10]
        fastest_responses = sorted(network_data, key=lambda x: x['their_avg_response'])[:10]
        categories = {
            'best_friends': [],
            'close_friends': [],
            'regular_friends': [],
            'occasional_friends': [],
            'distant_friends': []
        }
        for friend_data in network_data:
            total_messages = friend_data['total_messages']
            messages_per_day = total_messages / friend_data['friendship_duration_days'] if friend_data['friendship_duration_days'] > 0 else 0
            if total_messages >= 1000 and messages_per_day >= 2:
                categories['best_friends'].append(friend_data)
            elif total_messages >= 500 and messages_per_day >= 1:
                categories['close_friends'].append(friend_data)
            elif total_messages >= 200 and messages_per_day >= 0.5:
                categories['regular_friends'].append(friend_data)
            elif total_messages >= 50:
                categories['occasional_friends'].append(friend_data)
            else:
                categories['distant_friends'].append(friend_data)
        return {
            'total_friends': len(network_data),
            'total_messages': sum(f['total_messages'] for f in network_data),
            'most_messages': most_messages,
            'most_balanced': most_balanced,
            'longest_friendships': longest_friendships,
            'fastest_responses': fastest_responses,
            'categories': categories
        }, None
    else:
        # Original server-side processing logic
        network_data = []
        errors = []
        
        for friend in friends:
            try:
                analysis, error = analyze_friend_data(friend['id'], session_id, user_name)
                if analysis:
                    network_data.append(analysis)
                elif error:
                    errors.append(f"{friend['name']}: {error}")
            except Exception as e:
                errors.append(f"{friend['name']}: {e}")
                print(f"Error analyzing friend {friend['name']}: {e}")
        
        if not network_data:
            return None, f"No network data available. Errors: {'; '.join(errors)}"
        
        # Sort by different metrics
        most_messages = sorted(network_data, key=lambda x: x['total_messages'], reverse=True)[:10]
        most_balanced = sorted(network_data, key=lambda x: abs(50 - x['your_percentage']))[:10]
        longest_friendships = sorted(network_data, key=lambda x: x['friendship_duration_days'], reverse=True)[:10]
        fastest_responses = sorted(network_data, key=lambda x: x['their_avg_response'])[:10]
        
        # Categorize friendships
        categories = {
            'best_friends': [],
            'close_friends': [],
            'regular_friends': [],
            'occasional_friends': [],
            'distant_friends': []
        }
        
        for friend_data in network_data:
            total_messages = friend_data['total_messages']
            messages_per_day = total_messages / friend_data['friendship_duration_days'] if friend_data['friendship_duration_days'] > 0 else 0
            
            if total_messages >= 1000 and messages_per_day >= 2:
                categories['best_friends'].append(friend_data)
            elif total_messages >= 500 and messages_per_day >= 1:
                categories['close_friends'].append(friend_data)
            elif total_messages >= 200 and messages_per_day >= 0.5:
                categories['regular_friends'].append(friend_data)
            elif total_messages >= 50:
                categories['occasional_friends'].append(friend_data)
            else:
                categories['distant_friends'].append(friend_data)
        
        return {
            'total_friends': len(network_data),
            'total_messages': sum(f['total_messages'] for f in network_data),
            'most_messages': most_messages,
            'most_balanced': most_balanced,
            'longest_friendships': longest_friendships,
            'fastest_responses': fastest_responses,
            'categories': categories
        }, None

@app.route('/api/upload-processed', methods=['POST'])
def upload_processed_data():
    """Receive processed data from client-side ZIP processing."""
    try:
        data = request.get_json()
        
        if not data or 'friends' not in data:
            return jsonify({'success': False, 'error': 'Invalid data format'})
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Store session data
        sessions[session_id] = {
            'user_name': data.get('user_name', 'User'),
            'friends': data['friends'],
            'created_at': datetime.now().isoformat(),
            'analysis_complete': True,
            'client_processed': True  # Mark as client-processed
        }
        
        print(f"Received {len(data['friends'])} friends from client-side processing")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'friends': data['friends'],
            'message': f'Successfully processed {len(data["friends"])} friends!'
        })
        
    except Exception as e:
        print(f"Error processing uploaded data: {str(e)}")
        return jsonify({'success': False, 'error': f'Processing failed: {str(e)}'})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and data extraction."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    user_name = request.form.get('user_name', 'Rayaan Raza')
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    # Accept both ZIP files and direct messages folder
    if not (file.filename.endswith('.zip') or file.filename.endswith('.json')):
        return jsonify({'success': False, 'error': 'Please upload a ZIP file containing messages folder or individual message JSON files'})
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    try:
        log_memory_usage("before upload processing")
        
        if file.filename.endswith('.zip'):
            # Handle ZIP file (messages folder)
            zip_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.zip")
            file.save(zip_path)
            
            # Extract and analyze data with progress tracking
            print(f"Starting analysis for session {session_id}")
            log_memory_usage("before extraction")
            
            friends, error = extract_messages_from_zip(zip_path, session_id, user_name)
            
            # Clean up ZIP file
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
        else:
            # Handle individual JSON files (direct upload)
            friends, error = extract_from_json_files(file, session_id, user_name)
        
        if error:
            return jsonify({'success': False, 'error': error})
        
        # Force garbage collection
        gc.collect()
        log_memory_usage("after extraction")
        
        # Store session data
        sessions[session_id] = {
            'user_name': user_name,
            'friends': friends,
            'created_at': datetime.now().isoformat(),
            'analysis_complete': True
        }
        
        print(f"Analysis complete for session {session_id}. Found {len(friends)} friends.")
        
        # Final cleanup
        gc.collect()
        log_memory_usage("end of upload")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'friends': friends,
            'message': f'Analysis complete! Found {len(friends)} friends to analyze.'
        })
        
    except Exception as e:
        print(f"Error during upload/analysis: {str(e)}")
        # Cleanup on error
        zip_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'})

@app.route('/api/friend-details/<friend_id>', methods=['GET'])
def get_friend_details_endpoint(friend_id):
    """Get detailed friend information on-demand."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    details, error = get_friend_details(friend_id, session_id, session_data['user_name'])
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({
        'success': True,
        'details': details
    })

@app.route('/api/quick-stats/<friend_id>', methods=['GET'])
def get_quick_stats(friend_id):
    """Get quick stats for a friend without full analysis."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    friends = session_data['friends']
    friend = next((f for f in friends if f['id'] == int(friend_id)), None)
    if not friend:
        return jsonify({'success': False, 'error': 'Friend not found'})
    
    # Return basic stats without full analysis
    return jsonify({
        'success': True,
        'quick_stats': {
            'name': friend['name'],
            'message_files': friend.get('message_files', 0),
            'total_messages': friend.get('total_messages', 'Unknown'),
            'analyzed': friend.get('analyzed', False)
        }
    })

@app.route('/api/progress/<session_id>', methods=['GET'])
def get_progress(session_id):
    """Get analysis progress for a session."""
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    return jsonify({
        'success': True,
        'status': 'complete' if session_data.get('analysis_complete') else 'processing',
        'friends_count': len(session_data.get('friends', [])),
        'created_at': session_data.get('created_at')
    })

@app.route('/api/analysis/<friend_id>', methods=['GET'])
def get_friend_analysis(friend_id):
    """Get detailed analysis for a specific friend."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    cached_analysis = get_cached_analysis(friend_id, session_id)
    if cached_analysis:
        return jsonify({
            'success': True,
            'analysis': cached_analysis
        })

    analysis, error = analyze_friend_data(friend_id, session_id, session_data['user_name'])
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({
        'success': True,
        'analysis': analysis
    })

@app.route('/api/network', methods=['GET'])
def get_network_analysis():
    """Get social network analysis."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    network, error = analyze_network_data(session_id, session_data['user_name'])
    
    if error:
        return jsonify({'success': False, 'error': error})
    
    return jsonify({
        'success': True,
        'network': network
    })

@app.route('/api/friends', methods=['GET'])
def get_friends():
    """Get list of friends."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    return jsonify({
        'success': True,
        'friends': session_data['friends']
    })

@app.route('/api/search', methods=['GET'])
def search_friends():
    """Search friends by name."""
    session_id = request.args.get('session_id')
    query = request.args.get('q', '').lower()
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'})
    
    session_data = sessions.get(session_id)
    if not session_data:
        return jsonify({'success': False, 'error': 'Session not found'})
    
    if not query:
        return jsonify({
            'success': True,
            'friends': session_data['friends']
        })
    
    # Filter friends by name
    filtered_friends = [
        friend for friend in session_data['friends']
        if query in friend['name'].lower()
    ]
    
    return jsonify({
        'success': True,
        'friends': filtered_friends,
        'query': query
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - redirect to frontend or show API info."""
    return jsonify({
        'message': 'Instagram Friends Analyzer API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'upload': '/api/upload',
            'friends': '/api/friends',
            'analysis': '/api/analysis/<friend_id>',
            'network': '/api/network'
        },
        'instructions': 'This is the backend API. Use the frontend at http://localhost:5173 to interact with the application.'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 