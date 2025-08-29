from ruamel.yaml import YAML
import kevinlulee as kx
from io import StringIO

# 1) round-trip YAML instance (preserves comments, order, quotes)
yaml = YAML(typ="rt")
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=2, offset=2)

text = '''
# Global settings
server:
  host: "0.0.0.0"          
  port: 8080         

featureFlags:        # toggles below
  search: true
  beta: false

asdf: |  # asdf
    asdfasdf 
    asdfasdf

#sadfasd
'''
data = yaml.load(text)              # CommentedMap/CommentedSeq objects

# 3) modify values like a normal dict/list
data["featureFlags"]["beta"] = True
data["server"]["port"] = 9090

# 4) optionally add or tweak comments
#    - block comment before a key:
data.yaml_set_comment_before_after_key(
    "featureFlags",
    before="\nFeature toggles (edited with ruamel.yaml)\n"
)
#    - inline end-of-line (EOL) comment on a specific field:
data["server"].yaml_add_eol_comment("port to bind", key="port")

# 5) dump back out; comments/quotes/formatting are preserved
buf = StringIO()
s = yaml.dump(data, buf)
print(buf.getvalue())



