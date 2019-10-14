#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Add ~/bin to PATH
export PATH=${PATH}:~/bin

# Use gpg-agent as ssh-agent
unset SSH_AGENT_PID
if [[ "${gnupg_SSH_AUTH_SOCK_by:-0}" -ne $$ ]]; then
    export SSH_AUTH_SOCK="$(gpgconf --list-dirs agent-ssh-socket)"
fi

# Configure pinentry to use the correct TTY
export GPG_TTY=$(tty)
gpg-connect-agent updatestartuptty /bye >/dev/null

# Set color prompt
PS1='\[\033[01;32m\]\u@\h:\[\033[01;34m\]\w\[\033[00m\]$ '

# Search history with arrows
bind '"\e[A": history-search-backward'
bind '"\e[B": history-search-forward'

# Load bash aliases
if [[ -f ~/.bash_aliases ]]; then
    source ~/.bash_aliases
fi
