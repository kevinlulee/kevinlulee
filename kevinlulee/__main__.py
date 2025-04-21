# from pprint import pprint
# from kevinlulee import fdfind, clip

# python3('/home/kdog3682/projects/python/kevinlulee/kevinlulee/__main__.py', as_module=True)
# this would be recursive
temp = [
        "/home/kdog3682/2023/.git/",
        "/home/kdog3682/2023/~/GITHUB/typst-fletcher/.git/",
        "/home/kdog3682/2024/.git/",
        "/home/kdog3682/2024/prosemirror-math/.git/",
        "/home/kdog3682/2024-javascript/.git/",
        "/home/kdog3682/2024-javascript/csx/.git/",
        "/home/kdog3682/2024-javascript/datetime/.git/",
        "/home/kdog3682/2024-javascript/evalenv/.git/",
        "/home/kdog3682/2024-javascript/js-toolkit/.git/",
        "/home/kdog3682/2024-javascript/my-daily-tracker-website/.git/",
        "/home/kdog3682/2024-javascript/nodekit/.git/",
        "/home/kdog3682/2024-javascript/shapelang/.git/",
        "/home/kdog3682/2024-javascript/staging/.git/",
        "/home/kdog3682/2024-javascript/stdlib/.git/",
        "/home/kdog3682/2024-javascript/tml/.git/",
        "/home/kdog3682/2024-javascript/ttt/.git/",
        "/home/kdog3682/2024-javascript/txflow/.git/",
        "/home/kdog3682/2024-javascript/vuekit/.git/",
        "/home/kdog3682/@bkl/.git/",
        "/home/kdog3682/PYTHON/.git/",
        "/home/kdog3682/archive/2024-python/.git/",
        "/home/kdog3682/archive/2024-typst/.git/",
        "/home/kdog3682/archive/RESOURCES/.git/",
        "/home/kdog3682/kevinlulee/pytypst/.git/",
        "/home/kdog3682/kevinlulee/usefulscripts/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/lezer-ast-explorer/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/local-file-server/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/luli/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/react-codemirror-component/.git/",
        "/home/kdog3682/projects/old_projects/MyWebsites/tsx-react-stylex-quickstart/.git/",
        "/home/kdog3682/projects/old_projects/VSCodeExtensions/qwe-jump/.git/",
        "/home/kdog3682/projects/old_projects/appscript/.git/",
        "/home/kdog3682/projects/old_projects/crispy-umbrella/.git/",
        "/home/kdog3682/projects/old_projects/foxscribe/.git/",
        "/home/kdog3682/projects/old_projects/gdpm/.git/",
        "/home/kdog3682/projects/old_projects/greenleaf/.git/",
        "/home/kdog3682/projects/old_projects/hammymath/.git/",
        "/home/kdog3682/projects/old_projects/luli/.git/",
        "/home/kdog3682/projects/old_projects/mmgg/.git/",
        "/home/kdog3682/projects/old_projects/my-vitesse-app/.git/",
        "/home/kdog3682/projects/old_projects/pearbook/.git/",
        "/home/kdog3682/projects/python/kevinlulee/.git/",
        "/home/kdog3682/projects/python/maelstrom/.git/",
        "/home/kdog3682/projects/python/maelstrom2/.git/",
        "/home/kdog3682/projects/python/pytypst/.git/",
        "/home/kdog3682/projects/typst/csg5/.git/",
        "/home/kdog3682/projects/typst/mathbook/.git/",
        "/home/kdog3682/projects/typst/mathematical/.git/",
        "/home/kdog3682/projects/typst/typkit/.git/",
        "/home/kdog3682/documents/.git/",
        "/home/kdog3682/dotfiles/.git/",
]

# moved to maelstrom/plugins



s = """
    
local params = vim.lsp.util.make_position_params()

vim.g.abcd = vim.fn.json_encode(params)
vim.lsp.buf_request(0, 'textDocument/references', params, function(err, result, ctx, config)
  if err then
    vim.g.abc = err.message
    return
  end

  local json = vim.fn.json_encode(result)
  print(json)
end)

"""

s = """
-- Function to go to definition
local function go_to_definition()
  local params = vim.lsp.util.make_position_params()
  
  vim.lsp.buf_request(0, 'textDocument/definition', params, function(err, result, ctx, config)
    if err then
      print("Error: " .. (err.message or "unknown error"))
      return
    end
    
    if not result or vim.tbl_isempty(result) then
      print("No definition found")
      return
    end
    
    -- Handle both single result and array of results
    if result[1] then
      -- Multiple results, use the first one
      vim.lsp.util.jump_to_location(result[1], vim.lsp.get_client_by_id(ctx.client_id).offset_encoding)
    else
      -- Single result
      vim.lsp.util.jump_to_location(result, vim.lsp.get_client_by_id(ctx.client_id).offset_encoding)
    end
  end)
end

-- Call the function to go to definition
go_to_definition()
"""
import vim
vim.exec_lua(s)

a = 1
a = 1
abc = 111
alphalphalphalphalphalphalpha = abc

b = a
import time
time.sleep(0.5)
print(vim.vars.get('abc'))
print(vim.vars.get('abcd'))
