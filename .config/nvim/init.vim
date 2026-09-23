" Enable line numbering
set number

" Show the active mode
set showmode

" Use OSC52 clipboard when there is no desktop clipboard
if empty($DISPLAY) && empty($WAYLAND_DISPLAY)
  let g:clipboard = 'osc52'
endif

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

" Fix broken auto-indent of comments
:set indentkeys-=0#

" Fix indentation
autocmd FileType proto setlocal tabstop=4 shiftwidth=0 expandtab
autocmd FileType json setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType yaml setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType html setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType xml setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType markdown setlocal tabstop=2 shiftwidth=0 expandtab
autocmd FileType sql setlocal tabstop=4 shiftwidth=0 expandtab
autocmd FileType lua setlocal tabstop=4 shiftwidth=0 expandtab

" Configure colorscheme
set notermguicolors
colorscheme vim

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

Plug 'junegunn/fzf.vim'
Plug 'scrooloose/nerdtree'
Plug 'Xuyuanp/nerdtree-git-plugin'
Plug 'dense-analysis/ale'
Plug 'lewis6991/gitsigns.nvim'

call plug#end()

" Configure FZF
noremap <Leader>ff :Files<Cr>
noremap <Leader>fc :Rg<Cr>

" Configure NERDTree
noremap <Leader>tt :NERDTreeToggle<Cr>
noremap <Leader>tf :NERDTreeFind<Cr>

" Configure Gitsigns
lua << EOF
local ok, gitsigns = pcall(require, 'gitsigns')
if ok then
  gitsigns.setup()
end
EOF
noremap <Leader>hn :Gitsigns next_hunk<Cr>
noremap <Leader>hp :Gitsigns prev_hunk<Cr>
noremap <Leader>hu :Gitsigns undo_stage_hunk<Cr>
noremap <Leader>hr :Gitsigns reset_hunk<Cr>
noremap <Leader>hs :Gitsigns stage_hunk<Cr>
noremap <Leader>hv :Gitsigns preview_hunk<Cr>

" Confiure ALE
let g:ale_pattern_options = {
\   '.*\.env$': {'ale_enabled': 0},
\}

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
\   'python': ['pylsp', 'pyflakes', 'mypy'],
\   'c': ['clang', 'clangd'],
\   'ruby': ['ruby'],
\   'asm': [],
\   'rust': ['rustc', 'rls'],
\   'typescript': ['tsserver'],
\   'typescriptreact': ['tsserver'],
\   'lua': ['luac', 'lua-language-server'],
\   'proto': ['buf-lint'],
\   'sh': ['shellcheck'],
\   'sql': [],
\   'yaml': [],
\}

let g:ale_fixers = {
\   'json': ['jq'],
\   'jsonc': ['biome'],
\   'markdown': ['prettier'],
\   'go': ['goimports', 'gofumpt'],
\   'python': ['black', 'isort'],
\   'c': ['clang-format'],
\   'ruby': [],
\   'asm': [],
\   'rust': ['rustfmt'],
\   'typescript': ['prettier'],
\   'typescriptreact': ['prettier'],
\   'sql': ['pgformatter'],
\   'lua': ['stylua'],
\   'proto': ['buf-format'],
\   'html': ['prettier'],
\   'yaml': ['prettier'],
\}

let g:ale_c_clangformat_options = '--style "{IndentWidth: 4}"'
let g:ale_c_parse_makefile = 1

let g:ale_sql_pgformatter_options = "--no-extra-line --nogrouping --wrap-limit 90 --type-case 2"

let g:ale_json_jq_options = "--indent 4"
let g:ale_biome_options = "--json-formatter-indent-style=space"
