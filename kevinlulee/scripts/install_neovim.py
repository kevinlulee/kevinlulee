
import nvim
import kevinlulee as kx

def has_fuse():
    # Check if fusermount binary exists
    if shutil.which("fusermount") or shutil.which("fusermount3"):
        return True

    # Try checking loaded kernel modules
    try:
        output = subprocess.check_output(["lsmod"], text=True)
        if "fuse" in output.lower():
            return True
    except Exception:
        pass

    return False


# https://github.com/neovim/neovim/releases/download/nightly/nvim-linux-x86_64.appimage
# https://github.com/neovim/neovim/releases/download/nightly/nvim-win-arm64.msi
# https://github.com/neovim/neovim/releases
# it doesnt work
path = '/mnt/chromeos/MyFiles/Downloads/nvim-linux-x86_64.appimage'
if __name__ == "__main__":
    # chmod(path)
    # main()
    # print(has_fuse())
    # kx.clip(kx.get_most_recently_downloaded_file())
    # inline_request()
    print()



