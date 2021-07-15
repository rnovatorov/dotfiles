# Set alacritty as terminal
export TERMINAL=alacritty

# Set nvim as editor
export EDITOR=nvim
export VISUAL=${EDITOR}

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
