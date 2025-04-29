
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import webbrowser
import time
import os


def generate_ssh_keys(email):
    """
    Generate an SSH key pair for a given email and save it uniquely.

    writes 2 files
    and appends 1 file
    """

    assert "@" in email, f"the email '{email}' needs to be with @"
    email_name = email.split("@")[0]
    account_type = email_name
    private_key_path = os.path.expanduser(f"~/.ssh/id_ed25519_{email_name}")
    if os.path.exists(private_key_path):
        print(f'private key path: "{private_key_path}" already exists. early return')
        return
    public_key_path = f"{private_key_path}.pub"

    # Generate a new private key
    private_key = Ed25519PrivateKey.generate()

    # Serialize the private key to PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption(),  # No passphrase
    )

    # Get the corresponding public key
    public_key = private_key.public_key()

    # Serialize the public key to OpenSSH format with the email as a comment
    public_ssh = (
        public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        + f" {email}".encode()
    )

    # Save the private key to a file
    with open(private_key_path, "wb") as f:
        f.write(private_pem)

    # Save the public key to a file
    with open(public_key_path, "wb") as f:
        f.write(public_ssh)

    print(f"Private key saved to: {private_key_path}")
    print(f"Public key saved to: {public_key_path}")

    template = f"""Host github.com-{account_type}
  HostName github.com
  User git
  IdentityFile {private_key_path}"""
    #
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    with open(ssh_config_path, "a") as f:
        f.write("\n" + template)
        print(f"updated ~/.ssh/config")

    os.system("chmod 600 " + private_key_path)
    # this is necessary 
    webbrowser.open(public_key_path)
    time.sleep(1)


if __name__ == "__main__":
    emails = ["kdog3682@gmail.com", "kevinlulee1@gmail.com"]
    for email in emails:
        generate_ssh_keys(email)
