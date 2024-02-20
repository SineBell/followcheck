# Python script to compare who you follow on IG and who follows you

import json
import os
import sys

__version__ = '1.0.0'

"""
    followcheck

    Compare the lists of followers and following Instagram accounts 
    to easily figure out who's not following you back. 
    
    Does NOT get any information from Instagram by itself.
    Requires the user to already have JSON files of followers and following.

    Allows to specify on a dedicated file what accounts you expect are not 
    following you back, so you can focus on the unexpected ones. 

    Creates an output file with account name and Instagram link.
"""

# Input filenames for direct execution
# JSON file containing the following accounts
following_filename      = "following.json"     

# JSON file containing the followers accounts
followers_filename      = "followers_1.json"    

# Optinal simple text file with the accounts you expect are not following you
expected_notfollower    = "exclusion_list.txt"  

# Output filenames for direct execution
# Final list of the (unexpected) accounts that are not following you back
dump_file               = "not_followers.txt"


def parseFileList(filename):
    """
    filename : str

    Returns a list of accounts from a simple text file
    Only one account per line
    """
    with open(filename, 'r') as file:
        filelist = [line.strip() for line in file]
    return filelist

def compareJSON(followingJSON, followersJSON, excludedTXT=None):
    """
    FollowingJSON : str
    FollowersJSON : str
    ExcludedTXT   : str

    Read Meta's JSON files for following and followers accounts
    [Optional] Reads simple text file with excluded accounts
    Gets following that are not followers (and not excluded) 
    Returns a list of dicts of account info

    return : list [ dict1, dict2, ...]
    """
    with open(followingJSON, 'r') as file:
            following = json.load(file)["relationships_following"]
    with open(followersJSON, 'r') as file:
            followers = json.load(file)
    if (excludedTXT is not None):
        excluded = parseFileList(excludedTXT)
        return compare(following, followers, excluded=excluded)
    else:
        return compare(following, followers)

def compare(following, followers, excluded=None):
    """
    Following : list [ dict1, dict2, ...]
    Followers : list [ dict1, dict2, ...]
    excluded  : list [ str1, str2, ...]

    Compares lists for following and followers accounts
    List are made of dicts with accounts info 
    The individual dicts are structured as:
    {
        "title": "",
        "media_list_data": [],
        "string_list_data": [
            {
                "href": "https://www.instagram.com/account_name",
                "value": "account_name",
                "timestamp": 0000000000
            }
        ]
    }

    Returns a list of dicts of account info

    return : list [ dict1, dict2, ...]
    """
    followers_list = [ item['string_list_data'][0]['value'] for item in followers ]
    if (excluded is not None):
        tmp = [ item for item in following if item['string_list_data'][0]['value'] not in followers_list]
        return [ item for item in tmp if item['string_list_data'][0]['value'] not in excluded]
    else:
        return [ item for item in following if item['string_list_data'][0]['value'] not in followers_list]

def main():
    """
    Main script execution
    """
    # Get working directory as 1st argument or just use the current working directory
    if len(sys.argv) > 1:
        files_folder = sys.argv[1]
    else:
        files_folder = os.getcwd()
    
    # Load following file
    try :
        with open(os.path.join(files_folder, following_filename), 'r') as file:
            following = json.load(file)["relationships_following"]
    except FileNotFoundError:
        print(f"ERROR: file {following_filename} not found in {files_folder}")
        sys.exit(1)

    # Load followers file
    try :
        with open(os.path.join(files_folder, followers_filename), 'r') as file:
            followers = json.load(file)
    except FileNotFoundError:
        print(f"ERROR: file {followers_filename} not found in {files_folder}")
        sys.exit(1)

    # Report followers and following 
    print(f"              Accounts that are following you: {len(followers)}")
    print(f"                   Accounts you are following: {len(following)}")

    # Get the total list of accounts that are not following you back
    followers_list = [ item['string_list_data'][0]['value'] for item in followers ]
    notfollowing   = [ item for item in following if item['string_list_data'][0]['value'] not in followers_list ]
    print(f"        Total accounts not following you back: {len(notfollowing)}")
    
    # See if an exclusion list was provided 
    try :
        # Get the exclusion list and remove those account from the final list
        excluded = parseFileList(os.path.join(files_folder, expected_notfollower))
        notfollowing = [ item for item in notfollowing if item['string_list_data'][0]['value'] not in excluded ] 
        print(f"   Unexpected accounts not following you back: {len(notfollowing)}")
    except FileNotFoundError:
        pass
    
    # Generate output file
    with open(os.path.join(files_folder, dump_file), 'w') as file:
        for item in notfollowing:
             file.write(f"{item['string_list_data'][0]['value']}\n")
             file.write(f"{item['string_list_data'][0]['href']}\n\n")

    print(f"                               List dumped on: {os.path.join(files_folder, dump_file)}")



if __name__ == "__main__":
    main()
    