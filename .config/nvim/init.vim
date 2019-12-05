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

" Use Bash-like keys for command line
cnoremap <C-a> <Home>
cnoremap <C-e> <End>

" List plugins
call plug#begin()

Plug 'ctrlpvim/ctrlp.vim'
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'dense-analysis/ale'

call plug#end()

" Configure CtrlP
let g:ctrlp_map = '<leader>ff'

" Configure NERDTree
noremap <Leader>nt :NERDTreeToggle<CR>
noremap <Leader>nf :NERDTreeFind<CR>

" Confiure ALE
noremap <Leader>gd :ALEGoToDefinition<CR>
noremap <Leader>gy :ALEGoToTypeDefinition<CR>
noremap <Leader>gr :ALEFindReferences<CR>

let g:ale_fix_on_save = 1

let g:ale_linters = {
\   'go': ['gopls'],
\   'python': ['pyls'],
\}

let g:ale_fixers = {
\   'go': ['goimports'],
\   'python': ['black'],
\}
