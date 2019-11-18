" Show the active mode
set showmode

" Enable line numbering
set number

" Use system clipboard
set clipboard=unnamedplus

" Disable backup and swapfile
set nobackup
set nowritebackup
set noswapfile

" Set short interval for `CursorHold` autocommand event
set updatetime=100

" Enable support for russian keyboard layout
set spelllang=ru_yo,en_us
set keymap=russian-jcukenwin
set iminsert=0
set imsearch=0

" Set map leader
let mapleader = ","

" Set `jkl;` as a homerow
noremap h ;
noremap ; l
noremap l k
noremap k j
noremap j h

" Use `kl` to enter command mode
inoremap kl <ESC>

" Navigate windows with `jkl;`
nnoremap <C-w>h <C-w>;
nnoremap <C-w>; <C-w>l
nnoremap <C-w>l <C-w>k
nnoremap <C-w>k <C-w>j
nnoremap <C-w>j <C-w>h

" Bash-like keys for command line
cnoremap <C-a> <Home>
cnoremap <C-e> <End>

" Plugins
call plug#begin()

Plug 'ctrlpvim/ctrlp.vim'
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'airblade/vim-gitgutter'
Plug 'scrooloose/nerdcommenter'
Plug 'dense-analysis/ale'
Plug 'fatih/vim-go'

call plug#end()

" NERDTree mappings
noremap <Leader>nt :NERDTreeToggle<CR>
noremap <Leader>nf :NERDTreeFind<CR>
