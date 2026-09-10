#!/bin/sh
set -e
progdir=$(cd "$(dirname "$0")" && pwd)
exec >"$progdir/Z3yt-install-logfile.txt" 2>&1

export DEBIAN_FRONTEND=noninteractive
export GIT_TERMINAL_PROMPT=0
export GIT_HTTP_LOW_SPEED_LIMIT=1000
export GIT_HTTP_LOW_SPEED_TIME=60

ok=0
fail() {
    if [ "$ok" -eq 1 ]; then
        return 0
    fi
    echo "ERROR"
    # Braces, not brackets: a bracket makes the cd its own subshell and the
    # python then runs back in the original directory, finds no display module
    # and the failure never reaches the screen.
    ( { cd /temp/Z3yt 2>/dev/null || cd "$progdir/Z3yt" 2>/dev/null; } && \
        python3 -c "import display; display.draw_text('ERROR, CHECK LOGS')" ) || true
    cd / || true
    rm -rf /temp
    exit 1
}
trap fail EXIT

retry() {
    tries=$1
    shift
    n=1
    while [ "$n" -le "$tries" ]; do
        if "$@"; then
            return 0
        fi
        echo "attempt $n/$tries failed: $*"
        n=$((n + 1))
        sleep 5
    done
    return 1
}

msg() {
    # Same fallback as fail(), so a message still draws once /temp has gone.
    ( { cd /temp/Z3yt 2>/dev/null || cd "$progdir/Z3yt" 2>/dev/null; } && \
        python3 -c "import display; display.draw_text('''$1''')" ) || true
}

echo "Z3yt install started $(date)"

# Prefer IPv4: these handhelds often have AAAA records but no working IPv6.
if [ -f /etc/gai.conf ]; then
    grep -q '^precedence ::ffff:0:0/96' /etc/gai.conf 2>/dev/null || \
        echo 'precedence ::ffff:0:0/96  100' >> /etc/gai.conf
else
    echo 'precedence ::ffff:0:0/96  100' > /etc/gai.conf
fi

# If GitHub does not resolve (common on busy/captive WiFi), try public DNS.
if ! getent hosts github.com >/dev/null 2>&1; then
    echo "github.com did not resolve, trying public DNS"
    iface=$(ip route 2>/dev/null | awk '/default/ {print $5; exit}')
    if command -v resolvectl >/dev/null 2>&1 && [ -n "$iface" ]; then
        resolvectl dns "$iface" 1.1.1.1 8.8.8.8 9.9.9.9 || true
    fi
fi

# git or wget is needed to fetch the repo itself; everything else waits until
# afterwards so that it can be reported on screen.
if ! command -v git >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
    apt-get -y -o Acquire::Retries=5 update
    apt-get -y -o Acquire::Retries=5 install git wget
fi

clone_github() {
    rm -rf /temp
    git clone --depth 1 https://github.com/Z3R0C1PH3R/Z3yt.git /temp
}

fetch_tarball() {
    rm -rf /temp /tmp/z3yt.tgz /tmp/z3extract
    mkdir -p /tmp/z3extract
    wget --timeout=60 --tries=8 --retry-connrefused \
        -O /tmp/z3yt.tgz \
        https://codeload.github.com/Z3R0C1PH3R/Z3yt/tar.gz/refs/heads/main
    tar -xzf /tmp/z3yt.tgz -C /tmp/z3extract
    mv /tmp/z3extract/Z3yt-main /temp
    rm -rf /tmp/z3yt.tgz /tmp/z3extract
}

echo "Cloning Z3yt"
if ! retry 4 clone_github; then
    echo "git clone failed, trying GitHub tarball"
    retry 3 fetch_tarball
fi
test -f /temp/Z3yt/display.py
test -f /temp/YouTube-Z3.sh

msg "Installing packages..."
apt-get -y -o Acquire::Retries=5 update
apt-get -y -o Acquire::Retries=5 install git python3-pip mpv wget

msg "Installing packages...
Done
Installing pip dependencies..."
python3 -c "from PIL import Image; import requests" >/dev/null 2>&1 || \
    python3 -m pip install --default-timeout=300 --retries 10 pillow requests

msg "Installing packages...
Done
Installing pip dependencies...
Done
Installing yt-dlp..."
if ! wget --timeout=60 --tries=8 --retry-connrefused \
    -O /usr/bin/yt-dlp \
    https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp; then
    if [ ! -x /usr/bin/yt-dlp ]; then
        echo "yt-dlp download failed and no existing binary"
        exit 1
    fi
    echo "yt-dlp download failed, keeping existing binary"
fi
chmod a+rx /usr/bin/yt-dlp
ln -fs /usr/bin/yt-dlp /usr/bin/youtube-dl

msg "Installing packages...
Done
Installing pip dependencies...
Done
Installing yt-dlp...
Done
Installing Z3yt..."
cp -r /temp/Z3yt /temp/YouTube-Z3.sh "$progdir/"
chmod a+x "$progdir/YouTube-Z3.sh"

ok=1
# Z3apps installs several apps back to back, so it sets Z3APPS_NO_REBOOT and
# restarts once itself at the end. On its own this script still restarts.
if [ -n "$Z3APPS_NO_REBOOT" ]; then last="Done"; else last="Rebooting..."; fi
msg "Installing packages...
Done
Installing pip dependencies...
Done
Installing yt-dlp...
Done
Installing Z3yt...
Done
Install Successful
$last"
cd /
rm -rf /temp
sleep 5
[ -n "$Z3APPS_NO_REBOOT" ] || reboot
