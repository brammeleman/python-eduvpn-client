from typing import List, Dict, Optional, Tuple

from eduvpn.i18n import extract_translation


def input_int(max_: int):
    """
    Request the user to enter a number.
    """
    while True:
        choice = input("\n> ")
        if choice.isdigit() and int(choice) < max_:
            break
        else:
            print("error: invalid choice")
    return int(choice)


def provider_choice(institutes: List[dict], orgs: List[dict]) -> Tuple[str, bool]:
    """
    Ask the user to make a choice from a list of institute and secure internet providers.

    returns:
        url, bool. Bool indicates if it is secure_internet or not.
    """
    print("\nPlease choose server:\n")
    print("Institute access:")
    for i, row in enumerate(institutes):
        print(f"[{i}] {extract_translation(row['display_name'])}")

    print("Secure internet: \n")
    for i, row in enumerate(orgs, start=len(institutes)):
        print(f"[{i}] {extract_translation(row['display_name'])}")

    choice = input_int(max_=len(institutes) + len(orgs))

    if choice < len(institutes):
        return institutes[choice]['base_url'], False
    else:
        org = orgs[choice - len(institutes)]
        return org['secure_internet_home'], True


def menu(institutes: List[dict], orgs: List[dict], search_term: Optional[str] = None) -> Optional[Tuple[str, bool]]:
    """
    returns:
        url, bool. Bool indicates if it is secure_internet or not.
    """
    # todo: add initial search filtering
    return provider_choice(institutes, orgs)


def profile_choice(profiles: List[Dict]) -> str:
    """
    If multiple profiles are available, present user with choice which profile.
    """
    if len(profiles) > 1:
        print("\nplease choose a profile:\n")
        for i, profile in enumerate(profiles):
            print(f" * [{i}] {profile['display_name']}")
        choice = input_int(max_=len(profiles))
        return profiles[int(choice)]['profile_id']
    else:
        return profiles[0]['profile_id']


def write_to_nm_choice() -> bool:
    """
    When Network Manager is available, asks user to add VPN to Network Manager
    """
    print("\nWhat would you like to do with your VPN configuration:\n")
    print("* [0] Write .ovpn file to current directory")
    print("* [1] Add VPN configuration to Network Manager")
    return bool(input_int(max_=2))


def secure_internet_choice(secure_internets: List[dict]) -> Optional[str]:
    print("Do you want to select a secure internet location? If not we use the default.")
    while True:
        choice = input("\n[N/y] > ").strip().lower()
        if choice == 'n' or not choice:
            return None
        elif choice == 'y':
            print("\nplease choose a secure internet server:\n")
            for i, profile in enumerate(secure_internets):
                print(f" * [{i}] {extract_translation(profile['country_code'])}")
            choice = input_int(max_=len(secure_internets))
            return secure_internets[int(choice)]['base_url']
        else:
            print("error: invalid choice, please enter y, n or just leave empty")