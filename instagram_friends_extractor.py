import zipfile
import json
import os
import re
from pathlib import Path
from datetime import datetime
from collections import Counter
import emoji  # Add emoji library for better emoji detection

def extract_instagram_friends(zip_path):
    """
    Extract and print all friends you've chatted with from Instagram data ZIP.
    
    Args:
        zip_path (str): Path to the Instagram data ZIP file
    Returns:
        tuple: (friends_list, inbox_path) - list of friends and path to inbox folder
    """
    # User's name to filter out from participants
    USER_NAME = "Rayaan Raza"
    
    # Set to store unique friend names
    friends = set()
    inbox_path = None
    
    try:
        # Extract the ZIP file
        print(f"Extracting ZIP file: {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("extracted_instagram_data")
        
        # Navigate to the messages inbox folder
        inbox_path = Path("extracted_instagram_data/your_instagram_activity/messages/inbox")
        
        if not inbox_path.exists():
            print(f"Error: Could not find inbox folder at {inbox_path}")
            return [], None
        
        print(f"Found inbox folder at: {inbox_path}")
        
        # Iterate through each subfolder (chat thread)
        for chat_folder in inbox_path.iterdir():
            if chat_folder.is_dir():
                # Look for all message_*.json files in each chat folder
                message_files = list(chat_folder.glob("message_*.json"))
                
                if message_files:
                    # Use the first message file to get participants (they're the same across all files)
                    first_message_file = message_files[0]
                    try:
                        with open(first_message_file, 'r', encoding='utf-8') as f:
                            chat_data = json.load(f)
                        
                        # Extract participants from the chat
                        if 'participants' in chat_data:
                            for participant in chat_data['participants']:
                                if 'name' in participant:
                                    friend_name = participant['name']
                                    # Skip if it's the user themselves
                                    if friend_name != USER_NAME:
                                        friends.add(friend_name)
                    
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Error reading {first_message_file}: {e}")
                        continue
                else:
                    print(f"No message_*.json files found in {chat_folder}")
        
        # Convert set to sorted list
        friends_list = sorted(list(friends))
        
        # Print all unique friends
        if friends_list:
            print(f"\nFound {len(friends_list)} friends you've chatted with:")
            print("-" * 50)
            for i, friend in enumerate(friends_list, 1):
                print(f"{i}. {friend}")
        else:
            print("No friends found in the chat data.")
            
        return friends_list, inbox_path
            
    except zipfile.BadZipFile:
        print(f"Error: {zip_path} is not a valid ZIP file.")
        return [], None
    except FileNotFoundError:
        print(f"Error: File {zip_path} not found.")
        return [], None
    except Exception as e:
        print(f"An error occurred: {e}")
        return [], None

def select_friend(friends_list):
    """
    Allow user to select a friend by name or number.
    
    Args:
        friends_list (list): List of friend names
    Returns:
        str: Selected friend name or None if invalid selection
    """
    if not friends_list:
        return None
    
    print(f"\nSelect a friend to analyze messages with:")
    print("You can type their name or enter the number next to their name.")
    
    while True:
        selection = input("Enter your choice: ").strip()
        
        # Try to match by number first
        try:
            number = int(selection)
            if 1 <= number <= len(friends_list):
                selected_friend = friends_list[number - 1]
                print(f"Selected: {selected_friend}")
                return selected_friend
            else:
                print(f"Please enter a number between 1 and {len(friends_list)}")
        except ValueError:
            # Try to match by name
            selected_friend = None
            for friend in friends_list:
                if friend.lower() == selection.lower():
                    selected_friend = friend
                    break
            
            if selected_friend:
                print(f"Selected: {selected_friend}")
                return selected_friend
            else:
                print("Friend not found. Please try again.")

def analyze_messages(friend_name, inbox_path):
    """
    Analyze messages with a specific friend.
    
    Args:
        friend_name (str): Name of the friend to analyze
        inbox_path (Path): Path to the inbox folder
    """
    USER_NAME = "Rayaan Raza"
    
    # Find the chat folder for this friend
    chat_folder = None
    message_files = []
    
    print(f"Searching for one-to-one chat with {friend_name}...")
    
    one_to_one_chats = 0
    group_chats = 0
    
    for folder in inbox_path.iterdir():
        if folder.is_dir():
            # Look for all message_*.json files
            msg_files = list(folder.glob("message_*.json"))
            print(f"Found {len(msg_files)} message files in {folder.name}")
            
            # Debug: Show all message files found
            if msg_files:
                print(f"  Message files: {[f.name for f in msg_files]}")
            
            # Debug: Show all files in the folder
            all_files = list(folder.iterdir())
            print(f"  All files in folder: {[f.name for f in all_files]}")
            
            # Also look for any .json files that might contain messages
            json_files = list(folder.glob("*.json"))
            print(f"  All JSON files: {[f.name for f in json_files]}")
            
            if msg_files:
                try:
                    # Use first file to check participants
                    with open(msg_files[0], 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                    
                    # Check if this chat contains the selected friend
                    if 'participants' in chat_data:
                        participants = [p.get('name', '') for p in chat_data['participants']]
                        print(f"Participants in {folder.name}: {participants}")
                        
                        # Only look at one-to-one chats (2 participants: user + friend)
                        if (friend_name in participants and USER_NAME in participants and 
                            len(participants) == 2):
                            one_to_one_chats += 1
                            chat_folder = folder
                            message_files = sorted(msg_files, key=lambda x: x.name)  # Sort by filename
                            print(f"Found one-to-one chat folder: {folder.name}")
                            print(f"Message files: {[f.name for f in message_files]}")
                            break
                        elif friend_name in participants and USER_NAME in participants:
                            group_chats += 1
                            print(f"  Skipping group chat with {len(participants)} participants")
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error reading {msg_files[0]}: {e}")
                    continue
    
    print(f"\nSearch summary:")
    print(f"  One-to-one chats found: {one_to_one_chats}")
    print(f"  Group chats found: {group_chats}")
    
    if not message_files:
        print(f"\nCould not find one-to-one message data for {friend_name}")
        print("Note: This script only analyzes individual conversations, not group chats.")
        return
    
    try:
        # Combine messages from all message files
        all_messages = []
        total_files_read = 0
        
        print(f"\nReading {len(message_files)} message files...")
        
        for msg_file in message_files:
            try:
                # Check file size first
                file_size = msg_file.stat().st_size
                print(f"Reading {msg_file.name}... (Size: {file_size:,} bytes)")
                
                with open(msg_file, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    print(f"  Raw file content length: {len(raw_content)} characters")
                    print(f"  First 200 characters: {raw_content[:200]}...")
                    
                    # Try to parse JSON
                    chat_data = json.loads(raw_content)
                
                total_files_read += 1
                
                # Debug: Print the structure to understand the format
                print(f"  JSON keys: {list(chat_data.keys())}")
                
                # Try different possible message keys
                file_messages = []
                if 'messages' in chat_data:
                    file_messages = chat_data['messages']
                    print(f"  Using 'messages' key")
                elif 'conversation' in chat_data:
                    file_messages = chat_data['conversation']
                    print(f"  Using 'conversation' key")
                elif 'chat' in chat_data:
                    file_messages = chat_data['chat']
                    print(f"  Using 'chat' key")
                else:
                    print(f"  Warning: No messages key found. Available keys: {list(chat_data.keys())}")
                
                print(f"  Found {len(file_messages)} messages in {msg_file.name}")
                
                # Debug: Show first few messages to understand structure
                if file_messages and len(file_messages) > 0:
                    print(f"  First message keys: {list(file_messages[0].keys())}")
                    print(f"  First message sender: {file_messages[0].get('sender_name', 'N/A')}")
                    print(f"  First message content: {file_messages[0].get('content', 'N/A')[:50]}...")
                    
                    # Show a few more messages to verify they exist
                    if len(file_messages) > 1:
                        print(f"  Second message sender: {file_messages[1].get('sender_name', 'N/A')}")
                        print(f"  Second message content: {file_messages[1].get('content', 'N/A')[:50]}...")
                    
                    # Show messages from the specific friend we're looking for
                    friend_messages = [msg for msg in file_messages if msg.get('sender_name') == friend_name]
                    print(f"  Messages from {friend_name}: {len(friend_messages)}")
                    if friend_messages:
                        print(f"  First {friend_name} message: {friend_messages[0].get('content', 'N/A')[:50]}...")
                    
                    print(f"  Total messages in array: {len(file_messages)}")
                else:
                    print(f"  No messages found in array")
                
                if isinstance(file_messages, list):
                    all_messages.extend(file_messages)
                else:
                    print(f"  Warning: messages is not a list, type: {type(file_messages)}")
                    
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Error reading {msg_file}: {e}")
                continue
        
        print(f"\nSuccessfully read {total_files_read} files")
        print(f"Total messages found: {len(all_messages)}")
        
        if not all_messages:
            print(f"No messages found with {friend_name}")
            return
        
        # Initialize counters
        total_messages = len(all_messages)
        your_messages = 0
        their_messages = 0
        first_timestamp = None
        last_timestamp = None
        
        # Time analysis
        your_message_times = []
        their_message_times = []
        
        # Analyze each message
        for message in all_messages:
            sender = message.get('sender_name', '')
            timestamp_ms = message.get('timestamp_ms', 0)
            
            # Count messages by sender
            if sender == USER_NAME:
                your_messages += 1
                if timestamp_ms:
                    your_message_times.append(timestamp_ms)
            elif sender == friend_name:
                their_messages += 1
                if timestamp_ms:
                    their_message_times.append(timestamp_ms)
            
            # Track timestamps
            if timestamp_ms:
                if first_timestamp is None or timestamp_ms < first_timestamp:
                    first_timestamp = timestamp_ms
                if last_timestamp is None or timestamp_ms > last_timestamp:
                    last_timestamp = timestamp_ms
        
        # Convert timestamps to readable dates
        first_date = datetime.fromtimestamp(first_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S') if first_timestamp else "Unknown"
        last_date = datetime.fromtimestamp(last_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S') if last_timestamp else "Unknown"
        
        # Print analysis results
        print(f"\n📊 Message Analysis with {friend_name}")
        print("=" * 50)
        print(f"Total messages: {total_messages}")
        print(f"Messages sent by you: {your_messages}")
        print(f"Messages sent by {friend_name}: {their_messages}")
        print(f"First message: {first_date}")
        print(f"Last message: {last_date}")
        
        # Additional statistics
        if total_messages > 0:
            your_percentage = (your_messages / total_messages) * 100
            their_percentage = (their_messages / total_messages) * 100
            print(f"Your message percentage: {your_percentage:.1f}%")
            print(f"{friend_name}'s message percentage: {their_percentage:.1f}%")
        
        # Analyze message timing
        analyze_message_timing(your_message_times, their_message_times, friend_name)
        
        # Analyze response times
        analyze_response_times(all_messages, friend_name)
        
        # Analyze message content
        analyze_message_content(all_messages, friend_name)
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading message data: {e}")
    except Exception as e:
        print(f"An error occurred during analysis: {e}")

def analyze_message_content(messages, friend_name):
    """
    Analyze message content for word frequency, average message length, emojis, and shared posts.
    
    Args:
        messages (list): List of message dictionaries
        friend_name (str): Name of the friend being analyzed
    """
    USER_NAME = "Rayaan Raza"
    
    # Common stopwords to exclude
    stopwords = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 
        'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 
        'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 
        'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 
        'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 
        'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 
        'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 
        'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 
        'us', 'is', 'are', 'was', 'were', 'been', 'being', 'have', 'has', 'had', 'do', 
        'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
        'oh', 'yeah', 'yes', 'no', 'ok', 'okay', 'haha', 'lol', 'omg', 'wow', 'hey', 'hi',
        'hello', 'bye', 'goodbye', 'thanks', 'thank', 'you', 'your', 'yours', 'yourself',
        'yourselves', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves'
    }
    
    # Separate messages by sender
    your_messages = []
    their_messages = []
    
    # Track emojis and shared posts
    your_emojis = []
    their_emojis = []
    your_shared_posts = 0
    their_shared_posts = 0
    
    # Debug: Track message types
    debug_message_types = {"your_urls": 0, "their_urls": 0, "your_text": 0, "their_text": 0}
    
    for message in messages:
        sender = message.get('sender_name', '')
        content = message.get('content', '')
        
        # Debug: Show message structure for first few messages
        if len(messages) <= 10 or messages.index(message) < 5:
            print(f"DEBUG: Message from {sender}: {content[:100]}...")
            print(f"DEBUG: Message keys: {list(message.keys())}")
            # Check for additional fields that might indicate shared content
            for key, value in message.items():
                if key not in ['sender_name', 'timestamp_ms', 'content']:
                    print(f"DEBUG: Additional field '{key}': {value}")
        
        # Skip messages without content (media-only messages)
        if not content or not content.strip():
            continue
            
        # Skip messages that are just media indicators or system messages
        PLACEHOLDER_PHRASES = [
            "sent a photo", "sent a video", "sent a reel", "sent an attachment",
            "unsent a message", "reacted to", "video call", "missed video call",
            "you sent an attachment", "you unsent a message", "this message is no longer available",
            "sent a voice message", "sent a sticker", "sent a gif", "sent a story reply",
            "tayyab sent an attachment"  # Add this specific case from your data
        ]
        
        # Check if content matches any placeholder phrase
        content_lower = content.lower()
        if any(phrase.lower() in content_lower for phrase in PLACEHOLDER_PHRASES):
            continue
        
        # Check for shared posts (Instagram post links) - BEFORE URL filtering
        # Instagram links can be in various formats
        instagram_patterns = [
            "instagram.com/p/",
            "instagram.com/reel/",
            "instagram.com/tv/",
            "ig.me/p/",
            "ig.me/reel/",
            "ig.me/tv/"
        ]
        
        is_instagram_post = any(pattern in content for pattern in instagram_patterns)
        
        # Also check for story replies which might indicate shared content
        is_story_reply = "story reply" in content_lower or "replied to story" in content_lower
        
        if is_instagram_post or is_story_reply:
            if sender == USER_NAME:
                your_shared_posts += 1
                print(f"DEBUG: Found your shared content: {content[:100]}...")
            elif sender == friend_name:
                their_shared_posts += 1
                print(f"DEBUG: Found {friend_name}'s shared content: {content[:100]}...")
            continue  # Skip shared posts from text analysis
        
        # Skip other URLs (links shared) - but not Instagram posts
        if content.startswith('http') and not is_instagram_post:
            if sender == USER_NAME:
                debug_message_types["your_urls"] += 1
            elif sender == friend_name:
                debug_message_types["their_urls"] += 1
            continue
        
        # Extract emojis from content
        emojis_in_message = emoji.emoji_list(content)
        emoji_chars = [e['emoji'] for e in emojis_in_message]
        
        if sender == USER_NAME:
            your_messages.append(content)
            your_emojis.extend(emoji_chars)
            debug_message_types["your_text"] += 1
        elif sender == friend_name:
            their_messages.append(content)
            their_emojis.extend(emoji_chars)
            debug_message_types["their_text"] += 1
    
    # Analyze your messages
    print(f"\n📝 Your Message Content Analysis")
    print("-" * 40)
    if your_messages:
        your_avg_length = analyze_sender_messages(your_messages, stopwords, "You")
        analyze_emojis(your_emojis, "You")
        print(f"Posts shared: {your_shared_posts}")
    else:
        print("No text messages found from you.")
        print("Posts shared: 0")
    
    # Analyze their messages
    print(f"\n📝 {friend_name}'s Message Content Analysis")
    print("-" * 40)
    if their_messages:
        their_avg_length = analyze_sender_messages(their_messages, stopwords, friend_name)
        analyze_emojis(their_emojis, friend_name)
        print(f"Posts shared: {their_shared_posts}")
    else:
        print(f"No text messages found from {friend_name}.")
        print("Posts shared: 0")
    
    # Compare average lengths if both have messages
    if your_messages and their_messages:
        print(f"\n📊 Message Length Comparison")
        print("-" * 40)
        if your_avg_length > their_avg_length:
            print(f"You write longer messages on average ({your_avg_length:.1f} vs {their_avg_length:.1f} words)")
        elif their_avg_length > your_avg_length:
            print(f"{friend_name} writes longer messages on average ({their_avg_length:.1f} vs {your_avg_length:.1f} words)")
        else:
            print(f"Both of you write messages of similar length ({your_avg_length:.1f} words average)")
    
    # Compare emoji usage
    print(f"\n😊 Emoji Usage Comparison")
    print("-" * 40)
    print(f"Your emojis sent: {len(your_emojis)}")
    print(f"{friend_name}'s emojis sent: {len(their_emojis)}")
    
    if your_emojis and their_emojis:
        if len(your_emojis) > len(their_emojis):
            print(f"You use more emojis ({len(your_emojis)} vs {len(their_emojis)})")
        elif len(their_emojis) > len(your_emojis):
            print(f"{friend_name} uses more emojis ({len(their_emojis)} vs {len(your_emojis)})")
        else:
            print(f"Both of you use the same number of emojis ({len(your_emojis)})")
    
    # Compare post sharing
    print(f"\n📱 Post Sharing Comparison")
    print("-" * 40)
    print(f"Your posts shared: {your_shared_posts}")
    print(f"{friend_name}'s posts shared: {their_shared_posts}")
    
    if your_shared_posts > 0 or their_shared_posts > 0:
        if your_shared_posts > their_shared_posts:
            print(f"You share more posts ({your_shared_posts} vs {their_shared_posts})")
        elif their_shared_posts > your_shared_posts:
            print(f"{friend_name} shares more posts ({their_shared_posts} vs {your_shared_posts})")
        else:
            print(f"Both of you share the same number of posts ({your_shared_posts})")
    else:
        print("No posts were shared in this conversation.")
    
    # Debug output
    print(f"\n🔍 DEBUG: Message Type Breakdown")
    print("-" * 40)
    print(f"Your text messages: {debug_message_types['your_text']}")
    print(f"Your URLs (non-Instagram): {debug_message_types['your_urls']}")
    print(f"{friend_name}'s text messages: {debug_message_types['their_text']}")
    print(f"{friend_name}'s URLs (non-Instagram): {debug_message_types['their_urls']}")
    print(f"Your Instagram posts: {your_shared_posts}")
    print(f"{friend_name}'s Instagram posts: {their_shared_posts}")

def analyze_sender_messages(messages, stopwords, sender_name):
    """
    Analyze messages from a specific sender.
    
    Args:
        messages (list): List of message content strings
        stopwords (set): Set of stopwords to exclude
        sender_name (str): Name of the sender for display
    Returns:
        float: Average message length in words
    """
    all_words = []
    total_words = 0
    
    for message in messages:
        # Clean and tokenize the message
        words = re.findall(r'\b[a-zA-Z]+\b', message.lower())
        # Filter out stopwords and short words
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        all_words.extend(filtered_words)
        total_words += len(filtered_words)
    
    # Calculate average message length
    avg_length = total_words / len(messages) if messages else 0
    print(f"Average message length: {avg_length:.1f} words")
    print(f"Total text messages: {len(messages)}")
    
    # Get top 10 most common words
    if all_words:
        word_counts = Counter(all_words)
        top_words = word_counts.most_common(10)
        
        print(f"Top 10 most common words:")
        for i, (word, count) in enumerate(top_words, 1):
            print(f"  {i:2d}. '{word}' ({count} times)")
    else:
        print("No words found after filtering.")
    
    return avg_length

def analyze_emojis(emojis, sender_name):
    """
    Analyze emojis sent by a specific sender.
    
    Args:
        emojis (list): List of emoji characters
        sender_name (str): Name of the sender for display
    """
    if not emojis:
        print(f"No emojis found from {sender_name}.")
        return
    
    print(f"Emojis sent: {len(emojis)}")
    
    # Count unique emojis
    unique_emojis = set(emojis)
    print(f"Unique emojis used: {len(unique_emojis)}")
    
    # Get top 10 most common emojis
    emoji_counts = Counter(emojis)
    top_emojis = emoji_counts.most_common(10)
    
    if top_emojis:
        print(f"Top 10 most common emojis:")
        for i, (emoji_char, count) in enumerate(top_emojis, 1):
            print(f"  {i:2d}. '{emoji_char}' ({count} times)")
    else:
        print("No emojis found.")

def analyze_message_timing(your_message_times, their_message_times, friend_name):
    """
    Analyze message timing patterns including most common hours and days.
    
    Args:
        your_message_times (list): List of timestamps for your messages
        their_message_times (list): List of timestamps for their messages
        friend_name (str): Name of the friend being analyzed
    """
    if not your_message_times and not their_message_times:
        print(f"\n⏰ No message timing data available for {friend_name}.")
        return

    print(f"\n⏰ Message Timing Analysis with {friend_name}")
    print("=" * 50)
    
    # Analyze your message timing
    if your_message_times:
        print(f"\n📱 Your Message Timing")
        print("-" * 30)
        analyze_sender_timing(your_message_times, "You")
    else:
        print(f"\n📱 Your Message Timing")
        print("-" * 30)
        print("No messages sent by you.")
    
    # Analyze their message timing
    if their_message_times:
        print(f"\n📱 {friend_name}'s Message Timing")
        print("-" * 30)
        analyze_sender_timing(their_message_times, friend_name)
    else:
        print(f"\n📱 {friend_name}'s Message Timing")
        print("-" * 30)
        print(f"No messages sent by {friend_name}.")
    
    # Compare timing patterns
    if your_message_times and their_message_times:
        print(f"\n🔄 Timing Pattern Comparison")
        print("-" * 40)
        compare_timing_patterns(your_message_times, their_message_times, friend_name)

def analyze_sender_timing(message_times, sender_name):
    """
    Analyze timing patterns for a specific sender.
    
    Args:
        message_times (list): List of timestamps
        sender_name (str): Name of the sender
    """
    # Convert timestamps to datetime objects
    message_datetimes = [datetime.fromtimestamp(ts / 1000) for ts in message_times]
    
    # Extract hours and days
    hours = [dt.hour for dt in message_datetimes]
    days = [dt.strftime('%A') for dt in message_datetimes]
    
    # Count occurrences
    hour_counts = Counter(hours)
    day_counts = Counter(days)
    
    # Most common hours (top 5)
    print(f"Most active hours:")
    top_hours = hour_counts.most_common(5)
    for hour, count in top_hours:
        hour_str = f"{hour:02d}:00-{hour:02d}:59"
        percentage = (count / len(hours)) * 100
        print(f"  {hour_str}: {count} messages ({percentage:.1f}%)")
    
    # Most common days (all days)
    print(f"\nMost active days:")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        if day in day_counts:
            count = day_counts[day]
            percentage = (count / len(days)) * 100
            print(f"  {day}: {count} messages ({percentage:.1f}%)")
    
    # Time period analysis
    morning_count = sum(1 for h in hours if 6 <= h < 12)
    afternoon_count = sum(1 for h in hours if 12 <= h < 18)
    evening_count = sum(1 for h in hours if 18 <= h < 22)
    night_count = sum(1 for h in hours if h >= 22 or h < 6)
    
    total_messages = len(hours)
    print(f"\nTime period breakdown:")
    print(f"  Morning (6AM-12PM): {morning_count} messages ({(morning_count/total_messages)*100:.1f}%)")
    print(f"  Afternoon (12PM-6PM): {afternoon_count} messages ({(afternoon_count/total_messages)*100:.1f}%)")
    print(f"  Evening (6PM-10PM): {evening_count} messages ({(evening_count/total_messages)*100:.1f}%)")
    print(f"  Night (10PM-6AM): {night_count} messages ({(night_count/total_messages)*100:.1f}%)")

def compare_timing_patterns(your_times, their_times, friend_name):
    """
    Compare timing patterns between two people.
    
    Args:
        your_times (list): Your message timestamps
        their_times (list): Their message timestamps
        friend_name (str): Name of the friend
    """
    your_datetimes = [datetime.fromtimestamp(ts / 1000) for ts in your_times]
    their_datetimes = [datetime.fromtimestamp(ts / 1000) for ts in their_times]
    
    your_hours = [dt.hour for dt in your_datetimes]
    their_hours = [dt.hour for dt in their_datetimes]
    
    # Find peak hours for each person
    your_peak_hour = Counter(your_hours).most_common(1)[0][0] if your_hours else None
    their_peak_hour = Counter(their_hours).most_common(1)[0][0] if their_hours else None
    
    if your_peak_hour is not None and their_peak_hour is not None:
        print(f"Peak messaging hours:")
        print(f"  You: {your_peak_hour:02d}:00-{your_peak_hour:02d}:59")
        print(f"  {friend_name}: {their_peak_hour:02d}:00-{their_peak_hour:02d}:59")
        
        if your_peak_hour == their_peak_hour:
            print(f"  You both are most active at the same time!")
        else:
            hour_diff = abs(your_peak_hour - their_peak_hour)
            print(f"  Peak hours differ by {hour_diff} hour(s)")
    
    # Check if you're both night owls or early birds
    your_night_messages = sum(1 for h in your_hours if h >= 22 or h < 6)
    their_night_messages = sum(1 for h in their_hours if h >= 22 or h < 6)
    
    your_night_percentage = (your_night_messages / len(your_hours)) * 100 if your_hours else 0
    their_night_percentage = (their_night_messages / len(their_hours)) * 100 if their_hours else 0
    
    print(f"\nNight messaging patterns (10PM-6AM):")
    print(f"  You: {your_night_percentage:.1f}% of messages")
    print(f"  {friend_name}: {their_night_percentage:.1f}% of messages")
    
    if your_night_percentage > 30 and their_night_percentage > 30:
        print(f"  You're both night owls! 🌙")
    elif your_night_percentage < 10 and their_night_percentage < 10:
        print(f"  You're both early birds! 🌅")
    elif abs(your_night_percentage - their_night_percentage) > 20:
        print(f"  Different sleep schedules! 😴")
    else:
        print(f"  Similar messaging patterns! 📱")

def analyze_response_times(messages, friend_name):
    """
    Analyze response times between messages and conversation gaps.
    
    Args:
        messages (list): List of message dictionaries
        friend_name (str): Name of the friend being analyzed
    """
    USER_NAME = "Rayaan Raza"
    
    if not messages:
        print(f"\n⏱️ No messages found to analyze response times for {friend_name}.")
        return
    
    print(f"\n⏱️ Response Time Analysis with {friend_name}")
    print("=" * 50)
    
    # Sort messages by timestamp
    sorted_messages = sorted(messages, key=lambda x: x.get('timestamp_ms', 0))
    
    # Initialize tracking variables
    your_response_times = []  # Time between their message and your response
    their_response_times = []  # Time between your message and their response
    conversation_gaps = []  # Gaps longer than 24 hours
    current_conversation_start = None
    last_message_time = None
    
    # Analyze response times
    for i in range(len(sorted_messages) - 1):
        current_msg = sorted_messages[i]
        next_msg = sorted_messages[i + 1]
        
        current_sender = current_msg.get('sender_name', '')
        next_sender = next_msg.get('sender_name', '')
        current_time = current_msg.get('timestamp_ms', 0)
        next_time = next_msg.get('timestamp_ms', 0)
        
        if current_time > 0 and next_time > 0:
            time_diff_seconds = (next_time - current_time) / 1000
            time_diff_hours = time_diff_seconds / 3600
            
            # Track conversation gaps (more than 24 hours)
            if time_diff_hours > 24:
                gap_start = datetime.fromtimestamp(current_time / 1000)
                gap_end = datetime.fromtimestamp(next_time / 1000)
                gap_duration = time_diff_hours
                conversation_gaps.append({
                    'start': gap_start,
                    'end': gap_end,
                    'duration_hours': gap_duration,
                    'duration_days': gap_duration / 24
                })
            
            # Calculate response times (only for actual responses, not gaps)
            if time_diff_hours <= 24:
                if current_sender == friend_name and next_sender == USER_NAME:
                    # They sent a message, you responded
                    your_response_times.append(time_diff_seconds)
                elif current_sender == USER_NAME and next_sender == friend_name:
                    # You sent a message, they responded
                    their_response_times.append(time_diff_seconds)
    
    # Analyze your response times
    print(f"\n📱 Your Response Times to {friend_name}")
    print("-" * 40)
    if your_response_times:
        analyze_sender_response_times(your_response_times, "You")
    else:
        print("No response times found for your messages.")
    
    # Analyze their response times
    print(f"\n📱 {friend_name}'s Response Times to You")
    print("-" * 40)
    if their_response_times:
        analyze_sender_response_times(their_response_times, friend_name)
    else:
        print(f"No response times found for {friend_name}'s messages.")
    
    # Compare response speeds
    if your_response_times and their_response_times:
        print(f"\n🔄 Response Speed Comparison")
        print("-" * 40)
        compare_response_speeds(your_response_times, their_response_times, friend_name)
    
    # Analyze conversation gaps
    print(f"\n⏸️ Conversation Gaps Analysis")
    print("-" * 40)
    analyze_conversation_gaps(conversation_gaps, friend_name)

def analyze_sender_response_times(response_times, sender_name):
    """
    Analyze response times for a specific sender.
    
    Args:
        response_times (list): List of response times in seconds
        sender_name (str): Name of the sender
    """
    if not response_times:
        print(f"No response times found for {sender_name}.")
        return
    
    # Calculate statistics
    avg_time = sum(response_times) / len(response_times)
    median_time = sorted(response_times)[len(response_times) // 2]
    min_time = min(response_times)
    max_time = max(response_times)
    
    # Convert to readable format
    def format_time(seconds):
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    print(f"Total responses analyzed: {len(response_times)}")
    print(f"Average response time: {format_time(avg_time)}")
    print(f"Median response time: {format_time(median_time)}")
    print(f"Fastest response: {format_time(min_time)}")
    print(f"Slowest response: {format_time(max_time)}")
    
    # Response time categories
    instant_responses = sum(1 for t in response_times if t < 60)  # < 1 minute
    quick_responses = sum(1 for t in response_times if 60 <= t < 300)  # 1-5 minutes
    normal_responses = sum(1 for t in response_times if 300 <= t < 3600)  # 5-60 minutes
    slow_responses = sum(1 for t in response_times if 3600 <= t < 86400)  # 1-24 hours
    very_slow_responses = sum(1 for t in response_times if t >= 86400)  # > 24 hours
    
    total = len(response_times)
    print(f"\nResponse time breakdown:")
    print(f"  Instant (< 1 min): {instant_responses} ({instant_responses/total*100:.1f}%)")
    print(f"  Quick (1-5 min): {quick_responses} ({quick_responses/total*100:.1f}%)")
    print(f"  Normal (5-60 min): {normal_responses} ({normal_responses/total*100:.1f}%)")
    print(f"  Slow (1-24 hours): {slow_responses} ({slow_responses/total*100:.1f}%)")
    print(f"  Very slow (> 24 hours): {very_slow_responses} ({very_slow_responses/total*100:.1f}%)")

def compare_response_speeds(your_times, their_times, friend_name):
    """
    Compare response speeds between you and your friend.
    
    Args:
        your_times (list): Your response times
        their_times (list): Their response times
        friend_name (str): Name of the friend
    """
    your_avg = sum(your_times) / len(your_times)
    their_avg = sum(their_times) / len(their_times)
    
    print(f"Average response times:")
    print(f"  You: {your_avg:.1f} seconds")
    print(f"  {friend_name}: {their_avg:.1f} seconds")
    
    if your_avg < their_avg:
        speed_diff = their_avg - your_avg
        print(f"  You respond {speed_diff:.1f} seconds faster on average! 🚀")
    elif their_avg < your_avg:
        speed_diff = your_avg - their_avg
        print(f"  {friend_name} responds {speed_diff:.1f} seconds faster on average! 🚀")
    else:
        print(f"  You both respond at the same speed! ⚡")
    
    # Response consistency
    your_std = (sum((t - your_avg) ** 2 for t in your_times) / len(your_times)) ** 0.5
    their_std = (sum((t - their_avg) ** 2 for t in their_times) / len(their_times)) ** 0.5
    
    print(f"\nResponse consistency (lower = more consistent):")
    print(f"  You: {your_std:.1f} seconds standard deviation")
    print(f"  {friend_name}: {their_std:.1f} seconds standard deviation")
    
    if your_std < their_std:
        print(f"  You have more consistent response times! 📊")
    elif their_std < your_std:
        print(f"  {friend_name} has more consistent response times! 📊")
    else:
        print(f"  You both have similar response consistency! 📊")

def analyze_conversation_gaps(gaps, friend_name):
    """
    Analyze conversation gaps (periods of no communication).
    
    Args:
        gaps (list): List of gap dictionaries
        friend_name (str): Name of the friend
    """
    if not gaps:
        print(f"No conversation gaps found with {friend_name}.")
        return
    
    print(f"Found {len(gaps)} conversation gaps:")
    
    # Sort gaps by duration (longest first)
    gaps_sorted = sorted(gaps, key=lambda x: x['duration_hours'], reverse=True)
    
    # Show top 5 longest gaps
    print(f"\nLongest conversation gaps:")
    for i, gap in enumerate(gaps_sorted[:5], 1):
        start_str = gap['start'].strftime('%Y-%m-%d %H:%M')
        end_str = gap['end'].strftime('%Y-%m-%d %H:%M')
        duration_days = gap['duration_days']
        
        if duration_days >= 1:
            duration_str = f"{duration_days:.1f} days"
        else:
            duration_str = f"{gap['duration_hours']:.1f} hours"
        
        print(f"  {i}. {start_str} to {end_str} ({duration_str})")
    
    # Gap statistics
    gap_durations = [gap['duration_hours'] for gap in gaps]
    avg_gap = sum(gap_durations) / len(gap_durations)
    longest_gap = max(gap_durations)
    shortest_gap = min(gap_durations)
    
    print(f"\nGap statistics:")
    print(f"  Average gap: {avg_gap/24:.1f} days")
    print(f"  Longest gap: {longest_gap/24:.1f} days")
    print(f"  Shortest gap: {shortest_gap/24:.1f} days")
    
    # Gap frequency analysis
    gaps_by_month = {}
    for gap in gaps:
        month_key = gap['start'].strftime('%Y-%m')
        if month_key not in gaps_by_month:
            gaps_by_month[month_key] = 0
        gaps_by_month[month_key] += 1
    
    if gaps_by_month:
        most_gaps_month = max(gaps_by_month.items(), key=lambda x: x[1])
        print(f"  Month with most gaps: {most_gaps_month[0]} ({most_gaps_month[1]} gaps)")
    
    # Friendship intensity based on gaps
    total_gaps = len(gaps)
    if total_gaps == 0:
        print(f"  Friendship intensity: Very high (no gaps!) 💪")
    elif total_gaps <= 3:
        print(f"  Friendship intensity: High (few gaps) 👍")
    elif total_gaps <= 10:
        print(f"  Friendship intensity: Moderate (some gaps) 🤝")
    else:
        print(f"  Friendship intensity: Low (many gaps) 📉")

def perform_social_network_analysis(friends_list, inbox_path):
    """
    Perform comprehensive social network analysis across all friends.
    
    Args:
        friends_list (list): List of all friend names
        inbox_path (Path): Path to the inbox folder
    """
    USER_NAME = "Rayaan Raza"
    
    if not friends_list:
        print("No friends found for social network analysis.")
        return
    
    print(f"Analyzing messaging patterns across {len(friends_list)} friends...")
    
    # Collect data for all friendships
    friendship_data = {}
    successful_analyses = 0
    
    for friend in friends_list:
        print(f"  Analyzing {friend}...")
        friend_data = analyze_friendship_data(friend, inbox_path)
        if friend_data:
            friendship_data[friend] = friend_data
            successful_analyses += 1
        else:
            print(f"    No data found for {friend}")
    
    print(f"\nSuccessfully analyzed {successful_analyses}/{len(friends_list)} friendships")
    
    if not friendship_data:
        print("No friendship data could be analyzed.")
        return
    
    # Debug: Show summary of collected data
    print(f"\n📋 Data Collection Summary:")
    print("-" * 30)
    total_messages = sum(data['total_messages'] for data in friendship_data.values())
    print(f"Total messages across all friendships: {total_messages:,}")
    
    # Show top 5 by message count for verification
    sorted_by_messages = sorted(friendship_data.items(), key=lambda x: x[1]['total_messages'], reverse=True)
    print(f"Top 5 by message count:")
    for i, (friend, data) in enumerate(sorted_by_messages[:5], 1):
        print(f"  {i}. {friend}: {data['total_messages']:,} messages")
    
    # Perform various analyses
    print(f"\n📊 Social Network Analysis Results")
    print("=" * 50)
    
    # 1. Friendship rankings by activity
    rank_friendships_by_activity(friendship_data)
    
    # 2. Messaging pattern comparisons
    compare_messaging_patterns(friendship_data)
    
    # 3. Response time rankings
    rank_friendships_by_response_time(friendship_data)
    
    # 4. Friendship categories
    categorize_friendships(friendship_data)
    
    # 5. Social network insights
    generate_social_insights(friendship_data)

def analyze_friendship_data(friend_name, inbox_path):
    """
    Analyze basic data for a single friendship.
    
    Args:
        friend_name (str): Name of the friend
        inbox_path (Path): Path to the inbox folder
    Returns:
        dict: Friendship data or None if no data found
    """
    USER_NAME = "Rayaan Raza"
    
    # Find the chat folder for this friend
    chat_folder = None
    message_files = []
    
    # Search through all folders to find the one with this friend
    for folder in inbox_path.iterdir():
        if folder.is_dir():
            msg_files = list(folder.glob("message_*.json"))
            if msg_files:
                # Check all message files in this folder to find the right conversation
                for msg_file in msg_files:
                    try:
                        with open(msg_file, 'r', encoding='utf-8') as f:
                            chat_data = json.load(f)
                        
                        if 'participants' in chat_data:
                            participants = [p.get('name', '') for p in chat_data['participants']]
                            # Check if this is a one-to-one chat with the specific friend
                            if (friend_name in participants and USER_NAME in participants and 
                                len(participants) == 2):
                                chat_folder = folder
                                message_files = sorted(msg_files, key=lambda x: x.name)
                                break
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                # If we found the right folder, break out of the outer loop
                if chat_folder:
                    break
    
    if not message_files:
        return None
    
    # Collect basic statistics
    total_messages = 0
    your_messages = 0
    their_messages = 0
    first_timestamp = None
    last_timestamp = None
    your_response_times = []
    their_response_times = []
    
    try:
        # Process all message files for this conversation
        for msg_file in message_files:
            with open(msg_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            
            if 'messages' in chat_data:
                messages = chat_data['messages']
                total_messages += len(messages)
                
                for message in messages:
                    sender = message.get('sender_name', '')
                    timestamp_ms = message.get('timestamp_ms', 0)
                    
                    if sender == USER_NAME:
                        your_messages += 1
                        if timestamp_ms:
                            if first_timestamp is None or timestamp_ms < first_timestamp:
                                first_timestamp = timestamp_ms
                            if last_timestamp is None or timestamp_ms > last_timestamp:
                                last_timestamp = timestamp_ms
                    elif sender == friend_name:
                        their_messages += 1
                        if timestamp_ms:
                            if first_timestamp is None or timestamp_ms < first_timestamp:
                                first_timestamp = timestamp_ms
                            if last_timestamp is None or timestamp_ms > last_timestamp:
                                last_timestamp = timestamp_ms
        
        # Calculate response times (simplified version)
        sorted_messages = []
        for msg_file in message_files:
            with open(msg_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
            if 'messages' in chat_data:
                sorted_messages.extend(chat_data['messages'])
        
        sorted_messages.sort(key=lambda x: x.get('timestamp_ms', 0))
        
        for i in range(len(sorted_messages) - 1):
            current_msg = sorted_messages[i]
            next_msg = sorted_messages[i + 1]
            
            current_sender = current_msg.get('sender_name', '')
            next_sender = next_msg.get('sender_name', '')
            current_time = current_msg.get('timestamp_ms', 0)
            next_time = next_msg.get('timestamp_ms', 0)
            
            if current_time > 0 and next_time > 0:
                time_diff_seconds = (next_time - current_time) / 1000
                time_diff_hours = time_diff_seconds / 3600
                
                if time_diff_hours <= 24:  # Only count as response if within 24 hours
                    if current_sender == friend_name and next_sender == USER_NAME:
                        your_response_times.append(time_diff_seconds)
                    elif current_sender == USER_NAME and next_sender == friend_name:
                        their_response_times.append(time_diff_seconds)
        
        # Calculate averages
        your_avg_response = sum(your_response_times) / len(your_response_times) if your_response_times else 0
        their_avg_response = sum(their_response_times) / len(their_response_times) if their_response_times else 0
        
        # Calculate friendship duration
        friendship_duration_days = 0
        if first_timestamp and last_timestamp:
            duration_seconds = (last_timestamp - first_timestamp) / 1000
            friendship_duration_days = duration_seconds / 86400
        
        # Add debug information
        print(f"    Found {total_messages} messages ({your_messages} yours, {their_messages} theirs) over {friendship_duration_days:.1f} days")
        
        return {
            'total_messages': total_messages,
            'your_messages': your_messages,
            'their_messages': their_messages,
            'your_avg_response': your_avg_response,
            'their_avg_response': their_avg_response,
            'friendship_duration_days': friendship_duration_days,
            'messages_per_day': total_messages / friendship_duration_days if friendship_duration_days > 0 else 0,
            'your_response_count': len(your_response_times),
            'their_response_count': len(their_response_times)
        }
        
    except Exception as e:
        print(f"    Error analyzing {friend_name}: {e}")
        return None

def rank_friendships_by_activity(friendship_data):
    """
    Rank friendships by various activity metrics.
    
    Args:
        friendship_data (dict): Dictionary of friendship data
    """
    print(f"\n🏆 Friendship Rankings by Activity")
    print("-" * 40)
    
    # Sort by total messages
    sorted_by_total = sorted(friendship_data.items(), 
                           key=lambda x: x[1]['total_messages'], reverse=True)
    
    print(f"Top 10 Most Active Friendships (by total messages):")
    for i, (friend, data) in enumerate(sorted_by_total[:10], 1):
        print(f"  {i:2d}. {friend}: {data['total_messages']:,} messages")
    
    # Sort by messages per day
    sorted_by_daily = sorted(friendship_data.items(), 
                           key=lambda x: x[1]['messages_per_day'], reverse=True)
    
    print(f"\nTop 10 Most Active Friendships (by messages per day):")
    for i, (friend, data) in enumerate(sorted_by_daily[:10], 1):
        daily_rate = data['messages_per_day']
        if daily_rate > 0:
            print(f"  {i:2d}. {friend}: {daily_rate:.1f} messages/day")
    
    # Sort by friendship duration
    sorted_by_duration = sorted(friendship_data.items(), 
                              key=lambda x: x[1]['friendship_duration_days'], reverse=True)
    
    print(f"\nLongest Friendships (by duration):")
    for i, (friend, data) in enumerate(sorted_by_duration[:10], 1):
        duration = data['friendship_duration_days']
        if duration > 0:
            print(f"  {i:2d}. {friend}: {duration:.0f} days")

def compare_messaging_patterns(friendship_data):
    """
    Compare messaging patterns across all friendships.
    
    Args:
        friendship_data (dict): Dictionary of friendship data
    """
    print(f"\n📊 Messaging Pattern Comparison")
    print("-" * 40)
    
    # Calculate overall statistics
    total_friendships = len(friendship_data)
    total_messages = sum(data['total_messages'] for data in friendship_data.values())
    avg_messages_per_friendship = total_messages / total_friendships if total_friendships > 0 else 0
    
    print(f"Overall Statistics:")
    print(f"  Total friendships analyzed: {total_friendships}")
    print(f"  Total messages across all friendships: {total_messages:,}")
    print(f"  Average messages per friendship: {avg_messages_per_friendship:.1f}")
    
    # Find most balanced vs. one-sided friendships
    balance_scores = []
    for friend, data in friendship_data.items():
        total = data['total_messages']
        if total > 0:
            your_percentage = (data['your_messages'] / total) * 100
            balance_score = abs(50 - your_percentage)  # How far from 50/50
            balance_scores.append((friend, balance_score, your_percentage))
    
    balance_scores.sort(key=lambda x: x[1])  # Sort by balance (most balanced first)
    
    print(f"\nMost Balanced Friendships (closest to 50/50):")
    for i, (friend, balance_score, your_percentage) in enumerate(balance_scores[:5], 1):
        their_percentage = 100 - your_percentage
        print(f"  {i}. {friend}: You {your_percentage:.1f}% / Them {their_percentage:.1f}%")
    
    print(f"\nMost One-Sided Friendships:")
    for i, (friend, balance_score, your_percentage) in enumerate(balance_scores[-5:], 1):
        their_percentage = 100 - your_percentage
        print(f"  {i}. {friend}: You {your_percentage:.1f}% / Them {their_percentage:.1f}%")

def rank_friendships_by_response_time(friendship_data):
    """
    Rank friendships by response time patterns.
    
    Args:
        friendship_data (dict): Dictionary of friendship data
    """
    print(f"\n⚡ Response Time Rankings")
    print("-" * 40)
    
    # Filter friendships with response data
    friendships_with_responses = [(friend, data) for friend, data in friendship_data.items() 
                                 if data['your_response_count'] > 0 or data['their_response_count'] > 0]
    
    if not friendships_with_responses:
        print("No response time data available.")
        return
    
    # Rank by your response speed
    your_response_rankings = [(friend, data['your_avg_response']) 
                             for friend, data in friendships_with_responses 
                             if data['your_avg_response'] > 0]
    your_response_rankings.sort(key=lambda x: x[1])  # Sort by speed (fastest first)
    
    print(f"Friendships where YOU respond fastest:")
    for i, (friend, avg_time) in enumerate(your_response_rankings[:5], 1):
        if avg_time < 60:
            time_str = f"{avg_time:.1f} seconds"
        elif avg_time < 3600:
            time_str = f"{avg_time/60:.1f} minutes"
        else:
            time_str = f"{avg_time/3600:.1f} hours"
        print(f"  {i}. {friend}: {time_str}")
    
    # Rank by their response speed
    their_response_rankings = [(friend, data['their_avg_response']) 
                              for friend, data in friendships_with_responses 
                              if data['their_avg_response'] > 0]
    their_response_rankings.sort(key=lambda x: x[1])  # Sort by speed (fastest first)
    
    print(f"\nFriendships where THEY respond fastest:")
    for i, (friend, avg_time) in enumerate(their_response_rankings[:5], 1):
        if avg_time < 60:
            time_str = f"{avg_time:.1f} seconds"
        elif avg_time < 3600:
            time_str = f"{avg_time/60:.1f} minutes"
        else:
            time_str = f"{avg_time/3600:.1f} hours"
        print(f"  {i}. {friend}: {time_str}")

def categorize_friendships(friendship_data):
    """
    Categorize friendships into different types.
    
    Args:
        friendship_data (dict): Dictionary of friendship data
    """
    print(f"\n🏷️ Friendship Categories")
    print("-" * 40)
    
    categories = {
        'Best Friends': [],
        'Close Friends': [],
        'Regular Friends': [],
        'Occasional Friends': [],
        'Distant Friends': []
    }
    
    for friend, data in friendship_data.items():
        total_messages = data['total_messages']
        messages_per_day = data['messages_per_day']
        
        if total_messages >= 1000 and messages_per_day >= 2:
            categories['Best Friends'].append(friend)
        elif total_messages >= 500 and messages_per_day >= 1:
            categories['Close Friends'].append(friend)
        elif total_messages >= 200 and messages_per_day >= 0.5:
            categories['Regular Friends'].append(friend)
        elif total_messages >= 50:
            categories['Occasional Friends'].append(friend)
        else:
            categories['Distant Friends'].append(friend)
    
    for category, friends in categories.items():
        if friends:
            print(f"{category} ({len(friends)}):")
            for friend in friends:
                data = friendship_data[friend]
                print(f"  • {friend} ({data['total_messages']} messages, {data['messages_per_day']:.1f}/day)")

def generate_social_insights(friendship_data):
    """
    Generate overall social network insights.
    
    Args:
        friendship_data (dict): Dictionary of friendship data
    """
    print(f"\n💡 Social Network Insights")
    print("-" * 40)
    
    total_friendships = len(friendship_data)
    total_messages = sum(data['total_messages'] for data in friendship_data.values())
    
    # Most active friend
    most_active = max(friendship_data.items(), key=lambda x: x[1]['total_messages'])
    print(f"🎯 Your most active friendship: {most_active[0]} ({most_active[1]['total_messages']:,} messages)")
    
    # Most responsive friend (to you)
    responsive_friends = [(friend, data['their_avg_response']) 
                         for friend, data in friendship_data.items() 
                         if data['their_avg_response'] > 0]
    if responsive_friends:
        most_responsive = min(responsive_friends, key=lambda x: x[1])
        print(f"⚡ Most responsive friend: {most_responsive[0]} ({most_responsive[1]:.1f} seconds avg)")
    
    # Most balanced friendship
    balance_scores = []
    for friend, data in friendship_data.items():
        total = data['total_messages']
        if total > 0:
            your_percentage = (data['your_messages'] / total) * 100
            balance_score = abs(50 - your_percentage)
            balance_scores.append((friend, balance_score))
    
    if balance_scores:
        most_balanced = min(balance_scores, key=lambda x: x[1])
        print(f"⚖️ Most balanced friendship: {most_balanced[0]}")
    
    # Longest friendship
    longest_friendship = max(friendship_data.items(), key=lambda x: x[1]['friendship_duration_days'])
    duration = longest_friendship[1]['friendship_duration_days']
    print(f"⏰ Longest friendship: {longest_friendship[0]} ({duration:.0f} days)")
    
    # Social network health
    active_friendships = sum(1 for data in friendship_data.values() if data['total_messages'] >= 100)
    print(f"📈 Active friendships (100+ messages): {active_friendships}/{total_friendships}")
    
    if active_friendships >= total_friendships * 0.7:
        print(f"🌟 Your social network is very active!")
    elif active_friendships >= total_friendships * 0.5:
        print(f"👍 Your social network is moderately active.")
    else:
        print(f"🤔 Your social network could use more engagement.")

def main():
    """Main function to get ZIP path and extract friends."""
    print("Instagram Friends Extractor & Message Analyzer")
    print("=" * 50)
    
    # Get the ZIP file path from user
    zip_path = input("Please enter the path to your Instagram data ZIP file: ").strip()
    
    if not zip_path:
        print("No path provided. Exiting.")
        return
    
    # Remove quotes if user included them
    zip_path = zip_path.strip('"\'')
    
    # Extract and display friends
    friends_list, inbox_path = extract_instagram_friends(zip_path)
    
    if not friends_list or not inbox_path:
        print("Could not extract friends list. Exiting.")
        return
    
    # Allow user to select a friend for analysis
    selected_friend = select_friend(friends_list)
    
    if selected_friend:
        analyze_messages(selected_friend, inbox_path)
    
    # Perform social network analysis across all friends
    print(f"\n" + "="*60)
    print("🌐 SOCIAL NETWORK ANALYSIS")
    print("="*60)
    perform_social_network_analysis(friends_list, inbox_path)
    
    # Clean up extracted files
    if os.path.exists("extracted_instagram_data"):
        import shutil
        shutil.rmtree("extracted_instagram_data")
        print("\nCleaned up extracted files.")

if __name__ == "__main__":
    main() 