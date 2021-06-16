" Enable line numbering
set number

" Show the active mode
set showmode

" Use system clipboard
set clipboard=unnamedplus

" Disable backup and swapfile
set nobackup
set nowritebackup
set noswapfile

" Split naturally
set splitright
set splitbelow

" Hide buffers when they are abandoned
set hidden

" Enable support for russian keyboard layout
set spelllang=ru_yo,en_us
set keymap=russian-jcukenwin
set iminsert=0
set imsearch=0

" Set CursorHold event trigger timeout
set updatetime=100

" Fix indentation
autocmd FileType proto setlocal tabstop=4 shiftwidth=0 expandtab
autocmd FileType json setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType yaml setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType html setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType xml setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType markdown setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType sql setlocal tabstop=4 shiftwidth=0 expandtab

" No highlighting for sign column
highlight SignColumn none

" Use spaces as vertical separator fill chars
set fillchars-=vert:\| | set fillchars+=vert:\ 

" Set map leader
let mapleader = ","

" Set `jkl;` as a homerow
noremap h ;
noremap ; l
noremap l k
noremap k j
noremap j h

" Use `kl` to enter command mode
inoremap kl <Esc>

" Navigate windows with `jkl;`
nnoremap <C-W>h <C-W>;
nnoremap <C-W>; <C-W>l
nnoremap <C-W>l <C-W>k
nnoremap <C-W>k <C-W>j
nnoremap <C-W>j <C-W>h

" Use Bash-like keys for command line
cnoremap <C-A> <Home>
cnoremap <C-E> <End>

" List plugins
call plug#begin()

Plug 'ctrlpvim/ctrlp.vim'
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'dense-analysis/ale'
Plug 'airblade/vim-gitgutter'

call plug#end()

" Configure CtrlP
let g:ctrlp_map = '<Leader>ff'

" Configure NERDTree
noremap <Leader>tt :NERDTreeToggle<Cr>
noremap <Leader>tf :NERDTreeFind<Cr>

" Configure GitGutter
let g:gitgutter_map_keys = 0
noremap <Leader>hn :GitGutterNextHunk<Cr>
noremap <Leader>hp :GitGutterPrevHunk<Cr>
noremap <Leader>hu :GitGutterUndoHunk<Cr>
noremap <Leader>hs :GitGutterStageHunk<Cr>

" Confiure ALE
noremap <Leader>gd :ALEGoToDefinition<Cr>
noremap <Leader>gy :ALEGoToTypeDefinition<Cr>
noremap <Leader>gr :ALEFindReferences<Cr>
noremap <Leader>rn :ALERename<Cr>

let g:ale_fix_on_save = 1
command! ALEToggleFixOnSave execute "let g:ale_fix_on_save = g:ale_fix_on_save ? 0 : 1"

let g:ale_linters = {
\   'json': [],
\   'markdown': [],
\   'go': ['gopls'],
\   'python': ['pyls', 'pyflakes'],
\   'c': ['clang', 'clangd'],
\   'ruby': ['ruby', 'solargraph'],
\}

let g:ale_fixers = {
\   'json': ['jq'],
\   'markdown': ['prettier'],
\   'go': ['goimports'],
\   'python': ['black'],
\   'c': ['clang-format'],
\   'ruby': ['rubocop'],
\}

let g:ale_c_clangformat_options = '--style "{IndentWidth: 4}"'
let g:ale_c_parse_makefile = 1
