#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Add ~/bin to PATH
export PATH=${PATH}:~/bin

# Export ssh-agent socket
export SSH_AUTH_SOCK="$XDG_RUNTIME_DIR/ssh-agent.socket"

# Set color prompt
PS1='\[\033[01;32m\]\u@\h:\[\033[01;34m\]\w\[\033[00m\]$ '

# Search history with arrows
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# Load bash aliases
if [[ -f ~/.bash_aliases ]]; then
    source ~/.bash_aliases
fi
