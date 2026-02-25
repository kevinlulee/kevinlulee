from __future__ import annotations
import nvim
import kevinlulee as kx

a = "/home/kdog3682/projects/webdev/primer-react"
p = kx.get_paths(a, include='stories.tsx', depth = 0)
nvim.fs.clip(p)
