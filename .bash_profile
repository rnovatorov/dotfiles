#
# ~/.bash_profile
#

# Set vim as editor
export EDITOR=vim
export VISUAL=vim

# Add ~/bin to PATH
export PATH=${PATH}:~/bin

# Set ssh-agent socket
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"

# Load .bashrc
[[ -f ~/.bashrc ]] && . ~/.bashrc

# Start X
if systemctl -q is-active graphical.target && [[ ! $DISPLAY && $XDG_VTNR -eq 1 ]]; then
    exec startx
fi
