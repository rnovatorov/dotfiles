# Set vim as editor
export EDITOR=vim

# Add ~/bin to PATH
export PATH=${PATH}:~/bin

# Set ssh-agent socket
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"

# Set GOPATH
export GOPATH=~/code/go

# Add GOPATH/bin to PATH
export PATH=${PATH}:${GOPATH}/bin

# Load .bashrc
[[ -f ~/.bashrc ]] && . ~/.bashrc

# Start X
if systemctl -q is-active graphical.target && [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
    exec startx
fi
